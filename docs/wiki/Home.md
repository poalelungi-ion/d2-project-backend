# Study Progress Analysis (SPA) System — Project Wiki

Welcome to the central documentation wiki for the **Study Progress Analysis (SPA)** project developed at **Stiftung Universität Hildesheim (Software Systems Engineering - SSE)**.

The system allows university lecturers and academic staff to ingest heterogeneous exam spreadsheets (`.xlsx`, `.csv`, `.tsv`, `.ods`), review and validate student records with zero data corruption, track longitudinally aggregated course performance, and explore student trajectories across exam attempts.

---

## 📚 Wiki Table of Contents

### 1. Project Architecture & Code Documentation
* **[System Architecture](Architecture.md):** Complete high-level and component topology, data flows, and database ER schema.
* **[Frontend Client Architecture](Code-Documentation/Frontend-Architecture.md):** React 18, Vite, MUI layout, AG Grid data matrices, Zustand stores, and client API layers.
* **[Backend Service Architecture](Code-Documentation/Backend-Architecture.md):** FastAPI REST application, SQLAlchemy ORM, Alembic migrations, and JWT bearer auth.
* **[Deployment & Configuration Guide](Code-Documentation/Deployment-Guide.md):** Docker Compose setup, container registries, dynamic base URL injection, and CORS allowlisting.

---

### 2. Release Management & History
* **[Delimited Releases Log](Releases.md):** Semantic versioning releases with official Git tags, delimiting alpha milestones and the current beta release.
  * **Release v0.0.1-alpha (Inception — Sprint 0: Ignition):** Architectural blueprint, decoupled repositories, Docker Compose setup.
  * **Release v0.1.0-alpha (Early Alpha Milestone — Sprint 1):** Ingestion engine, multi-format parser, atomic DB transaction, preview grid.
  * **Release v0.2.0-alpha (Alpha Milestone 2 — Sprint 2):** Pass/Fail calculation, per-person student history, attempt categorization, and absence parsing.
  * **Release v0.3.0-beta (Beta Milestone 1 — Sprint 3):** Course Drive file repository, exam attempt comparison, granular marks editing, and dynamic zero-rebuild configuration.
  * **Release v0.4.0-beta (Beta Milestone 2 — Sprint 4 - Latest):** Strict column name standardization, dynamic review screen with inline editing, 1.0–5.0 numeric grades enforcement, free-form attempt fields, consolidated best marks, and Course Marks table viewport stability.

---

### 3. Sprint Planning & Iteration Delivery
* **[Sprint 0 (08/04/2026 – 08/17/2026)](sprints/Sprint-0.md):** Architectural blueprint, Docker setup, quality infrastructure.
* **[Sprint 1 (08/18/2026 – 08/31/2026)](sprints/Sprint-1.md):** Ingestion engine foundations, multi-format parsing, schema normalization.
* **[Sprint 2 (09/01/2026 – 09/14/2026)](sprints/Sprint-2.md):** **Delivered Alpha 2 Milestone (9 items)** — Pass/Fail calculation, Per-Person History, Attempt Categorization, absence codes.
* **[Sprint 3 (09/15/2026 – 09/29/2026)](sprints/Sprint-3.md):** **Delivered Beta 1 Milestone (69 Points, 27 Items)** — Course Drive UI, Exam Attempts Comparison, Tabular Data Paste Studio, Lecture View Restrictions, and Deployment Hardening.
* **[Sprint 4 (09/30/2026 – 11/05/2026)](sprints/Sprint-4.md):** **Current Beta Milestone (58 Points, 23 Items - Latest)** — Production Data Ingestion, Dynamic Column Mapping, Strict 1.0–5.0 Grades, Free-Form Attempts, Best Marks Analytics, Dedicated Course Drive Tab, and CourseMarksTable Fixes.

---

### 4. Developer Onboarding, Traceability & Handover
* **[Developer Onboarding Guide](Onboarding-Guide.md):** Day-1 setup, native & Docker development environments, coding conventions, and verification steps.
* **[Full Requirements & Code Traceability Matrix](Traceability-Matrix.md):** End-to-end mapping from agile User Stories & Tasks to Backend code, Frontend views, and automated tests.
* **[Project Handover & Delivery Checklist](Handover-Checklist.md):** Package verification, test accounts, database backup & restoration, and troubleshooting FAQ.

---

## 👥 Core Project Team

| Name | Role | Mail |
| :--- | :--- | :--- |
| **Ion Poalelungi** | Architecture & Lead Developer | poalelungi@uni-hildesheim.de |
| **Anna Chiriciuc** | Frontend & Quality Assurance | chiriciuc@uni-hildesheim.de |