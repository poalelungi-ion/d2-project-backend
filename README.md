# SPA System Documentation & Traceability Matrix

This document serves as the comprehensive guide mapping our agile User Stories and Requirements directly to the underlying architecture and source code. Our code philosophy prioritizes extreme readability, atomic transactions, and direct traceability to product requirements.

## 1. System Architecture Overview

The system follows a modern decoupled architecture:
* **Frontend Layer**: React.js SPA utilizing Material-UI (MUI) for responsive design and `AgGridReact` for enterprise-grade data handling.
* **Backend Layer**: FastAPI (Python) providing highly concurrent REST endpoints, strict Pydantic schemas for data validation, and SQLAlchemy for ORM.
* **Database Layer**: PostgreSQL database managing relational integrity.
* **Infrastructure**: Dockerized via `docker-compose` for reproducible deployments.

---

## 2. Setup and Execution (Docker)

The easiest way to run the application is using Docker Compose.

### Prerequisites
* Docker and Docker Compose installed.
* Ports `8000`, `5173`, and `5432` available on your local machine.

### Starting the Application
From the root directory of the project, run:
```bash
docker-compose up --build -d
```

* **Frontend:** Accessible at `http://localhost:5173`
* **Backend API Docs (Swagger):** Accessible at `http://localhost:8000/docs`

To view logs:
```bash
docker-compose logs -f
```

To stop the application:
```bash
docker-compose down
```

---

## 3. Traceability Matrix: User Stories -> Code

We ensure strict traceability between your product User Stories, Acceptance Criteria, and the exact lines of code that fulfill them.

### User Story 1: File Upload & Format Support
> **Story:** "As a lecturer, I want to upload an exam data file (.xlsx, .csv, .tsv, .ods) so its contents can be processed."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Successful upload & parsing of various formats | **Backend:** [`backend/main.py`](file:///C:/Users/ionut/Desktop/Project/SPA_System/backend/main.py). The `/api/upload/preview/` endpoint dynamically loads files into memory using `pandas.read_excel()` (with the `odfpy` engine for `.ods`) or `pandas.read_csv()` based on the file extension. |
| **AC2:** Handle unreadable/failed uploads with feedback | **Frontend:** [`frontend/src/App.jsx`](file:///C:/Users/ionut/Desktop/Project/SPA_System/frontend/src/App.jsx). The `handleUploadSubmit` function catches HTTP 400/500 errors and triggers a clear, red MUI Toast notification (e.g., "Error: Unsupported file format"). |

### User Story 2: Data Validation & Incomplete Records
> **Story:** "As a lecturer, I want each imported record to be checked for required fields so that incomplete records are visible before archive entry."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **Validation Engine:** Check Matrikelnummer, Name, Program, Semester | **Backend:** `/api/upload/preview/` parses raw rows and runs them through a strict dictionary mapping. It compiles a list of missing keys (e.g., `if not str(row.get('first_name')).strip(): missing.append('First Name')`). |
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
| **AC1:** Unified Form UI & Validation (First Name, Last Name, ID, Program) | **Frontend:** `App.jsx` uses a single `Dialog` component triggered by `openStudentForm()`. It strictly enforces validation in `validateStudentForm()` and explicitly splits standard 'Name' into 'First Name' and 'Last Name' in the UI. |
| **AC2:** Profile Creation (POST) | **Backend & Frontend:** `handleSaveStudent()` fires a POST to `/api/students/` when `studentFormMode === 'create'`. Upon success, triggers the exact `"Student profile created"` Toast and invokes `fetchData()`. |
| **AC3:** Profile Editing (PUT/PATCH) | **Backend & Frontend:** The edit pencil pre-populates the form. `handleSaveStudent()` fires a PUT to `/api/students/{id}`. Triggers `"Student profile updated"` Toast and invokes `fetchData()`. |
| **AC4:** Backend Processing, Token Auth & 409 Conflict | **Backend:** `main.py` explicitly attaches `Depends(verify_token)` to both `create_student` and `update_student` endpoints. Both endpoints execute a database check on `student_id` and raise an `HTTPException(409)` if it exists, which the UI cleanly catches. |


### User Story 6: Visual Analytics Dashboard
> **Story:** "As a user, I want to view a dashboard with students and all relevant information, historical trends, and comparative grading metrics."

| Requirement / Acceptance Criteria | Code Implementation Trace |
| :--- | :--- |
| **AC1:** Longitudinal Trend (Line Chart) | **Frontend:** Implemented using `Recharts LineChart`. Aggregates average grades per semester from `analyticsStudentTranscript` via the `getLongitudinalData()` helper. Triggered when a student is selected in the Analysis Hub. |
| **AC2:** Comparative Grade Curve (Histogram) | **Frontend:** Implemented using `Recharts BarChart`. Aggregates grades from `selectedCourse.marks` via `getGradeDistributionData()`. Highlights the selected student's specific grade using conditional `Cell` filling (orange vs blue). |
| **AC3:** Grade Distribution (Count) | **Frontend:** Handled inherently by the Histogram in AC2, counting exact frequency per grade bracket. |
| **AC4:** Pass vs. Fail Breakdown (Donut/Pie Chart) | **Frontend:** Implemented using `Recharts PieChart`. Aggregates pass/fail booleans from `selectedCourse.marks` via the `getPassFailData()` helper. |



---

## 4. Code Standards & Readability Pledges




Moving forward, the codebase adheres to the following human-centric design principles:

1. **Self-Documenting Functions:** Complex endpoints (like `upload_confirm`) are broken down into logical, numbered comments (`# 1. Ensure course exists`, `# 2. Process records`) mapping directly to business logic.
2. **Explicit Variable Naming:** We avoid ambiguous abbreviations. (e.g., `uploadCourseInfo` instead of `ucInfo`).
3. **Defensive Programming:** Extensive `try/except` blocks wrap critical backend loops, ensuring the system never crashes ungracefully and always returns clear JSON error messages.
4. **Decoupled Business Logic:** The frontend (`App.jsx`) is strictly responsible for presentation, validation visualization, and state management. The backend (`main.py`) acts as the single source of truth for business logic and data persistence.
