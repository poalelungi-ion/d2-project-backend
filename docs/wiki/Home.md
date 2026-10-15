# Study Progress Analysis (SPA) – Backend Service Wiki

Welcome to the backend engineering documentation for the **Study Progress Analysis (SPA)** platform developed at **Stiftung Universität Hildesheim (Software Systems Engineering - SSE)**.

> 📌 **Master Project Documentation & Frontend Portal:**
> For the overarching system overview, UI architecture, full agile sprint backlog, and complete user story traceability matrix, please visit the primary project hub repository:
> 🔗 **[`d2-project-client/docs/wiki`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client/-/tree/main/docs/wiki)**

---

## 📚 Backend Documentation Index

### 1. Architecture & Data Persistence
* **[System Architecture](Architecture.md):** Backend service topology, data flow sequence diagrams, and relational database ER schema.
* **[Backend Service Architecture](Code-Documentation/Backend-Architecture.md):** FastAPI application structure, SQLAlchemy models, Pydantic schemas, and Alembic migrations.
* **[Deployment & Configuration Guide](Code-Documentation/Deployment-Guide.md):** Docker Compose orchestration, CORS origin allowlisting, and security parameters.

---

### 2. Release Management & Version Milestones
* **[Delimited Releases Log](Releases.md):** Backend milestones and API contracts:
  * **Release v0.0.1-alpha (Sprint 0: Ignition):** Project setup, decoupled architecture, PostgreSQL 15 containerization.
  * **Release v0.1.0-alpha (Sprint 1):** Ingestion engine foundations, multi-format parsing, schema normalization.
  * **Release v0.2.0-alpha (Sprint 2):** Pass/Fail calculation, Per-Person History, Attempt Categorization, absence codes.
  * **Release v0.3.0-beta (Sprint 3 - Latest):** Course Drive file hub, exam attempt comparison, granular marks editing, and deployment hardening.

---

### 3. Developer Onboarding & Handover
* **[Developer Onboarding Guide](Onboarding-Guide.md):** Python virtual environment setup, Pytest test runner, and Docker workflow.
* **[Traceability Matrix](Traceability-Matrix.md):** Backend routes and automated tests mapped to User Stories.
* **[Project Handover Checklist](Handover-Checklist.md):** Package verification, test accounts, database backup & restoration.

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
