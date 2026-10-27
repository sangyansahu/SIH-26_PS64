from app.services.overlap_service import normalize_text, extract_keywords

def test_normalization_and_keywords():
    raw = "ABC Inst. of Tech. & Engg."
    norm = normalize_text(raw)
    assert "institute" in norm
    assert "technology" in norm
    assert "engineering" in norm
    assert "&" not in norm

    keywords = extract_keywords("Students are protesting regarding illegal capitation fee and marksheets withholding")
    assert "capitation" in keywords
    assert "marksheets" in keywords
    assert "withholding" in keywords
    assert "regarding" not in keywords # Stopword

def test_cross_bureau_overlap_detection(client, auth_headers):
    headers = auth_headers("admin@test.gov.in", "Admin@123")

    # Lodging Complaint 1 in Bureau 1 (PGRC)
    c1_res = client.post("/api/v1/complaints", json={
        "institution_code": "1-99990001",
        "category": "Fee Overcharging / Capitation",
        "subject": "Extortionate capitation fee demanded for laboratory access",
        "description": "College demands Rs 80000 unauthorized capitation fee from 3rd semester students.",
        "receiving_bureau_id": 1,
        "priority": "High",
        "external_reference": "REF-COMMON-99"
    }, headers=headers)
    assert c1_res.status_code == 201

    # Lodging Complaint 2 in Bureau 2 (Approval Bureau) with overlapping subject & identical ref
    c2_res = client.post("/api/v1/complaints", json={
        "institution_code": "1-99990001",
        "category": "Fee Overcharging / Capitation",
        "subject": "Capitation fee extortion violation of AICTE approval norms",
        "description": "Petition regarding illegal Rs 80000 capitation fee demanded from students.",
        "receiving_bureau_id": 2,
        "priority": "High",
        "external_reference": "REF-COMMON-99"
    }, headers=headers)
    assert c2_res.status_code == 201

    # Check overlaps queue
    overlaps_res = client.get("/api/v1/overlaps?review_status=pending", headers=headers)
    assert overlaps_res.status_code == 200
    data = overlaps_res.get_json()
    assert data["total"] >= 1

    overlap = data["overlaps"][0]
    assert overlap["match_score"] >= 0.80
    assert overlap["review_status"] == "pending"
    assert "case_a" in overlap and "case_b" in overlap

    # Test Official Review: Confirm Relationship
    link_id = overlap["id"]
    review_res = client.post(f"/api/v1/overlaps/{link_id}/review", json={
        "decision": "confirmed_related",
        "remarks": "Joint inquiry ordered between PGRC and Approval Bureau."
    }, headers=headers)
    assert review_res.status_code == 200
    rev = review_res.get_json()["overlap"]
    assert rev["relationship_type"] == "confirmed_related"
    assert rev["review_status"] == "confirmed"
    assert rev["reviewed_by_name"] == "Admin User"
