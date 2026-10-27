import io
import csv
from datetime import datetime, timezone
from sqlalchemy import func, and_, or_
from ..models import db, Complaint, Institution, Bureau, CaseLink

def get_dashboard_kpis(bureau_id=None):
    now = datetime.now(timezone.utc)
    base_query = db.session.query(Complaint)
    if bureau_id:
        base_query = base_query.filter(Complaint.current_bureau_id == bureau_id)

    total_complaints = base_query.count()
    open_cases = base_query.filter(Complaint.status.notin_(["Disposed", "Closed"])).count()
    action_required = base_query.filter(Complaint.status.in_(["Action Required", "Under Review"])).count()
    overdue_cases = base_query.filter(
        and_(
            Complaint.status.notin_(["Disposed", "Closed"]),
            Complaint.due_at.isnot(None),
            Complaint.due_at < now
        )
    ).count()
    escalated_cases = base_query.filter(Complaint.status == "Escalated").count()
    disposed_cases = base_query.filter(Complaint.status.in_(["Disposed", "Closed"])).count()

    # Potential overlap backlog
    overlap_query = db.session.query(CaseLink).filter(CaseLink.review_status == "pending")
    unreviewed_overlaps = overlap_query.count()

    return {
        "total_complaints": total_complaints,
        "open_cases": open_cases,
        "action_required": action_required,
        "overdue_cases": overdue_cases,
        "escalated_cases": escalated_cases,
        "disposed_cases": disposed_cases,
        "unreviewed_overlaps": unreviewed_overlaps,
    }

def get_analytics_breakdown(bureau_id=None, state=None):
    # 1. Bureau workload distribution
    bureaus = db.session.query(Bureau).filter(Bureau.is_active == True).all()
    bureau_stats = []
    for b in bureaus:
        total = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id).count()
        open_c = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id, Complaint.status.notin_(["Disposed", "Closed"])).count()
        disposed_c = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id, Complaint.status.in_(["Disposed", "Closed"])).count()
        bureau_stats.append({
            "bureau_id": b.id,
            "name": b.name,
            "code": b.code,
            "total": total,
            "open": open_c,
            "disposed": disposed_c,
        })

    # 2. Status distribution
    status_rows = db.session.query(Complaint.status, func.count(Complaint.id)).group_by(Complaint.status).all()
    status_distribution = {s: cnt for s, cnt in status_rows}

    # 3. Priority distribution
    priority_rows = db.session.query(Complaint.priority, func.count(Complaint.id)).group_by(Complaint.priority).all()
    priority_distribution = {p: cnt for p, cnt in priority_rows}

    # 4. Top categories
    category_rows = db.session.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).order_by(func.count(Complaint.id).desc()).limit(7).all()
    category_distribution = [{"category": c, "count": cnt} for c, cnt in category_rows]

    # 5. Overlap status breakdown
    overlap_rows = db.session.query(CaseLink.relationship_type, func.count(CaseLink.id)).group_by(CaseLink.relationship_type).all()
    overlap_distribution = {rel: cnt for rel, cnt in overlap_rows}

    # 6. State distribution
    state_rows = db.session.query(Institution.state, func.count(Complaint.id)).join(Complaint, Complaint.institution_id == Institution.id).group_by(Institution.state).order_by(func.count(Complaint.id).desc()).limit(8).all()
    state_distribution = [{"state": s, "count": cnt} for s, cnt in state_rows if s]

    return {
        "bureau_workload": bureau_stats,
        "status_distribution": status_distribution,
        "priority_distribution": priority_distribution,
        "category_distribution": category_distribution,
        "overlap_distribution": overlap_distribution,
        "state_distribution": state_distribution,
    }

def generate_cases_csv(bureau_id=None, status=None, priority=None) -> str:
    query = db.session.query(Complaint).join(Institution).join(Bureau, Complaint.current_bureau_id == Bureau.id)

    if bureau_id:
        query = query.filter(Complaint.current_bureau_id == bureau_id)
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Case Number",
        "External Reference",
        "Institution Name",
        "Institution Code",
        "State",
        "Category",
        "Subject",
        "Current Bureau",
        "Assigned Officer",
        "Priority",
        "Status",
        "Received Date",
        "Due Date",
        "Is Overdue",
        "Disposed Date"
    ])

    for c in complaints:
        writer.writerow([
            c.case_number,
            c.external_reference or "N/A",
            c.institution.name if c.institution else "N/A",
            c.institution.institution_code if c.institution else "N/A",
            c.institution.state if c.institution else "N/A",
            c.category,
            c.subject,
            c.current_bureau.code if c.current_bureau else "N/A",
            c.assigned_officer.name if c.assigned_officer else "Unassigned",
            c.priority,
            c.status,
            c.received_at.strftime("%Y-%m-%d") if c.received_at else "",
            c.due_at.strftime("%Y-%m-%d") if c.due_at else "",
            "YES" if c.is_overdue else "NO",
            c.disposed_at.strftime("%Y-%m-%d") if c.disposed_at else "",
        ])

    return output.getvalue()

def get_disposal_rates_report(period="monthly"):
    complaints = db.session.query(Complaint).all()
    groups = {}

    for c in complaints:
        dt = c.received_at or c.created_at
        if not dt:
            continue
        if period == "quarterly":
            quarter = (dt.month - 1) // 3 + 1
            key = f"Q{quarter} {dt.year}"
        else:
            key = dt.strftime("%b %Y")

        if key not in groups:
            groups[key] = {"period": key, "received": 0, "disposed": 0, "pending": 0}
        groups[key]["received"] += 1
        if c.status in ("Disposed", "Closed"):
            groups[key]["disposed"] += 1
        else:
            groups[key]["pending"] += 1

    report = []
    for k, v in groups.items():
        rate = round((v["disposed"] / v["received"] * 100), 1) if v["received"] > 0 else 0.0
        v["disposal_rate"] = rate
        report.append(v)

    return sorted(report, key=lambda x: x["period"], reverse=True)

def get_ageing_report():
    complaints = db.session.query(Complaint).filter(Complaint.status.notin_(["Disposed", "Closed"])).all()
    bands = {
        "< 7 days": {"range": "< 7 days", "count": 0, "cases": []},
        "8 - 15 days": {"range": "8 - 15 days", "count": 0, "cases": []},
        "16 - 30 days": {"range": "16 - 30 days", "count": 0, "cases": []},
        "31 - 60 days": {"range": "31 - 60 days", "count": 0, "cases": []},
        "> 60 days": {"range": "> 60 days", "count": 0, "cases": []},
    }

    for c in complaints:
        days = c.ageing_days
        entry = {
            "case_number": c.case_number,
            "bureau": c.current_bureau.code if c.current_bureau else "",
            "institution": c.institution.name if c.institution else "",
            "permanent_id": c.institution.institution_code if c.institution else "",
            "priority": c.priority,
            "days_pending": days,
            "is_overdue": c.is_overdue
        }
        if days <= 7:
            band_key = "< 7 days"
        elif days <= 15:
            band_key = "8 - 15 days"
        elif days <= 30:
            band_key = "16 - 30 days"
        elif days <= 60:
            band_key = "31 - 60 days"
        else:
            band_key = "> 60 days"

        bands[band_key]["count"] += 1
        bands[band_key]["cases"].append(entry)

    return list(bands.values())

def get_recurring_institutions_report():
    from ..models import Institution
    institutions = db.session.query(Institution).all()
    results = []

    for inst in institutions:
        comps = db.session.query(Complaint).filter_by(institution_id=inst.id).all()
        if len(comps) >= 2:
            bureaus_involved = list(set([c.current_bureau.code for c in comps if c.current_bureau]))
            open_count = sum(1 for c in comps if c.status not in ("Disposed", "Closed"))
            disposed_count = sum(1 for c in comps if c.status in ("Disposed", "Closed"))
            results.append({
                "institution_id": inst.id,
                "institution_name": inst.name,
                "permanent_id": inst.institution_code,
                "state": inst.state,
                "total_complaints": len(comps),
                "open_complaints": open_count,
                "disposed_complaints": disposed_count,
                "bureaus_involved": bureaus_involved,
                "bureau_count": len(bureaus_involved),
            })

    return sorted(results, key=lambda x: x["total_complaints"], reverse=True)

def generate_report_csv(report_type: str) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "disposal":
        data = get_disposal_rates_report("monthly")
        writer.writerow(["Period", "Received Cases", "Disposed Cases", "Pending Cases", "Disposal Rate (%)"])
        for r in data:
            writer.writerow([r["period"], r["received"], r["disposed"], r["pending"], f"{r['disposal_rate']}%"])
    elif report_type == "ageing":
        data = get_ageing_report()
        writer.writerow(["Age Band", "Active Pending Cases"])
        for r in data:
            writer.writerow([r["range"], r["count"]])
    elif report_type == "recurring":
        data = get_recurring_institutions_report()
        writer.writerow(["Permanent ID", "Institution Name", "State", "Total Complaints", "Open Cases", "Disposed Cases", "Bureaus Involved"])
        for r in data:
            writer.writerow([r["permanent_id"], r["institution_name"], r["state"], r["total_complaints"], r["open_complaints"], r["disposed_complaints"], ", ".join(r["bureaus_involved"])])
    else:
        # Default: cases csv
        return generate_cases_csv()

    return output.getvalue()

