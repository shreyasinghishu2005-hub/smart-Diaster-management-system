import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, session
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from routes.auth import auth_bp, get_current_user
from routes.user import user_bp
from routes.incidents import incidents_bp
from routes.admin import admin_bp
from routes.maps import maps_bp
from seed_data import seed_database

csrf = CSRFProtect()


def create_app(config_class=Config):
    """Application factory for Smart Disaster Management System."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Exempt API JSON endpoints from CSRF token verification
    csrf.exempt(maps_bp)

    # Ensure required directories exist
    upload_path = Path(app.config["UPLOAD_FOLDER"])
    upload_path.mkdir(parents=True, exist_ok=True)
    instance_path = Path(app.config.get("INSTANCE_DIR", app.root_path + "/instance"))
    instance_path.mkdir(parents=True, exist_ok=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(maps_bp)

    # Route to serve uploads from UPLOAD_FOLDER (handles local, Render, and Vercel /tmp)
    @app.route("/static/uploads/<path:filename>")
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(str(app.config["UPLOAD_FOLDER"]), filename)

    # Inject context processors for templates
    @app.context_processor
    def inject_global_template_vars():
        return {
            "current_user": get_current_user(),
            "prototype_notice": app.config.get("ACADEMIC_PROTOTYPE_NOTICE"),
            "now_year": 2026,
        }

    # Custom Jinja filters
    @app.template_filter("timeago")
    def timeago_filter(dt):
        """Format datetime as friendly relative or formatted time."""
        if not dt:
            return "N/A"
        try:
            return dt.strftime("%b %d, %Y at %I:%M %p")
        except Exception:
            return str(dt)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    # CLI command: initialize database
    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables."""
        with app.app_context():
            db.create_all()
            print("Database initialized successfully.")

    # CLI command: seed sample data
    @app.cli.command("seed-demo-data")
    def seed_data_command():
        """Seed fictional academic demonstration data."""
        with app.app_context():
            db.create_all()
            seed_database(app)

    # CLI command: create administrator account
    @app.cli.command("create-admin")
    def create_admin_command():
        """Create or promote an administrator account."""
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        full_name = input("Enter full name: ").strip()
        password = input("Enter admin password: ").strip()

        with app.app_context():
            existing = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing:
                existing.role = "admin"
                existing.set_password(password)
                db.session.commit()
                print(f"User '{username}' updated to Administrator role.")
            else:
                admin = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    phone="+1-555-000-0000",
                    role="admin",
                )
                admin.set_password(password)
                db.session.add(admin)
                db.session.commit()
                print(f"Administrator account '{username}' created successfully.")

    # Auto-initialize and seed database on first launch if not yet created
    with app.app_context():
        db.create_all()
        # Seed if empty
        if not User.query.first():
            print("First run detected: automatically seeding demonstration database...")
            seed_database(app)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
