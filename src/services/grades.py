"""
Grades Domain Service.
Handles grade retrieval and batch updates with optimistic concurrency control.
"""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.database.models import ExamResult
from src.router.dto import GradeUpdate


def get_all_grades(db: Session):
    results = db.query(ExamResult).all()
    data = []
    for r in results:
        data.append({
            "result_id": r.result_id,
            "student_id": r.student.student_id if r.student else None,
            "name": r.student.name if r.student else "Unknown",
            "course": r.exam.course.course_name if r.exam and r.exam.course else "Unknown",
            "semester": r.exam.semester if r.exam else "Unknown",
            "grade": r.grade,
            "passed": r.passed,
            "version": r.version,
        })
    return data


def update_grades_batch(db: Session, updates: List[GradeUpdate]):
    for u in updates:
        if not (1.0 <= u.grade <= 5.0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Grade must be between 1.0 and 5.0")
        result = db.query(ExamResult).filter(ExamResult.result_id == u.result_id).first()
        if result:
            if result.version != u.version:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
            result.grade = u.grade
            result.passed = u.passed

    try:
        db.commit()
        return {"status": "success", "message": "Grades updated successfully"}
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
    except Exception:
        db.rollback()
        raise
