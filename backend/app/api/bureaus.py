from flask import Blueprint, jsonify
from ..models import db, Bureau, User
from ..services.auth_service import jwt_required

bureaus_bp = Blueprint("bureaus", __name__, url_prefix="/api/v1/bureaus")

@bureaus_bp.route("", methods=["GET"])
@jwt_required
def list_bureaus():
    bureaus = db.session.query(Bureau).filter_by(is_active=True).order_by(Bureau.name).all()
    return jsonify({"bureaus": [b.to_dict() for b in bureaus]})

@bureaus_bp.route("/<int:bureau_id>/officers", methods=["GET"])
@jwt_required
def list_bureau_officers(bureau_id: int):
    officers = db.session.query(User).filter(
        User.bureau_id == bureau_id,
        User.is_active == True
    ).all()
    return jsonify({"officers": [u.to_dict() for u in officers]})
