from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from models import db, User

auth_bp = Blueprint("auth", __name__)


def get_current_user():
    """Retrieve logged in user from session, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(f):
    """Decorator to restrict access to authenticated users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to restrict access strictly to administrators."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Administrator login required.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        if session.get("user_role") != "admin":
            flash("Access denied: Administrative privileges required.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new citizen/user account."""
    if session.get("user_id"):
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Server-side validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if not email or "@" not in email:
            errors.append("Please provide a valid email address.")
        if not full_name:
            errors.append("Full name is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        # Check existing user
        if User.query.filter_by(username=username).first():
            errors.append("This username is already taken. Please choose another.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "register.html",
                username=username,
                email=email,
                full_name=full_name,
                phone=phone,
            )

        # Create new citizen user (Role defaults strictly to 'user')
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role="user",
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Log user in
        session["user_id"] = new_user.id
        session["username"] = new_user.username
        session["user_role"] = new_user.role
        session["full_name"] = new_user.full_name

        flash("Registration successful! Welcome to the Smart Disaster Management Portal.", "success")
        return redirect(url_for("user.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User and Administrator authentication."""
    if session.get("user_id"):
        if session.get("user_role") == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("user.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()  # username or email
        password = request.form.get("password", "")
        next_url = request.form.get("next") or request.args.get("next")

        if not identifier or not password:
            flash("Please provide both your username/email and password.", "danger")
            return render_template("login.html", identifier=identifier)

        # Look up user by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            session["username"] = user.username
            session["user_role"] = user.role
            session["full_name"] = user.full_name

            flash(f"Welcome back, {user.full_name}!", "success")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            if user.is_admin:
                return redirect(url_for("admin.admin_dashboard"))
            return redirect(url_for("user.dashboard"))

        flash("Invalid username/email or password. Please try again.", "danger")
        return render_template("login.html", identifier=identifier)

    return render_template("login.html", next=request.args.get("next"))


@auth_bp.route("/logout")
def logout():
    """Terminate user session securely."""
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("user.index"))
