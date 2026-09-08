"""
Tests for Architecture, Separation of Concerns, Transactions, and Swagger Security.
"""
import pytest
from fastapi import HTTPException

from tests.test_api import client, TestingSessionLocal
from src.database.models import Student, Course, Exam, ExamResult
from src.router.dto import StudentCreate, AddGradeRequest
from src.services.student import create_student, add_student_grade


def test_swagger_openapi_has_httpbearer():
    """Verifies OpenAPI schema includes HTTPBearer for Swagger UI testing."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "securitySchemes" in data["components"]
    assert "HTTPBearer" in data["components"]["securitySchemes"]
    assert data["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"


def test_service_separation_and_transaction_success():
    """Verifies services execute independently and manage atomic transactions."""
    db = TestingSessionLocal()
    try:
        # Create student via service
        dto = StudentCreate(student_id=7001, name="Transaction Tester", program="SE Master")
        res = create_student(db, dto)
        assert res["status"] == "success"
        assert res["student_id"] == 7001

        # Create course directly
        course = Course(course_id=501, course_name="Concurrency Lab")
        db.add(course)
        db.commit()

        # Add grade with transaction
        grade_dto = AddGradeRequest(course_id=501, semester="WISE_25", grade=1.3)
        grade_res = add_student_grade(db, 7001, grade_dto)
        assert grade_res["status"] == "success"

        # Verify persisted atomically
        saved_result = db.query(ExamResult).filter(ExamResult.student_id == 7001).first()
        assert saved_result is not None
        assert saved_result.grade == 1.3
        assert saved_result.passed is True
    finally:
        db.close()


def test_transaction_rollback_on_invalid_student():
    """Verifies transaction cleanly aborts and raises 404 when target student is missing."""
    db = TestingSessionLocal()
    try:
        grade_dto = AddGradeRequest(course_id=999, semester="WISE_25", grade=2.0)
        with pytest.raises(HTTPException) as exc_info:
            add_student_grade(db, 99999, grade_dto)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Student not found"
    finally:
        db.close()


def test_swagger_bearer_authorization_enforcement():
    """Verifies mutating endpoints reject unauthorized calls with 401 and accept valid tokens."""
    # Unauthorized
    bad_res = client.post(
        "/api/students/",
        json={"student_id": 8001, "name": "Auth Tester", "program": "SE Master"},
    )
    assert bad_res.status_code == 401

    # Authorized with valid Bearer token
    good_res = client.post(
        "/api/students/",
        headers={"Authorization": "Bearer sse-staff-token"},
        json={"student_id": 8001, "name": "Auth Tester", "program": "SE Master"},
    )
    assert good_res.status_code == 201
    assert good_res.json()["student_id"] == 8001

