from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import pandas as pd
import io
from fastapi import Header

def verify_token(authorization: str = Header(None)):
    if authorization != "Bearer sse-staff-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

router = APIRouter()

@router.get("/api/courses/")
def get_courses(db: Session = Depends(get_db)):
    """
    Retrieves the list of all courses alongside success metrics (pass rate, average grade) per course.
    """
    courses = db.query(models.Course).all()
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
                    "passed": r.passed,
                    "version": r.version
                })
        
        total = len(results)
        passed_results = [r for r in results if r.passed]
        passed = len(passed_results)
        avg_grade = sum(r.grade for r in passed_results) / passed if passed > 0 else 0
        
        # Sort semesters safely. E.g. SOSE_25, WISE_25. We can just take max() string-wise for a naive approach
        # or simply join them if there are multiple. For simplicity, we'll sort alphabetically and pick the last.
        latest_semester = sorted(list(semesters))[-1] if semesters else "N/A"

        data.append({
            "course_id": c.course_id,
            "course_name": c.course_name,
            "assigned_professor": getattr(c, 'professor', 'Not Assigned'),
            "semester": c.semester if getattr(c, 'semester', None) else latest_semester,
            "study_program": getattr(c, 'study_program', 'Not Assigned'),
            "total_attempts": total,
            "pass_rate": round((passed / total * 100), 1) if total > 0 else 0,
            "avg_grade": round(avg_grade, 2),
            "is_archived": c.is_archived,
            "version": c.version,
            "marks": marks_detailed
        })
    return data





@router.put("/api/courses/{course_id}/archive")
def update_course_archive(course_id: int, update: CourseArchiveUpdate, db: Session = Depends(get_db)):
    c = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    if c.version != update.version:
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
    c.is_archived = update.is_archived
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Data modified by another user. Please refresh.")
    return {"status": "success"}



