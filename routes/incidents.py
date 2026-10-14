import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
    abort,
)
from werkzeug.utils import secure_filename
from models import db, Incident, IncidentHistory, User
from routes.auth import get_current_user, login_required
from services.priority_service import classify_incident_priority, ml_classifier
from services.resource_service import get_combined_nearby_resources

incidents_bp = Blueprint("incidents", __name__)


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has an allowed image extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})


@incidents_bp.route("/report", methods=["GET", "POST"])
def report_incident():
    """Submit a new emergency report with interactive location selection and automatic priority scoring."""
    user = get_current_user()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        disaster_type = request.form.get("disaster_type", "").strip()
        description = request.form.get("description", "").strip()
        reporter_name = request.form.get("reporter_name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        location_name = request.form.get("location_name", "").strip()
        lat_str = request.form.get("latitude", "").strip()
        lng_str = request.form.get("longitude", "").strip()
        datetime_str = request.form.get("incident_datetime", "").strip()

        # Risk indicator flags
        has_trapped_or_injured = bool(request.form.get("has_trapped_or_injured"))
        is_hazard_spreading = bool(request.form.get("is_hazard_spreading"))
        has_structural_collapse = bool(request.form.get("has_structural_collapse"))

        errors = []

        # Server-side validation
        if not title or len(title) < 5:
            errors.append("Incident title must be at least 5 characters.")
        if disaster_type not in ["Flood", "Fire", "Earthquake", "Road Accident", "Medical Emergency", "Other"]:
            errors.append("Please select a valid disaster category.")
        if not description or len(description) < 15:
            errors.append("Please provide a detailed description (at least 15 characters).")
        if not reporter_name:
            errors.append("Reporter name is required.")
        if not contact_number or len(contact_number) < 7:
            errors.append("A valid emergency contact number is required.")
        if not location_name:
            errors.append("Location description or landmark is required.")

        # Coordinate validation
        try:
            latitude = float(lat_str)
            longitude = float(lng_str)
            if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
                errors.append("Coordinates are outside valid geographical bounds.")
        except (ValueError, TypeError):
            errors.append("Valid numerical Latitude and Longitude coordinates are required.")
            latitude, longitude = None, None

        # Datetime parsing
        if datetime_str:
            try:
                incident_datetime = datetime.fromisoformat(datetime_str)
            except ValueError:
                incident_datetime = datetime.now(timezone.utc)
        else:
            incident_datetime = datetime.now(timezone.utc)

        # File upload handling
        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                if allowed_file(file.filename):
                    original_name = secure_filename(file.filename)
                    # Unique prefix to prevent collision
                    unique_id = uuid.uuid4().hex[:8]
                    image_filename = f"{unique_id}_{original_name}"
                    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
                    upload_folder.mkdir(parents=True, exist_ok=True)
                    file.save(str(upload_folder / image_filename))
                else:
                    errors.append("Invalid file format. Allowed types: PNG, JPG, JPEG, WEBP.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "report_incident.html",
                user=user,
                title=title,
                disaster_type=disaster_type,
                description=description,
                reporter_name=reporter_name or (user.full_name if user else ""),
                contact_number=contact_number or (user.phone if user else ""),
                location_name=location_name,
                latitude=lat_str,
                longitude=lng_str,
                has_trapped_or_injured=has_trapped_or_injured,
                is_hazard_spreading=is_hazard_spreading,
                has_structural_collapse=has_structural_collapse,
            )

        # Automatic Rule-Based Priority Classification
        priority, score, reasons = classify_incident_priority(
            disaster_type=disaster_type,
            title=title,
            description=description,
            has_trapped_or_injured=has_trapped_or_injured,
            is_hazard_spreading=is_hazard_spreading,
            has_structural_collapse=has_structural_collapse,
        )

        # Store incident in SQLite database
        new_incident = Incident(
            title=title,
            disaster_type=disaster_type,
            description=description,
            reporter_name=reporter_name,
            contact_number=contact_number,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            incident_datetime=incident_datetime,
            image_filename=image_filename,
            priority=priority,
            priority_score=score,
            priority_reasons=json.dumps(reasons),
            status="Reported",
            user_id=user.id if user else None,
        )
        db.session.add(new_incident)
        db.session.flush()  # populate new_incident.id

        # Record initial audit entry
        initial_history = IncidentHistory(
            incident_id=new_incident.id,
            changed_by_id=user.id if user else None,
            changed_by_name=user.full_name if user else reporter_name,
            action="Reported",
            previous_status=None,
            new_status="Reported",
            previous_priority=None,
            new_priority=priority,
            notes=f"Emergency report filed. Automatic rule engine classified priority as '{priority}' (Score: {score}/100).",
        )
        db.session.add(initial_history)
        db.session.commit()

        flash(
            f"Emergency Report #{new_incident.id} submitted successfully! Classified as '{priority}' priority based on initial triage criteria.",
            "success",
        )
        return redirect(url_for("incidents.view_incident", incident_id=new_incident.id))

    # Pre-fill reporter information for logged-in users
    default_name = user.full_name if user else ""
    default_phone = user.phone if user and user.phone else ""

    return render_template(
        "report_incident.html",
        user=user,
        reporter_name=default_name,
        contact_number=default_phone,
    )


@incidents_bp.route("/incident/<int:incident_id>")
def view_incident(incident_id: int):
    """View detailed information, location map, priority justification, and status audit for an incident."""
    incident = db.get_or_404(Incident, incident_id)
    current_user = get_current_user()

    # Access control:
    # Administrators can view any report.
    # Authenticated citizens can view their own reports.
    # If the user is unauthenticated or not the owner/admin, restrict private view.
    is_owner = current_user and incident.user_id == current_user.id
    is_admin = current_user and current_user.is_admin

    if not is_admin and not is_owner:
        flash("You are not authorized to view the private records of this report.", "warning")
        return redirect(url_for("auth.login", next=request.path))

    # Fetch nearby emergency resources (Database + graceful OSM Overpass lookup)
    nearby_data = get_combined_nearby_resources(
        lat=incident.latitude, lon=incident.longitude, radius_km=15.0
    )

    # Scikit-learn demonstration classifier prediction for educational comparison
    combined_incident_text = f"{incident.title} {incident.description}"
    ml_result = ml_classifier.predict(combined_incident_text)

    return render_template(
        "incident_details.html",
        incident=incident,
        current_user=current_user,
        is_admin=is_admin,
        is_owner=is_owner,
        nearby_resources=nearby_data.get("resources", []),
        osm_count=nearby_data.get("osm_count", 0),
        database_count=nearby_data.get("database_count", 0),
        ml_prediction=ml_result,
    )
