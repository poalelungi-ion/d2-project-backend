# Study Progress Analysis (SPA) – Backend Service & Data Layer

[![Stage: Beta](https://img.shields.io/badge/Stage-Beta%20v0.4.0-blue.svg)](docs/wiki/Releases.md)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Database: PostgreSQL 15](https://img.shields.io/badge/Database-PostgreSQL%2015-336791.svg)](https://www.postgresql.org/)

FastAPI REST application and relational data layer powering the **Study Progress Analysis (SPA)** platform for **Stiftung Universität Hildesheim (Software Systems Engineering - SSE)**. 

The service ingests heterogeneous exam spreadsheets, ensures ACID transaction safety, handles absence code normalization, manages longitudinal course analytics, and serves student academic trajectories over an authenticated HTTP API.

> 📌 **Primary Project Repository & Master Documentation:**
> For the overarching system architecture, sprint boards, end-to-end user story traceability matrix, and client user interface, refer to the frontend project hub:
> 🔗 **[`d2-project-client`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client)**

---

## 🚀 Delimited Backend Releases & Official Git Branches

Following [Semantic Versioning 2.0.0](https://semver.org/), iterations are delimited by agile sprints, marking the progression from **Alpha** prototypes to the current **Beta** release.

| Milestone | Official Kanban Board | Git Release Branch | Git Release Commit | Git Tags | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Release v0.4.0-beta** | `D2-Project: Sprint 4`<br>*(Created 09/30/2026)* | [`release/sprint-4-v0.4.0-beta`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tree/release/sprint-4-v0.4.0-beta) | `release(sprint-4): D2-Project Sprint 4 - v0.4.0-beta - Production Data Ingestion & Course Marks Milestone` | [`v0.4.0-beta`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tags/v0.4.0-beta)<br>`release-sprint-4-v0.4.0-beta` | **Delivered (Beta Stage - Latest)** |
| **Release v0.3.0-beta** | `D2-Project: Sprint 3`<br>*(Created 09/18/2026)* | [`release/sprint-3-v0.3.0-beta`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tree/release/sprint-3-v0.3.0-beta) | `release(sprint-3): D2-Project Sprint 3 - v0.3.0-beta - Course Drive, Exam Analytics & Hardening` | [`v0.3.0-beta`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tags/v0.3.0-beta)<br>`release-sprint-3-v0.3.0-beta` | Delivered (Beta 1) |
| **Release v0.2.0-alpha** | `D2-Project: Sprint 2`<br>*(Created 09/03/2026)* | [`release/sprint-2-v0.2.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tree/release/sprint-2-v0.2.0-alpha) | `release(sprint-2): D2-Project Sprint 2 - v0.2.0-alpha - Core Analytics, Attempts & Absence Normalization` | [`v0.2.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tags/v0.2.0-alpha)<br>`release-sprint-2-v0.2.0-alpha` | Delivered (Alpha 2) |
| **Release v0.1.0-alpha** | `D2-Project: Sprint 1`<br>*(Created 08/14/2026)* | [`release/sprint-1-v0.1.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tree/release/sprint-1-v0.1.0-alpha) | `release(sprint-1): D2-Project Sprint 1 - v0.1.0-alpha - Ingestion & Validation Foundations` | [`v0.1.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tags/v0.1.0-alpha)<br>`release-sprint-1-v0.1.0-alpha` | Delivered (Alpha 1) |
| **Release v0.0.1-alpha** | `D2-Project: Ignition`<br>*(Created 08/03/2026)* | [`release/sprint-0-ignition`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tree/release/sprint-0-ignition) | `release(sprint-0): D2-Project Ignition - v0.0.1-alpha - Project Setup & Architecture` | [`release-ignition-sprint-0`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend/-/tags/release-ignition-sprint-0)<br>`v0.0.1-alpha` | Completed (Inception) |

---

## 🛠️ Backend Stack & Components

| Concern | Library / Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Modern type annotations, async handlers, and robust typing |
| **Web Framework** | FastAPI (ASGI) | High-performance asynchronous REST endpoints with auto-generated OpenAPI / Swagger specs |
| **ORM & Data Layer** | SQLAlchemy 2.0 | Declarative relational models, connection pooling, and atomic transaction handling |
| **Database** | PostgreSQL 15 | Relational ACID database provisioned and managed via Docker |
| **Migrations** | Alembic | Version-controlled schema migrations executed on startup |
| **Data Parsing** | Pandas + OpenPyXL | Ingestion engine supporting `.xlsx`, `.csv`, `.tsv`, and `.ods` files |
| **Authentication** | PyJWT + Passlib (bcrypt) | Stateless access tokens and rotating `httpOnly` refresh tokens |
| **Test Runner** | Pytest + httpx | Automated integration and regression test suites |

---

## 📁 Repository Structure

```
d2-project-backend/
  main.py                FastAPI application instantiation, CORS middleware, router registration
  config.py              Centralized environment configuration, secret validation, CORS parsing
  dependencies.py        Shared FastAPI dependencies (DB sessions, authenticated user validation)
  database.py            SQLAlchemy engine, scoped session factory, Base declarative class
  models.py              ORM entities: User, Course, Student, ExamResult, CourseFile, RefreshToken
  schemas.py             Pydantic request & response DTOs with validation rules
  seed.py                Sample university dataset for initial database seeding
  routers/               REST endpoints grouped by business domain:
    auth.py              Sign in, registration, token refresh, sign out
    courses.py           Course catalogue, details, editing, course drive files
    students.py          Student profiles, transcripts, Matrikelnummer validation
    grades.py            Exam mark recording, attempt categorization, grade adjustments
    upload.py            Spreadsheet parsing preview, column normalization, atomic commit
    stats.py             Semester distributions, KPI cards, passing rate analytics
  migrations/            Alembic migration versions and environment configurations
  tests/                 Pytest suite covering routers, services, security, and edge cases
  docs/wiki/             Backend-focused architecture, releases, and deployment guides
```

---

## ⚡ Running the Backend

### Option A: With Docker (PostgreSQL included)

```bash
# Build and run backend API and PostgreSQL database
docker compose up --build
```

- **API Base:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

### Option B: Local Virtualenv (Native Python)

Requires a running PostgreSQL instance (or set `DATABASE_URL` in `.env`):

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server with auto-reload
uvicorn main:app --reload --port 8000
```

---

## 🔒 Configuration & CORS Security Hardening

Configuration values are loaded from `.env` via `config.py`:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://spa_user:spa_password@db/spa_db` | PostgreSQL connection URL |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed client origins |
| `JWT_SECRET` | `insecure-development-secret-change-me` | Secret key for signing bearer tokens |
| `COOKIE_SECURE` | `false` | Set to `true` when deploying in production over HTTPS |

### Connecting Remote Clients (CORS Setup)

When deploying on a server or VM, the backend must be explicitly informed of the frontend's origin:

```env
CORS_ORIGINS=http://<YOUR_SERVER_IP_OR_DOMAIN>:5173
```

- **Trailing Slashes:** Automatically stripped by `config.py` (`.rstrip("/")`) to prevent preflight mismatch errors.
- **Wildcard Restrictions:** Wildcards (`*`) are disallowed because authentication relies on credentialed requests (`credentials: 'include'`) for secure `httpOnly` refresh cookies.

---

## 🗃️ Database Migrations (Alembic)

Database schema evolution is managed via Alembic:

- **Automatic Startup Migration:** On container boot, `run_migrations()` in `main.py` applies all pending migrations up to `head`.
- **Creating a Migration:**
  ```bash
  alembic revision --autogenerate -m "add_column_name"
  ```
- **Upgrading Manually:**
  ```bash
  alembic upgrade head
  ```

---

## 🧪 Testing & Quality Gates

```bash
# Execute full backend test suite
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing
```

---

## 👥 Core Project Team (Group D2)

| Name | Role | Email |
| :--- | :--- | :--- |
| **Sudarshan Bashyal** | Backend Lead & Security | `sudarshan.bashyal@uni-hildesheim.de` |
| **Ion Poalelungi** | Architecture & Frontend Lead | `poalelungi@uni-hildesheim.de` |
| **Anna Chiriciuc** | Frontend & Quality Assurance | `chiriciuc@uni-hildesheim.de` |
| **Yazan Al Rifaee** | Full-Stack Developer | `alrifaee@uni-hildesheim.de` |
| **Marvin Wucher** | Full-Stack Developer | `wucher@uni-hildesheim.de` |
| **Amara Aslam** | Frontend Developer | `aslam@uni-hildesheim.de` |
| **Aditi Joshi** | QA & Frontend Developer | `joshi@uni-hildesheim.de` |
