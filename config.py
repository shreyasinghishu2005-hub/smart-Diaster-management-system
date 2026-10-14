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

    # Detect Vercel serverless environment (requires /tmp for writable SQLite and uploads)
    IS_VERCEL = bool(os.environ.get("VERCEL"))

    if IS_VERCEL:
        INSTANCE_DIR = Path("/tmp") / "instance"
        UPLOAD_FOLDER = Path("/tmp") / "uploads"
    else:
        INSTANCE_DIR = BASE_DIR / "instance"
        UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"

    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # SQLite database inside instance directory (or PostgreSQL if DATABASE_URL is set)
    _db_url = os.environ.get(
        "DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'disaster_management.db'}"
    )
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads limit and allowed extensions
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
