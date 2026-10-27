from flask import Blueprint, request, jsonify, Response
from ..models import db, ImportBatch
from ..services.auth_service import (
    jwt_required,
    roles_required,
    get_current_user,
    ROLE_SYSTEM_ADMIN,
    ROLE_INDUSTRY,
)
from ..services.import_service import get_csv_template, preview_csv_import, commit_csv_import

imports_bp = Blueprint("imports", __name__, url_prefix="/api/v1/imports")

@imports_bp.route("/template", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def download_template():
    csv_text = get_csv_template()
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=aicte_complaints_template.csv"}
    )

@imports_bp.route("/preview", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def preview_import():
    content = ""
    if "file" in request.files:
        f = request.files["file"]
        content = f.read().decode("utf-8", errors="replace")
    elif request.data:
        content = request.data.decode("utf-8", errors="replace")
    elif request.is_json and "content" in request.json:
        content = request.json["content"]

    if not content.strip():
        return jsonify({"error": "No CSV content provided"}), 400

    res = preview_csv_import(content)
    if not res.get("is_valid"):
        return jsonify(res), 400

    return jsonify(res)

@imports_bp.route("/commit", methods=["POST"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def commit_import():
    data = request.get_json() or {}
    valid_rows = data.get("valid_rows", [])
    filename = data.get("filename", "batch_import.csv")
    user = get_current_user()

    if not valid_rows:
        return jsonify({"error": "No valid rows provided to commit"}), 400

    res = commit_csv_import(valid_rows, filename, user)
    return jsonify(res), 201

@imports_bp.route("/history", methods=["GET"])
@jwt_required
@roles_required(ROLE_SYSTEM_ADMIN, ROLE_INDUSTRY)
def list_import_history():
    batches = db.session.query(ImportBatch).order_by(ImportBatch.created_at.desc()).limit(30).all()
    return jsonify({"batches": [b.to_dict() for b in batches]})
