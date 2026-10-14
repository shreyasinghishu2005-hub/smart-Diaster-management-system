from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from models import db, Incident, IncidentHistory, ResponseAssignment, User
from routes.auth import admin_required, get_current_user
from services.resource_service import get_combined_nearby_resources

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    """Administrator executive dashboard with emergency KPIs, breakdowns, and recent incidents."""
    user = get_current_user()

    total_incidents = Incident.query.count()
    critical_count = Incident.query.filter_by(priority="Critical").count()
    high_count = Incident.query.filter_by(priority="High").count()
    medium_count = Incident.query.filter_by(priority="Medium").count()
    low_count = Incident.query.filter_by(priority="Low").count()

    reported_count = Incident.query.filter_by(status="Reported").count()
    under_review_count = Incident.query.filter_by(status="Under Review").count()
    in_progress_count = Incident.query.filter_by(status="Response in Progress").count()
    resolved_count = Incident.query.filter_by(status="Resolved").count()
    closed_count = Incident.query.filter_by(status="Closed").count()

    pending_total = reported_count + under_review_count
    resolved_total = resolved_count + closed_count

    # Breakdown by disaster category
    categories = ["Flood", "Fire", "Earthquake", "Road Accident", "Medical Emergency", "Other"]
    type_counts = {
        cat: Incident.query.filter_by(disaster_type=cat).count() for cat in categories
    }

    # Recent 10 incidents
    recent_incidents = (
        Incident.query.order_by(Incident.created_at.desc()).limit(10).all()
    )

    return render_template(
        "admin_dashboard.html",
        user=user,
        total_incidents=total_incidents,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        pending_total=pending_total,
        in_progress_count=in_progress_count,
        resolved_total=resolved_total,
        type_counts=type_counts,
        recent_incidents=recent_incidents,
    )


@admin_bp.route("/incidents")
@admin_required
def manage_incidents():
    """Incident management list with multi-parameter search, filtering, and sorting."""
    user = get_current_user()

    # Query filters
    search_q = request.args.get("q", "").strip()
    filter_type = request.args.get("type", "").strip()
    filter_priority = request.args.get("priority", "").strip()
    filter_status = request.args.get("status", "").strip()

    query = Incident.query

    if search_q:
        pattern = f"%{search_q}%"
        query = query.filter(
            (Incident.title.ilike(pattern))
            | (Incident.description.ilike(pattern))
            | (Incident.reporter_name.ilike(pattern))
            | (Incident.location_name.ilike(pattern))
        )

    if filter_type and filter_type != "All":
        query = query.filter_by(disaster_type=filter_type)

    if filter_priority and filter_priority != "All":
        query = query.filter_by(priority=filter_priority)

    if filter_status and filter_status != "All":
        query = query.filter_by(status=filter_status)

    incidents = query.order_by(Incident.created_at.desc()).all()

    return render_template(
        "manage_incidents.html",
        user=user,
        incidents=incidents,
        search_q=search_q,
        filter_type=filter_type,
        filter_priority=filter_priority,
        filter_status=filter_status,
        total_matched=len(incidents),
    )


@admin_bp.route("/incident/<int:incident_id>/manage", methods=["GET", "POST"])
@admin_required
def admin_incident_detail(incident_id: int):
    """Detailed incident management view with status updates, priority adjustments, assignments, and audit logs."""
    incident = db.get_or_404(Incident, incident_id)
    admin_user = get_current_user()

    if request.method == "POST":
        action_type = request.form.get("action_type")

        # 1. Update Status
        if action_type == "update_status":
            new_status = request.form.get("new_status")
            status_notes = request.form.get("status_notes", "").strip()
            valid_statuses = ["Reported", "Under Review", "Response in Progress", "Resolved", "Closed"]

            if new_status in valid_statuses and new_status != incident.status:
                old_status = incident.status
                incident.status = new_status
                incident.updated_at = datetime.now(timezone.utc)

                # Record history
                history = IncidentHistory(
                    incident_id=incident.id,
                    changed_by_id=admin_user.id,
                    changed_by_name=admin_user.full_name,
                    action="Status Changed",
                    previous_status=old_status,
                    new_status=new_status,
                    notes=status_notes or f"Status shifted from {old_status} to {new_status}.",
                )
                db.session.add(history)
                db.session.commit()
                flash(f"Incident #{incident.id} status updated to '{new_status}'.", "success")
            else:
                flash("No valid status change requested.", "warning")

        # 2. Adjust Priority
        elif action_type == "adjust_priority":
            new_priority = request.form.get("new_priority")
            priority_reason = request.form.get("priority_reason", "").strip()
            valid_priorities = ["Critical", "High", "Medium", "Low"]

            if not priority_reason:
                flash("Please provide an administrative justification when manually adjusting priority.", "danger")
            elif new_priority in valid_priorities and new_priority != incident.priority:
                old_priority = incident.priority
                incident.priority = new_priority
                incident.updated_at = datetime.now(timezone.utc)

                history = IncidentHistory(
                    incident_id=incident.id,
                    changed_by_id=admin_user.id,
                    changed_by_name=admin_user.full_name,
                    action="Priority Adjusted",
                    previous_priority=old_priority,
                    new_priority=new_priority,
                    notes=f"Priority adjusted from {old_priority} to {new_priority}. Reason: {priority_reason}",
                )
                db.session.add(history)
                db.session.commit()
                flash(f"Incident #{incident.id} priority reclassified to '{new_priority}'.", "success")

        # 3. Assign Response Unit
        elif action_type == "assign_team":
            team_name = request.form.get("team_name", "").strip()
            instructions = request.form.get("instructions", "").strip()

            if team_name:
                incident.assigned_team = team_name
                if incident.status in ["Reported", "Under Review"]:
                    incident.status = "Response in Progress"
                incident.updated_at = datetime.now(timezone.utc)

                assignment = ResponseAssignment(
                    incident_id=incident.id,
                    assigned_team=team_name,
                    assigned_by_id=admin_user.id,
                    assigned_by_name=admin_user.full_name,
                    status="Dispatched",
                    instructions=instructions,
                )
                history = IncidentHistory(
                    incident_id=incident.id,
                    changed_by_id=admin_user.id,
                    changed_by_name=admin_user.full_name,
                    action="Team Assigned",
                    new_status=incident.status,
                    notes=f"Emergency unit '{team_name}' dispatched with instructions: {instructions or 'Standard response dispatch'}.",
                )
                db.session.add(assignment)
                db.session.add(history)
                db.session.commit()
                flash(f"Team '{team_name}' dispatched to Incident #{incident.id}.", "success")
            else:
                flash("Please specify the responding unit or agency name.", "danger")

        # 4. Record Resolution
        elif action_type == "record_resolution":
            resolution_notes = request.form.get("resolution_notes", "").strip()
            close_incident = bool(request.form.get("close_incident"))

            if resolution_notes:
                incident.resolution_notes = resolution_notes
                old_status = incident.status
                incident.status = "Closed" if close_incident else "Resolved"
                incident.updated_at = datetime.now(timezone.utc)

                history = IncidentHistory(
                    incident_id=incident.id,
                    changed_by_id=admin_user.id,
                    changed_by_name=admin_user.full_name,
                    action="Resolution Recorded",
                    previous_status=old_status,
                    new_status=incident.status,
                    notes=f"Resolution details: {resolution_notes}",
                )
                db.session.add(history)
                db.session.commit()
                flash(f"Resolution logged for Incident #{incident.id}. Status set to {incident.status}.", "success")
            else:
                flash("Please enter comprehensive resolution notes before submitting.", "danger")

        return redirect(url_for("admin.admin_incident_detail", incident_id=incident.id))

    # Nearby resources for dispatch decisions
    nearby_data = get_combined_nearby_resources(
        lat=incident.latitude, lon=incident.longitude, radius_km=15.0
    )

    return render_template(
        "admin_incident_detail.html",
        admin_user=admin_user,
        incident=incident,
        nearby_resources=nearby_data.get("resources", []),
    )
