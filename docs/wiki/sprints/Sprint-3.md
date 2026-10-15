# Sprint 3: Course Drive, Advanced Exam Analytics & Deployment Hardening

* **Sprint Timeline:** `September 15, 2026 – September 29, 2026` (`15.09.2026 – 29.09.2026`)
* **Sprint Status:** Active
* **Total Story Points:** 69 Points
* **Total Work Items:** 27 Items (19 User Stories, 8 Technical Tasks)
* **Target Delivery Release:** Release v3.0.0

---

## 📊 Sprint 3 Backlog Overview

| # | Work Item ID | Type | Title / Description | Assignee | Points | Status | Priority |
| :-: | :--- | :--- | :--- | :--- | :-: | :---: | :---: |
| 1 | **#99880** | USER STORY | Semester selection should be implemented as dropdown menu | Amara Aslam | 1 pt | Developed | Normal |
| 2 | **#101369** | USER STORY | US-01: Architectural Restructuring & Development Workflow Rewrite | Ion Poalelungi | 3 pts | Developed | Normal |
| 3 | **#101370** | USER STORY | US-02: "Course Drive" UI - Foundation & Layout | Ion Poalelungi | 2 pts | Developed | Normal |
| 4 | **#101371** | USER STORY | US-03: Upload Path Migration to Course Drive | Marvin Wucher | 2 pts | Developed | Normal |
| 5 | **#101373** | USER STORY | US-04: Course Drive - Advanced File Management | Ion Poalelungi | 5 pts | Developed | Normal |
| 6 | **#95647** | USER STORY | View course details *(Parent: Course Management)* | Anna Chiriciuc | 3 pts | Tested | Normal |
| 7 | **#99901** | USER STORY | Batch Data Upload Merged with Relevant Tab | Anna Chiriciuc | 5 pts | Tested | Normal |
| 8 | **#99908** | USER STORY | Restrict Grade Editing to Lecture View Only | Yazan Al Rifaee | 5 pts | Developed | Normal |
| 9 | **#99914** | USER STORY | Remove Status Column | Aditi Joshi | 2 pts | New | Normal |
| 10 | **#99882** | TASK | Remove Teacher Dashboard | Anna Chiriciuc | 0 pts | Tested | High |
| 11 | **#99888** | USER STORY | Edit Button Added to Course Page | Yazan Al Rifaee | 1 pt | Developed | Normal |
| 12 | **#99896** | USER STORY | Average Grade Display per Semester | Yazan Al Rifaee | 3 pts | Developed | Normal |
| 13 | **#99917** | TASK | Remove Study Program in Edit Course | Anna Chiriciuc | 0 pts | Tested | Normal |
| 14 | **#99890** | TASK | Remove Demo/Test Files from the Upload | Marvin Wucher | 0 pts | Closed | Normal |
| 15 | **#99894** | TASK | Remove Passed Checkbox Column | Aditi Joshi | 0 pts | In progress | Normal |
| 16 | **#100550** | TASK | Document Setup | Ion Poalelungi | 0 pts | Tested | Normal |
| 17 | **#97930** | USER STORY | Student Data Profile | Ion Poalelungi | 3 pts | Tested | Normal |
| 18 | **#99913** | USER STORY | Study Program Selection Implemented as Dropdown Menu | Yazan Al Rifaee | 1 pt | Developed | Normal |
| 19 | **#99886** | TASK | Remove "Assigned Professor" Field from Edit Course Form | Ion Poalelungi | 0 pts | Tested | Normal |
| 20 | **#99889** | USER STORY | Hide Course Statistics When There Are No Submissions | Marvin Wucher | 5 pts | Developed | Normal |
| 21 | **#99892** | TASK | Remove Duplicate File Name Validation During Upload | Yazan Al Rifaee | 0 pts | In progress | Normal |
| 22 | **#95949** | USER STORY | Paste tabular data directly *(Parent: Data Pipeline)* | Yazan Al Rifaee | 5 pts | Developed | Normal |
| 23 | **#95642** | USER STORY | Login with a dedicated SSE account *(Parent: Auth)* | Sudarshan Bashyal | 5 pts | Developed | Normal |
| 24 | **#101779** | USER STORY | Compare exam attempts in Course Details | Sudarshan Bashyal | 8 pts | Developed | Normal |
| 25 | **#101780** | USER STORY | Filter Grades by Exam and Semester in Course Details | Sudarshan Bashyal | 5 pts | Developed | Normal |
| 26 | **#101781** | USER STORY | Edit exam detail from course overview | Yazan Al Rifaee | 3 pts | Developed | Normal |
| 27 | **#101782** | USER STORY | Add Semester in Detailed Course Marks | Marvin Wucher | 2 pts | Developed | Normal |

---

## 🎯 Thematic Feature Breakdown

### Theme 1: Course Drive File System (US-01 to US-04)
* **US-01 (#101369):** Complete architectural restructuring establishing unified course assets.
* **US-02 (#101370):** Built the primary "Course Drive" tabbed workspace in the Course Detail view, featuring card headers, upload actions, and empty states.
* **US-03 (#101371):** Migrated legacy ad-hoc upload links to route directly through the course file drive.
* **US-04 (#101373):** Advanced file metadata viewer, download capabilities, and spreadsheet source inspection.

### Theme 2: Advanced Exam Analytics & Sittings Comparison (#101779, #101780, #101781, #101782, #99896)
* **Exam Comparison Engine (#101779):** Side-by-side comparative inspection between Exam 1 and Exam 2 (or cross-semester sittings).
* **Granular Multi-Filter (#101780):** Mirrored filtering across semester dropdowns and sitting pickers with synchronized grid updates.
* **Course Overview Exam Editing (#101781):** In-place exam detail modifications without leaving the course roster.
* **Detailed Marks Semester Column (#101782):** Visual audit trail identifying precisely which semester each exam mark belongs to.
* **Average Grade per Semester (#99896):** Real-time weighted average recalculation excluding non-graded/excused entries.

### Theme 3: Data Ingestion Studio & Direct Tabular Paste (#95949, #99901, #99890, #99892)
* **Direct Tabular Paste (#95949):** Lecturers can copy cells directly from Excel/Numbers/Google Sheets and paste (`Ctrl+V`) into the interactive grid.
* **Unified Upload Wizard (#99901):** Merged drag-and-drop file ingestion and tabular pasting into a streamlined multi-step modal studio.
* **Duplicate File Name Handling (#99892) & Cleanup (#99890):** Streamlined upload validation by removing redundant blocking errors.

### Theme 4: Student Profiling & Roster Management (#97930, #95647, #99908, #99913, #99880)
* **Student Data Profile (#97930):** Full student management suite enabling profile creation, validation (unique Matrikelnummer), and transcript history.
* **Lecture-View Grade Editing (#99908):** Strict editing boundaries preventing unintended grade mutations outside official lecture management mode.
* **Standardized Dropdowns (#99880, #99913):** Replaced free-text input with canonical study programs and chronological semester dropdowns.

### Theme 5: Enterprise Deployment, Base URL & Security Hardening
* **Dynamic API Base URL:** Container startup injection via `/config.js` (`VITE_API_BASE_URL`) for zero-rebuild production updates.
* **CORS Allowlist Security:** Strict backend origin matching and credentialed cookie handling (`CORS_ORIGINS`).
* **In-Browser Settings & Easter Egg:** Auth layout settings modal with theme switcher, connectivity tester, and 10-tap Developer Mode dino game.

---

## 📈 Quality Assurance & CI/CD Status
* **Unit & Integration Tests:** 25 test suites, 218 unit tests passing (Vitest + Pytest).
* **Complexity Budget:** ESLint `max-lines-per-function` verified (< 500 lines) via modular component extraction.
* **Duplication Threshold:** 0% blocking duplicate code.
* **Code Traceability:** Fully mapped in `docs/TRACEABILITY.md`.
