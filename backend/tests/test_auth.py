def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@test.gov.in",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "token" in data
    assert data["user"]["email"] == "admin@test.gov.in"
    assert data["user"]["role"].upper() in ("ADMIN", "SYSTEM_ADMIN")

def test_login_invalid_credentials(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@test.gov.in",
        "password": "WrongPassword"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.get_json()["error"]

def test_get_me(client, auth_headers):
    headers = auth_headers("officer1@test.gov.in", "Officer@123")
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 200
    user = res.get_json()["user"]
    assert user["name"] == "PGRC Officer"
    assert user["role"].upper() in ("OFFICER", "INDUSTRY")
    assert user["bureau_code"] == "PGRC"

def test_unauthenticated_protected_route_rejected(client):
    """Under SIH 2026 security rules, login is mandatory; unauthenticated access returns 401."""
    res = client.get("/api/v1/complaints")
    assert res.status_code == 401
