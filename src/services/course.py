"""
Course Domain Service.
Encapsulates course querying, creation, updating, and archiving under optimistic locking.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.database.models import Course
from src.router.dto import (
    CourseArchiveUpdate,
    CourseCreate,
    CourseUpdate,
)
from src.services.grade_outcome import counted_attempts, mean_grade, result_outcome_fields


def get_all_courses(db: Session):
    """
    Retrieves all courses alongside aggregated pass rates and average grades.
    """
    courses = db.query(Course).all()
    data = []
    for c in courses:
        exams = c.exams
        results = []
        marks_detailed = []
        semesters = set()
        for e in exams:
            semesters.add(e.semester)
            results.extend(e.results)
            for r in e.results:
                marks_detailed.append({
                    "student_id": r.student.student_id if r.student else None,
                    "student_name": r.student.name if r.student else "Unknown",
                    "program": r.student.program if r.student else "Unknown",
                    "semester": e.semester,
                    "grade": r.grade,
                    **result_outcome_fields(r),
                    "version": r.version,
                })

        total = len(results)
        graded = counted_attempts(results)
        passed_results = [r for r in graded if r.passed]
        passed = len(passed_results)
        avg_grade = mean_grade(passed_results)
        latest_semester = sorted(list(semesters))[-1] if semesters else "N/A"

        data.append({
            "course_id": c.course_id,
            "course_name": c.course_name,
            "assigned_professor": getattr(c, "professor", "Not Assigned"),
            "semester": c.semester if getattr(c, "semester", None) else latest_semester,
            "study_program": getattr(c, "study_program", "Not Assigned"),
            "total_attempts": total,
            "pass_rate": round((passed / len(graded) * 100), 1) if graded else 0,
            "avg_grade": round(avg_grade, 2),
            "is_archived": c.is_archived,
            "version": c.version,
            "marks": marks_detailed,
        })
    return data


def create_course(db: Session, course_dto: CourseCreate):
    """
    Creates a new course in a transaction, enforcing uniqueness.
    """
    if course_dto.course_id:
        existing_id = db.query(Course).filter(Course.course_id == course_dto.course_id).first()
        if existing_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course ID already exists")

    existing = db.query(Course).filter(Course.course_name == course_dto.course_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course name already exists")

    new_course = Course(
        course_id=course_dto.course_id if course_dto.course_id else abs(hash(course_dto.course_name)) % (10**8),
        course_name=course_dto.course_name,
        semester=course_dto.semester,
        study_program=course_dto.study_program,
        professor=course_dto.professor,
    )
    try:
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        return {
            "status": "success",
            "course_id": new_course.course_id,
            "course_name": new_course.course_name,
        }
    except Exception:
        db.rollback()
        raise


def update_course(db: Session, course_id: int, course_dto: CourseUpdate):
    """
    Updates course metadata under optimistic locking.
    """
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.version != course_dto.version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")

    if course_dto.new_course_id and course_dto.new_course_id != course_id:
        existing_id = db.query(Course).filter(Course.course_id == course_dto.new_course_id).first()
        if existing_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course ID already exists")
        course.course_id = course_dto.new_course_id

    course.course_name = course_dto.course_name
    course.semester = course_dto.semester
    course.study_program = course_dto.study_program
    course.professor = course_dto.professor

    try:
        db.commit()
        return {"status": "success", "message": "Course updated successfully"}
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
    except Exception:
        db.rollback()
        raise


def archive_course(db: Session, course_id: int, archive_dto: CourseArchiveUpdate):
    """
    Toggles course archive state under optimistic locking.
    """
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.version != archive_dto.version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")

    course.is_archived = archive_dto.is_archived
    try:
        db.commit()
        return {"status": "success"}
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
    except Exception:
        db.rollback()
        raise
