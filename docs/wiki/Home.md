# Study Progress Analysis (SPA) System – Project Wiki

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
* **[Delimited Releases Log](Releases.md):** Formal release notes, semantic versioning gates, tagged builds, and release delivery artifacts.
  * **Release v1.0.0 (Foundations & Ingestion Pipeline):** Core parser, validation engine, atomic DB transaction, preview grid.
  * **Release v2.0.0 (Visual Analytics & Authenticated Identity):** SSE accounts, JWT session rotation, longitudinal trajectory charts, pass/fail histograms.
  * **Release v3.0.0 (Course Drive, Advanced Exam Analytics & Tabbed Studio):** File drive system, exam attempt comparison, granular marks editing, and dynamic runtime configuration.

---

### 3. Sprint Planning & Iteration Delivery
* **[Sprint 1 (08/18/2026 – 08/31/2026)](sprints/Sprint-1.md):** Ingestion engine, file parsers, schema normalization, preview table.
* **[Sprint 2 (09/01/2026 – 09/14/2026)](sprints/Sprint-2.md):** Secure SSE authentication, student transcripts, attempts categorization, charts suite.
* **[Sprint 3 (09/15/2026 – 09/29/2026)](sprints/Sprint-3.md):** **Active Iteration (69 Points, 27 User Stories & Tasks)** — Course Drive UI, Exam Attempts Comparison, Tabular Data Paste Studio, Lecture View Restrictions, and Deployment Hardening.

---

### 4. Developer Onboarding, Traceability & Handover
* **[Developer Onboarding Guide](Onboarding-Guide.md):** Day-1 setup, native & Docker development environments, coding conventions, and verification steps.
* **[Full Requirements & Code Traceability Matrix](Traceability-Matrix.md):** End-to-end mapping from agile User Stories & Tasks to Backend code, Frontend views, and automated tests.
* **[Project Handover & Delivery Checklist](Handover-Checklist.md):** Package verification, test accounts, database backup & restoration, and troubleshooting FAQ.

---

## 👥 Core Project Team (Group D2)

| Name | Role | Mail |
| :--- | :--- | :--- |
| **Ion Poalelungi** | Architecture & Frontend Lead | `poalelungi@uni-hildesheim.de` |
| **Anna Chiriciuc** | Frontend & Quality Assurance | `chiriciuc@uni-hildesheim.de` |
| **Sudarshan Bashyal** | Backend Lead & Security | `sudarshan.bashyal@uni-hildesheim.de` |
| **Yazan Al Rifaee** | Full-Stack Developer | `alrifaee@uni-hildesheim.de` |
| **Marvin Wucher** | Full-Stack Developer | `wucher@uni-hildesheim.de` |
| **Amara Aslam** | Frontend Developer | `aslam@uni-hildesheim.de` |
| **Aditi Joshi** | QA & Frontend Developer | `joshi@uni-hildesheim.de` |
