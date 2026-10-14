from flask import Blueprint, render_template, request, jsonify
from models import Incident, EmergencyResource
from services.resource_service import get_combined_nearby_resources, get_nearby_database_resources
from services.priority_service import classify_incident_priority, ml_classifier

maps_bp = Blueprint("maps", __name__)


@maps_bp.route("/map")
def view_map():
    """Full-page interactive emergency response map with filter controls and resource overlays."""
    return render_template("map.html")


@maps_bp.route("/api/incidents")
def api_incidents():
    """GeoJSON endpoint delivering incident reports for Leaflet rendering."""
    disaster_type = request.args.get("type")
    priority = request.args.get("priority")
    status = request.args.get("status")

    query = Incident.query

    if disaster_type and disaster_type != "All":
        query = query.filter_by(disaster_type=disaster_type)
    if priority and priority != "All":
        query = query.filter_by(priority=priority)
    if status and status != "All":
        if status == "Active":
            query = query.filter(Incident.status.in_(["Reported", "Under Review", "Response in Progress"]))
        elif status == "Resolved":
            query = query.filter(Incident.status.in_(["Resolved", "Closed"]))
        else:
            query = query.filter_by(status=status)

    incidents = query.all()
    features = [inc.to_geojson_feature() for inc in incidents]

    return jsonify({
        "type": "FeatureCollection",
        "count": len(features),
        "features": features,
    })


@maps_bp.route("/api/resources")
def api_resources():
    """GeoJSON endpoint delivering registered emergency facilities."""
    resource_type = request.args.get("type")
    query = EmergencyResource.query.filter_by(is_active=True)

    if resource_type and resource_type != "All":
        query = query.filter_by(resource_type=resource_type)

    resources = query.all()
    features = [res.to_geojson_feature() for res in resources]

    return jsonify({
        "type": "FeatureCollection",
        "count": len(features),
        "features": features,
    })


@maps_bp.route("/api/nearby-resources")
def api_nearby_resources():
    """Query nearby emergency resources within specified radius around lat/lon."""
    try:
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lng", 0))
        radius = float(request.args.get("radius", 15.0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinates or radius"}), 400

    results = get_combined_nearby_resources(lat, lon, radius_km=radius)
    return jsonify(results)


@maps_bp.route("/api/predict-ml", methods=["POST"])
def api_predict_ml():
    """Demonstration endpoint comparing rule-based triage score vs scikit-learn ML prediction."""
    data = request.get_json(silent=True) or request.form
    text = data.get("text", "").strip()
    disaster_type = data.get("disaster_type", "Other")

    if not text:
        return jsonify({"error": "No description text provided"}), 400

    rule_priority, score, reasons = classify_incident_priority(
        disaster_type=disaster_type,
        title="Sample Incident",
        description=text,
    )
    ml_result = ml_classifier.predict(text)

    return jsonify({
        "rule_engine": {
            "priority": rule_priority,
            "score": score,
            "reasons": reasons,
        },
        "ml_classifier": ml_result,
    })
