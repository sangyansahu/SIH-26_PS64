from flask import Blueprint, request, jsonify
from ..models import db, Institution, Complaint, AuditEvent
from ..services.auth_service import jwt_required, roles_required, get_current_user, ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY

from ..services.institution_service import get_institutions, get_institution_detail

institutions_bp = Blueprint("institutions", __name__, url_prefix="/api/v1/institutions")

@institutions_bp.route("", methods=["GET"])
@jwt_required
def list_institutions():
    search = request.args.get("search")
    state = request.args.get("state")
    institution_type = request.args.get("institution_type")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))

    data = get_institutions(
        search=search,
        state=state,
        institution_type=institution_type,
        page=page,
        per_page=per_page
    )
    return jsonify(data)

@institutions_bp.route("/meta", methods=["GET"])
@jwt_required
def get_institution_meta():
    states = [
        s[0] for s in db.session.query(Institution.state)
        .filter(Institution.state.isnot(None), Institution.state != "")
        .distinct().order_by(Institution.state).all()
    ]
    types = [
        t[0] for t in db.session.query(Institution.institution_type)
        .filter(Institution.institution_type.isnot(None), Institution.institution_type != "")
        .distinct().order_by(Institution.institution_type).all()
    ]
    return jsonify({"states": states, "institution_types": types})

@institutions_bp.route("/<int:inst_id>", methods=["GET"])
@jwt_required
def get_institution(inst_id: int):
    detail = get_institution_detail(inst_id)
    if not detail:
        return jsonify({"error": "Institution not found"}), 404
    return jsonify(detail)

@institutions_bp.route("", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def create_institution():
    data = request.get_json() or {}
    code = data.get("institution_code", "").strip()
    name = data.get("name", "").strip()
    state = data.get("state", "").strip()

    if not code or not name or not state:
        return jsonify({"error": "Institution Permanent ID, Name, and State are required"}), 400

    existing = db.session.query(Institution).filter_by(institution_code=code).first()
    if existing:
        return jsonify({"error": f"Institution with ID '{code}' already exists"}), 409

    inst = Institution(
        institution_code=code,
        name=name,
        institution_type=data.get("institution_type", "Engineering & Technology"),
        state=state,
        district=data.get("district"),
        address=data.get("address"),
        pincode=data.get("pincode"),
        website=data.get("website"),
    )
    if "aliases" in data:
        inst.set_aliases(data["aliases"])

    db.session.add(inst)
    db.session.commit()

    return jsonify({"message": "Institution registered successfully", "institution": inst.to_dict()}), 201

@institutions_bp.route("/<int:inst_id>", methods=["PATCH"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def update_institution(inst_id: int):
    inst = db.session.get(Institution, inst_id)
    if not inst:
        return jsonify({"error": "Institution not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        inst.name = data["name"].strip()
    if "institution_type" in data:
        inst.institution_type = data["institution_type"]
    if "state" in data:
        inst.state = data["state"].strip()
    if "district" in data:
        inst.district = data["district"].strip()
    if "address" in data:
        inst.address = data["address"]
    if "aliases" in data:
        inst.set_aliases(data["aliases"])

    db.session.commit()
    return jsonify({"message": "Institution updated", "institution": inst.to_dict()})

@institutions_bp.route("/<int:inst_id>/complaints", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def list_institution_complaints(inst_id: int):
    inst = db.session.get(Institution, inst_id)
    if not inst:
        return jsonify({"error": "Institution not found"}), 404

    complaints = db.session.query(Complaint).filter_by(institution_id=inst_id).order_by(Complaint.created_at.desc()).all()
    return jsonify({"complaints": [c.to_dict() for c in complaints]})

