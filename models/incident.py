from datetime import datetime, timezone
import json
from . import db


class Incident(db.Model):
    """Emergency incident report model with location, severity, and response state."""

    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    disaster_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    reporter_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(30), nullable=False)
    location_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    incident_datetime = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    image_filename = db.Column(db.String(255), nullable=True)

    # Priority classification: Critical, High, Medium, Low
    priority = db.Column(db.String(20), nullable=False, default="Medium", index=True)
    priority_score = db.Column(db.Integer, nullable=False, default=25)
    priority_reasons = db.Column(db.Text, nullable=True)  # JSON-serialized list of explanation strings

    # Lifecycle status: Reported, Under Review, Response in Progress, Resolved, Closed
    status = db.Column(db.String(30), nullable=False, default="Reported", index=True)

    # Assignment & resolution
    assigned_team = db.Column(db.String(120), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)

    # User association (nullable for guest/anonymous reports if needed, but linked when user is logged in)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    history = db.relationship(
        "IncidentHistory",
        backref="incident",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="desc(IncidentHistory.timestamp)",
    )
    assignments = db.relationship(
        "ResponseAssignment",
        backref="incident",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="desc(ResponseAssignment.assigned_at)",
    )

    @property
    def reasons_list(self) -> list:
        """Parse priority explanation reasons from JSON string."""
        if not self.priority_reasons:
            return []
        try:
            return json.loads(self.priority_reasons)
        except Exception:
            return [self.priority_reasons]

    @property
    def badge_class(self) -> str:
        """Return CSS badge class corresponding to incident priority."""
        return {
            "Critical": "badge-priority-critical",
            "High": "badge-priority-high",
            "Medium": "badge-priority-medium",
            "Low": "badge-priority-low",
        }.get(self.priority, "badge-priority-medium")

    @property
    def status_badge_class(self) -> str:
        """Return CSS badge class corresponding to incident status."""
        return {
            "Reported": "badge-status-reported",
            "Under Review": "badge-status-review",
            "Response in Progress": "badge-status-progress",
            "Resolved": "badge-status-resolved",
            "Closed": "badge-status-closed",
        }.get(self.status, "badge-status-reported")

    def to_geojson_feature(self) -> dict:
        """Serialize incident into GeoJSON-compatible structure for Leaflet.js."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "id": self.id,
                "title": self.title,
                "disaster_type": self.disaster_type,
                "priority": self.priority,
                "status": self.status,
                "location_name": self.location_name,
                "datetime": self.incident_datetime.strftime("%Y-%m-%d %H:%M UTC") if self.incident_datetime else "",
                "assigned_team": self.assigned_team or "Unassigned",
                "has_image": bool(self.image_filename),
                "image_url": f"/static/uploads/{self.image_filename}" if self.image_filename else None,
            },
        }

    def __repr__(self) -> str:
        return f"<Incident #{self.id} {self.title} [{self.priority} - {self.status}]>"


class IncidentHistory(db.Model):
    """Audit trail tracking every status and priority transition for accountability."""

    __tablename__ = "incident_history"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    changed_by_name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(60), nullable=False)
    previous_status = db.Column(db.String(30), nullable=True)
    new_status = db.Column(db.String(30), nullable=True)
    previous_priority = db.Column(db.String(20), nullable=True)
    new_priority = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<IncidentHistory #{self.id} on Incident #{self.incident_id}: {self.action}>"


class ResponseAssignment(db.Model):
    """Emergency response unit dispatch assignments and tracking."""

    __tablename__ = "response_assignments"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_team = db.Column(db.String(120), nullable=False)
    assigned_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    assigned_by_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default="Dispatched", nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ResponseAssignment #{self.id} Team: {self.assigned_team} on Incident #{self.incident_id}>"
