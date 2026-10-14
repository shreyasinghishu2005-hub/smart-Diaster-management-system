"""Database seeding script for Smart Disaster Management & Emergency Response System.

ALL DATA SEEDED BY THIS SCRIPT IS ENTIRELY FICTIONAL ACADEMIC DEMONSTRATION DATA.
DO NOT USE THIS DATA FOR REAL-WORLD EMERGENCY DISPATCH.
"""

from datetime import datetime, timedelta, timezone
import json
from models import db, User, Incident, IncidentHistory, ResponseAssignment, EmergencyResource


def seed_database(app):
    """Seed sample users, emergency facilities, incidents, and audit trails."""
    with app.app_context():
        # Check if already seeded
        if User.query.filter_by(username="admin").first():
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding initial academic prototype database...")

        # -------------------------------------------------------------
        # 1. Seed Users (Admin + Demo Citizens)
        # -------------------------------------------------------------
        admin = User(
            username="admin",
            email="admin@disaster-response.local",
            full_name="Emergency Operations Director",
            phone="+1-555-911-0001",
            role="admin",
        )
        admin.set_password("AdminSecure2026!")
        db.session.add(admin)

        citizen1 = User(
            username="john_citizen",
            email="john@example.com",
            full_name="Johnathan Doe",
            phone="+1-555-019-2834",
            role="user",
        )
        citizen1.set_password("CitizenPass123!")
        db.session.add(citizen1)

        citizen2 = User(
            username="sarah_volunteer",
            email="sarah@example.com",
            full_name="Sarah Jenkins",
            phone="+1-555-018-9921",
            role="user",
        )
        citizen2.set_password("CitizenPass123!")
        db.session.add(citizen2)

        db.session.flush()

        # -------------------------------------------------------------
        # 2. Seed Emergency Resources (Hospitals, Fire, Police, Shelters)
        # Coordinates centered around a metropolitan demo region (approx 37.77, -122.42)
        # -------------------------------------------------------------
        resources = [
            EmergencyResource(
                name="Metro Central Trauma Hospital",
                resource_type="Hospital",
                address="1001 Emergency Blvd, Central District",
                phone="+1-555-010-1001",
                latitude=37.7749,
                longitude=-122.4194,
                capacity="180 Acute Care Beds, 24/7 ICU & Level 1 Trauma",
                is_active=True,
            ),
            EmergencyResource(
                name="St. Jude Community Health Care",
                resource_type="Hospital",
                address="450 South Valley Way",
                phone="+1-555-010-1002",
                latitude=37.7650,
                longitude=-122.4080,
                capacity="85 Beds, Burn Unit & Ambulatory Care",
                is_active=True,
            ),
            EmergencyResource(
                name="Highland District General Hospital",
                resource_type="Hospital",
                address="890 North Park Road",
                phone="+1-555-010-1003",
                latitude=37.7890,
                longitude=-122.4350,
                capacity="120 Beds, Specialized Cardiac & Stroke Unit",
                is_active=True,
            ),
            EmergencyResource(
                name="Station 4 Central Fire & Heavy Rescue",
                resource_type="Fire Station",
                address="220 Main Street Station",
                phone="+1-555-010-2001",
                latitude=37.7790,
                longitude=-122.4120,
                capacity="4 Engines, 2 Ladder Trucks, 1 HazMat Unit",
                is_active=True,
            ),
            EmergencyResource(
                name="Westside Fire Brigade HQ",
                resource_type="Fire Station",
                address="705 Sunset Boulevard",
                phone="+1-555-010-2002",
                latitude=37.7610,
                longitude=-122.4410,
                capacity="3 Engines, 1 Technical Rescue Squad",
                is_active=True,
            ),
            EmergencyResource(
                name="Bay Harbor Fire & Water Rescue",
                resource_type="Fire Station",
                address="12 Marina Pier Road",
                phone="+1-555-010-2003",
                latitude=37.7920,
                longitude=-122.3990,
                capacity="2 Fireboats, 2 Engines, Amphibious Rescue",
                is_active=True,
            ),
            EmergencyResource(
                name="Metropolitan Police Central Precinct",
                resource_type="Police Station",
                address="300 Civic Center Plaza",
                phone="+1-555-010-3001",
                latitude=37.7815,
                longitude=-122.4165,
                capacity="24/7 Dispatch, 18 Rapid Patrol Units",
                is_active=True,
            ),
            EmergencyResource(
                name="South Precinct Law Enforcement",
                resource_type="Police Station",
                address="580 Industrial Parkway",
                phone="+1-555-010-3002",
                latitude=37.7520,
                longitude=-122.4010,
                capacity="12 Patrol Vehicles, Tactical Emergency Unit",
                is_active=True,
            ),
            EmergencyResource(
                name="Civic Auditorium Emergency Relief Shelter",
                resource_type="Relief Shelter",
                address="99 Exhibition Way",
                phone="+1-555-010-4001",
                latitude=37.7770,
                longitude=-122.4220,
                capacity="500 Evacuee Cots, Food Kitchen, Medical Station",
                is_active=True,
            ),
            EmergencyResource(
                name="Red Cross Community Relief Hub",
                resource_type="Relief Shelter",
                address="315 Mission Valley Avenue",
                phone="+1-555-010-4002",
                latitude=37.7680,
                longitude=-122.4180,
                capacity="300 Evacuee Capacity, Clean Water, Emergency Rations",
                is_active=True,
            ),
        ]
        db.session.add_all(resources)
        db.session.flush()

        # -------------------------------------------------------------
        # 3. Seed Realistic Incidents across all categories & statuses
        # -------------------------------------------------------------
        now = datetime.now(timezone.utc)

        # Incident 1: Critical Flash Flood
        inc1 = Incident(
            title="Severe Flash Flood Inundating Low-Lying Residential Colony",
            disaster_type="Flood",
            description="Rapidly rising flood waters reached 4 feet after monsoon downpour. Elderly citizens and families trapped on rooftops. Electric power lines submerged. Immediate water rescue boats required.",
            reporter_name="Johnathan Doe",
            contact_number="+1-555-019-2834",
            location_name="Maple Creek Residential Lane, Lowlands",
            latitude=37.7715,
            longitude=-122.4150,
            incident_datetime=now - timedelta(hours=2),
            priority="Critical",
            priority_score=85,
            priority_reasons=json.dumps([
                "Baseline category 'Flood': +35 pts",
                "Critical triggers detected: 'trapped' (+40)",
                "High risk indicators detected: 'rising water' (+25)",
                "Reporter flagged trapped persons / casualties (+35 pts)",
                "Reporter flagged rapidly spreading emergency (+20 pts)",
                "Calculated Total Severity Score: 85/100 -> Assigned 'Critical'"
            ]),
            status="Response in Progress",
            assigned_team="Bay Harbor Water Rescue Squad 3",
            user_id=citizen1.id,
        )
        db.session.add(inc1)
        db.session.flush()

        db.session.add(IncidentHistory(
            incident_id=inc1.id,
            changed_by_id=citizen1.id,
            changed_by_name=citizen1.full_name,
            action="Reported",
            new_status="Reported",
            new_priority="Critical",
            notes="Incident reported via citizen mobile portal. Triage classified as Critical.",
            timestamp=now - timedelta(hours=2),
        ))
        db.session.add(IncidentHistory(
            incident_id=inc1.id,
            changed_by_id=admin.id,
            changed_by_name=admin.full_name,
            action="Status Changed",
            previous_status="Reported",
            new_status="Response in Progress",
            notes="Verified drone footage; escalated to active deployment.",
            timestamp=now - timedelta(hours=1, minutes=40),
        ))
        db.session.add(ResponseAssignment(
            incident_id=inc1.id,
            assigned_team="Bay Harbor Water Rescue Squad 3",
            assigned_by_id=admin.id,
            assigned_by_name=admin.full_name,
            status="On Scene",
            instructions="Deploy two inflatable zodiac boats with life vests. Prioritize elderly evacuation to Civic Auditorium Relief Shelter.",
            assigned_at=now - timedelta(hours=1, minutes=35),
        ))

        # Incident 2: Critical Fire
        inc2 = Incident(
            title="Commercial Warehouse Structural Fire with Heavy Chemical Smoke",
            disaster_type="Fire",
            description="Massive fire erupted in textile and packaging storage facility. Heavy black toxic smoke billowing into adjacent residential blocks. Building roof showing signs of partial collapse.",
            reporter_name="Sarah Jenkins",
            contact_number="+1-555-018-9921",
            location_name="404 Industrial Logistics Avenue",
            latitude=37.7635,
            longitude=-122.4045,
            incident_datetime=now - timedelta(hours=3, minutes=15),
            priority="Critical",
            priority_score=90,
            priority_reasons=json.dumps([
                "Baseline category 'Fire': +35 pts",
                "Critical triggers detected: 'massive fire' (+35), 'collapse' (+35)",
                "High risk indicators detected: 'dense smoke' (+20), 'chemical' (+20)",
                "Reporter flagged building / structural collapse (+25 pts)",
                "Calculated Total Severity Score: 90/100 -> Assigned 'Critical'"
            ]),
            status="Response in Progress",
            assigned_team="Station 4 Heavy HazMat & Fire Unit",
            user_id=citizen2.id,
        )
        db.session.add(inc2)
        db.session.flush()

        db.session.add(IncidentHistory(
            incident_id=inc2.id,
            changed_by_id=citizen2.id,
            changed_by_name=citizen2.full_name,
            action="Reported",
            new_status="Reported",
            new_priority="Critical",
            notes="Emergency fire alarm reported. Triage scored 90/100 Critical.",
            timestamp=now - timedelta(hours=3, minutes=15),
        ))
        db.session.add(ResponseAssignment(
            incident_id=inc2.id,
            assigned_team="Station 4 Heavy HazMat & Fire Unit",
            assigned_by_id=admin.id,
            assigned_by_name=admin.full_name,
            status="On Scene",
            instructions="Establish 300-meter safety perimeter. Wear SCBA breathing apparatus. Protect adjacent fuel tanks.",
            assigned_at=now - timedelta(hours=3),
        ))

        # Incident 3: High Priority Road Accident
        inc3 = Incident(
            title="Multi-Vehicle Express Highway Crash with Trapped Passengers",
            disaster_type="Road Accident",
            description="Interstate corridor collision involving a passenger coach and two cars. Multiple injured victims with bleeding and fractures. Jaws of life required to extricate front passenger.",
            reporter_name="Officer Davis",
            contact_number="+1-555-010-3001",
            location_name="Interstate 80 Eastbound, Mile Marker 14",
            latitude=37.7850,
            longitude=-122.4280,
            incident_datetime=now - timedelta(hours=1),
            priority="High",
            priority_score=68,
            priority_reasons=json.dumps([
                "Baseline category 'Road Accident': +25 pts",
                "Critical triggers detected: 'trapped' (+40)",
                "High risk indicators detected: 'injured' (+25), 'bleeding' (+20)",
                "Calculated Total Severity Score: 68/100 -> Assigned 'High'"
            ]),
            status="Under Review",
            assigned_team="Metro Trauma Paramedic Unit 1",
            user_id=citizen1.id,
        )
        db.session.add(inc3)
        db.session.flush()

        db.session.add(IncidentHistory(
            incident_id=inc3.id,
            changed_by_id=citizen1.id,
            changed_by_name=citizen1.full_name,
            action="Reported",
            new_status="Reported",
            new_priority="High",
            notes="Highway collision filed. Initial triage: High.",
            timestamp=now - timedelta(hours=1),
        ))

        # Incident 4: High Priority Earthquake
        inc4 = Incident(
            title="Structural Wall Cracks & Chimney Damage Following 4.8 Tremor",
            disaster_type="Earthquake",
            description="Deep diagonal fissures visible in three-story residential apartment block. Residents evacuated to open square. Gas pipeline odor reported in basement.",
            reporter_name="Sarah Jenkins",
            contact_number="+1-555-018-9921",
            location_name="Heritage Hill Apartments, West District",
            latitude=37.7680,
            longitude=-122.4380,
            incident_datetime=now - timedelta(hours=4),
            priority="High",
            priority_score=60,
            priority_reasons=json.dumps([
                "Baseline category 'Earthquake': +40 pts",
                "Critical triggers detected: 'gas leak' (+30)",
                "Medium risk indicators: 'structural crack' (+15)",
                "Calculated Total Severity Score: 60/100 -> Assigned 'High'"
            ]),
            status="Reported",
            user_id=citizen2.id,
        )
        db.session.add(inc4)
        db.session.flush()

        db.session.add(IncidentHistory(
            incident_id=inc4.id,
            changed_by_id=citizen2.id,
            changed_by_name=citizen2.full_name,
            action="Reported",
            new_status="Reported",
            new_priority="High",
            notes="Seismic structural report filed.",
            timestamp=now - timedelta(hours=4),
        ))

        # Incident 5: Medical Emergency (Resolved)
        inc5 = Incident(
            title="Acute Cardiac Arrest at Community Recreation Hall",
            disaster_type="Medical Emergency",
            description="Elderly male collapsed during morning badminton session. Unconscious with erratic pulse. CPR initiated by hall staff with automated external defibrillator (AED) on hand.",
            reporter_name="Johnathan Doe",
            contact_number="+1-555-019-2834",
            location_name="Community Center, Court 2",
            latitude=37.7730,
            longitude=-122.4230,
            incident_datetime=now - timedelta(hours=6),
            priority="Critical",
            priority_score=75,
            priority_reasons=json.dumps([
                "Baseline category 'Medical Emergency': +30 pts",
                "Critical triggers detected: 'heart attack' (+35), 'unconscious' (+35)",
                "Calculated Total Severity Score: 75/100 -> Assigned 'Critical'"
            ]),
            status="Resolved",
            assigned_team="Paramedic Rapid Response 2",
            resolution_notes="Paramedics arrived within 6 minutes. Patient stabilized via defibrillation and transferred to Metro Central Trauma Hospital ICU. Vital signs stable.",
            user_id=citizen1.id,
        )
        db.session.add(inc5)
        db.session.flush()

        db.session.add(IncidentHistory(
            incident_id=inc5.id,
            changed_by_id=admin.id,
            changed_by_name=admin.full_name,
            action="Resolution Recorded",
            previous_status="Response in Progress",
            new_status="Resolved",
            notes="Patient delivered safely to Metro Central Trauma ICU. Resolution notes recorded.",
            timestamp=now - timedelta(hours=4, minutes=30),
        ))

        # Incident 6: Medium Fallen Tree (Resolved)
        inc6 = Incident(
            title="Large Fallen Oak Tree Blocking Arterial Transit Road",
            disaster_type="Other",
            description="Severe wind gusts brought down a 40-foot oak tree across both lanes of traffic. Power lines snapped but no sparks or fire observed. Commuter traffic completely halted.",
            reporter_name="Citizen Reporter",
            contact_number="+1-555-014-4422",
            location_name="Boulevard at 14th Street",
            latitude=37.7880,
            longitude=-122.4110,
            incident_datetime=now - timedelta(hours=8),
            priority="Medium",
            priority_score=30,
            priority_reasons=json.dumps([
                "Baseline category 'Other': +15 pts",
                "Medium risk indicators: 'tree fallen' (+15), 'traffic halted' (+15)",
                "Mitigating factors: 'no injuries' (-25)",
                "Calculated Total Severity Score: 30/100 -> Assigned 'Medium'"
            ]),
            status="Closed",
            assigned_team="Municipal Public Works Crew 5",
            resolution_notes="Tree cleared with chainsaws and chippers. Municipal electrical utility re-strung the secondary cable. Traffic flow restored.",
            user_id=citizen2.id,
        )
        db.session.add(inc6)
        db.session.flush()

        db.session.add(IncidentHistory(
            incident_id=inc6.id,
            changed_by_id=admin.id,
            changed_by_name=admin.full_name,
            action="Status Changed",
            previous_status="Resolved",
            new_status="Closed",
            notes="Post-incident safety inspection completed. Case closed.",
            timestamp=now - timedelta(hours=5),
        ))

        # Incident 7: Low Priority Minor Leak
        inc7 = Incident(
            title="Monsoon Water Accumulation Near School Crosswalk",
            disaster_type="Flood",
            description="Clogged storm drain causing localized rainwater pool about 3 inches deep near school crosswalk. Traffic moving at reduced speed, no vehicle or property damage.",
            reporter_name="School Safety Officer",
            contact_number="+1-555-013-3399",
            location_name="Lincoln Elementary Crosswalk, Oak Street",
            latitude=37.7600,
            longitude=-122.4300,
            incident_datetime=now - timedelta(hours=10),
            priority="Low",
            priority_score=15,
            priority_reasons=json.dumps([
                "Baseline category 'Flood': +35 pts",
                "Medium risk indicators: 'water logging' (+15)",
                "Mitigating factors: 'minor' (-15), 'safe' (-15)",
                "Calculated Total Severity Score: 15/100 -> Assigned 'Low'"
            ]),
            status="Closed",
            assigned_team="Drainage Maintenance Team A",
            resolution_notes="Drain grate unblocked of autumn leaves. Standing water receded in 20 minutes.",
            user_id=citizen1.id,
        )
        db.session.add(inc7)

        db.session.commit()
        print("Initial database seed completed successfully!")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    seed_database(app)
