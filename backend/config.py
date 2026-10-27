import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "aicte-portal-dev-secret-key-change-in-prod-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aicte-jwt-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    
    # Primary database: PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres@127.0.0.1:5432/aicte_complaints"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Cross-Bureau Overlap Detection Configuration
    OVERLAP_EXACT_MATCH_SCORE = 1.0
    OVERLAP_FUZZY_INSTITUTION_THRESHOLD = 0.82
    OVERLAP_TEXT_SIMILARITY_THRESHOLD = 0.45
    OVERLAP_HYBRID_ALERT_THRESHOLD = 0.60
    
    # Administrative & Demo Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000").split(",")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://postgres@127.0.0.1:5432/aicte_complaints_test"
    )
    WTF_CSRF_ENABLED = False
