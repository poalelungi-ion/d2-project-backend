# D2-Project: Sprint 4 (Production Data Ingestion, Course Marks & UI Refinement)

* **Official Kanban Board:** `D2-Project: Sprint 4` *(Created on: 09/30/2026)*
* **Sprint Timeline:** `September 30, 2026 – November 05, 2026` (`30.09.2026 – 05.11.2026`)
* **Sprint Status:** Closed / Beta Stage Delivered
* **Total Story Points:** 58 Points
* **Total Work Items:** 23 Items (18 User Stories, 3 Technical Tasks, 2 Critical Bug Fixes)
* **Git Release Branch:** [`release/sprint-4-v0.4.0-beta`](https://github.com/poalelungi-ion/d2-project-client/-/tree/release/sprint-4-v0.4.0-beta)
* **Git Release Tag:** [`v0.4.0-beta`](https://github.com/poalelungi-ion/d2-project-client/-/tags/v0.4.0-beta) (`release-sprint-4-v0.4.0-beta`)
* **Target Delivery Release:** `v0.4.0-beta` (Beta Stage Milestone - Latest)

---

## 📊 Sprint 4 Backlog Overview

| # | Work Item ID | Type | Title / Description | Assignee | Points | Status | Priority |
| :-: | :--- | :--- | :--- | :--- | :-: | :---: | :---: |
| 1 | **#99906** | USER STORY | Strict Column Name Standardization on File Import | Ion Poalelungi | 5 pts | Tested | High |
| 2 | **#104084** | USER STORY | Restrict Grade Parsing to Numeric 1.0–5.0 | Ion Poalelungi | 3 pts | Tested | High |
| 3 | **#104089 / #97743** | USER STORY | Design the Validation & Review Screen with Inline Editing | Ion Poalelungi | 8 pts | Tested | High |
| 4 | **#104102** | USER STORY | Redesign Study Program Mapping & Dynamic Column Ingestion | Ion Poalelungi | 5 pts | Tested | Normal |
| 5 | **#104109** | USER STORY | Free-Form Exam Attempt Text Field Across UI & Backend | Ion Poalelungi | 3 pts | Tested | Normal |
| 6 | **#104098** | USER STORY | Consolidated Best Mark Column in Course Marks Table | Ion Poalelungi | 3 pts | Tested | Normal |
| 7 | **#104104** | USER STORY | Display Chronological Mark History Upon Clicking Best Mark | Ion Poalelungi | 3 pts | Tested | Normal |
| 8 | **#99891** | USER STORY | Decimal Formatting for Grades Column (German Comma) | Ion Poalelungi | 2 pts | Tested | Normal |
| 9 | **#99896** | USER STORY | Average Grade Display per Semester in Course Header | Ion Poalelungi | 3 pts | Tested | Normal |
| 10 | **#99908** | USER STORY | Restrict Grade Editing to Lecture View Only | Ion Poalelungi | 3 pts | Tested | Normal |
| 11 | **#99888** | USER STORY | Edit Button Added to Course Page Header | Ion Poalelungi | 1 pt | Tested | Normal |
| 12 | **#99913 / #104081** | USER STORY | Study Program Selection Dropdown with Immediate Persistence | Ion Poalelungi | 2 pts | Tested | Normal |
| 13 | **#101781** | USER STORY | Edit Exam Detail from Course Overview | Ion Poalelungi | 2 pts | Tested | Normal |
| 14 | **#104092 / #104090** | USER STORY | Dedicated Course Drive Tab & Decoupling from Requirements | Anna Chiriciuc | 3 pts | Tested | Normal |
| 15 | **#104085** | USER STORY | Exclude Students Without Valid Grades from Persistence | Ion Poalelungi | 2 pts | Tested | Normal |
| 16 | **#104080** | USER STORY | Disable Default Seed Data in Production Delivery | Ion Poalelungi | 2 pts | Tested | Normal |
| 17 | **#104082 / #104083** | TASK | Deprecate Student Status Selector & Remove Graduate/Fail Actions | Ion Poalelungi | 2 pts | Tested | Normal |
| 18 | **#104086** | TASK | Remove Obsolete ECTS Column & Schema Fields | Ion Poalelungi | 1 pt | Tested | Normal |
| 19 | **#104087** | USER STORY | Restrict Data Upload Entry Point Exclusively to Course Detail | Anna Chiriciuc | 2 pts | Tested | Normal |
| 20 | **#104091** | USER STORY | Clear Staged File Capability Before Confirmation | Anna Chiriciuc | 1 pt | Tested | Normal |
| 21 | **#104095** | USER STORY | Full Viewport Responsive Layout Across Grids and Dialogs | Anna Chiriciuc | 3 pts | Tested | Normal |
| 22 | **#104096 / #104099** | BUG | Fix Dropdown Backgrounds & Review Row Deselection | Anna Chiriciuc | 2 pts | Tested | Normal |
| 23 | **MR !70** | BUG | Fix CourseMarksTable Flex Shrinking & Table Height Collapse | Ion Poalelungi | 3 pts | Tested | High |

---

## 🎯 Thematic Feature Breakdown

### Theme 1: Production Data Ingestion & Spreadsheet Normalization
* **Strict Column Header Standardization (#99906):** Ingestion engine mandates standard German academic column headers (`Matrikelnummer`, `Fach`, `Studiengang`, `Versuch`, `Bewertung`), providing explicit validation badges and error diagnostics when required fields are missing.
* **Validation & Review Screen with In-Flight Editing (#104089, #97743):** Multi-step upload wizard presents an interactive AG Grid review step allowing lecturers to inspect parsed rows, re-map unrecognized columns, and edit individual cell typos before committing to PostgreSQL.
* **Strict Numeric Grading (1.0–5.0) Enforcement (#104084):** Normalizes grade inputs strictly to the official German academic numerical scale (`1.0` through `5.0`), rejecting non-numeric tokens or malformed strings.
* **Dynamic Study Program Aliasing & Float Matrikelnummer Fixes (#104102):** Resolves varied faculty acronyms (e.g. `M.Sc. WINF` → `Wirtschaftsinformatik (Master of Science)`), cleans `.0` floating-point artifacts from numeric student ID columns, and automatically detects and ignores summary footer rows.
* **Clean Ingestion Safeguards (#104085, #104086, #104091):** Automatically excludes records missing valid grades from DB persistence, removes obsolete ECTS metadata, and enables discarding staged files before review.

### Theme 2: Grade Evaluation, Exam Tracking & Best Mark Analytics
* **Free-Form Exam Attempt Field (#104109):** Replaces rigid exam attempt pickers with a free-form attempt descriptor field, empowering lecturers to designate customized sittings (e.g., "Klausur 1", "Wiederholungsprüfung", "Retake Summer 2026").
* **Consolidated Best Mark Column (#104098):** Computes and displays the single best achieved grade across all attempts for each student in the primary Course Marks table.
* **Chronological Mark History View (#104104):** Clicking any student's Best Mark cell opens an interactive drawer presenting their chronological grade trajectory across all recorded sittings.
* **Localized Decimal Formatting (#99891):** Formats all displayed grades with standard German decimal comma notation (`1,0`, `1,3`, `2,0`, etc.).
* **Semester Grade Averages (#99896):** Calculates and renders real-time weighted grade averages for each semester directly in the course analytics summary.
* **Protected Lecture-View Grade Editing (#99908) & Exam Detail Editing (#101781):** Locks grade editing to dedicated lecture views to prevent accidental overwrites, while offering quick-action modals to edit exam metadata directly from the course overview.

### Theme 3: Responsive UI Layout & Critical Viewport Fixes
* **CourseMarksTable Layout & Height Fix (MR !70):** Corrected a flexbox container layout flaw in `CourseMarksTable.tsx` where `<Paper>` collapsed to 2px or truncated at row 9. Enforced full width, removed `flex: 1`, and disabled flex-shrinking to guarantee complete scrolling across single and comparative exam modes.
* **Full Viewport Utilization (#104095):** Redesigned page containers, AG Grid tables, and modal dialogues to utilize available viewport height and width without clipped cards or artificial vertical scroll locks.
* **Visual Polish & Menu Bug Fixes (#104096, #104099):** Fixed transparent backgrounds on Material-UI select menus and eliminated unintended row deselection when clicking individual rows during review.

### Theme 4: Navigation, Course Drive Vault & Roster Simplification
* **Dedicated Course Drive Tab (#104092, #104090):** Promoted the Course Document Repository to its own top-level tab in Course Details, cleanly separating document archival from exam spreadsheet uploading.
* **Contextual Data Upload Entry Point (#104087):** Streamlined upload navigation by launching ingestion directly from within the selected course context.
* **Study Program Dropdown & Live Update (#99913, #104081):** Upgraded study program text inputs to searchable dropdown menus that persist changes immediately to the database and update the active view.
* **Student Lifecycle Simplification (#104082, #104083):** Removed deprecated student status flags and graduate/fail lifecycle actions to align with SSE faculty management guidelines.
* **Clean Production Baseline (#104080):** Disabled automatic test data seeding in production deployments and removed synthetic demo distribution charts from empty states.

---

## 📈 Quality Assurance & CI/CD Status
* **Automated Test Suites:** 26 test suites, 234 unit & integration tests passing across client (Vitest) and backend (Pytest).
* **Live End-to-End Evaluation:** 11 dedicated live user story verification test suites executed against the running Docker stack with 100% pass rate.
* **GitLab CI Pipelines:** Both client (`#887528`) and backend (`#887496`) pipelines green on `main`.
* **Complexity & Duplication:** Zero blocking code duplication; ESLint and Ruff complexity gates verified.
