from flask import Blueprint, request, jsonify
from sqlalchemy import or_, desc
from ..models import db, CaseLink, Complaint
from ..services.auth_service import (
    jwt_required,
    roles_required,
    get_current_user,
    ROLE_SYSTEM_ADMIN,
    ROLE_INDUSTRY,
)
from ..services.overlap_service import review_case_link, scan_complaint_overlaps

overlaps_bp = Blueprint("overlaps", __name__, url_prefix="/api/v1/overlaps")

@overlaps_bp.route("", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def list_overlaps():
    review_status = request.args.get("review_status", "pending")
    relationship_type = request.args.get("relationship_type")
    min_score = request.args.get("min_score", type=float)

    query = db.session.query(CaseLink)

    if review_status != "all":
        query = query.filter(CaseLink.review_status == review_status)

    if relationship_type:
        query = query.filter(CaseLink.relationship_type == relationship_type)

    if min_score is not None:
        query = query.filter(CaseLink.match_score >= min_score)

    query = query.order_by(desc(CaseLink.match_score), desc(CaseLink.created_at))
    links = query.all()

    return jsonify({
        "overlaps": [l.to_dict() for l in links],
        "total": len(links),
        "pending_count": db.session.query(CaseLink).filter_by(review_status="pending").count(),
    })

@overlaps_bp.route("/<int:link_id>", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def get_overlap(link_id: int):
    link = db.session.get(CaseLink, link_id)
    if not link:
        return jsonify({"error": "Overlap record not found"}), 404
    return jsonify({"overlap": link.to_dict()})

@overlaps_bp.route("/<int:link_id>/review", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def review_overlap(link_id: int):
    data = request.get_json() or {}
    decision = data.get("decision")
    remarks = data.get("remarks", "")
    user = get_current_user()

    if not decision:
        return jsonify({"error": "Review decision is required"}), 400

    link, err = review_case_link(link_id, decision, user.id, remarks)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": f"Overlap link successfully marked as {decision}",
        "overlap": link.to_dict()
    })

@overlaps_bp.route("/rescan", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN)
def rescan_all():
    complaints = db.session.query(Complaint).all()
    count = 0
    for c in complaints:
        links = scan_complaint_overlaps(c.id)
        count += len(links)

    return jsonify({
        "message": f"Overlap scan completed across {len(complaints)} complaints",
        "links_identified": count
    })
