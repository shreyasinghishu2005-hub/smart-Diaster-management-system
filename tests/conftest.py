import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app import create_app
from config import TestConfig
from models import db, User, EmergencyResource


@pytest.fixture
def app():
    """Create and configure a fresh Flask app instance for testing."""
    application = create_app(TestConfig)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def init_test_users(app):
    """Seed test users into in-memory database."""
    with app.app_context():
        # Standard Citizen User
        user = User(
            username="testcitizen",
            email="citizen@test.local",
            full_name="Test Citizen",
            phone="+1-555-010-1111",
            role="user",
        )
        user.set_password("CitizenPass123!")
        db.session.add(user)

        # Another Citizen User for isolation testing
        other_user = User(
            username="othercitizen",
            email="other@test.local",
            full_name="Other Citizen",
            phone="+1-555-010-2222",
            role="user",
        )
        other_user.set_password("CitizenPass123!")
        db.session.add(other_user)

        # Administrator User
        admin = User(
            username="testadmin",
            email="admin@test.local",
            full_name="System Administrator",
            phone="+1-555-010-9999",
            role="admin",
        )
        admin.set_password("AdminPass123!")
        db.session.add(admin)

        db.session.commit()
