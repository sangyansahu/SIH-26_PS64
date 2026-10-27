import io
import re

def test_public_meta_and_institutions(client):
    # Test public metadata
    meta_res = client.get("/api/v1/public/meta")
    assert meta_res.status_code == 200
    meta = meta_res.get_json()
    assert "categories" in meta
    assert "bureaus" in meta
    assert len(meta["categories"]) >= 5
    assert len(meta["bureaus"]) >= 2

    # Test public institutions search
    inst_res = client.get("/api/v1/public/institutions?q=Indian")
    assert inst_res.status_code == 200
    inst_data = inst_res.get_json()
    assert "institutions" in inst_data
    assert len(inst_data["institutions"]) >= 1

def test_register_public_complaint_and_ticket_generation(client):
    payload = {
        "complainant_name": "Anita Verma",
        "complainant_email": "anita.verma@example.edu",
        "complainant_mobile": "9811223344",
        "institution_code": "1-99990001",
        "category": "Fee Overcharging / Capitation",
        "subject": "Unauthorized caution deposit not refunded",
        "description": "Graduated students have not received their caution deposit refund after 6 months."
    }

    res = client.post("/api/v1/public/complaints", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert "ticket_number" in data
    ticket = data["ticket_number"]
    
    # Must follow AICTE-2026-XXXXXX format
    assert re.match(r"^AICTE-2026-[A-Z0-9]{6}$", ticket)
    assert data["complaint"]["ticket_number"] == ticket
    assert data["complaint"]["status"] == "Received"

    # Test tracking with valid ticket number
    track_res = client.get(f"/api/v1/public/complaints/track/{ticket}")
    assert track_res.status_code == 200
    track_data = track_res.get_json()
    assert track_data["success"] is True
    comp = track_data["complaint"]
    assert comp["ticket_number"] == ticket
    assert comp["subject"] == payload["subject"]
    assert comp["category"] == payload["category"]
    assert "institution_name" in comp

    # Verify sensitive admin data is strictly excluded
    assert "assigned_officer_name" not in comp
    assert "assigned_user_id" not in comp
    assert "created_by_user_id" not in comp
    assert "actions" not in comp
    assert "internal_notes" not in comp

def test_register_public_complaint_with_file_upload(client):
    file_content = b"Official complaint affidavit and bank proof."
    file_storage = (io.BytesIO(file_content), "complaint_affidavit.pdf")

    res = client.post(
        "/api/v1/public/complaints",
        data={
            "complainant_name": "Suresh Kumar",
            "complainant_email": "suresh@example.org",
            "complainant_mobile": "9988776655",
            "institution_code": "1-99990001",
            "category": "Ragging Incident",
            "subject": "Anti-ragging committee inaction",
            "description": "Reported harassment to institutional cell with no response.",
            "file": file_storage
        },
        content_type="multipart/form-data"
    )

    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    ticket = data["ticket_number"]
    assert re.match(r"^AICTE-2026-[A-Z0-9]{6}$", ticket)
    assert data["complaint"]["has_supporting_document"] is True
    assert data["complaint"]["supporting_document_name"] == "complaint_affidavit.pdf"

    # Track complaint
    track_res = client.get(f"/api/v1/public/complaints/track/{ticket}")
    assert track_res.status_code == 200
    track_comp = track_res.get_json()["complaint"]
    assert track_comp["has_supporting_document"] is True
    assert track_comp["supporting_document_name"] == "complaint_affidavit.pdf"

def test_track_invalid_ticket(client):
    res = client.get("/api/v1/public/complaints/track/AICTE-2026-NONEXIST")
    assert res.status_code == 404
    assert "error" in res.get_json()

def test_register_missing_fields_validation(client):
    res = client.post("/api/v1/public/complaints", json={
        "complainant_name": "",
        "subject": "Test"
    })
    assert res.status_code == 400
    assert "error" in res.get_json()
