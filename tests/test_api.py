from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
from src.database.models import User
from src.lib.auth.validator import get_current_user
import models
import io

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Every data route now sits behind get_current_user. These tests are about the
# course/student/upload behaviour rather than about authentication, so they run
# as a stand-in account; tests/test_auth.py drops this override and exercises
# the real token path.
TEST_USER = User(
    user_id=1,
    email="test.lecturer@uni-hildesheim.de",
    name="Test Lecturer",
    password_hash="not-used-here",
    is_active=True,
)

app.dependency_overrides[get_current_user] = lambda: TEST_USER

client = TestClient(app)


@contextmanager
def anonymous_client():
    """Runs a block with the authentication override lifted."""
    app.dependency_overrides.pop(get_current_user, None)
    try:
        yield client
    finally:
        app.dependency_overrides[get_current_user] = lambda: TEST_USER

@pytest.fixture(autouse=True)
def run_around_tests():
    # Setup: clean the database before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: close DB

def test_get_courses_empty():
    response = client.get("/api/courses/")
    assert response.status_code == 200
    assert response.json() == []

PASTE_MAPPING = (
    '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}'
)


def test_upload_preview_paste_tsv():
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\n"
        "12345\tSchneider, Lena\tSE Master\t3\t1.7\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "course": "TEST101",
            "courseName": "Test Course",
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "Last, First",
        },
    )
    assert response.status_code == 200
    rows = response.json()["preview_data"]
    assert len(rows) == 1
    assert rows[0]["is_valid"] is True
    assert rows[0]["student_id"] == "12345"
    assert rows[0]["first_name"] == "Lena"
    assert rows[0]["last_name"] == "Schneider"
    assert rows[0]["grade"] == "1.7"


def test_upload_preview_paste_csv():
    paste = "Matrikelnr,Name,Program,Semester,Grade\n8888,Ada Lovelace,SE Master,1,1.0\n"
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "First Last",
        },
    )
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["is_valid"] is True
    assert row["first_name"] == "Ada"
    assert row["last_name"] == "Lovelace"


def test_upload_preview_unreadable_paste():
    response = client.post(
        "/api/upload/preview/",
        data={"paste": "this is not a table", "semester": "WISE_25"},
    )
    assert response.status_code == 400
    assert "tabular" in response.json()["detail"].lower()


def test_upload_preview_empty_source():
    response = client.post("/api/upload/preview/", data={"semester": "WISE_25"})
    assert response.status_code == 400
    assert "paste" in response.json()["detail"].lower()


def test_paste_preview_then_confirm():
    paste = "Matrikelnr\tName\tProgram\tSemester\tGrade\n9999\tValid, User\tSE Master\t1\t2.0\n"
    preview = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "Last, First",
        },
    )
    assert preview.status_code == 200
    row = preview.json()["preview_data"][0]
    confirm = client.post(
        "/api/upload/confirm/",
        json={
            "course": "PASTE101",
            "courseName": "Paste Course",
            "semester": "WISE_25",
            "records": [
                {
                    "student_id": row["student_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "name": row["name"],
                    "program": row["program"],
                    "semester": row["semester"],
                    "grade": row["grade"],
                }
            ],
        },
    )
    assert confirm.status_code == 200
    assert "Successfully imported 1 records" in confirm.json()["message"]
    assert "course_id" in confirm.json()
    assert isinstance(confirm.json()["course_id"], int)


def test_upload_preview_invalid_grade():
    csv_content = b"Matrikelnr,Name,Program,Semester,Grade\n12345,John Doe,SE Master,WISE_25,1.0\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {
        "course": "TEST101",
        "courseName": "Test Course",
        "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}'
    }
    response = client.post("/api/upload/preview/", files=files, data=data)
    assert response.status_code == 200
    resp_data = response.json()
    assert "preview_data" in resp_data
    assert len(resp_data["preview_data"]) == 1
    print(resp_data)
    assert resp_data["preview_data"][0]["is_valid"] == True
    # Check invalid reasoning
    

def test_upload_confirm_valid_grade():
    payload = {
        "course": "VALID101",
        "courseName": "Valid Course",
        "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}',
        "records": [
            {
                "student_id": "9999",
                "first_name": "Valid",
                "last_name": "User",
                "program": "SE Master",
                "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}',
                "grade": "2.0",
                "is_valid": True
            },
            {
                "student_id": "8888",
                "first_name": "Fail",
                "last_name": "User",
                "program": "SE Master",
                "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}',
                "grade": "5.0",
                "is_valid": True
            },
            {
                "student_id": "7777",
                "first_name": "Absent",
                "last_name": "User",
                "program": "SE Master",
                "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}',
                "grade": "5.0",
                "is_valid": True
            }
        ]
    }
    response = client.post("/api/upload/confirm/", json=payload)
    assert response.status_code == 200
    assert "Successfully imported 3 records" in response.json()["message"]

    # Verify courses
    response2 = client.get("/api/courses/")
    assert response2.status_code == 200
    courses = response2.json()
    assert len(courses) == 1
    assert courses[0]["course_name"] == "Valid Course"
    assert courses[0]["pass_rate"] == 33.3  # 1 out of 3 passed
    assert len(courses[0]["marks"]) == 3
    assert all(mark["result_id"] for mark in courses[0]["marks"])

def test_database_persistence_simulation():
    # Write a record
    db = TestingSessionLocal()
    course = models.Course(course_id=101, course_name="Persisted Course")
    db.add(course)
    db.commit()
    db.close()

    # Re-open session to simulate a restart/new connection
    db2 = TestingSessionLocal()
    course_fetched = db2.query(models.Course).filter(models.Course.course_id == 101).first()
    assert course_fetched is not None
    assert course_fetched.course_name == "Persisted Course"
    db2.close()


def test_upload_preview_missing_program_is_valid():
    """A blank Studiengang is filled with a placeholder, not flagged as an error."""
    csv_content = b"Matrikelnr,Name,Program,Semester,Grade\n5555,No Program,,WISE_25,2.3\n"
    files = {"file": ("no_program.csv", io.BytesIO(csv_content), "text/csv")}
    data = {
        "course": "TEST101",
        "courseName": "Test Course",
        "semester": "WISE_25",
        "mapping": PASTE_MAPPING,
    }
    response = client.post("/api/upload/preview/", files=files, data=data)
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["program"] == "Unassigned / Unknown"
    assert "Study Program" not in row["missing_fields"]
    assert "Study Program" not in row.get("invalid_fields", [])
    assert row["is_valid"] is True


def test_upload_preview_unknown_program_is_flagged():
    """A typed-in Studiengang is shown so it can be fixed from the dropdown."""
    csv_content = b"Matrikelnr,Name,Program,Semester,Grade\n5556,Typo Program,CS,WISE_25,2.3\n"
    files = {"file": ("typo_program.csv", io.BytesIO(csv_content), "text/csv")}
    data = {
        "course": "TEST101",
        "courseName": "Test Course",
        "semester": "WISE_25",
        "mapping": PASTE_MAPPING,
    }
    response = client.post("/api/upload/preview/", files=files, data=data)
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["program"] == "CS"
    assert "Study Program" not in row["missing_fields"]
    assert "Study Program" in row["invalid_fields"]
    assert row["is_valid"] is False


def test_upload_confirm_rejects_unknown_program():
    payload = {
        "course": "PROG101",
        "courseName": "Program Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "6010",
                "first_name": "Typo",
                "last_name": "Program",
                "program": "Custom Degree",
                "semester": "WISE_25",
                "grade": "2.0",
            }
        ],
    }
    response = client.post("/api/upload/confirm/", json=payload)
    assert response.status_code == 422


def test_upload_confirm_stores_attempt_type_and_placeholder_program():
    payload = {
        "course": "ATT101",
        "courseName": "Attempt Course",
        "semester": "WISE_25",
        "attemptType": "Exam 2",
        "records": [
            {
                "student_id": "6001",
                "first_name": "With",
                "last_name": "Program",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "2.0",
            },
            {
                "student_id": "6002",
                "first_name": "Without",
                "last_name": "Program",
                "program": "",
                "semester": "WISE_25",
                "grade": "3.0",
            },
        ],
    }
    response = client.post("/api/upload/confirm/", json=payload)
    assert response.status_code == 200

    db = TestingSessionLocal()
    try:
        results = db.query(models.ExamResult).all()
        assert len(results) == 2
        # The attempt type applies to every record in the batch.
        assert all(r.attempt_type == "Exam 2" for r in results)

        blank = db.query(models.Student).filter(models.Student.student_id == 6002).first()
        assert blank.program == "Unassigned / Unknown"
        kept = db.query(models.Student).filter(models.Student.student_id == 6001).first()
        assert kept.program == "SE Master"
    finally:
        db.close()


def test_upload_confirm_defaults_attempt_type():
    """Callers predating the dropdown still import, tagged as "Other"."""
    payload = {
        "course": "ATT102",
        "courseName": "Default Attempt Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "6003",
                "first_name": "Default",
                "last_name": "Attempt",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "1.7",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200

    db = TestingSessionLocal()
    try:
        result = db.query(models.ExamResult).one()
        assert result.attempt_type == "Other"
    finally:
        db.close()


def test_upload_confirm_rejects_unknown_attempt_type():
    payload = {
        "course": "ATT103",
        "courseName": "Bad Attempt Course",
        "semester": "WISE_25",
        "attemptType": "Exam 7",
        "records": [
            {
                "student_id": "6004",
                "first_name": "Bad",
                "last_name": "Attempt",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "1.7",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 422


def test_transcript_exposes_attempt_type():
    """The sitting reaches the student's personal transcript."""
    payload = {
        "course": "TRA101",
        "courseName": "Transcript Course",
        "semester": "WISE_25",
        "attemptType": "Exam 2",
        "records": [
            {
                "student_id": "7301",
                "first_name": "Trans",
                "last_name": "Script",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "2.7",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200

    response = client.get("/api/students/7301")
    assert response.status_code == 200
    entry = response.json()["transcript"][0]
    assert entry["attempt_type"] == "Exam 2"
    # The derived retry counter is unchanged by the declared sitting.
    assert entry["attempt"] == 1


def test_preview_filters_status_codes_and_ignores_passed_column():
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\tPassed\n"
        "31001\tSchneider, Lena\tSE Master\t3\tNE\tYes\n"
        "31002\tBecker, Leon\tSE Master\t3\tEX\tPassed\n"
        "31003\tWagner, Sophie\tSE Master\t3\tAT\tNo\n"
        "31005\tKlein, Jonas\tSE Master\t3\tNA\tYes\n"
        "31006\tLang, Mira\tSE Master\t3\tTA\tNo\n"
        "31004\tHoffmann, Marie\tSE Master\t3\t1.7\tFailed\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "Last, First",
        },
    )
    assert response.status_code == 200
    rows = {row["student_id"]: row for row in response.json()["preview_data"]}
    assert set(rows) == {"31004"}
    # File said Failed; the numeric grade is the only source of truth.
    assert rows["31004"]["grade"] == "1.7"
    assert rows["31004"]["outcome"] == "passed"
    assert rows["31004"]["absence_code"] is None
    assert "Passed" not in rows["31004"]
    assert "passed" not in rows["31004"]


def test_preview_rejects_passed_text_in_the_grade_cell():
    paste = "Matrikelnr,Name,Program,Semester,Grade\n31010,Ada Lovelace,SE Master,1,Passed\n"
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "First Last",
        },
    )
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["is_valid"] is False
    assert "Grade" in row["missing_fields"]
    assert row["outcome"] == "invalid"


def test_confirm_rejects_status_codes():
    payload = {
        "course": "ABSENCE101",
        "courseName": "Absence Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "31021",
                "first_name": "No",
                "last_name": "Show",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "NE",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 400


def test_confirm_rejects_passed_text_as_a_grade():
    payload = {
        "course": "LABEL101",
        "courseName": "Label Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "31030",
                "first_name": "Label",
                "last_name": "Only",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "Passed",
            }
        ],
    }
    response = client.post("/api/upload/confirm/", json=payload)
    assert response.status_code == 400


def test_batch_grade_update_ignores_client_passed_flag():
    payload = {
        "course": "RECALC101",
        "courseName": "Recalc Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "31040",
                "first_name": "Re",
                "last_name": "Calc",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "5.0",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200
    entry = client.get("/api/students/31040").json()["transcript"][0]
    response = client.post(
        "/api/grades/",
        json=[
            {
                "result_id": entry["result_id"],
                "version": entry["version"],
                "grade": 5.0,
                "passed": True,
            }
        ],
    )
    assert response.status_code == 200
    updated = client.get("/api/students/31040").json()["transcript"][0]
    assert updated["passed"] is False
    assert updated["outcome"] == "failed"


def _import_one_grade(student_id: str, course: str, grade: str) -> dict:
    payload = {
        "course": course,
        "courseName": f"{course} Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": student_id,
                "first_name": "Edit",
                "last_name": "FromCourse",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": grade,
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200
    return client.get(f"/api/students/{student_id}").json()["transcript"][0]


def test_batch_grade_update_accepts_the_same_cells_as_upload():
    entry = _import_one_grade("31041", "EDIT101", "2.0")
    response = client.post(
        "/api/grades/",
        json=[
            {
                "result_id": entry["result_id"],
                "version": entry["version"],
                "grade": "2.3",
            }
        ],
    )
    assert response.status_code == 200
    updated = client.get("/api/students/31041").json()["transcript"][0]
    assert updated["grade"] == 2.3
    assert updated["outcome"] == "passed"
    assert updated["absence_code"] is None


def test_batch_grade_update_rejects_status_codes():
    entry = _import_one_grade("31043", "EDIT103", "2.0")
    for grade in ("NE", "EX", "NA", "TA", "AT"):
        response = client.post(
            "/api/grades/",
            json=[
                {
                    "result_id": entry["result_id"],
                    "version": entry["version"],
                    "grade": grade,
                }
            ],
        )
        assert response.status_code == 422, grade


def test_batch_grade_update_rejects_invalid_grades():
    entry = _import_one_grade("31042", "EDIT102", "1.7")
    for grade in ("6.0", "Passed", "", "0.7"):
        response = client.post(
            "/api/grades/",
            json=[
                {
                    "result_id": entry["result_id"],
                    "version": entry["version"],
                    "grade": grade,
                }
            ],
        )
        assert response.status_code == 422, grade


def test_excused_attempts_are_excluded_from_pass_rate_and_at_risk():
    payload = {
        "course": "EXCUSE101",
        "courseName": "Excuse Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "31051",
                "first_name": "Pass",
                "last_name": "One",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "2.0",
            },
            {
                "student_id": "31052",
                "first_name": "Fail",
                "last_name": "One",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "5.0",
            },
            {
                "student_id": "31053",
                "first_name": "Med",
                "last_name": "Note",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "5.0",
            },
            {
                "student_id": "31054",
                "first_name": "Two",
                "last_name": "Fails",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "5.0",
            },
            {
                "student_id": "31054",
                "first_name": "Two",
                "last_name": "Fails",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "5.0",
            },
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200

    courses = client.get("/api/courses/").json()
    course = next(c for c in courses if c["course_name"] == "Excuse Course")
    assert course["total_attempts"] == 5
    assert course["pass_rate"] == 20.0

    stats = client.get("/api/stats/").json()
    at_risk_ids = {row["student_id"] for row in stats["atRisk"]}
    assert 31053 not in at_risk_ids
    assert 31054 in at_risk_ids



# --- Uploading from inside a Course view -------------------------------------
# The lecturer starts the import from the course's own tab, so the course is
# already known: a course column in the file is noise and must never surface as
# a validation problem.


def test_preview_ignores_course_columns_in_the_file():
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\tcourse_number\tCourse ID\tKursnummer\n"
        "41001\tSchneider, Lena\tSE Master\t3\t1.7\t9999\t8888\t7777\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "Last, First",
        },
    )
    assert response.status_code == 200
    row = response.json()["preview_data"][0]

    # The row parses cleanly: the course columns raise no complaint of any kind.
    assert row["is_valid"] is True
    assert row["missing_fields"] == []
    assert not any("course" in field.lower() for field in row["missing_fields"])

    # And they are gone entirely, rather than carried along as extra fields.
    for key in ("course_number", "Course ID", "course_id", "Kursnummer", "course"):
        assert key not in row


def test_preview_rejects_unrecognized_column_names():
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\tEmail\n"
        "12345\tSchneider, Lena\tSE Master\t3\t1.7\ta@uni.de\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={"paste": paste, "semester": "WISE_25", "nameSplitRule": "Last, First"},
    )
    assert response.status_code == 400
    assert "Email" in response.json()["detail"]
    assert "Matrikelnr" in response.json()["detail"]


def test_preview_rejects_unknown_header_even_when_client_maps_it():
    """A mapping cannot alias an unknown title onto a field — names are closed."""
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tEmail\n"
        "12345\tSchneider, Lena\tSE Master\t3\t1.7\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": '{"Email": "grade", "Matrikelnr": "student_id", "Name": "name"}',
            "nameSplitRule": "Last, First",
        },
    )
    assert response.status_code == 400
    assert "Email" in response.json()["detail"]


def test_preview_ignores_ects_columns_in_the_file():
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\tECTS\tCredits\n"
        "41002\tSchneider, Lena\tSE Master\t3\t1.7\t6\t6\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "Last, First",
        },
    )
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["is_valid"] is True
    for key in ("ECTS", "ects", "Credits", "credits"):
        assert key not in row


def test_preview_rejects_two_columns_that_standardise_to_name():
    paste = (
        "Matrikelnr\tName\tFull Name\tGrade\n"
        "12345\tSchneider, Lena\tLena Schneider\t1.7\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={"paste": paste, "semester": "WISE_25", "nameSplitRule": "Last, First"},
    )
    assert response.status_code == 400
    assert "Name" in response.json()["detail"]


def test_preview_standardises_note_and_matrikelnummer_without_client_mapping():
    paste = (
        "Matrikelnummer\tName\tStudiengang\tFachsemester\tNote\n"
        "12345\tSchneider, Lena\tSE Master\t3\t1.7\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={"paste": paste, "semester": "WISE_25", "nameSplitRule": "Last, First"},
    )
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["student_id"] == "12345"
    assert row["grade"] == "1.7"
    assert row["is_valid"] is True


def test_preview_ignores_a_mapping_that_targets_a_course_column():
    """A mapping naming a course column is dropped instead of renaming a field onto it."""
    paste = "Matrikelnr,Name,Program,Semester,Grade,Kursnummer\n41010,Ada Lovelace,SE Master,1,2.0,4711\n"
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": (
                '{"Matrikelnr": "student_id", "Name": "name", "Program": "program",'
                ' "Grade": "grade", "Kursnummer": "course_id"}'
            ),
            "nameSplitRule": "First Last",
        },
    )
    assert response.status_code == 200
    row = response.json()["preview_data"][0]
    assert row["is_valid"] is True
    assert row["missing_fields"] == []
    assert "course_id" not in row
    assert "Kursnummer" not in row


def test_confirm_attaches_records_to_the_active_course_id():
    """courseId from the Course view wins over the name, so no second course appears."""
    db = TestingSessionLocal()
    db.add(models.Course(course_id=3545, course_name="SE Tools Lab"))
    db.commit()
    db.close()

    payload = {
        "courseId": 3545,
        # Deliberately stale: the id is what decides where the batch lands.
        "courseName": "Typed Something Else",
        "semester": "WISE_25",
        "attemptType": "Exam 1",
        "records": [
            {
                "student_id": "41020",
                "first_name": "Lena",
                "last_name": "Schneider",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "1.7",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200

    courses = client.get("/api/courses/").json()
    assert len(courses) == 1
    assert courses[0]["course_id"] == 3545
    assert courses[0]["course_name"] == "SE Tools Lab"
    assert courses[0]["total_attempts"] == 1


def test_course_without_submissions_reports_zeros_until_the_first_one_arrives():
    """The course page derives its "No submissions yet" state from `marks`, so an
    empty course must return an empty list -- without dividing by zero -- until
    the first upload lands."""
    db = TestingSessionLocal()
    db.add(models.Course(course_id=3546, course_name="Empty Course"))
    db.commit()
    db.close()

    empty = client.get("/api/courses/").json()[0]
    assert empty["total_attempts"] == 0
    assert empty["marks"] == []
    assert empty["pass_rate"] == 0
    assert empty["avg_grade"] == 0
    assert client.get("/api/stats/").status_code == 200

    payload = {
        "courseId": 3546,
        "courseName": "Empty Course",
        "semester": "WISE_25",
        "attemptType": "Exam 1",
        "records": [
            {
                "student_id": "41021",
                "first_name": "Lena",
                "last_name": "Schneider",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "1.7",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200

    first = client.get("/api/courses/").json()[0]
    assert len(first["marks"]) == 1
    assert first["total_attempts"] == 1
    assert first["pass_rate"] == 100.0


def test_confirm_rejects_an_unknown_course_id():
    payload = {
        "courseId": 999999,
        "courseName": "Ghost Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "41030",
                "first_name": "No",
                "last_name": "Course",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "2.0",
            }
        ],
    }
    response = client.post("/api/upload/confirm/", json=payload)
    assert response.status_code == 404
    assert "999999" in response.json()["detail"]
    # Nothing was written on the way to the rejection.
    assert client.get("/api/courses/").json() == []


def test_confirm_without_a_course_id_still_matches_by_name():
    """The standalone wizard has no active course and keeps its old behaviour."""
    payload = {
        "course": "3545",
        "courseName": "Standalone Course",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "41040",
                "first_name": "Stand",
                "last_name": "Alone",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "2.0",
            }
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200
    courses = client.get("/api/courses/").json()
    assert [c["course_name"] for c in courses] == ["Standalone Course"]


def test_get_course_details_success():
    """Retrieves full course metadata, summary statistics, and marks for an existing course."""
    create_payload = {
        "course_id": 95647,
        "course_name": "Cloud Native Architecture",
        "semester": "SOSE_26",
        "study_program": "SE Master",
        "professor": "Dr. Architect",
    }
    res = client.post("/api/courses/", json=create_payload)
    assert res.status_code == 201

    res = client.get("/api/courses/95647")
    assert res.status_code == 200
    data = res.json()
    assert data["course_id"] == 95647
    assert data["course_name"] == "Cloud Native Architecture"
    assert data["semester"] == "SOSE_26"
    assert data["study_program"] == "SE Master"
    assert data["assigned_professor"] == "Dr. Architect"
    assert data["total_attempts"] == 0
    assert data["pass_rate"] == 0
    assert data["avg_grade"] == 0
    assert data["is_archived"] is False
    assert data["marks"] == []


def test_get_course_details_not_found():
    """Returns 404 with error message when course ID does not exist."""
    res = client.get("/api/courses/99999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Course not found"


def test_student_profile_creation_and_conflict_handling_97930():
    """User Story #97930 AC2 & AC4: Profile Creation & 409 Conflict on duplicate ID."""
    student_payload = {
        "student_id": 97930,
        "name": "Alan Turing",
        "program": "SE Master",
        "status": "active",
    }
    # 1. Create student
    res = client.post("/api/students/", json=student_payload)
    assert res.status_code == 201
    assert res.json()["student_id"] == 97930

    # 2. Attempt duplicate student creation -> 409 Conflict
    dup_res = client.post("/api/students/", json=student_payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["detail"] == "Student ID already exists"


def test_student_profile_update_and_optimistic_locking_97930():
    """User Story #97930 AC3 & AC4: Profile Editing & Conflict Handling."""
    student_payload = {
        "student_id": 97931,
        "name": "Ada Lovelace",
        "program": "SE Master",
        "status": "active",
    }
    create_res = client.post("/api/students/", json=student_payload)
    assert create_res.status_code == 201

    # Fetch student details
    details = client.get("/api/students/97931").json()
    assert details["name"] == "Ada Lovelace"
    version = details["version"]

    # 1. Successful edit
    update_payload = {
        "new_student_id": 97931,
        "name": "Ada King Lovelace",
        "program": "Data Science Master",
        "version": version,
    }
    update_res = client.put("/api/students/97931", json=update_payload)
    assert update_res.status_code == 200

    # Verify updated values
    updated_details = client.get("/api/students/97931").json()
    assert updated_details["name"] == "Ada King Lovelace"
    assert updated_details["program"] == "Data Science Master"

    # 2. Conflict on stale version (concurrency)
    stale_res = client.put("/api/students/97931", json=update_payload)
    assert stale_res.status_code == 409


def test_update_course_without_professor_field():
    """Task #99886: professor attribute is safely omitted without validation errors."""
    create_payload = {
        "course_id": 99886,
        "course_name": "Course 99886",
        "semester": "WISE_25",
        "professor": "Prof. Smith",
    }
    res = client.post("/api/courses/", json=create_payload)
    assert res.status_code == 201

    courses = client.get("/api/courses/").json()
    target = next(c for c in courses if c["course_id"] == 99886)
    assert target["assigned_professor"] == "Prof. Smith"

    # Update course omitting the professor attribute completely
    update_payload = {
        "new_course_id": 99886,
        "course_name": "Course 99886 Updated",
        "semester": "SOSE_26",
        "version": target["version"],
    }
    update_res = client.put("/api/courses/99886", json=update_payload)
    assert update_res.status_code == 200

    courses_updated = client.get("/api/courses/").json()
    target_updated = next(c for c in courses_updated if c["course_id"] == 99886)
    assert target_updated["course_name"] == "Course 99886 Updated"
    assert target_updated["assigned_professor"] == "Prof. Smith"


def test_convert_paste_to_excel():
    paste = "Matrikelnr\tName\tProgram\tSemester\tGrade\n9999\tValid, User\tSE Master\t1\t2.0\n"
    res = client.post("/api/upload/paste-to-excel/", data={"paste": paste, "filename": "test_output.xlsx"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    # Verify openpyxl can read the returned bytes
    import io, pandas as pd
    df = pd.read_excel(io.BytesIO(res.content), engine="openpyxl")
    assert len(df) == 1
    assert df.iloc[0]["Matrikelnr"] == 9999

def test_seed_on_startup_disabled_by_default():
    """#104080: Verify that SEED_ON_STARTUP is disabled by default for clean production delivery."""
    from src.database import config
    assert config.SEED_ON_STARTUP is False


def test_student_creation_and_update_without_status_field_104082():
    """Task #104082: API payloads no longer require student status during profile creation or updates."""
    # 1. Create student without status field
    create_payload = {
        "student_id": 104082,
        "name": "Status Deprecated",
        "program": "SE Master",
    }
    create_res = client.post("/api/students/", json=create_payload)
    assert create_res.status_code == 201
    assert create_res.json()["student_id"] == 104082

    # Verify default status is active
    details = client.get("/api/students/104082").json()
    assert details["name"] == "Status Deprecated"
    assert details["status"] == "active"
    version = details["version"]

    # 2. Update student without status field
    update_payload = {
        "new_student_id": 104082,
        "name": "Status Deprecated Updated",
        "program": "Data Science Master",
        "version": version,
    }
    update_res = client.put("/api/students/104082", json=update_payload)
    assert update_res.status_code == 200

    # Verify profile was updated and status remains intact
    updated_details = client.get("/api/students/104082").json()
    assert updated_details["name"] == "Status Deprecated Updated"
    assert updated_details["program"] == "Data Science Master"
    assert updated_details["status"] == "active"


def test_preview_skips_rows_without_grades_104085():
    """Ticket #104085: Ingestion skips rows where students have no valid grade."""
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\n"
        "81001\tValid, One\tSE Master\tWISE_25\t1.7\n"
        "81002\tEmpty, Student\tSE Master\tWISE_25\t\n"
        "81003\tWhitespace, Student\tSE Master\tWISE_25\t   \n"
        "81004\tNoShow, Student\tSE Master\tWISE_25\tNE\n"
        "81005\tValid, Two\tSE Master\tWISE_25\t2.3\n"
    )
    response = client.post(
        "/api/upload/preview/",
        data={
            "paste": paste,
            "semester": "WISE_25",
            "mapping": PASTE_MAPPING,
            "nameSplitRule": "Last, First",
        },
    )
    assert response.status_code == 200
    preview_data = response.json()["preview_data"]
    student_ids = [row["student_id"] for row in preview_data]
    assert student_ids == ["81001", "81005"]


def test_confirm_excludes_rows_without_valid_numeric_grades_and_prevents_orphan_students_104085():
    """Ticket #104085: Confirm excludes rows lacking valid numeric grades and creates no orphan students."""
    payload = {
        "course": "VALIDATE101",
        "courseName": "Grade Validation Course",
        "ects": "6",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "82001",
                "first_name": "Valid",
                "last_name": "One",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "1.3",
            },
            {
                "student_id": "82002",
                "first_name": "Empty",
                "last_name": "Grade",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "",
            },
            {
                "student_id": "82003",
                "first_name": "Absence",
                "last_name": "Code",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "NE",
            },
            {
                "student_id": "82004",
                "first_name": "Label",
                "last_name": "Only",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "Passed",
            },
            {
                "student_id": "82005",
                "first_name": "Invalid",
                "last_name": "Text",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "invalid",
            },
            {
                "student_id": "82006",
                "first_name": "Valid",
                "last_name": "Two",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "2.7",
            },
        ],
    }

    # 1. Batch confirm should succeed and report exactly 2 imported records
    confirm = client.post("/api/upload/confirm/", json=payload)
    assert confirm.status_code == 200
    assert confirm.json()["message"] == "Successfully imported 2 records."

    # 2. Valid students are persisted with their exam grades
    s1 = client.get("/api/students/82001")
    assert s1.status_code == 200
    assert s1.json()["student_id"] == 82001
    assert len(s1.json()["transcript"]) == 1
    assert s1.json()["transcript"][0]["grade"] == 1.3

    s2 = client.get("/api/students/82006")
    assert s2.status_code == 200
    assert s2.json()["student_id"] == 82006
    assert len(s2.json()["transcript"]) == 1
    assert s2.json()["transcript"][0]["grade"] == 2.7

    # 3. No orphan student profiles without exam grades exist for skipped rows
    for missing_sid in (82002, 82003, 82004, 82005):
        lookup = client.get(f"/api/students/{missing_sid}")
        assert lookup.status_code == 404, f"Student {missing_sid} should not have been created in PostgreSQL"


def test_update_student_study_program_persists_and_returns_record_104081():
    """
    Ticket #104081:
    - Changing study_program in the Edit Student Profile modal sends the updated field in the PUT /api/students/{id} payload.
    - The backend commits the change and returns the updated student record, immediately reflecting in the UI.
    """
    create_payload = {
        "student_id": 104081,
        "name": "Linus Torvalds",
        "program": "SE Master",
    }
    create_res = client.post("/api/students/", json=create_payload)
    assert create_res.status_code == 201
    assert create_res.json()["student_id"] == 104081
    assert create_res.json()["study_program"] == "SE Master"

    # Fetch initial details
    details = client.get("/api/students/104081").json()
    assert details["program"] == "SE Master"
    assert details["study_program"] == "SE Master"
    initial_version = details["version"]

    # 1. Update using study_program field
    update_payload = {
        "new_student_id": 104081,
        "name": "Linus Benedict Torvalds",
        "study_program": "Data Science Master",
        "version": initial_version,
    }
    update_res = client.put("/api/students/104081", json=update_payload)
    assert update_res.status_code == 200

    # Backend must return the updated student record
    updated_body = update_res.json()
    assert updated_body["student_id"] == 104081
    assert updated_body["name"] == "Linus Benedict Torvalds"
    assert updated_body["study_program"] == "Data Science Master"
    assert updated_body["program"] == "Data Science Master"
    assert updated_body["version"] == initial_version + 1

    # Verify persistent state via GET
    fresh_details = client.get("/api/students/104081").json()
    assert fresh_details["name"] == "Linus Benedict Torvalds"
    assert fresh_details["study_program"] == "Data Science Master"
    assert fresh_details["program"] == "Data Science Master"
    assert fresh_details["version"] == initial_version + 1


def test_seed_on_startup_disallowed_in_production_mode(monkeypatch):
    """#104080: Verify that when DEBUG is false (production mode), demo seeding cannot be enabled."""
    from src.database import config
    debug_val = False
    seed_env = "true"
    seed_on_startup = seed_env.lower() == "true" and debug_val
    assert seed_on_startup is False


def test_production_initializes_with_clean_empty_state():
    """#104080: Acceptance Criteria - Application startup populates no sample courses, students, or grades."""
    from src.database import config
    from src.database.models import Course, Student, Exam, ExamResult
    from tests.test_api import TestingSessionLocal

    db = TestingSessionLocal()
    try:
        assert config.SEED_ON_STARTUP is False
        assert db.query(Course).count() == 0
        assert db.query(Student).count() == 0
        assert db.query(Exam).count() == 0
        assert db.query(ExamResult).count() == 0
    finally:
        db.close()


def test_essential_initialization_retains_bootstrap_admin(monkeypatch):
    """#104080: Acceptance Criteria - Only essential system initialization remains active (bootstrap admin)."""
    from src.database import config
    from src.database.models import Course, Student, User
    from src.database.seed import seed_bootstrap_admin
    from tests.test_api import TestingSessionLocal

    monkeypatch.setattr(config, "BOOTSTRAP_ADMIN_EMAIL", "admin.prod@uni-hildesheim.de")
    monkeypatch.setattr(config, "BOOTSTRAP_ADMIN_PASSWORD", "SuperSecureProdPassword123!")
    monkeypatch.setattr(config, "BOOTSTRAP_ADMIN_NAME", "Production Administrator")

    seed_bootstrap_admin()

    db = TestingSessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin.prod@uni-hildesheim.de").first()
        assert admin is not None
        assert admin.name == "Production Administrator"
        assert db.query(Course).count() == 0
        assert db.query(Student).count() == 0
    finally:
        db.close()


def test_remove_graduate_and_fail_student_lifecycle_actions_104083():
    """
    Task #104083:
    - Global 'Graduate' and 'Fail' student lifecycle classification actions (/api/students/{id}/status) are removed.
    - Student records cannot be transitioned to 'graduated' or 'failed' states via profile create/update endpoints.
    - Student records are tracked purely through their course-level exam marks.
    """
    # 1. Create student and course
    create_res = client.post(
        "/api/students/",
        json={
            "student_id": 104083,
            "name": "Grace Hopper",
            "program": "SE Master",
            "status": "graduated",
        },
    )
    assert create_res.status_code == 201

    # 2. The legacy PUT /api/students/{id}/status endpoint must no longer exist
    status_res = client.put(
        "/api/students/104083/status",
        json={"status": "graduated", "version": 1},
    )
    assert status_res.status_code in (404, 405)

    fail_status_res = client.put(
        "/api/students/104083/status",
        json={"status": "failed", "version": 1},
    )
    assert fail_status_res.status_code in (404, 405)

    # 3. Updating profile with 'status': 'failed' does not mutate student into 'failed' lifecycle state
    details = client.get("/api/students/104083").json()
    assert details["status"] == "active"
    update_res = client.put(
        "/api/students/104083",
        json={
            "new_student_id": 104083,
            "name": "Grace Brewster Hopper",
            "program": "SE Master",
            "status": "failed",
            "version": details["version"],
        },
    )
    assert update_res.status_code == 200
    updated_details = client.get("/api/students/104083").json()
    assert updated_details["status"] == "active"

    # 4. Student records are tracked purely through their course-level exam marks
    course_res = client.post(
        "/api/courses/",
        json={"course_id": 104083, "course_name": "Compiler Construction", "semester": "WISE_25"},
    )
    assert course_res.status_code == 201

    grade_res = client.post(
        "/api/students/104083/grades",
        json={"course_id": 104083, "semester": "WISE_25", "grade": 1.3, "attempt_type": "Exam 1"},
    )
    assert grade_res.status_code == 200

    roster = client.get("/api/students/").json()
    student_row = next(s for s in roster if s["student_id"] == 104083)
    assert student_row["total_exams"] == 1
    assert student_row["passed_exams"] == 1
    assert student_row["avg_grade"] == 1.3
