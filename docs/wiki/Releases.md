# Release Management & Delimited Releases Log

The Study Progress Analysis (SPA) project follows [Semantic Versioning 2.0.0](https://semver.org/) (`0.MAJOR.MINOR-PRERELEASE`).
The project is currently in the **Beta Development Stage**, transitioning from early **Alpha** milestones. Each major iteration milestone is delimited by its corresponding sprint boundary and published as a tagged release in Git.

```mermaid
flowchart LR
    R0["v0.0.1-alpha<br/>(Sprint 0: Setup)"] --> R1["v0.1.0-alpha<br/>(Sprint 1: Early Alpha)"]
    R1 --> R2["v0.2.0-alpha<br/>(Sprint 2: Alpha 2)"]
    R2 --> R3["v0.3.0-beta<br/>(Sprint 3: Beta 1)"]
    R3 --> R4["v0.4.0-beta<br/>(Sprint 4: Current Beta)"]
```

---

## 🚀 Release v0.4.0-beta — Current Beta Milestone (Delimited by Sprint 4)
* **Release Date:** November 05, 2026 (`30.09.2026 – 05.11.2026`)
* **Stage:** **Beta Release (Latest)**
* **Sprint Cycle:** **Sprint 4**
* **Velocity Delivered:** 58 Story Points (23 Work Items)
* **GitLab Release Branch:** [`release/sprint-4-v0.4.0-beta`](https://github.com/poalelungi-ion/d2-project-client/-/tree/release/sprint-4-v0.4.0-beta)
* **GitLab Tag:** [`v0.4.0-beta`](https://github.com/poalelungi-ion/d2-project-client/-/tags/v0.4.0-beta) (`release-sprint-4-v0.4.0-beta`)

### Key Features Delivered
1. **Production Data Ingestion & Spreadsheet Normalization:**
   - Strict column header standardization (`Matrikelnummer`, `Fach`, `Studiengang`, `Versuch`, `Bewertung`) with missing-field alert diagnostics (`#99906`).
   - Interactive AG Grid review screen before persistence featuring dynamic column remapping and inline typo cell corrections (`#104089`, `#97743`).
   - Strict numeric grade enforcement (1.0–5.0) rejecting non-numeric status strings (`#104084`).
   - Automatic study program alias expansion (e.g. `M.Sc. WINF` → `Wirtschaftsinformatik (Master of Science)`), `.0` student ID float stripping, and summary footer filtering (`#104102`).
   - Automatic exclusion of student records lacking valid grades (`#104085`).
   - Decoupled obsolete ECTS schema fields (`#104086`) and added clear staged file capabilities (`#104091`).
2. **Grade Evaluation, Exam Tracking & Best Mark Analytics:**
   - Free-form exam attempt descriptors enabling custom sittings like "Klausur 1" or "Retake Summer 2026" (`#104109`).
   - Consolidated single Best Mark column in Course Marks table (`#104098`).
   - Interactive chronological mark history drawer upon clicking Best Mark cells (`#104104`).
   - Localized German decimal comma notation (`1,0`, `1,3`, `2,0`) across all grade views (`#99891`).
   - Real-time weighted average grade calculations rendered per semester (`#99896`).
   - Strict lecture-view-only grade editing guards (`#99908`) and quick exam detail editing modal (`#101781`).
3. **Responsive UI Layout & Course Marks Table Fixes:**
   - Resolved critical Paper container flex-shrinking in `CourseMarksTable.tsx` allowing complete scrolling in Single and Compare Exam modes (`MR !70`).
   - Full viewport responsive utilization across grids, cards, and modal dialogs (`#104095`).
   - Fixed Material-UI dropdown menu transparency and singular row click deselection in review (`#104096`, `#104099`).
4. **Navigation, Course Drive Vault & Roster Simplification:**
   - Dedicated Course Drive tab separating file management from ingestion (`#104092`, `#104090`).
   - Restricted upload entry point contextually to individual course pages (`#104087`).
   - Course overview edit button for quick metadata updates (`#99888`).
   - Standardized study program dropdown with immediate DB persistence (`#99913`, `#104081`).
   - Deprecated student status selector and graduate/fail lifecycle actions (`#104082`, `#104083`).
   - Clean production baseline: disabled automatic synthetic seeding and removed placeholder charts (`#104080`).

---

## 📦 Release v0.3.0-beta — Beta Milestone 1 (Delimited by Sprint 3)
* **Release Date:** September 29, 2026 (`15.09.2026 – 29.09.2026`)
* **Stage:** **Beta Release 1**
* **Sprint Cycle:** **Sprint 3**
* **Velocity Delivered:** 69 Story Points (27 Work Items)
* **GitLab Release Branch:** [`release/sprint-3-v0.3.0-beta`](https://github.com/poalelungi-ion/d2-project-client/-/tree/release/sprint-3-v0.3.0-beta)
* **GitLab Tag:** [`v0.3.0-beta`](https://github.com/poalelungi-ion/d2-project-client/-/tags/v0.3.0-beta) (`release-sprint-3-v0.3.0-beta`)

### Key Features Delivered
1. **Course Drive & Document Hub:**
   - Centralized file drive architecture per course (`US-01 #101369`, `US-02 #101370`, `US-03 #101371`, `US-04 #101373`).
   - Integrated source spreadsheet download and audit tracking.
2. **Advanced Exam Comparison & Multi-Filter:**
   - Side-by-side exam attempt comparison engine (`#101779`).
   - Synchronized mirrored semester and exam sitting filters (`#101780`).
   - Course marks semester traceability column (`#101782`).
   - Lecture-only grade modification guards (`#99908`).
3. **Tabular Data Ingestion Studio:**
   - Direct spreadsheet copy-paste (`Ctrl+V`) into AG Grid (`#95949`).
   - Consolidated upload modal merging drag-and-drop and clipboard paste (`#99901`).
4. **Student Data Profile Suite:**
   - Full student CRUD with unique Matrikelnummer enforcement and 409 conflict handling (`#97930`).
5. **Dynamic Configuration & Enterprise Deployment:**
   - Client startup environment injection via `/config.js` (`VITE_API_BASE_URL`).
   - Hardened backend CORS configuration (`CORS_ORIGINS`).
   - In-browser settings modal with live connection test and 10-tap Developer Mode Easter egg.

---

## 🏛️ Release v0.2.0-alpha — Alpha Milestone 2 (Delimited by Sprint 2)
* **Release Date:** September 14, 2026 (`01.09.2026 – 14.09.2026`)
* **Stage:** **Alpha Release 2**
* **Sprint Cycle:** **Sprint 2** (9 Work Items)
* **GitLab Release Branch:** [`release/sprint-2-v0.2.0-alpha`](https://github.com/poalelungi-ion/d2-project-client/-/tree/release/sprint-2-v0.2.0-alpha)
* **GitLab Tag:** [`v0.2.0-alpha`](https://github.com/poalelungi-ion/d2-project-client/-/tags/v0.2.0-alpha) (`release-sprint-2-v0.2.0-alpha`)

### Key Features Delivered
1. **Grade-Driven Pass/Fail Calculation & Absence Parsing (`#96054`):**
   - Automatically computes passing threshold (`grade <= 4.0`) with normalized absence codes (`na`, `ta`, `ne`).
2. **Aggregated Data View: Per-Person History (`#99859`):**
   - Longitudinal student history view displaying transcripts across semesters.
3. **Categorize Exam Attempts & Handle Missing Study Programs (`#96055`):**
   - Attempt categorization (`Exam 1`, `Exam 2`, `Other`) with graceful fallback for unassigned study programs.
4. **Ingestion & Dashboard Bug Fixes (`#99879`, `#99881`, `#99895`):**
   - Fixed drag-and-drop window freeze; fixed alphabetical semester sort to strict chronological order.
5. **Exam Distribution Metrics (`#99900`):**
   - Calculated and rendered student exam counts per semester.
6. **Core Ingestion Verification (`#95732`, `#96053`):**
   - Required field validation and initial spreadsheet import.

---

## 📦 Release v0.1.0-alpha — Early Alpha Milestone (Delimited by Sprint 1)
* **Release Date:** August 31, 2026 (`18.08.2026 – 31.08.2026`)
* **Stage:** **Alpha Release 1**
* **Sprint Cycle:** **Sprint 1**
* **GitLab Release Branch:** [`release/sprint-1-v0.1.0-alpha`](https://github.com/poalelungi-ion/d2-project-client/-/tree/release/sprint-1-v0.1.0-alpha)
* **GitLab Tag:** [`v0.1.0-alpha`](https://github.com/poalelungi-ion/d2-project-client/-/tags/v0.1.0-alpha) (`release-sprint-1-v0.1.0-alpha`)

### Key Features Delivered
1. **Multi-Format Spreadsheet Ingestion Foundations:**
   - Parsing engine supporting `.xlsx`, `.csv`, `.tsv`, and `.ods`.
2. **Data Validation Engine:**
   - Pre-commit missing field inspection and invalid row flagging.
3. **Atomic Transaction Guarantees:**
   - Zero partial saves; all-or-nothing database flush and commit.
4. **Interactive AG Grid Preview:**
   - Inline typo corrections and approved absence handling prior to permanent archival.

---

## 🏗️ Release v0.0.1-alpha — Project Inception Milestone (Delimited by Sprint 0)
* **Release Date:** August 17, 2026 (`04.08.2026 – 17.08.2026`)
* **Stage:** **Alpha Inception**
* **Sprint Cycle:** **Sprint 0: Ignition**
* **GitLab Release Branch:** [`release/sprint-0-ignition`](https://github.com/poalelungi-ion/d2-project-client/-/tree/release/sprint-0-ignition)
* **GitLab Tag:** [`release-ignition-sprint-0`](https://github.com/poalelungi-ion/d2-project-client/-/tags/release-ignition-sprint-0)

### Key Features Delivered
1. **Repository Topology & Stack Selection:**
   - Decoupled client (`d2-project-client`) and backend (`d2-project-backend`) repositories.
   - Initial Docker Compose orchestration with PostgreSQL 15.
2. **Quality Infrastructure & Linting:**
   - Type-aware ESLint 9 configuration, Pytest test runner, and Vitest setup.
3. **Traceability Framework:**
   - Base traceability conventions connecting user requirements to code.
