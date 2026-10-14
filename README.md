# Smart Disaster Management & Emergency Response System

> **ACADEMIC PROTOTYPE NOTICE:**  
> This software is a college engineering prototype developed for educational simulation, disaster response coordination evaluation, and academic demonstration. **It is NOT connected to real-world 112 / 911 emergency dispatch services.** In a real life-threatening emergency, immediately contact your local official emergency authorities directly.

---

## 1. Project Overview

The **Smart Disaster Management & Emergency Response System** is a centralized web platform designed to streamline emergency reporting, coordinate rapid disaster triage, visualize incident locations and nearby response resources on an interactive map, and empower disaster management administrators to track incidents throughout their entire lifecycle from initial report to verified resolution.

### Supported Emergency Categories:
- 🌊 **Floods** (Flash floods, water logging, dam breach)
- 🔥 **Fires** (Structural, commercial, chemical smoke, wildfire)
- 🌋 **Earthquakes** (Tremors, structural cracks, building collapse)
- 🚗 **Road Accidents** (Highway pileups, multi-vehicle collisions)
- 🏥 **Medical Emergencies** (Cardiac arrest, acute trauma, mass injuries)
- ⚠️ **Other Hazards** (Toxic gas leaks, fallen trees, live power lines)

---

## 2. Technology Stack

- **Backend:** Python 3.10+ & Flask 3.x
- **Database:** SQLite with Flask-SQLAlchemy ORM (Normalized 5-table relational schema)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Mapping & GIS:** Leaflet.js with OpenStreetMap and CartoDB (Light & Dark tiles) + Overpass API
- **Forms & Security:** Flask-WTF CSRF protection, Werkzeug secure password hashing, secure file uploads
- **Machine Learning (Future Enhancement Module):** Scikit-learn TF-IDF + Naive Bayes pipeline demonstration
- **Testing:** Pytest automated test suite (15 unit & integration tests)

---

## 3. Key System Features

### A. Citizen User Dashboard
- Clean, responsive portal overview showing submitted reports, active responses, and resolutions.
- Incident report tracking with color-coded priority and status badges.
- Dedicated view of report details, ground-zero GPS coordinates, and assigned responders.
- Quick access to official emergency telephone helplines (112, 101, 102/108, 100).

### B. Emergency Incident Reporting Form
- Incident title, disaster category, detailed description, and incident timestamp.
- Reporter details (Full Name, emergency callback number).
- Location selector: Interactive Leaflet map pin placement + manual decimal coordinate editing.
- One-click **"Use My GPS Location"** with explicit HTML5 browser permission handling.
- Critical Triage Flags: Trapped persons, rapidly spreading hazard, structural collapse.
- Scene photo upload validation (PNG, JPG, JPEG, WEBP up to 5 MB).

### C. Transparent Rule-Based Priority Triage
- Python rule engine in `services/priority_service.py` evaluating:
  - Base disaster weights (Earthquake: 40, Fire: 35, Flood: 35, Medical: 30, Road: 25, Other: 15)
  - Critical keyword triggers (+30 to +45 pts: *trapped*, *casualty*, *collapse*, *explosion*, *unconscious*)
  - High risk keywords (+20 to +25 pts: *injured*, *burns*, *bleeding*, *rising water*, *dense smoke*)
  - Mitigating keywords (-15 to -30 pts: *minor*, *safe*, *controlled*, *drill*, *no injuries*)
  - Explicit reporter situation checkboxes (+20 to +35 pts)
- Assigned Severity Categories:
  - **Critical** (Score ≥ 70) — Solid Red `#DC2626`
  - **High** (Score ≥ 45) — Accessible Orange `#EA580C`
  - **Medium** (Score ≥ 20) — Accessible Amber `#D97706`
  - **Low** (Score < 20) — Accessible Green `#16A34A`
- Transparent breakdown of points and triggers visible on each incident page.
- **Future Enhancement Module:** Side-by-side comparison with a Scikit-learn demonstration classifier.

### D. Interactive Emergency Map (Leaflet.js + OpenStreetMap)
- Color-coded pins for reported incidents with popups displaying titles, priorities, and statuses.
- Multi-parameter filter toolbar: filter by Disaster Category, Priority Level, and Active/Resolved status.
- Proximity discovery of nearby emergency infrastructure (Hospitals, Fire Stations, Police Stations, Shelters) using the Haversine distance formula with graceful OpenStreetMap Overpass API fallback.
- Dynamic tile switching: Automatically adapts between Light mode tiles and Dark mode tiles without page reload.

### E. Administrator Command Dashboard
- Executive KPI counter cards: Total Reports, Critical Urgency, High Urgency, Pending Review, In Progress, Resolved/Closed.
- Category and Priority distribution analytics with progress visualizers.
- Searchable incident registry with multi-column filtering.
- **Incident Command Center (`/admin/incident/<id>/manage`):**
  1. Update response status (Reported &rarr; Under Review &rarr; Response in Progress &rarr; Resolved &rarr; Closed).
  2. Override priority with mandatory justification audit notes.
  3. Dispatch emergency responder units (e.g. *Station 4 Heavy HazMat Unit*) with tactical instructions.
  4. Record comprehensive incident resolution notes.
  5. Chronological audit timeline logging every administrator action.

### F. UI/UX Design (Default Pure White `#FFFFFF` + Comprehensive Dark Theme)
- Default light mode with pure white `#FFFFFF` background, dark charcoal text, and subtle shadows.
- Complete dark mode palette: `#121212` background, `#1E1E1E` cards, `#252525` secondary surfaces, `#F5F5F5` text, and `#60A5FA` accents.
- Navbar theme toggle button (Sun ☀️ / Moon 🌙) with instant client-side switching and `localStorage` persistence.
- Inline theme script in `<head>` preventing unstyled theme flashing (FOUC).

---

## 4. Project Directory Structure

```text
smart-disaster-management/
├── app.py                      # Flask application factory, routes registration & CLI commands
├── config.py                   # Central application, database, upload & security configuration
├── requirements.txt            # Python dependencies specification
├── seed_data.py                # Academic demonstration database seeder
├── pytest.ini                  # Automated test runner configuration
├── .env.example                # Example environment variables template
├── .gitignore                  # Git ignore rules for virtualenv, DB & cache
├── README.md                   # Complete documentation & college viva guide
├── instance/
│   └── disaster_management.db  # SQLite persistent relational database
├── models/
│   ├── __init__.py             # SQLAlchemy instance and model exports
│   ├── user.py                 # User account model, password hashing & RBAC
│   ├── incident.py             # Incident, IncidentHistory & ResponseAssignment models
│   └── emergency_resource.py   # Emergency facilities model (Hospitals, Fire, Police)
├── routes/
│   ├── __init__.py             # Blueprint initialization
│   ├── auth.py                 # Registration, login, logout, and RBAC decorators
│   ├── user.py                 # Landing page, citizen dashboard, and my-reports
│   ├── incidents.py            # Reporting form, priority evaluation, and details
│   ├── admin.py                # Operations dashboard, incident directory & management
│   └── maps.py                 # Fullscreen map, GeoJSON APIs & ML demo endpoint
├── services/
│   ├── priority_service.py     # Rule-based priority engine & Scikit-learn ML module
│   └── resource_service.py     # Haversine distance calculations & OSM Overpass lookup
├── templates/
│   ├── base.html               # Master layout with theme toggle, navbar & disclaimer
│   ├── index.html              # Modern landing page & public hotline directory
│   ├── login.html              # Authentication form with college demo credentials
│   ├── register.html           # Citizen registration form
│   ├── dashboard.html          # Citizen user dashboard
│   ├── report_incident.html    # Emergency reporting form with Leaflet location picker
│   ├── incident_details.html   # Report detail view, triage breakdown & nearby facilities
│   ├── my_reports.html         # Citizen submitted reports history table
│   ├── admin_dashboard.html    # Executive administrator command console
│   ├── manage_incidents.html   # Searchable incident management table
│   ├── admin_incident_detail.html # Status transitions, priority overrides & team dispatch
│   ├── map.html                # Fullscreen interactive emergency map
│   └── errors/
│       ├── 403.html            # Access denied template
│       ├── 404.html            # Page not found template
│       ├── 413.html            # File size limit exceeded template
│       └── 500.html            # Server error template
├── static/
│   ├── css/
│   │   └── style.css           # Centralized CSS variables, light/dark themes & components
│   ├── js/
│   │   ├── main.js             # Theme switcher, validation & UI handlers
│   │   └── map.js              # Leaflet maps, tile layers & geocoding
│   └── uploads/                # Scene photograph uploads directory
└── tests/
    ├── conftest.py             # Pytest fixtures and in-memory test DB
    ├── test_auth.py            # Registration, login, hashing & RBAC tests
    ├── test_incidents.py       # Reporting, validation, isolation & admin dispatch tests
    └── test_priority.py        # Priority engine keywords, scoring & ML tests
```

---

## 5. Installation & Setup Guide

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed
- Git (optional)

### Step 1: Clone or Navigate to the Directory
```bash
cd "d:\diaster management"
```

### Step 2: Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an ExecutionPolicy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional)
The application includes robust defaults for local development. To customize settings, copy `.env.example`:
```bash
copy .env.example .env     # Windows
cp .env.example .env       # Linux / macOS
```

### Step 5: Initialize Database & Seed Demonstration Data
The application automatically creates and seeds the database on first run. If you wish to re-seed manually:
```bash
flask init-db
flask seed-demo-data
```

To create a new custom administrator account via CLI:
```bash
flask create-admin
```

### Step 6: Start the Development Server
```bash
python app.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## 6. Pre-Seeded Demonstration Accounts

All data seeded into the database is **purely fictional academic demonstration data**.

| Role | Username | Email | Password | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin@disaster-response.local` | `AdminSecure2026!` | Access all reports, dispatch units, override priority, audit logs |
| **Citizen User 1** | `john_citizen` | `john@example.com` | `CitizenPass123!` | File reports, track personal incidents, view map |
| **Citizen User 2** | `sarah_volunteer`| `sarah@example.com` | `CitizenPass123!` | File reports, track personal incidents, view map |

---

## 7. Running Automated Tests

A comprehensive test suite of 15 tests covers authentication, security isolation, priority classification, and administrator workflows:

```bash
pytest -v
```

Expected output:
```text
tests/test_auth.py::test_user_registration_success PASSED
tests/test_auth.py::test_registration_validation_errors PASSED
tests/test_auth.py::test_login_and_logout PASSED
tests/test_auth.py::test_login_invalid_credentials PASSED
tests/test_auth.py::test_role_based_access_control PASSED
tests/test_incidents.py::test_submit_incident_report PASSED
tests/test_incidents.py::test_incident_validation_rejects_missing_coords PASSED
tests/test_incidents.py::test_user_privacy_isolation PASSED
tests/test_incidents.py::test_admin_manage_incident_status_and_priority PASSED
tests/test_incidents.py::test_map_api_geojson_feed PASSED
tests/test_priority.py::test_critical_priority_with_trapped_and_casualty_keywords PASSED
tests/test_priority.py::test_high_priority_for_road_accident_with_injuries PASSED
tests/test_priority.py::test_low_priority_for_controlled_minor_incident PASSED
tests/test_priority.py::test_score_clamping PASSED
tests/test_priority.py::test_scikit_learn_ml_classifier_prediction PASSED
============================= 15 passed =============================
```

---

## 8. Running and Debugging in VS Code

1. Open the project folder in VS Code:
   ```bash
   code .
   ```
2. Select the Python interpreter:
   - Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS).
   - Type `Python: Select Interpreter`.
   - Choose `./venv/Scripts/python.exe`.
3. Create `.vscode/launch.json` (optional for F5 debugging):
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Flask Server",
               "type": "debugpy",
               "request": "launch",
               "module": "flask",
               "env": {
                   "FLASK_APP": "app.py",
                   "FLASK_ENV": "development",
                   "FLASK_DEBUG": "1"
               },
               "args": [
                   "run",
                   "--no-debugger",
                   "--no-reload"
               ],
               "jinja": true
           }
       ]
   }
   ```
4. Press `F5` to start debugging with breakpoints.

---

## 9. College Project Evaluation & Viva Demonstration Guide

When presenting this project to internal and external examiners, follow this structured demonstration sequence:

### Demonstration Walkthrough Script

1. **Homepage & Mission Statement (`/`):**
   - Show the pure white modern design with emergency helpline directory (112, 101, 108, 100).
   - Point out the prominent academic disclaimer banner.
   - Click the **Dark Mode** toggle in the navbar to demonstrate instantaneous theme adaptation and CSS variable switching.

2. **Citizen Registration & Login (`/register`, `/login`):**
   - Demonstrate citizen login with `john_citizen` / `CitizenPass123!`.
   - Highlight that citizens access their personal dashboard (`/dashboard`) showing their submitted incident counts.

3. **Submitting a New Emergency Report (`/report`):**
   - Click **"Report Emergency"**.
   - Show the interactive Leaflet map: click anywhere to drop a pin. Show how coordinates update dynamically in the input fields.
   - Enter title: *"Severe Chemical Spill with Trapped Workers"*.
   - Check the **"Casualties / Trapped Persons"** checkbox.
   - Submit the form and show that the rule engine immediately classifies the report as **Critical Priority** (Score: 85+/100) with detailed evaluation factors!

4. **Incident Details & Resource Proximity (`/incident/<id>`):**
   - Show the Ground Zero map.
   - Point out the **Nearby Emergency Responders** list showing real-time Haversine proximity to hospitals, fire stations, and police stations (e.g., *"1.2 km away"*).
   - Show the **Scikit-Learn Machine Learning Demonstration Card** comparing the rule-based decision with the TF-IDF NLP prediction.

5. **Security & Privacy Access Control:**
   - Log out and log in as `sarah_volunteer`.
   - Attempt to navigate to John's private incident URL (`/incident/1`). Show that access is blocked with a security warning!

6. **Administrator Operations Command (`/admin/dashboard`):**
   - Log in with `admin` / `AdminSecure2026!`.
   - Show the KPI metric counters (Total, Critical, Pending, In Progress, Resolved).
   - Show the disaster category distribution bar charts.
   - Navigate to **Manage All Incidents** (`/admin/incidents`) and demonstrate searching by keyword and filtering by priority.

7. **Incident Command & Dispatching (`/admin/incident/<id>/manage`):**
   - Change response status from `Reported` &rarr; `Response in Progress`.
   - Dispatch a response unit: *"Station 4 Heavy HazMat Unit"* with instructions.
   - Record resolution notes and mark as `Resolved`.
   - Show the bottom **Chronological Operational Audit Trail** documenting every administrator action with exact timestamps.

8. **Fullscreen Emergency Map (`/map`):**
   - Demonstrate filtering pins by disaster category and priority.
   - Toggle the emergency facility overlay layer on and off.
   - Switch between Light and Dark themes to showcase tile layer swapping.

---

## 10. Frequently Asked Questions (Viva / Oral Exam Preparation)

**Q1: Why did you choose a rule engine instead of purely relying on machine learning for emergency triage?**  
*Answer:* In life-critical emergency systems, explainability, predictability, and auditability are paramount. A rule-based engine offers deterministic, auditable decisions with transparent explanations. Machine learning models can suffer from hallucinations, data drift, or false confidence. However, to demonstrate future potential, we included a Scikit-learn NLP prototype module for comparative evaluation.

**Q2: How does the nearby emergency resource discovery work?**  
*Answer:* The application implements the great-circle Haversine distance formula to calculate distances between the reported incident coordinates and registered facilities in SQLite. When an internet connection is available, it gracefully queries OpenStreetMap's Overpass API; if offline or rate-limited, it falls back seamlessly to the verified local facilities without failing.

**Q3: How is Role-Based Access Control (RBAC) enforced?**  
*Answer:* Roles (`user` vs `admin`) are stored in the `users` table and recorded in encrypted server-side Flask sessions upon authentication. Custom Python decorators (`@login_required`, `@admin_required`) protect routes. Furthermore, object-level ownership checks ensure citizens can only view their own incident records, while administrators have system-wide oversight.

**Q4: How does the Light/Dark theme switching function without page reloads?**  
*Answer:* The application uses CSS Custom Properties (variables) defined under `:root` and `[data-theme="dark"]`. A JavaScript listener toggles the `data-theme` attribute on the root HTML element, stores the preference in `localStorage`, and emits a custom DOM event so Leaflet updates its tile layers dynamically. An inline script in `<head>` applies the saved preference before the DOM renders to prevent flashing.

---

## 11. Screenshot Capture Checklist for Project Documentation

| # | Screen Name | URL Route | Key Elements to Capture |
| :--- | :--- | :--- | :--- |
| 1 | **Landing Page (Light Mode)** | `/` | Hero section, helpline directory, metric cards, pure white styling |
| 2 | **Landing Page (Dark Mode)** | `/` | Dark `#121212` background, accessible contrast text |
| 3 | **Citizen Dashboard** | `/dashboard` | Submission counters, recent report list, action buttons |
| 4 | **Reporting Form with Map Pin** | `/report` | Leaflet pin drop, coordinate inputs, triage checkboxes |
| 5 | **Incident Details & Triage** | `/incident/1` | Priority meter, rule breakdown, ML prediction, nearby facilities |
| 6 | **Admin Command Console** | `/admin/dashboard` | KPI summary cards, category progress bars, incident feed |
| 7 | **Admin Management Center** | `/admin/incident/1/manage` | Status change form, team dispatch form, resolution notes, audit timeline |
| 8 | **Fullscreen Live Map** | `/map` | Colored priority markers, facility overlays, category filters |
| 9 | **Automated Test Run** | Terminal | `pytest -v` showing all 15 tests passing |
