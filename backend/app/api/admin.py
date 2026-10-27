from flask import Blueprint, request, jsonify
from ..models import db, User, AuditEvent, Bureau, Complaint
from ..services.auth_service import jwt_required, roles_required, get_current_user, normalize_role, ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY, ROLE_USER

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")

SYSTEM_SETTINGS = {
    "system_name": "AICTE Integrated Complaint Monitoring & Coordination Platform",
    "version": "AICTE-CMP v2.0-SIH2026",
    "auto_assignment_enabled": True,
    "sla_days": {
        "Critical": 7,
        "High": 15,
        "Medium": 30,
        "Low": 45,
    },
    "reminder_intervals_days": [5, 2, 1],
    "escalation_rules": {
        "auto_escalate_overdue_days": 5,
        "escalate_to": "Bureau Head / Senior Monitoring Authority",
        "repeat_delay_threshold": 3,
    },
    "categories": [
        "Fee Overcharging / Capitation",
        "Faculty Quality / Non-Payment",
        "Infrastructure Deficiencies",
        "Ragging Incident",
        "Approval / Accreditation Fraud",
        "Admission Irregularity",
        "General Administration",
    ],
}

@admin_bp.route("/analytics", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def get_system_analytics():
    from datetime import datetime, timezone
    from sqlalchemy import func
    from ..models import CaseAction, Institution

    now = datetime.now(timezone.utc)
    total_received = db.session.query(Complaint).count()
    pending = db.session.query(Complaint).filter(Complaint.status.in_(["Received", "New"])).count()
    under_process = db.session.query(Complaint).filter(Complaint.status.in_(["Under Review", "Action Required", "Awaiting Response", "Escalated"])).count()
    disposed = db.session.query(Complaint).filter(Complaint.status.in_(["Disposed", "Closed"])).count()
    
    # Transferred cases (count complaints with transfer actions)
    transferred_comp_ids = db.session.query(CaseAction.complaint_id).filter_by(action_type="bureau_transfer").distinct().all()
    transferred = len(transferred_comp_ids)

    # Overdue cases
    overdue = db.session.query(Complaint).filter(
        Complaint.status.notin_(["Disposed", "Closed"]),
        Complaint.due_at.isnot(None),
        Complaint.due_at < now
    ).count()

    # Bureau-wise breakdown
    bureaus = db.session.query(Bureau).order_by(Bureau.name).all()
    bureau_breakdown = []
    for b in bureaus:
        b_total = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id).count()
        b_pending = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id, Complaint.status.in_(["Received", "New"])).count()
        b_under_process = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id, Complaint.status.in_(["Under Review", "Action Required", "Awaiting Response", "Escalated"])).count()
        b_disposed = db.session.query(Complaint).filter(Complaint.current_bureau_id == b.id, Complaint.status.in_(["Disposed", "Closed"])).count()
        b_overdue = db.session.query(Complaint).filter(
            Complaint.current_bureau_id == b.id,
            Complaint.status.notin_(["Disposed", "Closed"]),
            Complaint.due_at.isnot(None),
            Complaint.due_at < now
        ).count()
        bureau_breakdown.append({
            "id": b.id,
            "code": b.code,
            "name": b.name,
            "total": b_total,
            "pending": b_pending,
            "under_process": b_under_process,
            "disposed": b_disposed,
            "overdue": b_overdue,
        })

    # Region-wise (state) breakdown
    state_rows = db.session.query(
        Institution.state,
        func.count(Complaint.id).label("total")
    ).join(Complaint, Complaint.institution_id == Institution.id).group_by(Institution.state).order_by(func.count(Complaint.id).desc()).all()

    region_breakdown = [{"region": s or "Unassigned", "total": t} for s, t in state_rows]

    return jsonify({
        "totals": {
            "received": total_received,
            "pending": pending,
            "under_process": under_process,
            "disposed": disposed,
            "transferred": transferred,
            "overdue": overdue,
        },
        "bureau_breakdown": bureau_breakdown,
        "region_breakdown": region_breakdown,
    })

@admin_bp.route("/data-quality", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def get_data_quality():
    from ..models import Institution
    # 1. Missing or invalid institution Permanent IDs
    missing_ids = []
    institutions = db.session.query(Institution).all()
    for inst in institutions:
        if not inst.institution_code or inst.institution_code.strip() in ("", "N/A", "PENDING", "0") or not inst.institution_code.startswith("1-"):
            missing_ids.append({
                "institution_id": inst.id,
                "name": inst.name,
                "institution_code": inst.institution_code or "MISSING",
                "state": inst.state,
                "issue": "Missing or non-conforming AICTE Permanent ID format",
            })

    # 2. Inconsistent institution names (complaints with names differing or institutions with ambiguous aliases)
    inconsistent_names = []
    complaints = db.session.query(Complaint).join(Institution).all()
    for comp in complaints:
        if comp.institution:
            norm_c = comp.institution.name.strip().lower()
            norm_subj = comp.subject.strip().lower()
            # Check if aliases differ from registered name
            for al in comp.institution.alias_list:
                if al and al.lower() not in norm_c and len(al) > 4:
                    inconsistent_names.append({
                        "case_number": comp.case_number,
                        "registered_name": comp.institution.name,
                        "permanent_id": comp.institution.institution_code,
                        "alias_conflict": al,
                        "bureau": comp.current_bureau.code if comp.current_bureau else "",
                        "issue": f"Institution known under multiple alias variations ({al})",
                    })
                    break

    # 3. Incomplete records (missing descriptions, categories, or contact info)
    incomplete_records = []
    for comp in complaints:
        issues = []
        if not comp.description or len(comp.description.strip()) < 10:
            issues.append("Description is brief or missing")
        if not comp.category or comp.category == "General Administration":
            issues.append("Uncategorized / generic category")
        if not comp.complainant_email and not comp.complainant_mobile:
            issues.append("No complainant contact details on record")
        if not comp.assigned_user_id and comp.status not in ("Disposed", "Closed") and comp.ageing_days > 7:
            issues.append(f"Unassigned for {comp.ageing_days} days (exceeds intake SLA)")

        if issues:
            incomplete_records.append({
                "case_number": comp.case_number,
                "permanent_id": comp.institution.institution_code if comp.institution else "",
                "institution_name": comp.institution.name if comp.institution else "",
                "bureau": comp.current_bureau.code if comp.current_bureau else "",
                "status": comp.status,
                "issues": issues,
            })

    return jsonify({
        "summary": {
            "missing_ids_count": len(missing_ids),
            "inconsistent_names_count": len(inconsistent_names),
            "incomplete_records_count": len(incomplete_records),
            "total_quality_flags": len(missing_ids) + len(inconsistent_names) + len(incomplete_records),
        },
        "missing_ids": missing_ids[:20],
        "inconsistent_names": inconsistent_names[:20],
        "incomplete_records": incomplete_records[:20],
    })

@admin_bp.route("/bureaus", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def list_bureaus():
    bureaus = db.session.query(Bureau).order_by(Bureau.id.asc()).all()
    return jsonify({"bureaus": [b.to_dict() for b in bureaus]})

@admin_bp.route("/bureaus", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def create_bureau():
    data = request.get_json() or {}
    code = (data.get("code") or "").strip().upper()
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()

    if not code or not name:
        return jsonify({"error": "Bureau code and name are required"}), 400

    existing = db.session.query(Bureau).filter_by(code=code).first()
    if existing:
        return jsonify({"error": f"Bureau with code '{code}' already exists"}), 409

    bureau = Bureau(code=code, name=name, description=description, is_active=True)
    db.session.add(bureau)
    db.session.commit()
    return jsonify({"message": "Bureau created successfully", "bureau": bureau.to_dict()}), 201

@admin_bp.route("/bureaus/<int:bureau_id>", methods=["PATCH"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def update_bureau(bureau_id: int):
    bureau = db.session.get(Bureau, bureau_id)
    if not bureau:
        return jsonify({"error": "Bureau not found"}), 404

    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        bureau.name = data["name"].strip()
    if "code" in data and data["code"].strip():
        bureau.code = data["code"].strip().upper()
    if "description" in data:
        bureau.description = data["description"].strip()
    if "is_active" in data:
        bureau.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({"message": "Bureau updated successfully", "bureau": bureau.to_dict()})

@admin_bp.route("/categories", methods=["GET"])
@jwt_required
def list_categories():
    return jsonify({"categories": SYSTEM_SETTINGS["categories"]})

@admin_bp.route("/categories", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def add_category():
    data = request.get_json() or {}
    cat_name = (data.get("category") or data.get("name") or "").strip()
    if not cat_name:
        return jsonify({"error": "Category name is required"}), 400

    if cat_name not in SYSTEM_SETTINGS["categories"]:
        SYSTEM_SETTINGS["categories"].append(cat_name)

    return jsonify({"message": f"Category '{cat_name}' added", "categories": SYSTEM_SETTINGS["categories"]}), 201

@admin_bp.route("/categories/<string:cat_name>", methods=["DELETE"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def remove_category(cat_name: str):
    import urllib.parse
    decoded = urllib.parse.unquote(cat_name)
    if decoded in SYSTEM_SETTINGS["categories"]:
        SYSTEM_SETTINGS["categories"].remove(decoded)
    return jsonify({"message": f"Category '{decoded}' removed", "categories": SYSTEM_SETTINGS["categories"]})

@admin_bp.route("/escalation-config", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def get_escalation_config():
    return jsonify({
        "sla_days": SYSTEM_SETTINGS["sla_days"],
        "reminder_intervals_days": SYSTEM_SETTINGS["reminder_intervals_days"],
        "escalation_rules": SYSTEM_SETTINGS["escalation_rules"],
    })

@admin_bp.route("/escalation-config", methods=["PATCH"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def update_escalation_config():
    data = request.get_json() or {}
    if "sla_days" in data and isinstance(data["sla_days"], dict):
        SYSTEM_SETTINGS["sla_days"].update(data["sla_days"])
    if "reminder_intervals_days" in data and isinstance(data["reminder_intervals_days"], list):
        SYSTEM_SETTINGS["reminder_intervals_days"] = [int(x) for x in data["reminder_intervals_days"]]
    if "escalation_rules" in data and isinstance(data["escalation_rules"], dict):
        SYSTEM_SETTINGS["escalation_rules"].update(data["escalation_rules"])

    return jsonify({
        "message": "Prescribed timelines and escalation rules updated",
        "config": {
            "sla_days": SYSTEM_SETTINGS["sla_days"],
            "reminder_intervals_days": SYSTEM_SETTINGS["reminder_intervals_days"],
            "escalation_rules": SYSTEM_SETTINGS["escalation_rules"],
        }
    })

@admin_bp.route("/users", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def list_users():
    role_filter = request.args.get("role")
    search = request.args.get("search", "").strip().lower()

    query = db.session.query(User)
    if role_filter:
        norm_filter = normalize_role(role_filter)
        query = query.filter(User.role == norm_filter)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term),
                User.designation.ilike(search_term),
            )
        )

    users = query.order_by(User.id.asc()).all()
    return jsonify({"users": [u.to_dict() for u in users]})

@admin_bp.route("/users", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def create_user():
    """
    System Admin is the only role capable of creating Industry accounts.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip()
    password = data.get("password", "").strip()
    raw_role = data.get("role", ROLE_INDUSTRY)
    role = normalize_role(raw_role)
    bureau_id = data.get("bureau_id")
    designation = data.get("designation", "").strip()

    if not email or not password or not name:
        return jsonify({"error": "Name, email, and initial password are required"}), 400

    existing = db.session.query(User).filter_by(email=email).first()
    if existing:
        return jsonify({"error": "An account with this email address already exists"}), 409

    if bureau_id:
        bureau = db.session.get(Bureau, int(bureau_id))
        if not bureau:
            return jsonify({"error": "Selected department / industry bureau does not exist"}), 400
    else:
        bureau_id = None

    admin_actor = get_current_user()
    user = User(
        name=name,
        email=email,
        role=role,
        bureau_id=bureau_id,
        designation=designation or ("Industry Officer" if role == ROLE_INDUSTRY else "System User"),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # Log audit event
    audit = AuditEvent(
        user_id=admin_actor.id if admin_actor else None,
        action="USER_CREATED",
        entity_type="User",
        entity_id=user.id,
        ip_address=request.remote_addr,
    )
    audit.set_details({
        "created_email": user.email,
        "created_role": user.role,
        "bureau_id": user.bureau_id,
        "designation": user.designation,
    })
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": f"{role} account created successfully", "user": user.to_dict()}), 201

@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def update_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User account not found"}), 404

    data = request.get_json() or {}
    admin_actor = get_current_user()
    changes = {}

    if "is_active" in data:
        old_val = user.is_active
        user.is_active = bool(data["is_active"])
        changes["is_active"] = {"old": old_val, "new": user.is_active}

    if "name" in data and data["name"].strip():
        user.name = data["name"].strip()
        changes["name"] = user.name

    if "role" in data:
        user.role = normalize_role(data["role"])
        changes["role"] = user.role

    if "bureau_id" in data:
        user.bureau_id = int(data["bureau_id"]) if data["bureau_id"] else None
        changes["bureau_id"] = user.bureau_id

    if "designation" in data:
        user.designation = data["designation"].strip()
        changes["designation"] = user.designation

    if "password" in data and data["password"].strip():
        user.set_password(data["password"].strip())
        changes["password_reset"] = True

    audit = AuditEvent(
        user_id=admin_actor.id if admin_actor else None,
        action="USER_UPDATED",
        entity_type="User",
        entity_id=user.id,
        ip_address=request.remote_addr,
    )
    audit.set_details(changes)
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "User account updated successfully", "user": user.to_dict()})

@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def reset_user_password(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User account not found"}), 404

    data = request.get_json() or {}
    new_password = data.get("password", "").strip()
    if not new_password or len(new_password) < 4:
        return jsonify({"error": "Password must be at least 4 characters long"}), 400

    user.set_password(new_password)
    admin_actor = get_current_user()
    audit = AuditEvent(
        user_id=admin_actor.id if admin_actor else None,
        action="PASSWORD_RESET_BY_ADMIN",
        entity_type="User",
        entity_id=user.id,
        ip_address=request.remote_addr,
    )
    audit.set_details({"target_user_email": user.email, "target_user_role": user.role})
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": f"Password reset successfully for {user.name} ({user.email})"})

@admin_bp.route("/industries", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def list_industries():
    """
    View all industries / departments and their operational capacity.
    """
    bureaus = db.session.query(Bureau).order_by(Bureau.id.asc()).all()
    results = []
    for b in bureaus:
        user_count = db.session.query(User).filter_by(bureau_id=b.id, is_active=True).count()
        total_complaints = db.session.query(Complaint).filter(
            db.or_(Complaint.current_bureau_id == b.id, Complaint.receiving_bureau_id == b.id)
        ).count()
        open_complaints = db.session.query(Complaint).filter(
            db.or_(Complaint.current_bureau_id == b.id, Complaint.receiving_bureau_id == b.id),
            Complaint.status.notin_(["Disposed", "Closed"])
        ).count()

        results.append({
            "id": b.id,
            "name": b.name,
            "code": b.code,
            "description": b.description,
            "is_active": b.is_active,
            "user_count": user_count,
            "total_complaints": total_complaints,
            "open_complaints": open_complaints,
        })

    return jsonify({"industries": results})

@admin_bp.route("/settings", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def get_settings():
    return jsonify({"settings": SYSTEM_SETTINGS})

@admin_bp.route("/settings", methods=["PATCH"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def update_settings():
    data = request.get_json() or {}
    if "categories" in data and isinstance(data["categories"], list):
        SYSTEM_SETTINGS["categories"] = [c.strip() for c in data["categories"] if c.strip()]
    if "sla_days" in data and isinstance(data["sla_days"], dict):
        SYSTEM_SETTINGS["sla_days"].update(data["sla_days"])
    if "auto_assignment_enabled" in data:
        SYSTEM_SETTINGS["auto_assignment_enabled"] = bool(data["auto_assignment_enabled"])

    admin_actor = get_current_user()
    audit = AuditEvent(
        user_id=admin_actor.id if admin_actor else None,
        action="SETTINGS_UPDATED",
        entity_type="System",
        entity_id=1,
        ip_address=request.remote_addr,
    )
    audit.set_details(data)
    db.session.add(audit)
    db.session.commit()

    return jsonify({"message": "System settings updated successfully", "settings": SYSTEM_SETTINGS})

@admin_bp.route("/audit-logs", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def get_audit_logs():
    limit = int(request.args.get("limit", 50))
    logs = db.session.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return jsonify({"audit_logs": [log.to_dict() for log in logs]})

@admin_bp.route("/system-status", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def get_system_status():
    try:
        pg_version = db.session.execute(db.text("SELECT version();")).scalar()
        db_status = "Connected (Healthy)"
    except Exception as e:
        pg_version = "Unavailable"
        db_status = f"Error: {str(e)}"

    total_users = db.session.query(User).count()
    active_industry_users = db.session.query(User).filter_by(role=ROLE_INDUSTRY, is_active=True).count()
    total_complaints = db.session.query(Complaint).count()

    return jsonify({
        "status": "Operational",
        "database": db_status,
        "postgresql_version": pg_version,
        "portal_version": SYSTEM_SETTINGS["version"],
        "total_users": total_users,
        "active_industry_users": active_industry_users,
        "total_complaints": total_complaints,
    })
