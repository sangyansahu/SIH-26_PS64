# AICTE Integrated Complaint Monitoring & Coordination Portal
### Smart India Hackathon 2026 | Problem Statement ID: 26264

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-blue.svg)](https://www.postgresql.org/)
[![Vue](https://img.shields.io/badge/Vue.js-3.5-emerald.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-sky.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Pytest-11%20Passed-brightgreen.svg)]()

---

## 1. Executive Summary & Problem Context

In the governance of higher technical education in India, institution-related complaints are frequently received and processed across disconnected AICTE departments, including:
- **Public Grievance Redressal Cell (PGRC)**: Citizen, student, and faculty grievances regarding unfair practices, fee extortion, and service rules.
- **Approval Bureau (AB)**: Extension of Approval (EoA), land/infrastructure compliance, and sanctioned intake irregularities.
- **Ragging Prevention Cell (RPC)**: Mandatory anti-ragging compliance, helpline referrals, and disciplinary inquiries.
- **Policy & Academic Planning Bureau (PAPB)**: Minimum faculty qualification standards, curriculum compliance, and accreditation discrepancies.
- **Finance & Accounts Bureau (FAB)**: Scholarship grant disbursement and financial audit scrutiny.

When departmental databases are fragmented, authorities struggle to see an institution's **complete regulatory history**, leading to duplicated inquiries, conflicting regulatory actions, and delayed enforcement.

### The Solution
The **AICTE Integrated Complaint Monitoring & Coordination Portal** consolidates cross-departmental records into a single administrative view. The system includes a **Cross-Bureau Overlap Detection Engine** that correlates complaints concerning the same institution across departments, while strictly preserving departmental autonomy, procedural audit trails, and officer review authority without destructive auto-merging.

---

## 2. Architecture & Technology Stack

```
                              ┌──────────────────────────────────┐
                              │     Vue 3 + TypeScript SPA       │
                              │ (Tailwind CSS, Pinia, Vue Router)│
                              └─────────────────┬────────────────┘
                                                │ REST API (JSON / Cookies)
                                                ▼
                              ┌──────────────────────────────────┐
                              │       Python Flask REST API      │
                              │ (/api/v1/ Blueprints, Auth, RBAC)│
                              └───────┬──────────────────┬───────┘
                                      │                  │
                SQLAlchemy 2.x ORM    ▼                  ▼  RapidFuzz Matching
                     ┌──────────────────┐      ┌───────────────────────────┐
                     │  PostgreSQL 16   │      │ 4-Stage Overlap Detection │
                     │ Primary Database │      │  (Exact, Fuzzy, Content)  │
                     └──────────────────┘      └───────────────────────────┘
```

### Frontend
- **Framework**: Vue.js 3 (Composition API with `<script setup>`)
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: Vue Router 4 (role-guarded routes)
- **State Management**: Pinia
- **Styling**: Tailwind CSS (Impeccable administrative design discipline: warm/neutral surfaces, ink typography, semantic status indicators)
- **Icons**: Lucide Icons
- **HTTP Client**: Axios with JWT session interceptors

### Backend
- **Framework**: Python 3.11+, Flask 3.1
- **Architecture**: Versioned REST API (`/api/v1/`) structured with modular Flask Blueprints
- **ORM & Data Layer**: SQLAlchemy 2.x
- **Database Migrations**: Flask-Migrate & Alembic
- **Primary Database**: PostgreSQL 16 (psycopg2-binary)
- **Fuzzy Correlation Engine**: RapidFuzz (token set ratio, alias resolution)
- **Automated Testing**: Pytest with automated test database isolation

---

## 3. Repository Structure

```
aicte-complaint-portal/
├── backend/
│   ├── app/
│   │   ├── api/                 # Flask REST API Blueprints
│   │   │   ├── admin.py         # User administration & audit logs
│   │   │   ├── auth.py          # JWT login, logout, session verification
│   │   │   ├── bureaus.py       # AICTE bureaus & cell officers
│   │   │   ├── complaints.py    # Case registration, assignment, transfers
│   │   │   ├── imports.py       # CSV validation preview & commit
│   │   │   ├── institutions.py  # Institution directory & cross-bureau roll-ups
│   │   │   ├── notifications.py # In-app alerts & deadline monitors
│   │   │   ├── overlaps.py      # Cross-bureau overlap review queue
│   │   │   └── reports.py       # Dynamic KPI metrics & CSV export
│   │   ├── models/              # SQLAlchemy relational models
│   │   │   ├── audit_event.py   # Consequential action audit log
│   │   │   ├── bureau.py        # AICTE departments
│   │   │   ├── case_action.py   # Immutable action history
│   │   │   ├── case_link.py     # Unique ordered overlap links
│   │   │   ├── complaint.py     # Case records with overdue calculation
│   │   │   ├── import_batch.py  # Ingestion batch history
│   │   │   ├── institution.py   # Institution profiles & AICTE Permanent ID
│   │   │   ├── notification.py  # Real in-app alerts
│   │   │   └── user.py          # Users with password hashing & RBAC
│   │   └── services/            # Pure business logic layer
│   │       ├── auth_service.py
│   │       ├── complaint_service.py
│   │       ├── import_service.py
│   │       ├── institution_service.py
│   │       ├── notification_service.py
│   │       ├── overlap_service.py  # 4-stage correlation pipeline
│   │       └── report_service.py
│   ├── tests/                   # Automated Pytest suite
│   ├── config.py                # Database and threshold configuration
│   ├── requirements.txt
│   ├── run.py                   # API entry point (port 5000)
│   └── seed.py                  # Reproducible test dataset with Scenarios A-F
├── frontend/
│   ├── src/
│   │   ├── api/client.ts        # Axios API client
│   │   ├── components/          # Reusable UI primitives (Badges, Cards, Modals)
│   │   ├── layouts/AppLayout.vue# Administrative application shell
│   │   ├── router/index.ts      # Navigation guards & role restrictions
│   │   ├── stores/              # Pinia state stores
│   │   ├── types/index.ts       # TypeScript domain interfaces
│   │   └── views/               # Complete operational pages
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── scripts/
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 4. Quick Start Guide (Local Development)

### 1-Click Automated Launch (Windows)
Simply double-click [`run.bat`](file:///f:/SIH64/run.bat) in the project root, or execute:
```cmd
run.bat
```
`run.bat` automatically handles the entire lifecycle:
1. **System Check**: Verifies Python (3.11+) and Node.js/npm.
2. **Portable PostgreSQL**: Detects local PostgreSQL; downloads, extracts, and initializes portable PostgreSQL 16 into `SIH64\pgsql` automatically if missing.
3. **Database Readiness**: Starts the local database service, creates databases, and seeds initial records.
4. **Environment & Dependencies**: Creates `backend\.venv`, installs `requirements.txt`, and runs `npm install` if missing.
5. **Orchestrated Startup**: Launches the Flask REST API on `http://localhost:5000` and Vue 3 frontend on `http://localhost:5173`.
6. **Browser Auto-Launch**: Automatically opens `http://localhost:5173` with 1-click credential switchers ready.

To stop all servers and PostgreSQL cleanly, press `[Q]` in the launcher or run [`stop.bat`](file:///f:/SIH64/stop.bat).

---

### Manual Setup Workflow

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 14+ running locally on port 5432

### Step 1: Clone and Configure Environment
```bash
git clone <repo-url>
cd aicte-complaint-portal
cp .env.example .env
```

### Step 2: Set up Backend & Database
```bash
cd backend
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# Run the reproducible seed command (creates tables & scenario records):
python seed.py

# Start the Flask API server (runs on http://127.0.0.1:5000):
python run.py
```

### Step 3: Set up & Start Frontend
In a new terminal:
```bash
cd frontend
npm install

# Start Vite development server (runs on http://127.0.0.1:5173):
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.

---

## 5. Docker Compose Workflow (Optional Convenience)

To launch the entire stack (PostgreSQL + Flask + Vue) with one command:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:5000`
- PostgreSQL: `localhost:5432`

---

## 6. Three Separate Login Roles & Official Demo Credentials

The portal implements **three separate login roles**, each with its dedicated dashboard, workflows, and backend-enforced authorization policies. A **1-click quick credentials switcher** is available directly on the sign-in screen:

| Role | User ID / Email | Password | Dedicated Dashboard Route | Primary Permissions & Responsibilities |
| :--- | :--- | :--- | :--- | :--- |
| **1. Public User / Complainant** | `user` *(or `user@aicte.gov.in`)* | `user` *(or `User@12345`)* | `/user` | Lodge grievances, track status, view recorded outcomes, respond to official queries & upload missing documents without re-filing, download official acknowledgement. Strict backend isolation (sees only own complaints). |
| **2. AICTE Bureau Official** | `industry` *(or `officer.pgrc@aicte.gov.in`)* | `industry` *(or `Officer@12345`)* | `/` | Manage assigned & bureau-wide cases, verify potential overlaps side-by-side (`Confirmed Overlap`, `False Alert`, `Needs Review`), record coordination notes, next actions, track case ageing, inspect Institution 360° profiles. |
| **3. System Administrator** | `admin` *(or `admin@aicte.gov.in`)* | `admin` *(or `Admin@12345`)* | `/admin` | System-wide analytics with bureau/region breakdowns, user & role management, SLA & escalation configuration, monthly/quarterly reports with CSV export, audit logs & system health, data quality flags, configurable categories & bureaus. |

### Feature Implementation Matrix

#### 1. Public User / Complainant Dashboard (`/user`)
- **File a New Complaint**: Full modal with AICTE Permanent ID institution lookup, category selection, detailed description, and supporting document uploads.
- **Track Existing Complaints**: Real-time table displaying Complaint Tracking ID, current status, responsible Bureau/Cell, submission date, and latest operational update.
- **Notifications & Responses**: Real-time notification feed tracking acknowledgements, bureau transfers, queries for additional information, and final case disposals.
- **Complaint History**: Consolidated list of all previously lodged complaints showing recorded regulatory outcomes in one unified view.
- **Additional Information Requests**: Interactive response interface enabling complainants to reply to official clarification queries and upload missing documentation **without** having to lodge a new complaint.
- **Downloadable Acknowledgement & Status Summary**: Clean, printable official Government of India / AICTE acknowledgement receipt with Permanent ID, docket number, barcode placeholder, and statutory filing summary (`window.print()`).
- **Access Restriction (Backend-Enforced)**: Complainant endpoints strictly verify session identity: public users can ONLY retrieve their own records; internal bureau remarks, sensitive regulatory memos, and third-party cases return HTTP `403 Forbidden`.

#### 2. AICTE Bureau Official Dashboard (`/`)
- **My Assigned Cases**: Dedicated view of complaints assigned directly to the logged-in officer, highlighting priority, SLA status, target deadline, and next operational action.
- **Bureau-Wide Case Management**: Bureau-wide view of all cases within the officer's department, displaying responsible officers with reassignment capability for authorized officers.
- **Overlap Detection & Verification**: Side-by-side comparative inspection of flagged case pairs showing AICTE Permanent IDs, complaints descriptions, and action histories. Officers mark decisions as:
  - `Confirmed Overlap`
  - `False Alert`
  - `Needs Review`
- **Overlap Resolution Workflow**: Complete procedural workflow that links confirmed overlapping cases, automatically notifies relevant Bureaus, and immutably records coordination actions without destructive auto-merging (each case keeps its unique ID, owner, and history).
- **Institution 360° Profile**: Comprehensive institutional dossier aggregating all historical and active cases across all AICTE Bureaus, current case owners, status distributions, and previous regulatory actions.
- **Deadline & Overdue Alerts**: Urgency queue highlighting cases approaching deadlines, overdue breaches, escalation flags, and pending required steps.
- **Transfer & Coordination Requests**: Formal cross-bureau transfer request modal with recorded transfer rationale, bureau notifications, and coordination remarks.
- **Action History & Case Updates**: Chronological audit trail recording regulatory decisions, remarks, attachments, status transitions, and next actions with timestamp and officer ID.
- **Case Ageing Indicator**: Real-time calculation of total days pending from registration date.
- **Next Action Tracking**: Operational tracking of what immediate step must happen next, target due date, and responsible assignee.
- **Related Case Linking**: Non-destructive relationship linking between independent complaints.
- **Coordination Notes**: Cross-bureau shared notebook documenting agreed multi-departmental actions to eliminate contradictory regulatory directives.
- **Priority & Escalation Queue**: Instant filtering for overdue, high-priority, and repeatedly delayed cases.
- **Advanced Search & Filters**: Multi-parameter search across Permanent ID, institution name, status, priority, and date range.

#### 3. System Administrator Dashboard (`/admin`)
- **System-Wide Analytics**: Real-time totals for received, pending, under-process, disposed, transferred, and overdue cases, accompanied by Bureau-wise and Region-wise operational distributions.
- **Institution & Case Overview**: Global search across all technical institutions in India with consolidated cross-bureau complaint histories.
- **User & Role Management**: Create new user accounts, toggle active/disabled status, assign officers to bureaus, and reset account credentials.
- **Deadline & Escalation Configuration**: Interactive configuration of statutory resolution timelines (Critical, High, Medium, Low SLA days), reminder thresholds, and auto-escalation rules.
- **Reports & Export**: Dynamic generation of monthly and quarterly analytical reports on disposal rates, ageing distributions, bureau workloads, and recurring institutional complaints, with instant CSV export.
- **Audit Logs & System Health**: Immutable audit stream capturing status modifications, officer reassignments, overlap verifications, and permission updates, alongside real-time system health checks (PostgreSQL database connectivity, schema integrity, and active services).
- **Data Import & Validation**: Authorized bureau CSV/Excel bulk ingestion with preview mode that validates data integrity, checks AICTE Permanent IDs, and reports row errors before committing.
- **Data Quality Flags**: Automated scanner identifying missing Permanent IDs, inconsistent institution names, and incomplete dossiers.
- **Configurable Case Categories & Bureaus**: Create and update complaint categories and AICTE Bureaus dynamically without requiring source code modifications.

---

## 7. Demonstration Scenarios (Pre-Seeded)

The portal comes pre-loaded with realistic scenarios designed for hackathon evaluation:

- **Scenario A: Cross-Bureau Potential Overlap**:
  - `AICTE-2026-PGRC-0001` (Public Grievance Cell) and `AICTE-2026-AB-0002` (Approval Bureau) both concern *Apex Institute of Technology and Management* regarding unapproved capitation fee extortion.
  - The overlap pipeline flags this pair with a **100% match score** (exact AICTE Permanent ID match + identical CPGRAMS external ref + shared salient keywords `#capitation`, `#caution`, `#withholding`).
  - Officials can open the **Overlap Review Queue**, inspect side-by-side case cards, and click **Confirm Related**, **Mark Unrelated**, or **Defer Decision**.
- **Scenario B: Same Institution, Unrelated Complaints**:
  - Complaints `AICTE-2026-AB-0003` (Chemistry lab safety) and `AICTE-2026-RPC-0004` (Hostel anti-ragging) both concern *National Institute of Technical Excellence (Pune)*.
  - The engine recognizes the shared institution but categorizes them as distinct operational matters rather than duplicates.
- **Scenario C: Overdue Complaint**:
  - Complaint `AICTE-2026-PAPB-0005` (Kalinga Academy) has breached its statutory SLA deadline.
  - Highlighted with red urgency badges, prominent overdue banners, and automated escalation notifications.
- **Scenario D: Resolved Complaint with Audit Trail**:
  - Complaint `AICTE-2026-PGRC-0006` (Delhi Polytechnic) contains an immutable chronological history from intake, through inspection directives, to formal disposal with RTGS payment proof.
- **Scenario E: Enforced Bureau Isolation**:
  - A PGRC Officer attempting to modify or assign cases belonging to the Approval Bureau is strictly rejected by the backend with HTTP `403 Forbidden`.
- **Scenario F: Safe CSV Import Preview**:
  - The CSV Ingestion wizard previews uploaded batches row-by-row, flagging invalid institution references or missing fields without corrupting active records.

---

## 8. Multi-Stage Overlap Detection Pipeline

The pipeline operates in 4 auditable stages:

1. **Stage A: Exact Identifier Matching**:
   - Compares AICTE Permanent IDs (`1-10293847`) and external references (CPGRAMS dockets, High Court writ numbers). Yields high-confidence matches.
2. **Stage B: Institution Identity Resolution**:
   - Normalizes institutional names by stripping punctuation and expanding standard Indian educational abbreviations (`Inst.` → `Institute`, `Tech.` → `Technology`, `Engg.` → `Engineering`).
   - Computes token set ratio and alias cross-matching via RapidFuzz, penalized if institutions reside in different states.
3. **Stage C: Content & Topic Similarity**:
   - Matches regulatory categories (`Fee Overcharging`, `Ragging`, `Approval Fraud`).
   - Extracts salient keywords using domain-specific stopword filtering and calculates Jaccard token overlap alongside token sort ratios.
4. **Stage D: Explainable Synthesis & Human Review**:
   - Synthesizes an overall weighted score ($0.0$ to $1.0$).
   - Generates an explainable human-readable rationale (e.g., *"Identical AICTE ID; 85% keyword overlap regarding capitation fee; cross-departmental case between PGRC and AB"*).
   - Enforces unique canonical ordered indexing `(id_a < id_b)` to prevent duplicate links.

---

## 9. Automated Testing & Verification

The backend test suite runs against an isolated PostgreSQL test database:

```bash
cd backend
pytest -v
```

### Verified Test Results (11 Passed):
- `tests/test_auth.py`: Token login, invalid credentials rejection, `/api/v1/auth/me`, 401 unauthorized checks.
- `tests/test_complaints.py`: Case registration, status updates, auditable action history timeline, and 403 bureau boundary restrictions.
- `tests/test_overlap.py`: Normalization pipeline, keyword extraction, automated cross-bureau overlap detection, and official review decisions.
- `tests/test_import.py`: CSV preview validation, row error reporting, and batch commit transactions.

### Frontend Production Build:
```bash
cd frontend
npm run build
```
- Compiles with Vue TypeScript compiler (`vue-tsc -b`) and Vite production bundler in under 2 seconds with **0 errors**.

---

## 10. Security & Privacy Highlights

- **Role-Based Access Control**: Strict backend verification on every endpoint; frontend controls are backed by server-side authorization.
- **Password Security**: Passwords hashed using `werkzeug.security` (PBKDF2-SHA256 with dynamic salt).
- **Session Protection**: JWT authentication supported via `Authorization: Bearer <token>` and `HttpOnly`, `SameSite=Lax` cookies.
- **Audit Trails**: Consequential regulatory actions (logins, status updates, assignments, transfers, overlap decisions, CSV imports) record immutable `AuditEvent` records with user ID, IP address, and payload snapshots.
- **Data Integrity**: Parameterized ORM queries prevent SQL injection; canonical ordered link constraints prevent duplicate relationship links.

---

## 11. Official SIH 2026 Compliance

This software has been developed exclusively to address **Problem Statement 26264**:
- Internal administrative intelligence portal (not a generic public intake form).
- Solves cross-departmental silos between AICTE Bureaus.
- 100% locally runnable using free and open-source tooling without paid external AI APIs or cloud dependencies.
