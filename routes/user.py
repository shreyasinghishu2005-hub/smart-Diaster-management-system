from flask import Blueprint, render_template, session, redirect, url_for
from models import db, Incident, EmergencyResource
from routes.auth import login_required, get_current_user

user_bp = Blueprint("user", __name__)


@user_bp.route("/")
def index():
    """Public landing page displaying platform overview, emergency contacts, and disclaimer."""
    total_incidents = Incident.query.count()
    active_incidents = Incident.query.filter(
        Incident.status.in_(["Reported", "Under Review", "Response in Progress"])
    ).count()
    resolved_incidents = Incident.query.filter(
        Incident.status.in_(["Resolved", "Closed"])
    ).count()
    active_facilities = EmergencyResource.query.filter_by(is_active=True).count()

    recent_public_incidents = (
        Incident.query.order_by(Incident.created_at.desc()).limit(4).all()
    )

    return render_template(
        "index.html",
        total_incidents=total_incidents,
        active_incidents=active_incidents,
        resolved_incidents=resolved_incidents,
        active_facilities=active_facilities,
        recent_incidents=recent_public_incidents,
    )


@user_bp.route("/dashboard")
@login_required
def dashboard():
    """Citizen user dashboard showing recent reports, status summary, and map preview."""
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    # User's personal incident reports
    user_incidents = (
        Incident.query.filter_by(user_id=user.id)
        .order_by(Incident.created_at.desc())
        .all()
    )

    total_submitted = len(user_incidents)
    pending_count = sum(1 for i in user_incidents if i.status in ["Reported", "Under Review"])
    in_progress_count = sum(1 for i in user_incidents if i.status == "Response in Progress")
    resolved_count = sum(1 for i in user_incidents if i.status in ["Resolved", "Closed"])

    # Recent 5 submissions for dashboard table
    recent_submissions = user_incidents[:5]

    return render_template(
        "dashboard.html",
        user=user,
        total_submitted=total_submitted,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        recent_submissions=recent_submissions,
    )


@user_bp.route("/my-reports")
@login_required
def my_reports():
    """Listing of all emergency reports submitted by the logged in user."""
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    reports = (
        Incident.query.filter_by(user_id=user.id)
        .order_by(Incident.created_at.desc())
        .all()
    )

    return render_template("my_reports.html", user=user, reports=reports)
