import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from ..models import db, Institution, Bureau, Complaint
from ..services.complaint_service import create_complaint, get_complaint_by_ticket

public_bp = Blueprint("public", __name__, url_prefix="/api/v1/public")

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "txt"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@public_bp.route("/complaints", methods=["POST"])
def register_public_complaint():
    """
    Public endpoint for registering citizen/student/faculty grievances.
    Generates a unique ticket number AICTE-2026-XXXXXX on backend.
    Accepts JSON or multipart/form-data.
    """
    if request.is_json:
        data = request.get_json() or {}
        uploaded_file = None
    else:
        data = request.form.to_dict()
        uploaded_file = request.files.get("file") or request.files.get("document")

    # Validation
    complainant_name = (data.get("complainant_name") or "").strip()
    complainant_email = (data.get("complainant_email") or "").strip()
    subject = (data.get("subject") or "").strip()
    description = (data.get("description") or "").strip()
    category = (data.get("category") or "").strip()

    if not complainant_name:
        return jsonify({"error": "Complainant name is required"}), 400
    if not complainant_email or "@" not in complainant_email:
        return jsonify({"error": "A valid complainant email address is required"}), 400
    if not subject:
        return jsonify({"error": "Complaint subject is required"}), 400
    if not description:
        return jsonify({"error": "Complaint description is required"}), 400
    if not category:
        return jsonify({"error": "Complaint category is required"}), 400

    # Ensure institution reference is valid
    institution_id = data.get("institution_id")
    institution_name = (data.get("institution_name") or "").strip()
    if not institution_id and not institution_name and not data.get("institution_code"):
        return jsonify({"error": "Target institution name or selection is required"}), 400

    # Handle file upload if present
    doc_name = None
    doc_url = None
    if uploaded_file and uploaded_file.filename:
        original_name = uploaded_file.filename
        if not allowed_file(original_name):
            return jsonify({"error": "File type not supported. Allowed formats: PDF, PNG, JPG, JPEG, DOC, DOCX, TXT."}), 400
        
        upload_dir = current_app.config.get("UPLOAD_FOLDER") or os.path.join(current_app.root_path, "..", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        safe_name = secure_filename(original_name)
        unique_filename = f"{uuid.uuid4().hex[:12]}_{safe_name}"
        file_path = os.path.join(upload_dir, unique_filename)
        uploaded_file.save(file_path)
        
        doc_name = original_name
        doc_url = f"/api/v1/public/files/{unique_filename}"

    complaint_payload = {
        "complainant_name": complainant_name,
        "complainant_email": complainant_email,
        "complainant_mobile": (data.get("complainant_mobile") or "").strip() or None,
        "institution_id": int(institution_id) if institution_id else None,
        "institution_code": data.get("institution_code"),
        "institution_name": institution_name,
        "institution_state": data.get("institution_state"),
        "category": category,
        "subject": subject,
        "description": description,
        "priority": data.get("priority"),
        "supporting_document_name": doc_name,
        "supporting_document_url": doc_url,
        "source": "Public Portal",
    }

    try:
        complaint = create_complaint(complaint_payload, current_user=None)
        return jsonify({
            "success": True,
            "message": "Complaint successfully registered",
            "ticket_number": complaint.ticket_number,
            "case_number": complaint.case_number,
            "complaint": complaint.to_public_dict()
        }), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to register complaint", "details": str(e)}), 500

@public_bp.route("/complaints/track/<ticket_number>", methods=["GET"])
def track_complaint(ticket_number: str):
    """
    Public lookup by ticket number (or case number).
    Strictly filters out sensitive internal data: officer names, internal notes, audit logs.
    """
    if not ticket_number:
        return jsonify({"error": "Ticket number is required"}), 400
    
    comp = get_complaint_by_ticket(ticket_number)
    if not comp:
        return jsonify({
            "error": "No grievance record found matching reference. Please check your ticket number (format: AICTE-2026-XXXXXX)."
        }), 404

    return jsonify({
        "success": True,
        "complaint": comp.to_public_dict()
    })

@public_bp.route("/institutions", methods=["GET"])
def search_institutions():
    """
    Public search endpoint to help citizens select their AICTE institution.
    """
    q = (request.args.get("q") or "").strip()
    limit = min(int(request.args.get("limit", 20)), 50)
    
    query = db.session.query(Institution)
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            db.or_(
                Institution.name.ilike(search_term),
                Institution.institution_code.ilike(search_term),
                Institution.state.ilike(search_term),
                Institution.district.ilike(search_term)
            )
        )
    institutions = query.order_by(Institution.name.asc()).limit(limit).all()
    
    return jsonify({
        "institutions": [
            {
                "id": inst.id,
                "name": inst.name,
                "institution_code": inst.institution_code,
                "state": inst.state,
                "district": inst.district,
                "institution_type": inst.institution_type
            }
            for inst in institutions
        ]
    })

@public_bp.route("/meta", methods=["GET"])
def get_public_meta():
    """
    Metadata for public form categories and bureaus.
    """
    categories = [
        "Fee Overcharging / Capitation",
        "Faculty Quality / Non-Payment",
        "Infrastructure Deficiencies",
        "Ragging Incident",
        "Approval / Accreditation Fraud",
        "Admission Irregularity",
        "General Administration"
    ]
    bureaus = [
        {"id": b.id, "name": b.name, "code": b.code}
        for b in db.session.query(Bureau).filter_by(is_active=True).order_by(Bureau.id.asc()).all()
    ]
    return jsonify({
        "categories": categories,
        "bureaus": bureaus
    })

@public_bp.route("/files/<path:filename>", methods=["GET"])
def download_public_file(filename: str):
    """
    Serve uploaded supporting documents safely.
    """
    upload_dir = current_app.config.get("UPLOAD_FOLDER") or os.path.join(current_app.root_path, "..", "uploads")
    return send_from_directory(upload_dir, filename)
