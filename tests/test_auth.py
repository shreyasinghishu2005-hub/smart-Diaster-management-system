"""Automated tests for user registration, authentication, hashing, and role permissions."""

from models import User


def test_user_registration_success(client, app):
    """Test standard citizen registration."""
    response = client.post(
        "/register",
        data={
            "username": "newcitizen",
            "email": "newcitizen@example.com",
            "full_name": "New Citizen",
            "phone": "+1-555-999-8888",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    with app.app_context():
        user = User.query.filter_by(username="newcitizen").first()
        assert user is not None
        assert user.role == "user"  # Role must default to 'user'
        assert user.check_password("SecurePassword123!") is True
        assert user.password_hash != "SecurePassword123!"  # Must be hashed


def test_registration_validation_errors(client):
    """Test registration failure on invalid inputs."""
    # Mismatched passwords
    res1 = client.post(
        "/register",
        data={
            "username": "invaliduser",
            "email": "invalid@example.com",
            "full_name": "Invalid User",
            "password": "Password123",
            "confirm_password": "MismatchPassword",
        },
        follow_redirects=True,
    )
    assert b"Passwords do not match" in res1.data

    # Password too short
    res2 = client.post(
        "/register",
        data={
            "username": "shortpwd",
            "email": "short@example.com",
            "full_name": "Short Pwd",
            "password": "123",
            "confirm_password": "123",
        },
        follow_redirects=True,
    )
    assert b"Password must be at least 6 characters" in res2.data


def test_login_and_logout(client, init_test_users):
    """Test citizen login and secure session termination."""
    # Successful citizen login
    login_res = client.post(
        "/login",
        data={"identifier": "testcitizen", "password": "CitizenPass123!"},
        follow_redirects=True,
    )
    assert login_res.status_code == 200
    assert b"Welcome back" in login_res.data
    assert b"Citizen Emergency Dashboard" in login_res.data

    # Logout
    logout_res = client.get("/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"safely logged out" in logout_res.data


def test_login_invalid_credentials(client, init_test_users):
    """Test login rejection on incorrect password."""
    res = client.post(
        "/login",
        data={"identifier": "testcitizen", "password": "WrongPassword!"},
        follow_redirects=True,
    )
    assert b"Invalid username/email or password" in res.data


def test_role_based_access_control(client, init_test_users):
    """Ensure normal citizen cannot access administrative routes."""
    # 1. Unauthenticated request to admin dashboard redirects to login
    anon_res = client.get("/admin/dashboard", follow_redirects=True)
    assert b"Administrator login required" in anon_res.data

    # 2. Login as regular citizen
    client.post(
        "/login",
        data={"identifier": "testcitizen", "password": "CitizenPass123!"},
        follow_redirects=True,
    )

    # 3. Regular citizen attempting to access admin dashboard is denied
    forbidden_res = client.get("/admin/dashboard", follow_redirects=True)
    assert b"Administrative privileges required" in forbidden_res.data

    # 4. Login as administrator succeeds and accesses admin console
    client.get("/logout")
    admin_login = client.post(
        "/login",
        data={"identifier": "testadmin", "password": "AdminPass123!"},
        follow_redirects=True,
    )
    assert b"Emergency Operations Command Dashboard" in admin_login.data
