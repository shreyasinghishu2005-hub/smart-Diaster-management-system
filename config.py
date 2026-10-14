import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "smart-disaster-mgmt-dev-key-academic-prototype-2026-xyz"
    )

    # SQLite database inside the instance directory (or PostgreSQL if DATABASE_URL is set on Render)
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    _db_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'disaster_management.db'}"
    )
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 Megabytes limit
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Security & session flags
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Prevent CSRF token expiry during long form filling

    # Academic Prototype Notice
    ACADEMIC_PROTOTYPE_NOTICE = (
        "ACADEMIC PROTOTYPE ONLY: This application is a college simulation project "
        "and is NOT connected to official 911 / 112 emergency services. In a real emergency, "
        "immediately contact your local emergency authorities directly."
    )


class TestConfig(Config):
    """Configuration for automated test suite."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads" / "test_uploads"
