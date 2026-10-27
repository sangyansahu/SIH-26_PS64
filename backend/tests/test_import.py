def test_csv_preview_and_validation(client, auth_headers):
    headers = auth_headers("admin@test.gov.in", "Admin@123")

    csv_data = """institution_code,institution_name,category,subject,description,bureau_code,priority,external_reference
1-99990001,Indian Institute of Advanced Science,Fee Overcharging / Capitation,Caution money dispute,Caution fee non-refundable,PGRC,Medium,EXT-001
9-99999999,Unknown Institute Nowhere,Fee Overcharging / Capitation,Another complaint,Description here,PGRC,Low,EXT-002
"""

    res = client.post("/api/v1/imports/preview", data=csv_data, headers={**headers, "Content-Type": "text/csv"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_rows"] == 2
    assert data["valid_count"] == 1
    assert data["invalid_count"] == 1
    assert "Institution not found" in data["invalid_rows"][0]["errors"][0]

def test_csv_commit_batch(client, auth_headers):
    headers = auth_headers("admin@test.gov.in", "Admin@123")

    valid_rows = [{
        "institution_id": 1,
        "institution_code": "1-99990001",
        "institution_name": "Indian Institute of Advanced Science",
        "category": "Infrastructure Deficiencies",
        "subject": "Fire equipment not certified",
        "description": "Annual audit found expired fire extinguishers.",
        "bureau_id": 1,
        "bureau_code": "PGRC",
        "priority": "Medium",
        "external_reference": "IMP-001"
    }]

    commit_res = client.post("/api/v1/imports/commit", json={
        "filename": "annual_audit.csv",
        "valid_rows": valid_rows
    }, headers=headers)
    assert commit_res.status_code == 201
    data = commit_res.get_json()
    assert data["committed_count"] == 1
    assert data["failed_count"] == 0

    # Verify import batch appears in history
    hist_res = client.get("/api/v1/imports/history", headers=headers)
    assert hist_res.status_code == 200
    batches = hist_res.get_json()["batches"]
    assert len(batches) >= 1
    assert batches[0]["filename"] == "annual_audit.csv"
