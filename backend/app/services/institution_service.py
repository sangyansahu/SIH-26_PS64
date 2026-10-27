from sqlalchemy import or_, desc, asc
from datetime import datetime, timezone
from ..models import db, Institution, Complaint, CaseLink, Bureau

def get_institutions(search=None, state=None, institution_type=None, page=1, per_page=15):
    query = db.session.query(Institution)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Institution.name.ilike(search_term),
                Institution.institution_code.ilike(search_term),
                Institution.aliases.ilike(search_term),
                Institution.district.ilike(search_term),
            )
        )

    if state:
        query = query.filter(Institution.state.ilike(f"%{state}%"))

    if institution_type:
        query = query.filter(Institution.institution_type == institution_type)

    query = query.order_by(asc(Institution.name))
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [item.to_dict(include_stats=True) for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 1
    }

def get_institution_detail(institution_id: int):
    inst = db.session.get(Institution, institution_id)
    if not inst:
        return None

    # Consolidated cross-bureau complaint landscape
    complaints = db.session.query(Complaint).filter(Complaint.institution_id == inst.id).order_by(desc(Complaint.received_at)).all()

    # Department breakdown
    bureau_counts = {}
    bureaus = db.session.query(Bureau).all()
    for b in bureaus:
        bureau_counts[b.code] = 0

    status_counts = {
        "Received": 0,
        "Under Review": 0,
        "Action Required": 0,
        "Awaiting Response": 0,
        "Escalated": 0,
        "Disposed": 0,
        "Closed": 0
    }

    now = datetime.now(timezone.utc)
    overdue_count = 0
    complaint_ids = [c.id for c in complaints]

    for c in complaints:
        if c.current_bureau:
            bureau_counts[c.current_bureau.code] = bureau_counts.get(c.current_bureau.code, 0) + 1
        if c.status in status_counts:
            status_counts[c.status] += 1
        else:
            status_counts[c.status] = 1

        if c.is_overdue:
            overdue_count += 1

    # Fetch active overlaps involving these complaints
    overlaps = []
    if complaint_ids:
        links = db.session.query(CaseLink).filter(
            or_(
                CaseLink.complaint_id_a.in_(complaint_ids),
                CaseLink.complaint_id_b.in_(complaint_ids)
            )
        ).all()
        overlaps = [link.to_dict() for link in links]

    return {
        "institution": inst.to_dict(include_stats=True),
        "complaints": [c.to_dict(include_details=False) for c in complaints],
        "summary": {
            "total_complaints": len(complaints),
            "open_cases": sum(1 for c in complaints if c.status not in ("Disposed", "Closed")),
            "disposed_cases": sum(1 for c in complaints if c.status in ("Disposed", "Closed")),
            "overdue_cases": overdue_count,
            "escalated_cases": status_counts.get("Escalated", 0),
            "bureau_distribution": bureau_counts,
            "status_distribution": status_counts,
            "total_overlaps_flagged": len(overlaps),
        },
        "potential_overlaps": overlaps
    }
