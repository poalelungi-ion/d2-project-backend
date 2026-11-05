# Backend Service Architecture

The backend is built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL 15**, providing a high-throughput, ACID-compliant API service for academic ingestion and analytics.

---

## 📁 Source Code Organization

```
d2-project-backend/
  main.py                FastAPI application instance, startup migration hooks, CORS setup
  config.py              Centralized environment configuration and normalization
  dependencies.py        FastAPI dependency injection (get_db, get_current_user)
  database.py            SQLAlchemy async/sync engine, sessionmaker, schema safety
  models.py              Declarative ORM models (User, Student, Course, ExamResult, RefreshToken)
  schemas.py             Pydantic v2 validation DTOs and request/response contracts
  seed.py                Realistic academic seed dataset for empty database initialization
  routers/
    auth.py              Registration, login, cookie rotation, account info
    courses.py           Course catalogue, details, creation, update, archival
    students.py          Student roster, profiles, academic transcripts, trajectory status
    grades.py            Mark updates, historical exam edits, grade audit trails
    upload.py            Spreadsheet previewing, column mappings, atomic ingestion confirm
    stats.py             Longitudinal pass-rates, grade curves, dashboard KPI metrics
  migrations/            Alembic database migration versions and environment scripts
  tests/                 Pytest test suites (unit, integration, and security checks)
```

---

## ⚡ Data Ingestion Pipeline & Atomic Guarantees

The ingestion service (`routers/upload.py` and `services/ingestion.py`) handles multi-format file parsing (`.xlsx`, `.csv`, `.tsv`, `.ods`) through a 2-phase process:

```mermaid
sequenceDiagram
    autonumber
    actor Lecturer as University Lecturer
    participant Client as Frontend (AG Grid)
    participant API as FastAPI Ingestion Router
    participant DB as PostgreSQL Database

    Lecturer->>Client: Upload Spreadsheet / Paste Data
    Client->>API: POST /api/upload/preview/ (Multipart File or JSON)
    API->>API: Parse via Pandas / Map Headers / Drop Course Cols
    API->>API: Validate Mandatory Fields (Matrikelnummer, Name, Semester)
    API-->>Client: Return Parsed Rows + Missing Fields Warning Flags
    Lecturer->>Client: Inspect in AG Grid & Correct Missing Data
    Lecturer->>Client: Click "Confirm Import"
    Client->>API: POST /api/upload/confirm/ (Validated JSON Payload)
    loop Each Row
        API->>DB: Upsert Course & Student Records (db.flush())
        API->>DB: Insert ExamResult with Attempt Type (db.flush())
    end
    alt All rows valid
        API->>DB: db.commit() [Atomic Success]
        API-->>Client: 200 OK (Success Modal & Stats Refresh)
    else Error during write
        API->>DB: db.rollback() [Zero Partial Saves]
        API-->>Client: 400/500 JSON Error (MUI Toast Notification)
    end
```

---

## 🛡️ CORS Normalization & Allowed Origins

To guarantee strict security while allowing flexible server deployments:
* The backend reads `CORS_ORIGINS` from `.env`.
* In `config.py`, origins are parsed and trailing slashes are automatically stripped:
  ```python
  CORS_ORIGINS = [orig.strip().rstrip("/") for orig in os.getenv("CORS_ORIGINS", "").split(",") if orig.strip()]
  ```
* Because authentication requests utilize `httpOnly` refresh cookies (`credentials: 'include'`), wildcards (`*`) are prohibited by browser CORS specifications.
