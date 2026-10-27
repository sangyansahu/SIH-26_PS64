import secrets
import string
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_, and_, desc, asc
from ..models import db, Complaint, CaseAction, Institution, Bureau, User, AuditEvent, Notification
from .overlap_service import scan_complaint_overlaps

def generate_ticket_number() -> str:
    """
    Generate globally unique ticket number in format AICTE-2026-XXXXXX.
    Uses 6 alphanumeric characters and checks for database uniqueness.
    """
    year = 2026
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(30):
        suffix = "".join(secrets.choice(alphabet) for _ in range(6))
        candidate = f"AICTE-{year}-{suffix}"
        exists = db.session.query(Complaint.id).filter_by(ticket_number=candidate).first()
        if not exists:
            return candidate
    # Fallback to microsecond-based suffix
    fallback_suffix = f"{int(datetime.now(timezone.utc).timestamp() * 1000) % 1000000:06d}"
    return f"AICTE-{year}-{fallback_suffix}"

def generate_case_number(bureau_id: int) -> str:
    bureau = db.session.get(Bureau, bureau_id)
    code = bureau.code if bureau else "GEN"
    year = datetime.now().year
    # Count complaints for this bureau to generate sequential number
    count = db.session.query(Complaint).filter(Complaint.receiving_bureau_id == bureau_id).count() + 1
    return f"AICTE-{year}-{code}-{count:04d}"

def calculate_due_date(priority: str) -> datetime:
    now = datetime.now(timezone.utc)
    p_lower = (priority or "").lower()
    if p_lower == "critical":
        return now + timedelta(days=7)
    elif p_lower == "high":
        return now + timedelta(days=15)
    elif p_lower == "low":
        return now + timedelta(days=45)
    return now + timedelta(days=30)  # Medium / default

def get_complaints(
    search=None,
    status=None,
    priority=None,
    bureau_id=None,
    institution_id=None,
    is_overdue=None,
    sort_by="created_at",
    sort_dir="desc",
    page=1,
    per_page=15,
    user=None
):
    query = db.session.query(Complaint).join(Institution).join(Bureau, Complaint.current_bureau_id == Bureau.id)

    # Permission scoping: officers are focused on their Bureau or all records if configured
    # The requirement states: "An authorized official should be able to open an institution's profile and understand which complaints concern that institution, which departments are handling them... Provide appropriate unauthorized and forbidden responses for restricted modifications"
    # For viewing: authorities have cross-bureau visibility, but officers filtering their own bureau can pass bureau_id.

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Complaint.case_number.ilike(search_term),
                Complaint.external_reference.ilike(search_term),
                Complaint.subject.ilike(search_term),
                Complaint.description.ilike(search_term),
                Complaint.category.ilike(search_term),
                Institution.name.ilike(search_term),
                Institution.institution_code.ilike(search_term),
            )
        )

    if status:
        query = query.filter(Complaint.status == status)

    if priority:
        query = query.filter(Complaint.priority == priority)

    if bureau_id:
        query = query.filter(
            or_(
                Complaint.current_bureau_id == bureau_id,
                Complaint.receiving_bureau_id == bureau_id
            )
        )

    if institution_id:
        query = query.filter(Complaint.institution_id == institution_id)

    if is_overdue is True or str(is_overdue).lower() == "true":
        now = datetime.now(timezone.utc)
        query = query.filter(
            and_(
                Complaint.status.notin_(["Disposed", "Closed"]),
                Complaint.due_at.isnot(None),
                Complaint.due_at < now
            )
        )

    # Sorting
    sort_column = getattr(Complaint, sort_by, Complaint.created_at)
    if sort_dir.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [item.to_dict() for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 1
    }

def get_complaint_by_ticket(ticket_or_case: str):
    """
    Search for a complaint by unique ticket number (AICTE-2026-XXXXXX) or case number.
    """
    if not ticket_or_case:
        return None
    val = ticket_or_case.strip()
    return db.session.query(Complaint).filter(
        or_(
            Complaint.ticket_number.ilike(val),
            Complaint.case_number.ilike(val)
        )
    ).first()

def create_complaint(data: dict, current_user: User = None):
    institution_id = data.get("institution_id")
    if not institution_id:
        # Check if institution_code provided
        code = data.get("institution_code")
        if code:
            inst = db.session.query(Institution).filter_by(institution_code=code).first()
            if inst:
                institution_id = inst.id
    
    if not institution_id:
        inst_name = (data.get("institution_name") or "").strip()
        if inst_name:
            inst = db.session.query(Institution).filter(Institution.name.ilike(inst_name)).first()
            if not inst:
                import random
                code = f"1-{random.randint(10000000, 99999999)}"
                inst = Institution(
                    institution_code=code,
                    name=inst_name,
                    state=data.get("institution_state") or "All India",
                    institution_type="Engineering & Technology"
                )
                db.session.add(inst)
                db.session.flush()
            institution_id = inst.id

    if not institution_id:
        raise ValueError("Valid institution reference is required")

    inst = db.session.get(Institution, institution_id)
    if not inst:
        raise ValueError(f"Institution with ID {institution_id} does not exist")

    category = (data.get("category") or "General Administration").strip()
    priority = data.get("priority")
    if not priority:
        if "ragging" in category.lower():
            priority = "Critical"
        else:
            priority = "Medium"

    receiving_bureau_id = data.get("receiving_bureau_id")
    if not receiving_bureau_id and current_user and current_user.bureau_id:
        receiving_bureau_id = current_user.bureau_id
    
    if not receiving_bureau_id:
        default_bureau = db.session.query(Bureau).first()
        default_id = default_bureau.id if default_bureau else 1
        cat_lower = category.lower()
        if "ragging" in cat_lower:
            rpc = db.session.query(Bureau).filter_by(code="RPC").first()
            receiving_bureau_id = rpc.id if rpc else default_id
        elif any(k in cat_lower for k in ["approval", "accreditation", "infrastructure", "eoa"]):
            ab = db.session.query(Bureau).filter_by(code="AB").first()
            receiving_bureau_id = ab.id if ab else default_id
        elif any(k in cat_lower for k in ["curriculum", "academic", "faculty", "syllabus"]):
            papb = db.session.query(Bureau).filter_by(code="PAPB").first()
            receiving_bureau_id = papb.id if papb else default_id
        elif any(k in cat_lower for k in ["fee", "finance", "scholarship", "fund", "capitation"]):
            fab = db.session.query(Bureau).filter_by(code="FAB").first()
            receiving_bureau_id = fab.id if fab else default_id
        else:
            pgrc = db.session.query(Bureau).filter_by(code="PGRC").first()
            receiving_bureau_id = pgrc.id if pgrc else default_id

    current_bureau_id = data.get("current_bureau_id") or receiving_bureau_id

    # Automatically generate backend-enforced unique ticket number (AICTE-2026-XXXXXX)
    ticket_number = generate_ticket_number()
    case_number = data.get("case_number") or generate_case_number(receiving_bureau_id)
    due_at = data.get("due_at") or calculate_due_date(priority)
    source = data.get("source") or ("Public Portal" if not current_user else "Casework Intake")

    complaint = Complaint(
        ticket_number=ticket_number,
        case_number=case_number,
        external_reference=data.get("external_reference"),
        institution_id=institution_id,
        category=category,
        subject=data.get("subject", "").strip(),
        description=data.get("description", "").strip(),
        complainant_name=(data.get("complainant_name") or "").strip() or None,
        complainant_email=(data.get("complainant_email") or "").strip() or None,
        complainant_mobile=(data.get("complainant_mobile") or "").strip() or None,
        supporting_document_name=data.get("supporting_document_name"),
        supporting_document_url=data.get("supporting_document_url"),
        source=source,
        receiving_bureau_id=receiving_bureau_id,
        current_bureau_id=current_bureau_id,
        assigned_user_id=data.get("assigned_user_id"),
        priority=priority,
        status=data.get("status", "Received"),
        due_at=due_at,
        created_by_user_id=current_user.id if current_user else None,
    )
    db.session.add(complaint)
    db.session.flush()

    # Create initial case action record
    action = CaseAction(
        complaint_id=complaint.id,
        action_type="case_intake",
        description=f"Complaint lodged via {complaint.source}. Ticket: {complaint.ticket_number}. Assigned to Bureau '{complaint.receiving_bureau.code if complaint.receiving_bureau else ''}'. Initial status: '{complaint.status}'.",
        old_status=None,
        new_status=complaint.status,
        old_bureau_id=None,
        new_bureau_id=complaint.current_bureau_id,
        performed_by_id=current_user.id if current_user else None,
    )
    db.session.add(action)

    # Record Audit Event
    audit = AuditEvent(
        user_id=current_user.id if current_user else None,
        action="COMPLAINT_CREATED",
        entity_type="Complaint",
        entity_id=complaint.id,
    )
    audit.set_details({
        "ticket_number": complaint.ticket_number,
        "case_number": complaint.case_number,
        "institution_id": complaint.institution_id,
        "priority": complaint.priority,
        "category": complaint.category,
        "source": complaint.source,
    })
    db.session.add(audit)
    db.session.commit()

    # Trigger automatic cross-bureau overlap detection scan
    try:
        scan_complaint_overlaps(complaint.id)
    except Exception as e:
        # Overlap scan should not fail complaint registration
        pass

    return complaint

def update_complaint_status(complaint_id: int, new_status: str, remarks: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Public complainants cannot modify complaint status"

    if not current_user.is_system_admin and current_user.bureau_id and comp.current_bureau_id:
        if current_user.bureau_id != comp.current_bureau_id:
            return None, "Forbidden: Officers cannot modify cases belonging to another Bureau"

    old_status = comp.status
    comp.status = new_status
    comp.last_action_at = datetime.now(timezone.utc)

    if new_status in ("Disposed", "Closed"):
        comp.disposed_at = datetime.now(timezone.utc)
        comp.resolution_summary = remarks

    action = CaseAction(
        complaint_id=comp.id,
        action_type="status_change",
        description=remarks or f"Status changed from {old_status} to {new_status}",
        old_status=old_status,
        new_status=new_status,
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    audit = AuditEvent(
        user_id=current_user.id,
        action="STATUS_UPDATED",
        entity_type="Complaint",
        entity_id=comp.id,
    )
    audit.set_details({"old_status": old_status, "new_status": new_status, "remarks": remarks})
    db.session.add(audit)
    db.session.commit()

    return comp, None

def assign_complaint(complaint_id: int, assign_to_user_id: int, remarks: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Public complainants cannot assign complaints"

    if not current_user.is_system_admin and current_user.bureau_id and comp.current_bureau_id:
        if current_user.bureau_id != comp.current_bureau_id:
            return None, "Forbidden: Officers cannot assign cases belonging to another Bureau"

    target_user = db.session.get(User, assign_to_user_id) if assign_to_user_id else None
    old_assigned_id = comp.assigned_user_id
    comp.assigned_user_id = assign_to_user_id
    comp.last_action_at = datetime.now(timezone.utc)

    action_desc = f"Case assigned to {target_user.name if target_user else 'Unassigned'} ({target_user.designation if target_user else ''})."
    if remarks:
        action_desc += f" Remarks: {remarks}"

    action = CaseAction(
        complaint_id=comp.id,
        action_type="assignment",
        description=action_desc,
        old_status=comp.status,
        new_status=comp.status,
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    # Send notification to assigned user
    if target_user:
        notif = Notification(
            user_id=target_user.id,
            notification_type="case_assigned",
            title=f"Case Assigned: {comp.case_number}",
            message=f"You have been assigned to handle complaint {comp.case_number} concerning '{comp.institution.name}'. Priority: {comp.priority}.",
            related_complaint_id=comp.id,
        )
        db.session.add(notif)

    db.session.commit()
    return comp, None

def transfer_bureau(complaint_id: int, target_bureau_id: int, remarks: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Public complainants cannot transfer complaints"


    target_bureau = db.session.get(Bureau, target_bureau_id)
    if not target_bureau:
        return None, "Target bureau not found"

    old_bureau_id = comp.current_bureau_id
    old_bureau_code = comp.current_bureau.code if comp.current_bureau else "UNKNOWN"
    comp.current_bureau_id = target_bureau_id
    comp.assigned_user_id = None  # Reset assigned officer upon transfer across bureaus
    comp.last_action_at = datetime.now(timezone.utc)

    desc_text = f"Case transferred from {old_bureau_code} to {target_bureau.code} ({target_bureau.name})."
    if remarks:
        desc_text += f" Reason: {remarks}"

    action = CaseAction(
        complaint_id=comp.id,
        action_type="bureau_transfer",
        description=desc_text,
        old_status=comp.status,
        new_status=comp.status,
        old_bureau_id=old_bureau_id,
        new_bureau_id=target_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    # Notify target bureau
    notif = Notification(
        bureau_id=target_bureau_id,
        notification_type="case_transferred",
        title=f"Case Transferred to {target_bureau.code}: {comp.case_number}",
        message=f"Complaint {comp.case_number} has been transferred to your Bureau from {old_bureau_code}. Reason: {remarks}",
        related_complaint_id=comp.id,
    )
    db.session.add(notif)

    # Notify complainant
    if comp.created_by_user_id:
        c_notif = Notification(
            user_id=comp.created_by_user_id,
            notification_type="case_transferred",
            title=f"Grievance Transferred: {comp.case_number}",
            message=f"Your grievance {comp.case_number} has been transferred to {target_bureau.name} ({target_bureau.code}) for regulatory inquiry.",
            related_complaint_id=comp.id,
        )
        db.session.add(c_notif)

    db.session.commit()
    return comp, None

def request_complainant_info(complaint_id: int, query_text: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Only authorized officers can request information"

    comp.query_to_complainant = query_text.strip()
    old_status = comp.status
    comp.status = "Awaiting Response"
    comp.last_action_at = datetime.now(timezone.utc)

    action = CaseAction(
        complaint_id=comp.id,
        action_type="info_request",
        description=f"Additional information / documentation requested from complainant: {query_text}",
        old_status=old_status,
        new_status="Awaiting Response",
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    # Notify complainant
    if comp.created_by_user_id:
        notif = Notification(
            user_id=comp.created_by_user_id,
            notification_type="info_required",
            title=f"Additional Information Required: {comp.case_number}",
            message=f"AICTE officer has requested additional details or missing documents: {query_text}. Please respond via your complainant dashboard.",
            related_complaint_id=comp.id,
        )
        db.session.add(notif)

    db.session.commit()
    return comp, None

def respond_complainant_query(complaint_id: int, response_text: str, documents: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    # Strict ownership check
    is_owner = (comp.created_by_user_id == current_user.id) or (
        comp.complainant_email and comp.complainant_email.strip().lower() == current_user.email.strip().lower()
    )
    if not is_owner:
        return None, "Forbidden: You are not authorized to respond to this grievance"

    comp.complainant_response = response_text.strip()
    if documents:
        comp.additional_documents = documents.strip()

    old_status = comp.status
    comp.status = "Under Review"
    comp.last_action_at = datetime.now(timezone.utc)

    action = CaseAction(
        complaint_id=comp.id,
        action_type="info_response",
        description=f"Complainant submitted response to official query: {response_text}" + (f" (Documents attached: {documents})" if documents else ""),
        old_status=old_status,
        new_status="Under Review",
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    # Notify assigned officer or bureau
    target_uid = comp.assigned_user_id
    notif = Notification(
        user_id=target_uid,
        bureau_id=comp.current_bureau_id if not target_uid else None,
        notification_type="info_received",
        title=f"Information Received: {comp.case_number}",
        message=f"Complainant has provided requested documentation for grievance {comp.case_number}.",
        related_complaint_id=comp.id,
    )
    db.session.add(notif)

    db.session.commit()
    return comp, None

def record_coordination_note(complaint_id: int, note_text: str, target_bureau_id: int, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Only authorized officials can add coordination notes"

    now_str = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M")
    officer_bureau = current_user.bureau.code if current_user.bureau else "AICTE"
    new_entry = f"[{now_str} | {current_user.name} ({officer_bureau})]: {note_text.strip()}\n"
    
    comp.coordination_notes = (comp.coordination_notes or "") + new_entry
    comp.last_action_at = datetime.now(timezone.utc)

    action = CaseAction(
        complaint_id=comp.id,
        action_type="coordination_note",
        description=f"Coordination note added: {note_text.strip()}",
        old_status=comp.status,
        new_status=comp.status,
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    if target_bureau_id:
        t_bureau = db.session.get(Bureau, target_bureau_id)
        if t_bureau:
            notif = Notification(
                bureau_id=target_bureau_id,
                notification_type="coordination_note",
                title=f"Cross-Bureau Note: {comp.case_number}",
                message=f"{current_user.name} ({officer_bureau}) recorded a cross-Bureau coordination note concerning '{comp.institution.name}': {note_text.strip()}",
                related_complaint_id=comp.id,
            )
            db.session.add(notif)

    db.session.commit()
    return comp, None

def update_next_action(complaint_id: int, next_action: str, next_action_due: str, assignee: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Only authorized officials can update next action"

    comp.next_action = next_action.strip() if next_action else None
    if next_action_due:
        try:
            comp.next_action_due = datetime.fromisoformat(next_action_due.replace("Z", "+00:00"))
        except Exception:
            pass
    comp.next_action_assignee = assignee.strip() if assignee else current_user.name
    comp.last_action_at = datetime.now(timezone.utc)

    action = CaseAction(
        complaint_id=comp.id,
        action_type="next_action_update",
        description=f"Next action defined: {comp.next_action} (Assigned to: {comp.next_action_assignee})",
        old_status=comp.status,
        new_status=comp.status,
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)
    db.session.commit()
    return comp, None

def escalate_complaint(complaint_id: int, reason: str, current_user: User):
    comp = db.session.get(Complaint, complaint_id)
    if not comp:
        return None, "Complaint not found"

    if current_user.is_user:
        return None, "Forbidden: Only authorized officials can escalate complaints"

    old_status = comp.status
    comp.is_escalated = True
    comp.escalation_reason = reason.strip()
    comp.status = "Escalated"
    comp.priority = "Critical"
    comp.last_action_at = datetime.now(timezone.utc)

    action = CaseAction(
        complaint_id=comp.id,
        action_type="escalation",
        description=f"Case escalated to Senior Monitoring Queue. Rationale: {reason.strip()}",
        old_status=old_status,
        new_status="Escalated",
        old_bureau_id=comp.current_bureau_id,
        new_bureau_id=comp.current_bureau_id,
        performed_by_id=current_user.id,
    )
    db.session.add(action)

    # Notify System Admin and Bureau officers
    notif = Notification(
        role="SYSTEM_ADMIN",
        notification_type="case_escalated",
        title=f"Case Escalated: {comp.case_number}",
        message=f"Case {comp.case_number} concerning '{comp.institution.name}' was escalated by {current_user.name}. Reason: {reason.strip()}",
        related_complaint_id=comp.id,
    )
    db.session.add(notif)

    db.session.commit()
    return comp, None

def manual_link_cases(comp_id_a: int, comp_id_b: int, reason: str, current_user: User):
    from ..models import CaseLink
    if comp_id_a == comp_id_b:
        return None, "Cannot link a case to itself"

    id_a, id_b = (comp_id_a, comp_id_b) if comp_id_a < comp_id_b else (comp_id_b, comp_id_a)
    ca = db.session.get(Complaint, id_a)
    cb = db.session.get(Complaint, id_b)
    if not ca or not cb:
        return None, "One or both complaints not found"

    existing = db.session.query(CaseLink).filter_by(complaint_id_a=id_a, complaint_id_b=id_b).first()
    if existing:
        existing.relationship_type = "confirmed_overlap"
        existing.review_status = "confirmed"
        existing.review_remarks = reason.strip()
        existing.reviewed_by_id = current_user.id
        existing.reviewed_at = datetime.now(timezone.utc)
        link = existing
    else:
        link = CaseLink(
            complaint_id_a=id_a,
            complaint_id_b=id_b,
            relationship_type="confirmed_overlap",
            match_score=1.0,
            match_method="manual_coordination",
            match_reason=reason.strip() or "Cases confirmed as overlapping by Bureau Official",
            review_status="confirmed",
            reviewed_by_id=current_user.id,
            reviewed_at=datetime.now(timezone.utc),
            review_remarks=reason.strip() or "Manually linked by official",
        )
        db.session.add(link)

    # Add case action to BOTH complaints documenting linkage
    action_a = CaseAction(
        complaint_id=ca.id,
        action_type="overlap_verification",
        description=f"Confirmed Overlap linked with Case {cb.case_number} ({cb.current_bureau.code if cb.current_bureau else ''}). Rationale: {reason.strip()}",
        old_status=ca.status,
        new_status=ca.status,
        performed_by_id=current_user.id,
    )
    action_b = CaseAction(
        complaint_id=cb.id,
        action_type="overlap_verification",
        description=f"Confirmed Overlap linked with Case {ca.case_number} ({ca.current_bureau.code if ca.current_bureau else ''}). Rationale: {reason.strip()}",
        old_status=cb.status,
        new_status=cb.status,
        performed_by_id=current_user.id,
    )
    db.session.add(action_a)
    db.session.add(action_b)

    # Notify involved bureaus
    bureaus_to_notify = set()
    if ca.current_bureau_id:
        bureaus_to_notify.add(ca.current_bureau_id)
    if cb.current_bureau_id:
        bureaus_to_notify.add(cb.current_bureau_id)

    for b_id in bureaus_to_notify:
        notif = Notification(
            bureau_id=b_id,
            notification_type="overlap_confirmed",
            title=f"Confirmed Overlap Linked: {ca.case_number} & {cb.case_number}",
            message=f"Cases {ca.case_number} and {cb.case_number} concerning '{ca.institution.name}' have been verified and linked for cross-Bureau coordination.",
            related_complaint_id=ca.id,
        )
        db.session.add(notif)

    db.session.commit()
    return link, None

