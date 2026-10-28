# CampusPark AI - Smart Parking Management System

A complete, responsive web application for college campuses managing vehicle entry & exit, automated slot availability, AI vehicle detection, OpenCV license plate recognition (ANPR), congestion control, CCTV monitoring, lost vehicle/key assistance, priority parking, overcrowding alarms, and downloadable reports.

---

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide Icons
- **Backend**: Python 3.12, FastAPI, SQLAlchemy ORM, Uvicorn
- **Database**: PostgreSQL (with automatic zero-config local SQLite fallback for standalone development)
- **Visual Analytics**: Recharts (Area charts, Bar charts, Donut distribution)
- **Real-time Live Telemetry**: Full-duplex WebSockets with automatic reconnection
- **AI Integration**: OpenCV image processing, contour filtering, aspect ratio classifier, ANPR engine
- **Reporting Engine**: CSV (streaming), Excel (OpenPyXL styled workbooks), and PDF (ReportLab tabular exports)

---

## Main Application Pages

1. **Overview Dashboard (`/dashboard`)**:
   - Total capacity, real-time occupied vs available bays, occupancy percentage.
   - Today's gate circulation volume (entries vs exits) and camera health status.
   - Hourly Inflow & Outflow Timeline (Recharts AreaChart) and Zone Occupancy distribution.
   - Live Barrier & Gate Activity Log with simulated detection badges.
   - Quick report export & quick vehicle entry triggers.

2. **Live Parking Map & Zones (`/map`)**:
   - Geospatial campus parking grid with real-time slot telemetry.
   - 5 Campus Zones: *North Gate Primary Lot*, *South Engineering Complex*, *Admin & Faculty VIP Plaza*, *EV Green Mobility Hub*, *Central Auditorium & Sports Pavilion*.
   - Filter by bay type (Standard, EV, VIP, Handicap, Two-Wheeler) and availability.
   - Clickable bays displaying sensor telemetry and manual occupancy toggling.

3. **Vehicle Entry and Exit Records (`/sessions`)**:
   - Complete historical and active parking sessions.
   - Duplicate open session detection (blocks duplicate active entry attempts).
   - Manual license plate correction modal with mandatory audit reason logging.
   - Search, status filtering, and pagination.

4. **Parking Slot Management (`/slots`)**:
   - Complete bay inventory across all floors and zones.
   - Create new bays, edit properties, and bind physical IoT ultrasonic sensors.
   - Quick toggle between occupied and free states.

5. **AI Detection & ANPR Events (`/ai-detections`)**:
   - **Pluggable Architecture**: Clean service interface (`BaseANPRProvider`) supporting `OpenCVANPREngine` for real CV analysis and `MockANPRProvider` for local testing without physical cameras.
   - **Vehicle Category Detection**: Classifies CAR, MOTORCYCLE, BUS, SUV, TRUCK, and EV from frames.
   - **Number Plate Localization & Cropping**: Isolates rectangular plate contours, normalizes dimensions, and crops high-resolution plate snapshots.
   - **OCR Character Recognition & Scoring**: Character segmentation, font template matching, and confidence score estimation.
   - **Configurable Confidence Threshold**: Stored in `SystemSetting` (default 85%). Low-confidence plates are held as `PENDING_VERIFICATION`.
   - **Duplicate Session Prevention**: Blocks duplicate open parking sessions on ENTRY if the vehicle is already inside the campus.
   - **Exit Clearance Safety Lock**: Unverified OCR detections below threshold never automatically open exit barriers; operator manual review is required.
   - **Audit Trail & Raw OCR Preservation**: Original OCR and detected plates are permanently preserved in `AuditLog` whenever corrections are applied.
   - **Registered User Matching**: Automatically correlates plates with student, faculty, and administrative vehicle registrations.

6. **Traffic & Congestion Analytics (`/congestion`)**:
   - Real-time gate queue lengths and event-derived average gate waiting times.
   - Zone occupancy calculation against configurable Warning (75%) and Critical (90%) thresholds.
   - Automated overcrowding condition detection & alert generation.
   - Near-term predictive parking demand forecasting (+1h, +2h, +3h, +4h arrival/departure models).
   - AI traffic mitigation and automated lane dispatch advisory.

7. **Smart Exit Management (`/smart-exit`)**:
   - **AI End-of-Day Smart Exit Sequencing Engine**:
     - Integrates college timetable dismissal times (16:30 Engineering, 17:00 Sciences, 17:15 Events, 18:00 Faculty).
     - Generates safe zone-based vehicle exit sequence using queue lengths, pedestrian crossings, route capacity, and blocked lanes.
     - **Safety Guarantee**: Never releases vehicles into an unsafe/blocked route; throttles zones adjacent to active pedestrian crossings.
     - **Neutral Vehicle Policy**: No biased assumption that bikes must always exit before cars; evaluates safety objectively.
     - **Staff Control Interlock**: System proposes phased sequence recommendations; authorized security staff retain ultimate operational control and approval (`PENDING_APPROVAL` -> `APPROVED`).
     - **Dynamic Resequencing**: Real-time recalculation whenever route conditions, lane blocks, or queues change.
     - **Audit Trail & Manual Overrides**: Mandatory justification required for manual overrides, logged permanently to `AuditLog`.
     - **Post-Clearing Overstay Tracking**: Monitors vehicles remaining inside campus past the scheduled clearing window for security sweeps.
     - **Comprehensive End-of-Day Report**: Planned vs actual clearing time, delays, peak gate queues, and sequence audit trail.
   - Outbound vehicle clearance, Fastag RFID settlement, and boom barrier arm actuators (`OPEN`, `CLOSE`, `EMERGENCY_HOLD`).

8. **CCTV Camera Monitoring (`/cctv`)**:
   - **Camera Telemetry & Quotas**: Real-time camera code, name, gate name (North Gate A/B, South Gate, Admin Portico, EV Quad, Sports Complex Gate), physical location, and IP address.
   - **Stream & Pipeline Health**: Heartbeat watchdog monitoring, stream connection status (`CONNECTED`, `UNAVAILABLE`, `DEGRADED`, `FAILED`), and AI vision pipeline status (`ACTIVE`, `IDLE`, `PROCESSING_FAILURE`, `PAUSED`).
   - **NVR Storage Quotas & Retention Policy**: Storage usage gauges (GB used, total GB, percentage), configured retention policy (30/60 days), and automated capacity threshold tracking.
   - **Automated Watchdog Alarms**: Real-time alert dispatch for:
     1. Camera failure (hardware heartbeat loss / OFFLINE)
     2. Unavailable video stream (HLS / RTSP signal loss)
     3. AI vision processing failure
     4. Storage nearing capacity (warning at 85%+, critical at 95%+)
   - **Role-Based Security & Privacy Interlock**: Raw video streams and NVR feeds are strictly restricted to authorized security command and administrators (`HTTP 403 Forbidden` for regular users).
   - **Zero Credentials Frontend Exposure**: Camera passwords and NVR master secrets remain strictly server-side; time-limited signed proxy tokens are issued for authorized playback.
   - **Audit Trail on Stream View**: Every camera feed viewed is permanently logged to `AuditLog` (`CAMERA_STREAM_VIEWED`).
   - **Digital Watermarked Footage Export**: Authorized operators can export clips with mandatory documented justification, generating an immutable SHA-256 digital watermark and recording `CCTV_FOOTAGE_EXPORTED` in the audit log.
   - **Recent Incident & ANPR Linkage**: Inspects recent vehicle detections, plate thumbnails, and linked hardware issue tickets directly from the camera modal.

9. **Lost Vehicle & Key Assistance (`/assistance`)**:
   - **Dedicated Assistance Portal**: Specialized submission form for *Lost Key*, *Forgotten Parking Location*, *Vehicle Not Found*, and *Other Incident*.
   - **Authentication & Sensitive Lookup Security**: Requires authenticated users; strictly protects sensitive location searches (regular users can only view their own vehicle's last recorded zone; unauthorized cross-user lookups are blocked with HTTP 403).
   - **CCTV & Physical Key Disclaimer**: Explicit system notice that CCTV cameras cannot identify or track physical keys; lost-and-found repository physical verification is required.
   - **Interactive Zone Lookup Tool**: Searches active parking sessions to pinpoint last verified zone, slot bay, and entry gate with security confirmation.
   - **Attachment Support**: Upload images of lost items, key tags, permits, or vehicle registration papers.
   - **Incident Ticket Lifecycle**: Generates unique ticket numbers (`TCK-YYYYMMDD-XXXX`), tracks status (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CANCELLED`), priority levels, assigned security officer, and resolution notes.
   - **Security Staff Owner Outreach**: Security officers can log verified owner contacts (Phone, Email, In-Person) directly into the ticket with immutable `AuditLog` records.

10. **Priority Parking Management (`/priority`)**:
    - **Campus Policy Categories**: 5 configured campus priority categories per university regulations:
      1. `ACCESSIBLE` (Handicap permit bays, mobility assistance, 12h max, permit required).
      2. `EMERGENCY` (Campus ambulances, fire response, quick-response patrol units, 24h max, emergency route access).
      3. `FACULTY` (University leadership, professors, deans, 10h max).
      4. `VISITOR` (Official campus guests, visiting dignitaries, guest house, 8h max).
      5. `GENERAL` (Student and staff priority reservation during exam periods, 6h max).
    - **Safety Interlock**: Non-emergency users and normal reservations are strictly prevented from reserving emergency slots or emergency evacuation routes (rejected with HTTP 400).
    - **Dynamic Expiry Evaluation**: Automatic evaluation of reservations past their end timestamp, transitioning status to `EXPIRED` and releasing allocated bays.
    - **Restricted Bay Violation Checker**: Operator tool to verify if a vehicle parked in a restricted bay (Handicap, VIP, Faculty, Emergency) is authorized; immediately dispatches a `CRITICAL` Overcrowding/Security Alert and audit entry if an unauthorized vehicle is detected.
    - **Security Manual Overrides**: Authorized security staff can reassign bays or update reservation parameters with mandatory audit reason logging.
    - **Compliance & Utilization Reports**: Comprehensive dashboard and modal showing bay utilization percentage, category distribution, and status breakdown.

11. **Overcrowding Alerts (`/alerts`)**:
    - Configurable occupancy thresholds (Warning: 75%, Critical: 90%).
    - Active alarm notifications with operator acknowledgement.
    - Emergency broadcast tool that pushes messages to digital campus VMS LED displays.

12. **Device Health & Hardware Issues (`/devices`)**:
    - **IoT Hardware Network**: Monitors Ultrasonic sensors, Fastag RFID readers, boom barrier relays, and VMS space displays with live ping diagnostics.
    - **User-Reported Device Issue Form**: Allows students, faculty, and staff to file tickets (`DEV-YYYYMMDD-XXXX`) for stuck barriers, offline cameras, vision anomalies, or damaged sensors.
    - **Ticket Lifecycle & Dispatch Workflow**: Security command can acknowledge tickets, assign technicians/officers (`IN_PROGRESS`), and resolve issues with mandatory documented root-cause notes.
    - **Chronological Incident History**: Full timeline tracking showing every state transition, actor, role, and dispatch notes.

13. **Analytics & Downloadable Reports (`/reports`)**:
    - Weekly vehicle turnover bar charts and commuter fleet mix donut charts.
    - Export on demand in **CSV**, **Excel (.xlsx)**, and **PDF** formats with date range filters.

14. **User & Role Management (`/users`)**:
    - Role-based access control (Admin, Security, Faculty, Student).
    - Manage credentials, registered vehicle plates, campus departments, and activation.

15. **Settings & Audit Logs (`/settings`)**:
    - Configurable congestion thresholds, simulation toggles, and hourly parking fees.
    - Security Action Audit Trail tracking plate corrections, barrier commands, and logins.

---

## Default User Accounts (Seed Data)

The system automatically initializes seed data on startup:

| Role | Email | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@campus.edu` | `Admin@123` | Full access: settings, users, audit, slots, barrier |
| **Security Staff** | `security@campus.edu` | `Security@123` | Gate operations, CCTV, Smart Exit, assistance tickets |
| **Faculty Member**| `prof.sharma@campus.edu` | `Faculty@123` | Priority bay reservations, session history |
| **Student** | `alex.student@campus.edu` | `Student@123` | Assistance reporting, space availability view |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- (Optional) Docker or PostgreSQL 15+

### Option A: Quick Standalone Launch (Unified App)

The backend directly serves the pre-built frontend distribution and provides an SQLite database out-of-the-box:

```bash
# 1. Activate Python virtual environment
.\venv\Scripts\activate   # On Windows
source venv/bin/activate  # On Linux/macOS

# 2. Run the unified application
python run.py
```
Open **`http://127.0.0.1:8000`** in your browser.
API Swagger Documentation is available at **`http://127.0.0.1:8000/docs`**.

---

### Option B: Development Mode (Vite + FastAPI Hot Reload)

To develop with frontend hot-module reloading:

**Terminal 1 (Backend API):**
```bash
.\venv\Scripts\uvicorn backend.app.main:app --reload --port 8000
```

**Terminal 2 (Frontend Dev Server):**
```bash
cd frontend
npm run dev
```
Open **`http://localhost:5173`**. Requests to `/api` and `/ws` are automatically proxied to the backend.

---

### Option C: Using PostgreSQL with Docker

To use a full production PostgreSQL database:

```bash
# 1. Launch PostgreSQL container
docker compose up -d

# 2. Update .env:
# DATABASE_URL=postgresql+psycopg2://postgres:postgrespassword@localhost:5432/campus_parking

# 3. Start backend
python run.py
```

---

## Running Automated Tests

Run AI Traffic & Smart Exit Sequencing tests:
```bash
$env:PYTHONPATH="."
.\venv\Scripts\python backend/tests/test_traffic_smart_exit.py
.\venv\Scripts\python backend/tests/run_traffic_exit_api_tests.py
```
This runs 24 automated unit and live API tests verifying:
- Gate queue tracking and average waiting time calculations
- Configurable zone occupancy and congestion levels
- Overcrowding detection & automated alert generation
- Near-term predictive demand forecasting (+1h, +2h, +3h, +4h)
- College timetable integration & authorized staff plan initiation
- Safe zone-based vehicle exit sequencing with capacity constraints
- Strict safety verification: blocked routes are never released into
- Neutral vehicle type policy (no arbitrary bike-first assumption)
- Dynamic recalculation when route conditions or queues change
- Authorized staff approval and activation workflow
- Manual security overrides with mandatory audit justification
- Real-time tracking of overstay vehicles past planned clearing time
- Comprehensive End-of-Day Traffic & Clearing Audit Report generation

Run ANPR verification tests:
```bash
.\venv\Scripts\python backend/tests/run_anpr_tests.py
.\venv\Scripts\python backend/tests/run_anpr_api_tests.py
```
This runs 17 automated tests verifying:
- Vehicle category classification (Cars, Motorcycles, Buses, SUVs, EVs, Trucks)
- Number plate localization, contour isolation, and plate image cropping
- Character OCR segmentation and confidence scoring
- Configurable confidence threshold updates and audit logging
- Registered student/faculty vehicle matching
- Duplicate open parking session prevention on ENTRY
- Unverified OCR results blocking automated EXIT barrier release
- Manual security verification and correction preserving original raw OCR
- Real frame processing vs explicitly labeled simulation harness (`is_simulated = True`)

Run Assistance & Priority Parking tests:
```bash
$env:PYTHONPATH="."
.\venv\Scripts\python backend/tests/test_assistance_priority.py
.\venv\Scripts\python backend/tests/run_assistance_priority_api_tests.py
```
This runs 18 automated unit and live API tests verifying:
- Authorized vehicle location lookup and last verified zone detection
- Strict privacy enforcement: blocking unauthorized users from searching others' plates (403 Forbidden)
- Sensitive lookup audit trail logging
- Assistance ticket lifecycle for Lost Key, Forgotten Location, Vehicle Not Found with attachments
- Security staff ticket status updates, resolution notes, and verified owner outreach logging
- Mandatory CCTV physical key limitation disclaimer
- Campus policy category definitions (Accessible, Emergency, Faculty, Visitor, General)
- Safety policy interlock: rejecting non-emergency users from reserving emergency slots or routes (400 Bad Request)
- Dynamic expiry evaluation and automated bay release
- Restricted slot violation detection and critical security alert dispatch
- Security manual override with mandatory justification and audit logging
- Category utilization, bay occupancy, and compliance report generation

Run CCTV & Device Health Management tests:
```bash
$env:PYTHONPATH="."
.\venv\Scripts\python backend/tests/test_cctv_device_health.py
.\venv\Scripts\python backend/tests/run_cctv_device_api_tests.py
```
This runs 20 automated unit and live API tests verifying:
- Camera operational telemetry (online/offline, heartbeat, stream status, AI pipeline status, storage usage, retention policy)
- Privacy & role-based access control: regular users blocked from CCTV live stream access (403 Forbidden)
- Authorized stream viewing mints sanitized proxy URL without exposing credentials and logs `CAMERA_STREAM_VIEWED` in `AuditLog`
- Camera status modification logs health diagnostics and audit trail
- Automated diagnostic alerts for camera failure, unavailable stream, AI processing failure, and storage nearing capacity (>85%)
- Authorized footage export with mandatory justification, SHA-256 digital watermark, and `CCTV_FOOTAGE_EXPORTED` audit log
- User-reported device issue form submission (`DEV-YYYYMMDD-XXXX`)
- Full ticket workflow: Staff acknowledgement, technician assignment, resolution notes, and chronological timeline history
- IoT hardware ping diagnostic latency and heartbeat recovery
- Strict secrecy verification: server credentials and NVR master secrets never exposed in frontend schemas

Run general backend tests:
```bash
$env:PYTHONPATH="."
.\venv\Scripts\python backend/tests/test_live_server.py
```
This runs automated integration tests verifying:
- Health check & token authentication
- Dashboard metrics and zone breakdowns
- Duplicate open parking session detection
- Smart exit validation & tariff calculation
- Congestion analytics & CCTV camera status
- CSV report generation
- Frontend SPA delivery

---

## AI Hardware Simulation & ANPR Modes

Per safety and auditing requirements:
- When physical cameras are offline or absent, the background **Simulation Service** generates realistic vehicle turnover and camera heartbeats.
- Every simulated event is tagged with `is_simulated = True` and displays an amber **`[SIMULATED]`** badge.
- Real vehicle image uploads processed by OpenCV are tagged as `is_simulated = False` and display a green **`[REAL ANPR]`** badge.
- Operators can pause or start simulation at any time using the header banner or the Settings page.
