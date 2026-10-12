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
            "ects": "6",
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
            "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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


def test_preview_absence_codes_and_ignores_passed_column():
    paste = (
        "Matrikelnr\tName\tProgram\tSemester\tGrade\tPassed\n"
        "31001\tSchneider, Lena\tSE Master\t3\tNE\tYes\n"
        "31002\tBecker, Leon\tSE Master\t3\tEX\tPassed\n"
        "31003\tWagner, Sophie\tSE Master\t3\tAT\tNo\n"
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
    assert rows["31001"]["outcome"] == "failed"
    assert rows["31001"]["absence_code"] == "NE"
    assert rows["31001"]["is_valid"] is True
    assert rows["31002"]["outcome"] == "failed"
    assert rows["31002"]["absence_code"] == "EX"
    assert rows["31003"]["outcome"] == "excused"
    assert rows["31003"]["absence_code"] == "AT"
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


def test_confirm_persists_absence_outcomes():
    payload = {
        "course": "ABSENCE101",
        "courseName": "Absence Course",
        "ects": "6",
        "semester": "WISE_25",
        "records": [
            {
                "student_id": "31021",
                "first_name": "No",
                "last_name": "Show",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "NE",
            },
            {
                "student_id": "31022",
                "first_name": "Med",
                "last_name": "Note",
                "program": "SE Master",
                "semester": "WISE_25",
                "grade": "AT",
            },
        ],
    }
    assert client.post("/api/upload/confirm/", json=payload).status_code == 200
    ne = client.get("/api/students/31021").json()["transcript"][0]
    at = client.get("/api/students/31022").json()["transcript"][0]
    assert ne["passed"] is False
    assert ne["outcome"] == "failed"
    assert ne["absence_code"] == "NE"
    assert ne["grade"] == 5.0
    assert at["passed"] is False
    assert at["outcome"] == "excused"
    assert at["absence_code"] == "AT"
    assert at["grade"] is None


def test_confirm_rejects_passed_text_as_a_grade():
    payload = {
        "course": "LABEL101",
        "courseName": "Label Course",
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
                "grade": "NE",
            }
        ],
    )
    assert response.status_code == 200
    failed = client.get("/api/students/31041").json()["transcript"][0]
    assert failed["grade"] == 5.0
    assert failed["outcome"] == "failed"
    assert failed["absence_code"] == "NE"

    excused = client.post(
        "/api/grades/",
        json=[
            {
                "result_id": failed["result_id"],
                "version": failed["version"],
                "grade": "AT",
            }
        ],
    )
    assert excused.status_code == 200
    sitting = client.get("/api/students/31041").json()["transcript"][0]
    assert sitting["grade"] is None
    assert sitting["outcome"] == "excused"
    assert sitting["absence_code"] == "AT"


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
        "ects": "6",
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
                "grade": "AT",
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
    assert course["total_attempts"] == 6
    assert course["pass_rate"] == 20.0
    mark = next(m for m in course["marks"] if m["student_id"] == 31053 and m["outcome"] == "excused")
    assert mark["grade"] is None

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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "ects": "6",
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
        "status": "graduated",
        "version": version,
    }
    update_res = client.put("/api/students/97931", json=update_payload)
    assert update_res.status_code == 200

    # Verify updated values
    updated_details = client.get("/api/students/97931").json()
    assert updated_details["name"] == "Ada King Lovelace"
    assert updated_details["program"] == "Data Science Master"
    assert updated_details["status"] == "graduated"

    # 2. Conflict on stale version (concurrency)
    stale_res = client.put("/api/students/97931", json=update_payload)
    assert stale_res.status_code == 409

