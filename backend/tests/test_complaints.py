def test_create_and_get_complaint(client, auth_headers):
    headers = auth_headers("admin@test.gov.in", "Admin@123")
    
    # Create complaint
    create_res = client.post("/api/v1/complaints", json={
        "institution_code": "1-99990001",
        "category": "Fee Overcharging / Capitation",
        "subject": "Mandatory donation demanded for exam admit cards",
        "description": "College administration is blocking hall tickets unless students pay an unauthorized sports development fee of Rs 10,000.",
        "receiving_bureau_id": 1,
        "priority": "High"
    }, headers=headers)
    
    assert create_res.status_code == 201
    created_data = create_res.get_json()["complaint"]
    assert created_data["case_number"].startswith("AICTE-")
    assert created_data["priority"] == "High"
    assert created_data["status"] == "Received"
    assert created_data["institution_name"] == "Indian Institute of Advanced Science"
    
    comp_id = created_data["id"]

    # Get complaint details
    get_res = client.get(f"/api/v1/complaints/{comp_id}", headers=headers)
    assert get_res.status_code == 200
    comp = get_res.get_json()["complaint"]
    assert len(comp["actions"]) >= 1
    assert comp["actions"][0]["action_type"] == "case_intake"

def test_status_update_and_timeline(client, auth_headers):
    admin_headers = auth_headers("admin@test.gov.in", "Admin@123")
    
    # Create complaint
    create_res = client.post("/api/v1/complaints", json={
        "institution_code": "1-99990001",
        "category": "Ragging Incident",
        "subject": "Hostel harassment incident",
        "description": "First year students harassed in hostel.",
        "receiving_bureau_id": 1,
        "priority": "Critical"
    }, headers=admin_headers)
    comp_id = create_res.get_json()["complaint"]["id"]

    # Update status to "Under Review"
    status_res = client.post(f"/api/v1/complaints/{comp_id}/actions", json={
        "status": "Under Review",
        "remarks": "Anti-ragging squad deployed for on-site inquiry."
    }, headers=admin_headers)
    assert status_res.status_code == 200
    comp = status_res.get_json()["complaint"]
    assert comp["status"] == "Under Review"
    
    # Verify timeline has both intake and status_change actions
    assert len(comp["actions"]) >= 2
    action_types = [a["action_type"] for a in comp["actions"]]
    assert "status_change" in action_types

def test_officer_bureau_restriction(client, auth_headers):
    admin_headers = auth_headers("admin@test.gov.in", "Admin@123")
    officer1_headers = auth_headers("officer1@test.gov.in", "Officer@123")  # Bureau 1 (PGRC)
    officer2_headers = auth_headers("officer2@test.gov.in", "Officer@123")  # Bureau 2 (AB)

    # Create complaint owned by Bureau 2 (Approval Bureau)
    create_res = client.post("/api/v1/complaints", json={
        "institution_code": "1-99990001",
        "category": "Approval / Accreditation Fraud",
        "subject": "Approval document falsification",
        "description": "Falsified fire safety NOC submitted.",
        "receiving_bureau_id": 2,
        "priority": "High"
    }, headers=admin_headers)
    comp_id = create_res.get_json()["complaint"]["id"]

    # Officer 1 (from Bureau 1) tries to update case of Bureau 2 -> Should be rejected with 403 Forbidden!
    forbidden_res = client.post(f"/api/v1/complaints/{comp_id}/actions", json={
        "status": "Disposed",
        "remarks": "Unauthorized attempt to close case."
    }, headers=officer1_headers)
    assert forbidden_res.status_code == 403
    assert "Forbidden" in forbidden_res.get_json()["error"]

    # Officer 2 (from Bureau 2) updates it -> Should succeed!
    allowed_res = client.post(f"/api/v1/complaints/{comp_id}/actions", json={
        "status": "Under Review",
        "remarks": "Authorized review started."
    }, headers=officer2_headers)
    assert allowed_res.status_code == 200
    assert allowed_res.get_json()["complaint"]["status"] == "Under Review"
