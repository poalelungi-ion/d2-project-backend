# Developer Onboarding & Project Handover Guide

Welcome to the **Study Progress Analysis (SPA)** system team! This guide provides everything a new developer, maintainer, or evaluator needs to understand, run, develop, and hand off the application with confidence.

---

## 🎯 1. System Mission & Core Domain

The **Study Progress Analysis (SPA)** platform is designed for university lecturers and faculty administrators at **Stiftung Universität Hildesheim (Software Systems Engineering - SSE)**. 

### Core Responsibilities
1. **Heterogeneous Exam Data Ingestion:** Parse varied formats (`.xlsx`, `.csv`, `.tsv`, `.ods`) or direct clipboard paste (`Ctrl+V`) from spreadsheets.
2. **Interactive Data Validation & Correction:** Catch missing or malformed records prior to database insertion; allow instant cell edits in AG Grid without raw SQL intervention.
3. **Course Drive & Document Management:** Course-scoped file repository to store, download, and review submitted exam spreadsheets.
4. **Longitudinal Student Trajectories & Analytics:** Visualize historical grade curves, pass/fail ratios, and per-attempt progress across sittings (`Exam 1` vs `Exam 2`).
5. **Strict University Authentication:** Role-aware access control enforcing the `@uni-hildesheim.de` domain with rotating JWT refresh cookies.

---

## 💻 2. Prerequisites & Tooling

Before getting started, ensure the following are installed:
* **Docker Engine** (v24.0+) & **Docker Compose** (v2.20+)
* **Node.js** (v20.x or v22.x LTS) & **npm** (v10.x+)
* **Python** (v3.11+) & **pip**
* **Git** (v2.40+)

---

## 🚀 3. Day-1 Quickstart (5 Minutes)

### Option A: Complete Dockerized Environment (Recommended)

1. **Clone the repositories into a shared parent folder:**
   ```bash
   mkdir spa-project && cd spa-project
   git clone https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client.git
   git clone https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-backend.git
   ```

2. **Set up the central environment file:**
   ```bash
   cp d2-project-client/.env.example .env
   # Or copy from root .env.example if available
   ```

3. **Start the complete stack:**
   ```bash
   docker compose up -d --build
   ```

4. **Verify running containers:**
   ```bash
   docker compose ps
   ```

5. **Access the application:**
   * **Frontend UI:** [http://localhost:5173](http://localhost:5173)
   * **FastAPI Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   * **PostgreSQL:** `localhost:5432` (`spa_user` / `spa_password` / `spa_db`)

---

### Option B: Native Local Development (No Docker for App Code)

#### 1. Start PostgreSQL Only
```bash
docker run -d --name spa_postgres \
  -e POSTGRES_USER=spa_user \
  -e POSTGRES_PASSWORD=spa_password \
  -e POSTGRES_DB=spa_db \
  -p 5432:5432 \
  postgres:15-alpine
```

#### 2. Start Backend Service
```bash
cd d2-project-backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
# Run migrations and start API
uvicorn main:app --reload --port 8000
```

#### 3. Start Frontend Client
```bash
cd ../d2-project-client
npm install
npm run dev
```

---

## 🧪 4. Day-1 Sanity & Verification Suite

Always run the test suites to verify that the local environment matches production CI quality gates:

### Client Verification
```bash
cd d2-project-client

# 1. Type check
npm run typecheck

# 2. Run unit tests
npm test

# 3. Production build check
npm run build
```

### Backend Verification
```bash
cd d2-project-backend

# 1. Run pytest suite
pytest
```

---

## 📐 5. Codebase Directory Maps

### Client Topology (`d2-project-client`)
```
src/
  api/                    # The ONLY layer communicating with backend HTTP endpoints
    client.ts             # Base URL resolver, fetch client, 401 refresh interceptor
    auth.ts, courses.ts, students.ts, grades.ts, uploads.ts
  components/
    common/               # UniHildesheimLogo, PillowBadge, StatCard
    drive/                # Course Drive file repository UI (#101370, #101373)
    features/             # Full application screens
      auth/               # LoginForm, RegisterForm, AuthSettingsDialog
      batchUpload/        # Multi-step upload wizard & tabular paste studio (#95949, #99901)
      courseDetail/       # Hero card, exam comparison, marks table (#101779, #101780)
      settings/           # SettingsDialog, BackendApiConnectionSection, ProfDinoGame
      AnalysisHub.tsx     # Student trajectory charts & comparative grade curves
      CourseDetail.tsx    # Course hub view with Drive, Marks, and Comparisons
      StudentDetail.tsx   # Student academic profile & transcript (#97930)
      SystemLogs.tsx      # System audit trail and diagnostic logs suite
  hooks/
    useAppLogic.tsx       # Central shared state and navigation handlers
  stores/                 # Zustand reactive state stores
    authStore.ts, themeStore.ts, studyProgramStore.ts, systemLogStore.ts
```

### Backend Topology (`d2-project-backend`)
```
d2-project-backend/
  main.py                 # FastAPI initialization, CORS middleware, router mounts
  config.py               # Environment configuration and trailing slash normalizer
  dependencies.py         # Shared dependencies (get_db, get_current_user)
  database.py             # SQLAlchemy engine & session factory
  models.py               # ORM models (User, RefreshToken, Student, Course, ExamResult)
  schemas.py              # Pydantic validation schemas & DTO contracts
  routers/
    auth.py               # Login, register, token refresh, current user profile
    courses.py            # Course management & course-scoped data
    students.py           # Student roster, profiles, and transcript histories
    grades.py             # Lecture-only grade modifications and audit trails
    upload.py             # File preview, header mappings, atomic import confirm
    stats.py              # Visual dashboard aggregations & KPIs
  migrations/             # Alembic database migrations
```

---

## 🌿 6. Development Workflow & Git Rules

1. **Branching Convention:**
   * Feature branches: `feature/<ticket-id>-<short-description>` (e.g. `feature/101370-course-drive-ui`)
   * Bugfix branches: `fix/<ticket-id>-<short-description>` (e.g. `fix/99879-drag-and-drop-upload`)
2. **Quality Gates & Budgets:**
   * **Function Length:** Maximum **500 lines** per function (`max-lines-per-function`). Extract modular sections if growing large.
   * **Complexity:** Maximum **20** cyclomatic complexity (`complexity`).
3. **Commit Conventions:**
   * Use conventional commit headers: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`.
   * When pairing on Windows, bypass symlink husky hooks if needed using `git commit --no-verify`.
   * Always include pair programming attribution trailers:
     ```
     Co-authored-by: Ion Poalelungi <poalelungi@uni-hildesheim.de>
     Co-authored-by: Anna Chiriciuc <chiriciuc@uni-hildesheim.de>
     ```

---

## 🔑 7. Security & Authentication Architecture

1. **Email Domain Enforced:** Only emails ending in `@uni-hildesheim.de` are permitted to register (`UNIVERSITY_EMAIL_DOMAIN`).
2. **Dual-Token Authentication:**
   * **Access Token:** Short-lived (15 min), held purely in memory (`client.ts`), passed as `Bearer` header.
   * **Refresh Token:** Long-lived (14 days), delivered via `httpOnly` secure cookie scoped to `/api/auth`.
   * **Token Rotation:** Any call to `/api/auth/refresh` revokes the old token and issues a new pair.
3. **Zero Plaintext Passwords:** Hashed with salted `bcrypt` (`BCRYPT_ROUNDS=12`).
4. **CORS Security:** Must list exact origins in `CORS_ORIGINS` (wildcards prohibited with credentialed cookies).
