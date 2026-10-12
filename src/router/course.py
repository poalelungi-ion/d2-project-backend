"""
Course Router (HTTP Controller).
Handles course catalogue querying, creation, updating, and archiving.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.router.dto import (
    CourseArchiveUpdate,
    CourseCreate,
    CourseUpdate,
)
from src.services import course as course_service

router = APIRouter()


@router.get("/api/courses/", summary="Get all courses")
def get_courses(db: Session = Depends(get_db)):
    """Retrieves all courses alongside pass rates and average grades."""
    return course_service.get_all_courses(db)


# [Ticket #95647 - View course details: Data Retrieval & Presentation]
# Endpoint to retrieve detailed course dashboard payload by course_id.
# Queries backend for core metadata (Course Name, ID, Semester, Study Program)
# and summary metrics. Returns HTTP 404 when course_id does not exist.
@router.get("/api/courses/{course_id}", summary="Get course details by ID")
def get_course_details(course_id: int, db: Session = Depends(get_db)):
    """Retrieves a single course by its ID alongside pass rates, average grades, and marks."""
    return course_service.get_course_details(db, course_id)


@router.post(
    "/api/courses/",
    status_code=status.HTTP_201_CREATED,
    summary="Create course",
)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Creates a new course in the catalogue (requires a signed-in user)."""
    return course_service.create_course(db, course)


@router.put(
    "/api/courses/{course_id}",
    summary="Update course",
)
def update_course(course_id: int, course: CourseUpdate, db: Session = Depends(get_db)):
    """Updates course metadata under optimistic locking (requires a signed-in user)."""
    return course_service.update_course(db, course_id, course)


@router.put("/api/courses/{course_id}/archive", summary="Archive or unarchive course")
def update_course_archive(course_id: int, update: CourseArchiveUpdate, db: Session = Depends(get_db)):
    """Toggles course archive state."""
    return course_service.archive_course(db, course_id, update)
