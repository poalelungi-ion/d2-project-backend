# Traceability Matrix: User Stories -> Code

Maps the agile User Stories and their Acceptance Criteria to the code that
fulfils them.

The system lives in two repositories. Paths below are relative to whichever
repository owns the file:

| Prefix | Repository |
| :--- | :--- |
| no prefix, e.g. `routers/upload.py` | `d2-project-backend` (this one) |
| `client:`, e.g. `client:src/App.tsx` | `d2-project-client` |

---

We ensure strict traceability between your product User Stories, Acceptance Criteria, and the exact lines of code that fulfill them.

### User Story 1: File Upload & Format Support
> **Story:** "As a lecturer, I want to upload an exam data file (.xlsx, .csv, .tsv, .ods) so its contents can be processed."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Successful upload & parsing of various formats | **Backend:** `routers/upload.py`. The `/api/upload/preview/` endpoint dynamically loads files into memory using `pandas.read_excel()` (with the `odfpy` engine for `.ods`) or `pandas.read_csv()` based on the file extension. |
| **AC2:** Handle unreadable/failed uploads with feedback | **Frontend:** `client:src/hooks/useAppLogic.tsx`. The `handleUploadSubmit` function catches HTTP 400/500 errors and triggers a clear, red MUI Toast notification (e.g., "Error: Unsupported file format"). |

### User Story 2: Data Validation & Incomplete Records
> **Story:** "As a lecturer, I want each imported record to be checked for required fields so that incomplete records are visible before archive entry."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **Validation Engine:** Check Matrikelnummer, Name, Semester | **Backend:** `/api/upload/preview/` parses raw rows and runs them through a strict dictionary mapping. It compiles a list of missing keys (e.g., `if not str(row.get('first_name')).strip(): missing.append('First Name')`). Study Program is deliberately **not** in this list -- see User Story 7. |
| **AC1:** Complete records are accepted | **Backend & Frontend:** Rows with `len(missing) == 0` receive an `is_valid = True` boolean. The UI renders these with a standard background. |
| **AC2:** Missing fields are explicitly flagged & named | **Frontend:** The `AgGridReact` table uses `getRowStyle` to apply a warning background to `is_valid == false` rows. A dedicated cellRenderer outputs the exact missing fields: `<span style={{color: '#d32f2f'}}>Missing: {params.value.join(', ')}</span>`. |

### User Story 3: Interactive Preview & Edge Cases
> **Story:** "As a lecturer, I want to preview imported records in an interactive table before saving, to identify and review issues."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Data presented in an interactive table | **Frontend:** Step 4 implements `AgGridReact`. All columns have `editable: true` enabled, allowing immediate inline correction of typos. |
| **AC3:** Handle "Approved absence" edge cases ("na"/"ta") | **Frontend:** The grid's `onGridReady` hook explicitly searches for `['na', 'ta', 'ne']` grades and automatically deselects them. The `onRowSelected` hook intercepts intentional manual checks by the teacher and instantly overrides the cell value to `5.0`. |
| **AC4:** Post-Import Confirmation Screen | **Frontend:** After the `POST /confirm/` promise resolves successfully, React state advances to `setActiveStep(4)`, rendering the Success Modal and a global success Toast. |

### User Story 4: Permanent Archive & No Partial Saves
> **Story:** "As a lecturer, I want to save a reviewed import permanently. No partial saves on failure."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Successful save permanently stores data | **Backend:** The `upload_confirm()` function maps the frontend JSON payload directly into `models.ExamResult`, `models.Student`, and `models.Course` SQLAlchemy objects. |
| **AC2:** No partial saves (Atomic Transactions) | **Backend:** The processing loop relies strictly on `db.flush()` to prepare rows. A single `db.commit()` is called at the very end of the function. If an exception triggers, a `db.rollback()` executes, guaranteeing ACID compliance and zero partial data corruption. |


### User Story 5: Student Profile Creation & Editing
> **Story:** "As a lecturer, I want to create new student profiles and edit existing ones so that their academic records and information remain accurate and up to date."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Unified Form UI & Validation (First Name, Last Name, ID, Program) | **Frontend:** `client:src/components/forms/StudentFormDialog.tsx` renders a single `Dialog`, opened by `openStudentForm()` and validated by `validateStudentForm()` in `client:src/hooks/useAppLogic.tsx`. It explicitly splits a standard 'Name' into 'First Name' and 'Last Name' in the UI. |
| **AC2:** Profile Creation (POST) | **Backend & Frontend:** `handleSaveStudent()` fires a POST to `/api/students/` when `studentFormMode === 'create'`. Upon success, triggers the exact `"Student profile created"` Toast and invokes `fetchData()`. |
| **AC3:** Profile Editing (PUT/PATCH) | **Backend & Frontend:** The edit pencil pre-populates the form. `handleSaveStudent()` fires a PUT to `/api/students/{id}`. Triggers `"Student profile updated"` Toast and invokes `fetchData()`. |
| **AC4:** Backend Processing, Token Auth & 409 Conflict | **Backend:** these endpoints require a signed-in user -- `src/router/router.py` includes the student router with `dependencies=[Depends(get_current_user)]` (see User Story 9). Both endpoints execute a database check on `student_id` and raise an `HTTPException(409)` if it exists, which the UI cleanly catches. |


### User Story 6: Visual Analytics Dashboard
> **Story:** "As a user, I want to view a dashboard with students and all relevant information, historical trends, and comparative grading metrics."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Longitudinal Trend (Line Chart) | **Frontend:** Implemented using `Recharts LineChart`. Aggregates average grades per semester from `analyticsStudentTranscript` via the `getLongitudinalData()` helper. Triggered when a student is selected in the Analysis Hub. |
| **AC2:** Comparative Grade Curve (Histogram) | **Frontend:** Implemented using `Recharts BarChart`. Aggregates grades from `selectedCourse.marks` via `getGradeDistributionData()`. Highlights the selected student's specific grade using conditional `Cell` filling (orange vs blue). |
| **AC3:** Grade Distribution (Count) | **Frontend:** Handled inherently by the Histogram in AC2, counting exact frequency per grade bracket. |
| **AC4:** Pass vs. Fail Breakdown (Donut/Pie Chart) | **Frontend:** Implemented using `Recharts PieChart`. Aggregates pass/fail booleans from `selectedCourse.marks` via the `getPassFailData()` helper. |


### User Story 7: Attempt Type & Graceful Study Program Handling
> **Story:** "As a Lecturer, I want to categorize my uploads by exam attempt and have the system gracefully handle missing study program data, so that my valid records aren't rejected due to minor missing fields."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Attempt Type dropdown (Exam 1 / Exam 2 / Other) | **Frontend:** `client:src/components/features/batchUpload/CourseInfoStep.tsx` renders an MUI `Select` over the `ATTEMPT_TYPES` list. The choice lives in wizard state as `UploadCourseInfo.attemptType` (`client:src/types.ts`, defaulted to `'Exam 1'` in `UploadWizardProvider.tsx`) and is sent by `confirmImport()` in `client:src/hooks/useApi.ts`. |
| **AC2:** Attempt Type saved for every student record in the upload | **Backend:** `models.ExamResult.attempt_type` stores it per result; `upload_confirm` in `routers/upload.py` passes `attempt_type=req.attemptType` when building each `ExamResult`, so one dropdown choice tags the whole batch. `schemas.AttemptType` restricts the value to the three allowed strings (422 otherwise) and defaults to `"Other"` for callers predating the dropdown. |
| **AC3:** An empty Study Program is not a validation error | **Backend:** the `missing.append('Study Program')` check was removed from `/api/upload/preview/`, so such rows keep `is_valid = True`. **Frontend:** those rows are therefore neither red-flagged by `getRowStyle` nor skipped by the auto-select in `ReviewStep.tsx`, and `MapColumnsStep.tsx` lists Study program as `optional`. |
| **AC4:** Empty study programs stored as `"Unassigned / Unknown"` | **Backend:** `routers/upload.py` defines `UNASSIGNED_PROGRAM` and applies it twice -- in `/api/upload/preview/`, so the review grid shows exactly what will be saved, and again in `upload_confirm` when creating the `Student`, since the grid is editable and the field can be cleared after preview. |
| **Visibility:** the saved attempt is readable back | **Backend:** `get_student_details` in `routers/students.py` returns `attempt_type` on each transcript entry. **Frontend:** `transcriptColumns` (`client:src/components/features/columns.tsx`) renders it as the read-only **Exam** column of the Personal Transcript grid, beside the derived **Attempt #** counter. |
| **Schema evolution** | **Backend:** the project has no migration tool and `create_all` never alters existing tables, so `database.ensure_schema()` adds post-release columns (`exam_results.attempt_type`) to an already-deployed database. It is idempotent and runs from `main.py` on startup. |

### User Story 8: Course-Scoped Exam Data Upload
> **Story:** "As a Lecturer, I want to initiate exam data uploads directly from within a specific Course tab, so that the system automatically knows which course the data belongs to without me typing it."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** The "Upload Exam Data" button lives inside the Course view | **Frontend:** `client:src/components/features/CourseDetail.tsx` renders it in the course header beside Archive/Restore. It navigates to `ROUTES.upload` carrying `{ courseId, courseName }` as react-router location state. |
| **AC2:** The active `course_id` is grabbed from the page and attached to the upload | **Frontend:** `courseHandoff()` in `client:src/components/features/batchUpload/BatchUploadWizard.tsx` narrows that state and hands it to `UploadWizardProvider`, which seeds `UploadCourseInfo.courseId` (and, since a course's id is its course number, `courseNumber`). `confirmImport()` in `client:src/hooks/useApi.ts` sends it as `courseId`. The `CourseInfoStep` shows the course read-only when `courseLocked` is true, so it cannot be edited into a different course. **Backend:** `resolve_course()` in `src/services/ingestion.py` looks the course up by primary key when `UploadConfirmRequest.courseId` is set (`src/router/dto/upload_dto.py`), so the batch attaches to exactly that course instead of being matched — or newly created — by name. An unknown id is a 404 with nothing written. |
| **AC3:** A `course_number` / `course_id` column in the file is completely ignored | **Backend:** `src/services/ingestion.py` defines `COURSE_COLUMN_NAMES` and `is_course_column()`, which normalises a header to its alphanumerics so `course_number`, `Course ID`, `Kursnummer` and friends all match. `_is_dropped_column()` combines it with the existing pass/fail rule, and `preview_upload()` applies it twice: mapping entries naming a course column are filtered out before `df.rename()`, and any surviving column is dropped from the dataframe. |
| **AC4:** No validation error is shown for the `course_number` column | **Backend:** because the column is dropped before the row loop, it never reaches the `missing_fields` checks — rows keep `is_valid = True`. Covered by `test_preview_ignores_course_columns_in_the_file` and `test_preview_ignores_a_mapping_that_targets_a_course_column` in `tests/test_api.py`. **Frontend:** `MapColumnsStep.tsx` and `CourseInfoStep.tsx` state plainly that course columns in the file are ignored. |
| **Standalone wizard unaffected** | The "Batch Upload" nav entry opens the wizard with no handoff, so `courseId` stays `null`, the Course Number / Course Name fields stay editable, and `resolve_course()` falls back to matching by name (`test_confirm_without_a_course_id_still_matches_by_name`). |

### User Story 9: Secure Account Authentication
> **Story:** "As a lecturer, I want to securely authenticate my account so that my course and student data remain protected from unauthorized access."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** The UI provides a secure login form for username and password entry | **Frontend:** `client:src/components/features/auth/LoginForm.tsx` renders the form; the password field is `type="password"` with `autoComplete="current-password"`, so it is masked and never enters the browser's plain-text autofill history. `client:src/components/features/auth/RegisterForm.tsx` is its counterpart for account creation. `validation.ts` flags empty and malformed input before a round trip, and the backend DTOs re-check everything. Covered by `client:src/components/features/auth/LoginForm.test.tsx` and `validation.test.ts`. |
| **AC2:** Passwords are hashed and salted, never stored in plaintext | **Backend:** `src/lib/auth/passwords.py` hashes with bcrypt at `BCRYPT_ROUNDS` (12 by default); each call to `bcrypt.gensalt()` produces a fresh random salt that is carried inside the resulting hash, so two accounts with the same password store different digests. The only password column in the schema is `users.password_hash` (`migrations/versions/0004_add_users_and_refresh_tokens.py`) — there is nothing that could hold a plaintext or reversible value. Input past bcrypt's 72-byte ceiling is rejected by `RegisterRequest` rather than silently truncated. Verified by `test_password_is_stored_as_a_bcrypt_hash_not_plaintext` and `test_equal_passwords_get_different_hashes` in `tests/test_auth.py`. |
| **AC3:** Transmission occurs over HTTPS | **Deferred to deployment.** Nothing in the application code terminates TLS; the reverse proxy in front of it does. What the code contributes is `COOKIE_SECURE` (`src/database/config.py`), which marks the refresh cookie `Secure` so the browser refuses to send it over plain HTTP once the flag is on. Set it to `true` in the same change that puts the site behind HTTPS. |
| **Access tokens** | `src/lib/auth/tokens.py` issues a short-lived (`ACCESS_TOKEN_TTL_MINUTES`) JWT returned in the login response body. The client holds it in a module variable in `client:src/api/client.ts` and nowhere persistent, so it cannot be read back off the machine after the tab closes. |
| **Refresh tokens** | Long-lived (`REFRESH_TOKEN_TTL_DAYS`) and delivered as an `httpOnly` cookie scoped to `/api/auth`, so no script on the page can read it. `refresh_session()` in `src/services/auth.py` rotates it on every use and records each issuance's `jti` in `refresh_tokens` — never the token itself. Replaying a rotated token revokes every session for that account (`test_replaying_a_rotated_token_drops_every_session_for_that_account`). A `typ` claim checked on decode stops a refresh token being replayed as a bearer token (`test_a_refresh_token_is_not_accepted_as_a_bearer_token`). |
| **Protecting the data endpoints** | `src/router/router.py` includes every data router with `dependencies=[Depends(get_current_user)]`, so courses, students, grades, uploads and stats all require a valid access token — including the read endpoints, which were previously open. Applying the guard at inclusion means a newly added endpoint is protected by default. Covered by `test_data_endpoints_refuse_anonymous_requests`. This replaces the former shared `API_TOKEN`, which was compiled into the JavaScript bundle and therefore held by anyone who loaded the page. |
| **University email rule** | `config.UNIVERSITY_EMAIL_DOMAIN` is the single source of truth, enforced by `normalize_university_email()` in `src/router/dto/auth_dto.py`. It compares the part after the final `@` whole, so an address that merely ends with the domain does not pass. `client:src/utils/constants.ts` mirrors it for form feedback only. Covered by `test_registration_rejects_addresses_outside_the_university_domain` and `client:src/utils/constants.test.ts`. |


---

## Code Standards & Readability Pledges




Moving forward, the codebase adheres to the following human-centric design principles:

1. **Self-Documenting Functions:** Complex endpoints (like `upload_confirm`) are broken down into logical, numbered comments (`# 1. Ensure course exists`, `# 2. Process records`) mapping directly to business logic.
2. **Explicit Variable Naming:** We avoid ambiguous abbreviations. (e.g., `uploadCourseInfo` instead of `ucInfo`).
3. **Defensive Programming:** Extensive `try/except` blocks wrap critical backend loops, ensuring the system never crashes ungracefully and always returns clear JSON error messages.
4. **Decoupled Business Logic & Component Modularity:** The frontend is decoupled into purpose-driven React components (`AnalysisHub`, `CoursesAdmin`, `BatchUploadWizard`) with shared state in the `useAppLogic` hook, and reaches the backend only through `client:src/api/`. The backend `main.py` is an entry point only: it creates the app, validates the authentication configuration, applies CORS and mounts the routers, delegating all domain logic to `routers/`. The two halves are separate repositories and meet solely at the HTTP API.
