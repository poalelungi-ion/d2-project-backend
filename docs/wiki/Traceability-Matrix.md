# Full Requirements & Code Traceability Matrix

This document provides strict, bidirectional traceability connecting agile **User Stories & Tasks** to their **Acceptance Criteria**, **Backend API Endpoints**, **Frontend React Components**, and **Automated Verification Tests**.

---

## 📌 Traceability Legend
* `BE:` Backend implementation in `d2-project-backend`
* `FE:` Frontend implementation in `d2-project-client`
* `Test:` Automated test suite validating the requirement

---

## 🚀 Sprint 3 Traceability Registry (09/15/2026 – 09/29/2026)

| Work Item ID & Title | Acceptance Criteria | Backend Implementation | Frontend Implementation | Automated Verification Tests |
| :--- | :--- | :--- | :--- | :--- |
| **US-01 (#101369)**<br/>*Architectural Restructuring & Workflow Rewrite* | Refactor ingestion & course model hierarchy into modular architecture. | `src/router/dto/upload_dto.py`, `src/services/ingestion.py` | `src/types.ts`, `src/hooks/useAppLogic.tsx` | `tests/test_api.py`<br/>`src/api/client.test.ts` |
| **US-02 (#101370)**<br/>*"Course Drive" UI - Foundation & Layout* | Course-scoped file repository tab with hero card, empty state, and action buttons. | `routers/courses.py`<br/>`GET /api/courses/{id}` | `src/components/drive/CourseDrive.tsx`, `src/components/features/CourseDetail.tsx` | `src/components/drive/CourseDrive.test.tsx`<br/>*(US-02 tests pass)* |
| **US-03 (#101371)**<br/>*Upload Path Migration to Course Drive* | In-course "Upload Exam Data" initiates course-locked handoff to upload wizard. | `routers/upload.py`<br/>`resolve_course()` | `src/components/features/batchUpload/BatchUploadWizard.tsx` (`courseHandoff`) | `src/components/features/batchUpload/uploadRedirect.test.ts` |
| **US-04 (#101373)**<br/>*Course Drive - Advanced File Management* | File metadata cards, spreadsheet source inspector, and status audit tracking. | `models.Course`, `models.ExamResult` | `src/components/drive/CourseDrive.tsx` | `src/components/drive/CourseDrive.test.tsx` |
| **US #95647**<br/>*View Course Details* | Displays core metadata, lecturer tags, semester overview, and upload action. | `GET /api/courses/{id}` | `src/components/features/CourseDetail.tsx`, `src/components/features/courseDetail/CourseHeroCard.tsx` | `src/components/features/CourseDetail.test.tsx` |
| **US #99901**<br/>*Batch Data Upload Merged with Relevant Tab* | Drag & drop and tabular paste unified into cohesive tabbed modal studio. | `POST /api/upload/preview/` | `src/components/features/batchUpload/BatchUploadWizard.tsx` | `src/components/features/batchUpload/SelectFileStep.test.tsx` |
| **US #99908**<br/>*Restrict Grade Editing to Lecture View Only* | Prevent inline grade mutations unless lecturer explicitly enters Individual Marks edit mode. | `PUT /api/grades/{id}` | `src/components/features/CourseDetail.tsx`, `src/components/features/courseDetail/CourseMarksTable.tsx` | `src/components/features/CourseDetail.test.tsx`<br/>*(Lecture-view edit test)* |
| **US #99914**<br/>*Remove Status Column* | Redundant status column removed from simplified student tables. | Cleaned DTO models | `src/components/features/columns.tsx` | `src/routes/CourseDetail.test.tsx` |
| **TASK #99882**<br/>*Remove Teacher Dashboard* | Obsolete dashboard replaced by direct Analysis Hub and Course Drive navigation. | Router updates | `src/app/navigation.ts`, `src/App.tsx` | `src/components/features/SystemLogs.test.tsx` |
| **US #99888**<br/>*Edit Button Added to Course Page* | Accessible action button allowing direct course metadata editing. | `PUT /api/courses/{id}` | `src/components/forms/EditCourseDialog.tsx` | `src/components/features/CourseDetail.test.tsx` |
| **US #99896**<br/>*Average Grade Display per Semester* | Dynamically calculate weighted average grade per semester, excluding non-numeric/excused sittings. | `routers/stats.py`<br/>`GET /api/stats/summary` | `src/components/features/CourseDetail.tsx`, `src/utils/courseMarks.ts` | `src/utils/courseMarks.test.ts`<br/>*(45 test cases)* |
| **TASK #99917**<br/>*Remove Study Program in Edit Course* | Remove irrelevant study program field from course editing form. | `CourseUpdateRequest` | `src/components/forms/EditCourseDialog.tsx` | `src/components/features/CourseDetail.test.tsx` |
| **TASK #99890**<br/>*Remove Demo/Test Files from the Upload* | Cleanse sample mock spreadsheets from production build assets. | Static asset cleanup | `src/components/features/batchUpload/` | Production Vite build verification |
| **TASK #99894**<br/>*Remove Passed Checkbox Column* | Replaced binary checkbox with standard German numeric grade pill rendering. | Schema alignment | `src/components/features/courseDetail/CourseMarksTable.tsx` | `src/utils/gradeOutcome.test.ts` |
| **TASK #100550**<br/>*Document Setup* | Comprehensive deployment, Docker Compose, and developer onboarding instructions. | `d2-project-backend/README.md` | `d2-project-client/README.md`, `README.md` | Traceability verification |
| **US #97930**<br/>*Student Data Profile* | Complete student profile creation, editing, unique ID check, and 409 conflict handling. | `POST /api/students/`<br/>`PUT /api/students/{id}` | `src/components/forms/StudentFormDialog.tsx`, `src/components/features/StudentDetail.tsx` | `src/components/forms/StudentFormDialog.test.tsx`<br/>*(7 test cases)* |
| **US #99913**<br/>*Study Program Selection Implemented as Dropdown* | Standardize study program assignment through canonical dropdown selection. | `config.py` | `src/utils/studyProgram.ts`, `src/components/features/settings/StudyProgramAliasesSection.tsx` | `src/utils/studyProgram.test.ts` |
| **TASK #99886**<br/>*Remove "Assigned Professor" Field from Edit Course Form* | Eliminate deprecated professor input field from course management. | `schemas.py` | `src/components/forms/EditCourseDialog.tsx` | `src/components/features/CourseDetail.test.tsx` |
| **US #99889**<br/>*Hide Course Statistics When There Are No Submissions* | Gracefully display empty states instead of NaN/zero charts when a course lacks submissions. | `routers/stats.py` | `src/components/features/CourseDetail.tsx` | `src/components/features/CourseDetail.test.tsx` |
| **TASK #99892**<br/>*Remove Duplicate File Name Validation During Upload* | Allow re-uploading updated versions of a file using the same filename. | `routers/upload.py` | `src/components/features/batchUpload/SelectFileStep.tsx` | `src/components/features/batchUpload/SelectFileStep.test.tsx` |
| **US #95949**<br/>*Paste Tabular Data Directly* | Enable lecturers to copy spreadsheet cells and paste (`Ctrl+V`) into AG Grid preview. | `routers/upload.py`<br/>`preview_upload()` | `src/utils/tabularPaste.ts`, `src/components/features/batchUpload/BatchUploadWizard.tsx` | `src/utils/tabularPaste.test.ts`<br/>*(3 test cases)* |
| **US #95642**<br/>*Login with Dedicated SSE Account* | Secure university authentication enforcing `@uni-hildesheim.de` domain and token rotation. | `POST /api/auth/login`<br/>`POST /api/auth/refresh` | `src/components/features/auth/LoginForm.tsx`, `src/app/SessionGate.tsx` | `src/components/features/auth/LoginForm.test.tsx`<br/>`tests/test_auth.py` |
| **US #101779**<br/>*Compare Exam Attempts in Course Details* | Side-by-side comparative examination of Exam 1 vs. Exam 2 with metric diff indicators. | `routers/courses.py`<br/>`GET /api/courses/{id}/marks` | `src/components/features/courseDetail/ExamComparisonBar.tsx` | `src/components/features/CourseDetail.test.tsx`<br/>*(Comparison test suite)* |
| **US #101780**<br/>*Filter Grades by Exam and Semester in Course Details* | Mirrored filtering synchronization between semester picker and sitting dropdowns. | `GET /api/courses/{id}/marks?semester=...&attempt=...` | `src/components/features/CourseDetail.tsx` | `src/components/features/CourseDetail.test.tsx`<br/>*(Filter sync suite)* |
| **US #101781**<br/>*Edit Exam Detail from Course Overview* | Rapidly update sitting dates, attempt types, or exam labels directly from the overview. | `PATCH /api/grades/{id}` | `src/components/features/courseDetail/CourseMarksTable.tsx` | `src/components/features/CourseDetail.test.tsx` |
| **US #101782**<br/>*Add Semester in Detailed Course Marks* | Explicit semester audit column displayed across all individual marks records. | `models.ExamResult.semester` | `src/components/features/courseDetail/CourseMarksTable.tsx` | `src/components/features/courseDetail/CourseMarksTable.test.tsx` |
| **US #99880**<br/>*Semester Selection Dropdown* | Chronological semester list supporting both winter and summer terms in all dialogs. | `schemas.SemesterEnum` | `src/utils/semester.ts` | `src/utils/semester.test.ts`<br/>*(8 test cases)* |

---

## 📦 Sprint 2 Traceability Registry (09/01/2026 – 09/14/2026 · Release v0.2.0-alpha)

| Work Item ID & Title | Acceptance Criteria | Backend Implementation | Frontend Implementation | Automated Verification Tests |
| :--- | :--- | :--- | :--- | :--- |
| **US #96054**<br/>*Grade-Driven Pass/Fail Calculation* | Derive pass/fail status (`<= 4.0`) and parse absence codes (`na`, `ta`, `ne`). | `models.ExamResult.status` | `src/utils/gradeOutcome.ts`, `CourseMarksTable.tsx` | `src/utils/gradeOutcome.test.ts`<br/>*(10 test cases)* |
| **US #99859**<br/>*Aggregated Data View: Per-Person History* | View aggregated historical exam records and attempts per student. | `routers/students.py` | `src/components/features/StudentDetail.tsx` | `src/utils/studentTranscript.test.ts` |
| **US #96055**<br/>*Categorize Exam Attempts & Missing Programs* | Attempt categorization (`Exam 1`/`2`/`Other`) and graceful study program fallback. | `models.ExamResult.attempt_type` | `src/components/features/batchUpload/CourseInfoStep.tsx` | `tests/test_api.py`<br/>`src/api/client.test.ts` |
| **BUG #99879**<br/>*Drag and Drop Window Malfunction* | Resolve drag & drop window drop-freeze across browsers. | Input stream handling | `src/components/features/batchUpload/SelectFileStep.tsx` | `src/components/features/batchUpload/SelectFileStep.test.tsx` |
| **BUG #99881**<br/>*Semester Chronological Sorting* | Enforce chronological sorting (Winter/Summer) instead of alphabetical. | `schemas.SemesterEnum` | `src/utils/semester.ts` | `src/utils/semester.test.ts`<br/>*(8 test cases)* |
| **US #95732**<br/>*Upload an Exam Data File* | Upload and parse `.xlsx`, `.csv`, `.tsv`, `.ods` files. | `routers/upload.py` | `src/components/features/batchUpload/` | `tests/test_upload.py` |
| **US #96053**<br/>*Validate Required Fields* | Pre-commit validation of Matrikelnummer, Name, Semester. | `routers/upload.py` | `src/components/features/batchUpload/ReviewStep.tsx` | `tests/test_api.py` |
| **US #99900**<br/>*Display Exams Taken per Semester* | Render distribution count of exams taken by students per semester. | `routers/stats.py` | `src/components/features/ExamsHeatmap.tsx` | `src/components/features/ExamsHeatmap.test.tsx` |
| **US #99895**<br/>*Redirect After Course Import* | Auto-redirect from upload wizard directly to imported course view. | Ingestion response contract | `src/hooks/useAppLogic.tsx` | `uploadRedirect.test.ts` |

---

## 🏛️ Sprint 1 Foundations Traceability (Release v0.1.0-alpha)

| Requirement | Description | Implementation Trace | Test Coverage |
| :--- | :--- | :--- | :--- |
| **Multi-Format Ingestion** | Ingest `.xlsx`, `.csv`, `.tsv`, `.ods` via Pandas. | BE: `routers/upload.py`<br/>FE: `SelectFileStep.tsx` | `tests/test_upload.py` |
| **ACID Archival** | Atomic transaction guarantees zero partial writes on upload errors. | BE: `upload_confirm()` (`db.flush()` + `db.commit()`) | `tests/test_api.py` |
| **Interactive Preview** | AG Grid inline spreadsheet review prior to database commit. | FE: `ReviewStep.tsx` (`AgGridReact`) | `ReviewStep.test.tsx` |
