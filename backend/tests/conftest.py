import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.models import db, User, Bureau, Institution
from config import TestConfig

@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        # Seed baseline bureaus
        b1 = Bureau(id=1, name="Public Grievance Redressal Cell", code="PGRC")
        b2 = Bureau(id=2, name="Approval Bureau", code="AB")
        db.session.add_all([b1, b2])
        db.session.flush()

        # Seed baseline users
        admin = User(name="Admin User", email="admin@test.gov.in", role="admin")
        admin.set_password("Admin@123")

        officer1 = User(name="PGRC Officer", email="officer1@test.gov.in", role="officer", bureau_id=1)
        officer1.set_password("Officer@123")

        officer2 = User(name="AB Officer", email="officer2@test.gov.in", role="officer", bureau_id=2)
        officer2.set_password("Officer@123")

        senior = User(name="Senior Viewer", email="senior@test.gov.in", role="senior_authority")
        senior.set_password("Senior@123")

        # Seed baseline institution
        inst = Institution(
            id=1,
            institution_code="1-99990001",
            name="Indian Institute of Advanced Science",
            aliases='["IIAS Bangalore"]',
            institution_type="Engineering & Technology",
            state="Karnataka",
            district="Bengaluru Urban",
        )

        db.session.add_all([admin, officer1, officer2, senior, inst])
        db.session.commit()
        db.session.remove()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    def _get_headers(email="admin@test.gov.in", password="Admin@123"):
        res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert res.status_code == 200, f"Login failed for {email}: {res.get_json()}"
        token = res.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}
    return _get_headers
