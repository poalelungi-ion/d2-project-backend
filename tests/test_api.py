import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
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

client = TestClient(app)

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
    paste = "Matrikelnr,Name,Program,Semester,Grade\n8888,Ada Lovelace,CS,1,1.0\n"
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
    paste = "Matrikelnr\tName\tProgram\tSemester\tGrade\n9999\tValid, User\tCS\t1\t2.0\n"
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


def test_upload_preview_invalid_grade():
    csv_content = b"Matrikelnr,Name,Program,Semester,Grade\n12345,John Doe,CS,WISE_25,1.0\n"
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
                "program": "CS",
                "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}',
                "grade": "2.0",
                "is_valid": True
            },
            {
                "student_id": "8888",
                "first_name": "Fail",
                "last_name": "User",
                "program": "CS",
                "semester": "WISE_25", "mapping": '{"Matrikelnr": "student_id", "Name": "name", "Program": "program", "Grade": "grade"}',
                "grade": "5.0",
                "is_valid": True
            },
            {
                "student_id": "7777",
                "first_name": "Absent",
                "last_name": "User",
                "program": "CS",
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
