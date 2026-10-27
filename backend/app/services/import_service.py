import io
import csv
from datetime import datetime, timezone
from ..models import db, Institution, Bureau, Complaint, CaseAction, ImportBatch, AuditEvent, User
from .overlap_service import scan_complaint_overlaps
from .complaint_service import generate_case_number, calculate_due_date

CSV_HEADERS = [
    "institution_code",
    "institution_name",
    "category",
    "subject",
    "description",
    "bureau_code",
    "priority",
    "external_reference"
]

def get_csv_template() -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)
    writer.writerow([
        "1-10293847",
        "National Institute of Technology Karnataka",
        "Fee Overcharging / Capitation",
        "Illegal laboratory caution deposit collection",
        "Students are being forced to pay unauthorized non-refundable maintenance fees despite AICTE fee circular compliance guidelines.",
        "PGRC",
        "High",
        "CPGRAMS-2026-0891"
    ])
    writer.writerow([
        "1-20491823",
        "Apex Institute of Pharmacy",
        "Faculty Quality / Non-Payment",
        "Non-payment of faculty salary for 5 consecutive months",
        "Management has withheld 6th Pay commission approved salaries and PF contributions for 14 assistant professors.",
        "AB",
        "Medium",
        "PGRC-REF-4421"
    ])
    return output.getvalue()

def preview_csv_import(csv_content: str):
    """
    Parses and validates CSV rows without modifying the database.
    Returns preview summary with valid rows and detailed row-by-row errors.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]

    # Verify minimum required headers
    required = ["category", "subject", "description"]
    missing_headers = [h for h in required if h not in fieldnames]
    if missing_headers:
        return {
            "is_valid": False,
            "error": f"Missing required CSV columns: {', '.join(missing_headers)}. Expected columns: {', '.join(CSV_HEADERS)}"
        }

    bureaus_by_code = {b.code.upper(): b for b in db.session.query(Bureau).all()}
    institutions_by_code = {i.institution_code.strip(): i for i in db.session.query(Institution).all()}
    institutions_by_name = {i.name.strip().lower(): i for i in db.session.query(Institution).all()}

    valid_rows = []
    invalid_rows = []
    row_num = 1

    for row in reader:
        row_num += 1
        cleaned = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
        errors = []

        # Check required fields
        if not cleaned.get("subject"):
            errors.append("Subject is missing")
        if not cleaned.get("description"):
            errors.append("Description is missing")
        if not cleaned.get("category"):
            errors.append("Category is missing")

        # Bureau validation
        bureau_code = cleaned.get("bureau_code", "PGRC").upper()
        bureau = bureaus_by_code.get(bureau_code)
        if not bureau:
            errors.append(f"Invalid Bureau code '{bureau_code}'. Available: {list(bureaus_by_code.keys())}")

        # Institution resolution
        inst_code = cleaned.get("institution_code", "")
        inst_name = cleaned.get("institution_name", "")
        matched_inst = None
        
        if inst_code and inst_code in institutions_by_code:
            matched_inst = institutions_by_code[inst_code]
        elif inst_name and inst_name.lower() in institutions_by_name:
            matched_inst = institutions_by_name[inst_name.lower()]
        elif not inst_code and not inst_name:
            errors.append("Institution code or name must be supplied")
        else:
            errors.append(f"Institution not found in directory ('{inst_code or inst_name}')")

        priority = cleaned.get("priority", "Medium").capitalize()
        if priority not in ["Low", "Medium", "High", "Critical"]:
            priority = "Medium"

        row_data = {
            "row_index": row_num,
            "institution_code": inst_code,
            "institution_name": matched_inst.name if matched_inst else inst_name,
            "institution_id": matched_inst.id if matched_inst else None,
            "category": cleaned.get("category", ""),
            "subject": cleaned.get("subject", ""),
            "description": cleaned.get("description", ""),
            "bureau_code": bureau.code if bureau else bureau_code,
            "bureau_id": bureau.id if bureau else None,
            "priority": priority,
            "external_reference": cleaned.get("external_reference", ""),
        }

        if errors:
            row_data["errors"] = errors
            invalid_rows.append(row_data)
        else:
            valid_rows.append(row_data)

    return {
        "is_valid": True,
        "total_rows": len(valid_rows) + len(invalid_rows),
        "valid_count": len(valid_rows),
        "invalid_count": len(invalid_rows),
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows,
    }

def commit_csv_import(valid_rows: list, filename: str, current_user: User):
    """
    Commits validated rows to PostgreSQL in a transaction.
    Triggers overlap detection and records audit trail.
    """
    if not valid_rows:
        return {"success": False, "error": "No valid rows provided to commit"}

    batch = ImportBatch(
        filename=filename or "import.csv",
        total_rows=len(valid_rows),
        success_rows=0,
        failed_rows=0,
        status="completed",
        created_by_id=current_user.id if current_user else None,
    )
    db.session.add(batch)
    db.session.flush()

    created_complaint_ids = []

    for row in valid_rows:
        try:
            receiving_bureau_id = row.get("bureau_id") or 1
            priority = row.get("priority", "Medium")
            due_at = calculate_due_date(priority)
            case_number = generate_case_number(receiving_bureau_id)

            comp = Complaint(
                case_number=case_number,
                external_reference=row.get("external_reference") or None,
                institution_id=row.get("institution_id"),
                category=row.get("category"),
                subject=row.get("subject"),
                description=row.get("description"),
                receiving_bureau_id=receiving_bureau_id,
                current_bureau_id=receiving_bureau_id,
                priority=priority,
                status="Received",
                due_at=due_at,
                created_by_user_id=current_user.id if current_user else None,
            )
            db.session.add(comp)
            db.session.flush()

            action = CaseAction(
                complaint_id=comp.id,
                action_type="csv_import",
                description=f"Imported via batch #{batch.id} ({filename})",
                old_status=None,
                new_status="Received",
                old_bureau_id=None,
                new_bureau_id=receiving_bureau_id,
                performed_by_id=current_user.id if current_user else None,
            )
            db.session.add(action)
            created_complaint_ids.append(comp.id)
            batch.success_rows += 1
        except Exception as e:
            batch.failed_rows += 1

    # Record Audit Event
    audit = AuditEvent(
        user_id=current_user.id if current_user else None,
        action="CSV_IMPORT_COMMITTED",
        entity_type="ImportBatch",
        entity_id=batch.id,
    )
    audit.set_details({
        "filename": filename,
        "total_committed": batch.success_rows,
        "failed": batch.failed_rows
    })
    db.session.add(audit)
    db.session.commit()

    # Trigger overlap scans for imported complaints
    for cid in created_complaint_ids:
        try:
            scan_complaint_overlaps(cid)
        except Exception:
            pass

    return {
        "success": True,
        "batch_id": batch.id,
        "committed_count": batch.success_rows,
        "failed_count": batch.failed_rows,
    }
