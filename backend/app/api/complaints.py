from flask import Blueprint, request, jsonify
from sqlalchemy import or_, desc
from ..models import db, Complaint
from ..services.auth_service import (
    jwt_required,
    roles_required,
    get_current_user,
    ROLE_SYSTEM_ADMIN,
    ROLE_INDUSTRY,
    ROLE_USER,
)
from ..services.complaint_service import (
    get_complaints,
    create_complaint,
    update_complaint_status,
    assign_complaint,
    transfer_bureau,
    request_complainant_info,
    respond_complainant_query,
    record_coordination_note,
    update_next_action,
    escalate_complaint,
    manual_link_cases,
)

complaints_bp = Blueprint("complaints", __name__, url_prefix="/api/v1/complaints")

@complaints_bp.route("", methods=["GET"])
@jwt_required
def list_complaints():
    user = get_current_user()

    # User / Complainant role enforcement:
    # Public complainants can ONLY view their own complaints, strictly sanitized
    if user.is_user:
        query = db.session.query(Complaint).filter(
            or_(
                Complaint.created_by_user_id == user.id,
                Complaint.complainant_email.ilike(user.email)
            )
        ).order_by(desc(Complaint.created_at))
        items = query.all()
        return jsonify({
            "items": [c.to_public_dict(include_history=True) for c in items],
            "total": len(items),
            "page": 1,
            "per_page": len(items),
            "pages": 1,
        })

    # Industry / System Admin: full view across all industries/departments
    search = request.args.get("search")
    status = request.args.get("status")
    priority = request.args.get("priority")
    bureau_id = request.args.get("bureau_id", type=int)
    institution_id = request.args.get("institution_id", type=int)
    is_overdue = request.args.get("is_overdue")
    sort_by = request.args.get("sort_by", "created_at")
    sort_dir = request.args.get("sort_dir", "desc")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))

    data = get_complaints(
        search=search,
        status=status,
        priority=priority,
        bureau_id=bureau_id,
        institution_id=institution_id,
        is_overdue=is_overdue,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page,
        user=user
    )
    return jsonify(data)

@complaints_bp.route("/meta", methods=["GET"])
@jwt_required
def get_complaints_meta():
    db_cats = [
        c[0] for c in db.session.query(Complaint.category)
        .filter(Complaint.category.isnot(None), Complaint.category != "")
        .distinct().order_by(Complaint.category).all()
    ]
    canonical_cats = [
        "Fee Overcharging / Capitation",
        "Faculty Quality / Non-Payment",
        "Infrastructure Deficiencies",
        "Ragging Incident",
        "Approval / Accreditation Fraud",
        "Admission Irregularity",
        "General Administration"
    ]
    categories = sorted(list(set(db_cats + canonical_cats)))
    statuses = ["New", "Received", "Under Review", "Action Required", "Awaiting Response", "Escalated", "Disposed", "Closed"]
    priorities = ["Critical", "High", "Medium", "Low"]
    return jsonify({
        "categories": categories,
        "statuses": statuses,
        "priorities": priorities
    })

@complaints_bp.route("/<int:comp_id>", methods=["GET"])
@jwt_required
def get_complaint(comp_id: int):
    comp = db.session.get(Complaint, comp_id)
    if not comp:
        return jsonify({"error": "Complaint not found"}), 404

    user = get_current_user()
    if user.is_user:
        # Strict privacy enforcement: cannot view other people's complaints
        is_owner = (comp.created_by_user_id == user.id) or (
            comp.complainant_email and comp.complainant_email.strip().lower() == user.email.strip().lower()
        )
        if not is_owner:
            return jsonify({"error": "Forbidden: You do not have permission to access this complaint"}), 403
        return jsonify({"complaint": comp.to_public_dict(include_history=True)})

    # Industry / System Admin: full complaint details with actions & overlap matches
    return jsonify({"complaint": comp.to_dict(include_details=True)})

@complaints_bp.route("", methods=["POST"])
@jwt_required
def lodge_complaint():
    data = request.get_json() or {}
    user = get_current_user()

    if not data.get("subject") or not data.get("description"):
        return jsonify({"error": "Subject and description are required"}), 400

    if user.is_user:
        # Auto-bind complainant credentials
        data["complainant_name"] = data.get("complainant_name") or user.name
        data["complainant_email"] = user.email

    try:
        complaint = create_complaint(data, user)
        res_data = complaint.to_public_dict(include_history=True) if user.is_user else complaint.to_dict(include_details=True)
        return jsonify({
            "message": "Complaint successfully registered",
            "ticket_number": complaint.ticket_number,
            "case_number": complaint.case_number,
            "complaint": res_data
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to register complaint: {str(e)}"}), 500

@complaints_bp.route("/<int:comp_id>/actions", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def update_status(comp_id: int):
    data = request.get_json() or {}
    new_status = data.get("status")
    remarks = data.get("remarks", "")
    user = get_current_user()

    if not new_status:
        return jsonify({"error": "New status is required"}), 400

    comp, err = update_complaint_status(comp_id, new_status, remarks, user)
    if err:
        return jsonify({"error": err}), 403 if "Forbidden" in err else 400

    return jsonify({
        "message": "Status updated successfully",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/assign", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def assign_officer(comp_id: int):
    data = request.get_json() or {}
    assign_to_user_id = data.get("user_id")
    remarks = data.get("remarks", "")
    user = get_current_user()

    comp, err = assign_complaint(comp_id, assign_to_user_id, remarks, user)
    if err:
        return jsonify({"error": err}), 403 if "Forbidden" in err else 400

    return jsonify({
        "message": "Case assigned successfully",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/transfer", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def transfer_case(comp_id: int):
    data = request.get_json() or {}
    target_bureau_id = data.get("target_bureau_id")
    remarks = data.get("remarks", "")
    user = get_current_user()

    if not target_bureau_id:
        return jsonify({"error": "Target Bureau ID is required"}), 400

    comp, err = transfer_bureau(comp_id, target_bureau_id, remarks, user)
    if err:
        return jsonify({"error": err}), 403 if "Forbidden" in err else 400

    return jsonify({
        "message": "Case transferred successfully",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/request-info", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def request_info(comp_id: int):
    data = request.get_json() or {}
    query_text = data.get("query", "").strip()
    user = get_current_user()

    if not query_text:
        return jsonify({"error": "Query or description of requested information is required"}), 400

    comp, err = request_complainant_info(comp_id, query_text, user)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Additional information requested from complainant",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/respond-query", methods=["POST"])
@jwt_required
def respond_query(comp_id: int):
    data = request.get_json() or {}
    response_text = data.get("response", "").strip()
    documents = data.get("documents", "").strip()
    user = get_current_user()

    if not response_text:
        return jsonify({"error": "Response explanation is required"}), 400

    comp, err = respond_complainant_query(comp_id, response_text, documents, user)
    if err:
        return jsonify({"error": err}), 403 if "Forbidden" in err else 400

    return jsonify({
        "message": "Information submitted successfully. Case is now under review.",
        "complaint": comp.to_public_dict(include_history=True) if user.is_user else comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/coordination-note", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def add_coordination_note(comp_id: int):
    data = request.get_json() or {}
    note_text = data.get("note", "").strip()
    target_bureau_id = data.get("target_bureau_id")
    user = get_current_user()

    if not note_text:
        return jsonify({"error": "Coordination note text is required"}), 400

    comp, err = record_coordination_note(comp_id, note_text, target_bureau_id, user)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Coordination note recorded successfully",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/next-action", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def update_action(comp_id: int):
    data = request.get_json() or {}
    next_action = data.get("next_action", "").strip()
    next_action_due = data.get("next_action_due")
    assignee = data.get("assignee", "").strip()
    user = get_current_user()

    comp, err = update_next_action(comp_id, next_action, next_action_due, assignee, user)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Next action updated successfully",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/escalate", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def escalate_case(comp_id: int):
    data = request.get_json() or {}
    reason = data.get("reason", "").strip()
    user = get_current_user()

    if not reason:
        return jsonify({"error": "Escalation reason is required"}), 400

    comp, err = escalate_complaint(comp_id, reason, user)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Case escalated successfully",
        "complaint": comp.to_dict(include_details=True)
    })

@complaints_bp.route("/<int:comp_id>/link", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def link_case(comp_id: int):
    data = request.get_json() or {}
    target_comp_id = data.get("target_complaint_id")
    reason = data.get("reason", "").strip()
    user = get_current_user()

    if not target_comp_id:
        return jsonify({"error": "Target complaint ID to link is required"}), 400

    link, err = manual_link_cases(comp_id, int(target_comp_id), reason, user)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Related cases linked successfully with preserved independent identities and histories.",
        "link": link.to_dict()
    })

@complaints_bp.route("/<int:comp_id>/acknowledgement", methods=["GET"])
@jwt_required
def get_acknowledgement(comp_id: int):
    comp = db.session.get(Complaint, comp_id)
    if not comp:
        return jsonify({"error": "Complaint not found"}), 404

    user = get_current_user()
    if user.is_user:
        is_owner = (comp.created_by_user_id == user.id) or (
            comp.complainant_email and comp.complainant_email.strip().lower() == user.email.strip().lower()
        )
        if not is_owner:
            return jsonify({"error": "Forbidden: You cannot access this acknowledgement"}), 403

    ack = {
        "acknowledgement_number": f"AICTE/ACK/{comp.ticket_number or comp.case_number}",
        "ticket_number": comp.ticket_number or comp.case_number,
        "case_number": comp.case_number,
        "submission_date": comp.created_at.strftime("%d-%b-%Y %H:%M UTC") if comp.created_at else "N/A",
        "complainant_name": comp.complainant_name or user.name,
        "complainant_email": comp.complainant_email or user.email,
        "institution_name": comp.institution.name if comp.institution else "N/A",
        "institution_permanent_id": comp.institution.institution_code if comp.institution else "N/A",
        "institution_state": comp.institution.state if comp.institution else "N/A",
        "category": comp.category,
        "subject": comp.subject,
        "description": comp.description,
        "current_status": comp.status,
        "responsible_bureau": comp.current_bureau.name if comp.current_bureau else "Public Grievance Redressal Cell",
        "bureau_code": comp.current_bureau.code if comp.current_bureau else "PGRC",
        "resolution_summary": comp.resolution_summary,
        "disposed_at": comp.disposed_at.strftime("%d-%b-%Y") if comp.disposed_at else None,
        "official_disclaimer": "This is an official computer-generated acknowledgement by the All India Council for Technical Education (AICTE), Ministry of Education, Government of India. No physical signature is required."
    }
    return jsonify({"acknowledgement": ack})

