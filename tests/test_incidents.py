"""Automated tests for incident reporting, priority persistence, lifecycle updates, and access controls."""

from models import db, Incident, IncidentHistory, User


def test_submit_incident_report(client, init_test_users, app):
    """Test citizen submitting an emergency incident report."""
    # Login as citizen
    client.post(
        "/login",
        data={"identifier": "testcitizen", "password": "CitizenPass123!"},
        follow_redirects=True,
    )

    # Submit emergency report
    report_res = client.post(
        "/report",
        data={
            "title": "Severe Flash Flood Inundating Streets",
            "disaster_type": "Flood",
            "description": "Rising floodwaters have submerged vehicles and residents are trapped on second floors.",
            "reporter_name": "Test Citizen",
            "contact_number": "+1-555-019-2834",
            "location_name": "742 Evergreen Terrace",
            "latitude": "37.7749",
            "longitude": "-122.4194",
            "has_trapped_or_injured": "1",
            "is_hazard_spreading": "1",
        },
        follow_redirects=True,
    )
    assert report_res.status_code == 200
    assert b"submitted successfully" in report_res.data

    with app.app_context():
        inc = Incident.query.filter_by(title="Severe Flash Flood Inundating Streets").first()
        assert inc is not None
        assert inc.disaster_type == "Flood"
        assert inc.priority == "Critical"
        assert inc.status == "Reported"
        assert inc.priority_score >= 70

        # Check initial audit trail
        history = IncidentHistory.query.filter_by(incident_id=inc.id).first()
        assert history is not None
        assert history.action == "Reported"
        assert history.new_status == "Reported"


def test_incident_validation_rejects_missing_coords(client, init_test_users):
    """Test that reports without valid coordinates are rejected."""
    client.post(
        "/login",
        data={"identifier": "testcitizen", "password": "CitizenPass123!"},
        follow_redirects=True,
    )

    res = client.post(
        "/report",
        data={
            "title": "Invalid Incident No Coordinates",
            "disaster_type": "Fire",
            "description": "Fire burning near industrial zone with heavy smoke.",
            "reporter_name": "Test Citizen",
            "contact_number": "+1-555-019-2834",
            "location_name": "Industrial Zone",
            "latitude": "",
            "longitude": "invalid_number",
        },
        follow_redirects=True,
    )
    assert b"Valid numerical Latitude and Longitude coordinates are required" in res.data


def test_user_privacy_isolation(client, init_test_users, app):
    """Ensure citizens cannot view other citizens' private reports, while admins can view all."""
    # 1. Citizen 1 logs in and reports an incident
    client.post(
        "/login",
        data={"identifier": "testcitizen", "password": "CitizenPass123!"},
        follow_redirects=True,
    )
    client.post(
        "/report",
        data={
            "title": "Citizen 1 Private Incident",
            "disaster_type": "Medical Emergency",
            "description": "Medical incident requiring emergency paramedic support immediately.",
            "reporter_name": "Citizen One",
            "contact_number": "+1-555-010-1111",
            "location_name": "Private Address 1",
            "latitude": "37.7750",
            "longitude": "-122.4180",
        },
        follow_redirects=True,
    )

    with app.app_context():
        inc = Incident.query.filter_by(title="Citizen 1 Private Incident").first()
        inc_id = inc.id

    # Citizen 1 can view own report
    view_own = client.get(f"/incident/{inc_id}")
    assert view_own.status_code == 200
    assert b"Citizen 1 Private Incident" in view_own.data

    # 2. Citizen 2 logs in
    client.get("/logout")
    client.post(
        "/login",
        data={"identifier": "othercitizen", "password": "CitizenPass123!"},
        follow_redirects=True,
    )

    # Citizen 2 is blocked from viewing Citizen 1's report
    forbidden_view = client.get(f"/incident/{inc_id}", follow_redirects=True)
    assert b"not authorized to view the private records" in forbidden_view.data

    # 3. Administrator logs in and can view any incident
    client.get("/logout")
    client.post(
        "/login",
        data={"identifier": "testadmin", "password": "AdminPass123!"},
        follow_redirects=True,
    )
    admin_view = client.get(f"/incident/{inc_id}")
    assert admin_view.status_code == 200
    assert b"Citizen 1 Private Incident" in admin_view.data


def test_admin_manage_incident_status_and_priority(client, init_test_users, app):
    """Test administrative status progression, priority adjustment, and responder dispatch."""
    # Create test incident
    with app.app_context():
        user = User.query.filter_by(username="testcitizen").first()
        inc = Incident(
            title="Road Accident on Freeway",
            disaster_type="Road Accident",
            description="Vehicle collision blocking both lanes.",
            reporter_name="Citizen",
            contact_number="+1-555-019-2834",
            location_name="Freeway Mile 5",
            latitude=37.7800,
            longitude=-122.4200,
            priority="Medium",
            status="Reported",
            user_id=user.id,
        )
        db.session.add(inc)
        db.session.commit()
        inc_id = inc.id

    # Login as admin
    client.post(
        "/login",
        data={"identifier": "testadmin", "password": "AdminPass123!"},
        follow_redirects=True,
    )

    # 1. Update status to 'Response in Progress'
    status_res = client.post(
        f"/admin/incident/{inc_id}/manage",
        data={
            "action_type": "update_status",
            "new_status": "Response in Progress",
            "status_notes": "Unit dispatched and en route.",
        },
        follow_redirects=True,
    )
    assert status_res.status_code == 200
    assert b"status updated to" in status_res.data
    assert b"Response in Progress" in status_res.data

    # 2. Adjust priority to 'High'
    priority_res = client.post(
        f"/admin/incident/{inc_id}/manage",
        data={
            "action_type": "adjust_priority",
            "new_priority": "High",
            "priority_reason": "Drone camera shows fuel spill hazard on roadway.",
        },
        follow_redirects=True,
    )
    assert priority_res.status_code == 200
    assert b"priority reclassified to" in priority_res.data
    assert b"High" in priority_res.data

    # 3. Assign responder team
    assign_res = client.post(
        f"/admin/incident/{inc_id}/manage",
        data={
            "action_type": "assign_team",
            "team_name": "Station 4 Heavy Rescue",
            "instructions": "Approach from south exit.",
        },
        follow_redirects=True,
    )
    assert assign_res.status_code == 200
    assert b"dispatched to Incident" in assign_res.data

    # Verify database state and history audit trail
    with app.app_context():
        updated_inc = db.session.get(Incident, inc_id)
        assert updated_inc.status == "Response in Progress"
        assert updated_inc.priority == "High"
        assert updated_inc.assigned_team == "Station 4 Heavy Rescue"

        # Verify audit history logged every step
        history_actions = [h.action for h in updated_inc.history]
        assert "Status Changed" in history_actions
        assert "Priority Adjusted" in history_actions
        assert "Team Assigned" in history_actions


def test_map_api_geojson_feed(client, init_test_users, app):
    """Test GeoJSON map endpoints for Leaflet.js."""
    with app.app_context():
        inc = Incident(
            title="Map Feed Test Incident",
            disaster_type="Fire",
            description="Structural fire report for map test.",
            reporter_name="Citizen",
            contact_number="+1-555-019-2834",
            location_name="Downtown",
            latitude=37.7749,
            longitude=-122.4194,
            priority="Critical",
            status="Reported",
        )
        db.session.add(inc)
        db.session.commit()

    res = client.get("/api/incidents")
    assert res.status_code == 200
    data = res.get_json()
    assert data["type"] == "FeatureCollection"
    assert data["count"] >= 1
    feature = data["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert "title" in feature["properties"]
    assert "priority" in feature["properties"]
