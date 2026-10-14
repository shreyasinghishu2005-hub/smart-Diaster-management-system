from datetime import datetime, timezone
from . import db


class EmergencyResource(db.Model):
    """Emergency responder facility: hospital, fire station, police station, or shelter."""

    __tablename__ = "emergency_resources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    resource_type = db.Column(
        db.String(50), nullable=False, index=True
    )  # Hospital, Fire Station, Police Station, Relief Shelter
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self) -> dict:
        """Serialize resource to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "resource_type": self.resource_type,
            "address": self.address,
            "phone": self.phone or "N/A",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacity": self.capacity or "N/A",
            "is_active": self.is_active,
        }

    def to_geojson_feature(self) -> dict:
        """Serialize resource to GeoJSON feature for Leaflet."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "resource_type": self.resource_type,
                "address": self.address,
                "phone": self.phone or "N/A",
                "capacity": self.capacity or "Available",
                "is_active": self.is_active,
            },
        }

    def __repr__(self) -> str:
        return f"<EmergencyResource #{self.id} {self.name} ({self.resource_type})>"
