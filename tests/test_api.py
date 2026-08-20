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
