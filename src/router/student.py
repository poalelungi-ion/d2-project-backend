"""
Student Router (HTTP Controller).
Extracts request parameters, validates input DTOs, and delegates domain execution to StudentService.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.lib.auth.validator import verify_token
from src.router.dto import (
    AddGradeRequest,
    StudentCreate,
    StudentStatusUpdate,
    StudentUpdate,
)
from src.services import student as student_service

router = APIRouter()


@router.get("/api/students/", summary="Get complete student roster")
def get_students(db: Session = Depends(get_db)):
    """Retrieves the complete student roster with aggregate performance metrics."""
    return student_service.get_all_students(db)


@router.post(
    "/api/students/",
    dependencies=[Depends(verify_token)],
    status_code=status.HTTP_201_CREATED,
    summary="Create student profile",
)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Creates a new student profile in the database (Protected endpoint)."""
    return student_service.create_student(db, student)


@router.put(
    "/api/students/{student_id}",
    dependencies=[Depends(verify_token)],
    summary="Update student profile",
)
def update_student(student_id: int, update: StudentUpdate, db: Session = Depends(get_db)):
    """Updates an existing student profile under optimistic concurrency control (Protected endpoint)."""
    return student_service.update_student(db, student_id, update)


@router.put("/api/students/{student_id}/status", summary="Update student status")
def update_student_status(student_id: int, update: StudentStatusUpdate, db: Session = Depends(get_db)):
    """Updates a student's active/graduated/failed status."""
    return student_service.update_student_status(db, student_id, update)


@router.post("/api/students/{student_id}/grades", summary="Add or update student grade")
def add_student_grade(student_id: int, request: AddGradeRequest, db: Session = Depends(get_db)):
    """Records a grade for a student using atomic database transaction."""
    return student_service.add_student_grade(db, student_id, request)
