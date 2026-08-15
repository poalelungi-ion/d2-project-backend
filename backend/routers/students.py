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

@router.get("/api/students/")
def get_students(db: Session = Depends(get_db)):
    """
    Retrieves the complete student roster with their aggregate performance metrics (average grade, credits).
    """
    students = db.query(models.Student).all()
    data = []
    for s in students:
        results = s.results
        total = len(results)
        passed_results = [r for r in results if r.passed]
        passed = len(passed_results)
        avg_grade = sum(r.grade for r in passed_results) / passed if passed > 0 else 0
        
        data.append({
            "student_id": s.student_id,
            "name": s.name,
            "program": s.program,
            "status": s.status,
            "total_exams": total,
            "passed_exams": passed,
            "avg_grade": round(avg_grade, 2),
            "version": s.version
        })
    return data



@router.get("/api/students/{student_id}")
def get_student_details(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    transcript = []
    course_attempts = {}
    
    # Sort by exam_id to approximate chronological order
    sorted_results = sorted(student.results, key=lambda r: r.exam_id)
    
    for r in sorted_results:
        c_name = r.exam.course.course_name
        course_attempts[c_name] = course_attempts.get(c_name, 0) + 1
        transcript.append({
            "result_id": r.result_id,
            "student_id": student.student_id,
            "name": student.name,
            "course": c_name,
            "semester": r.exam.semester,
            "grade": r.grade,
            "passed": r.passed,
            "version": r.version,
            "attempt": course_attempts[c_name],
            "version": r.version
        })
        
    transcript.sort(key=lambda x: (x["course"], x["attempt"]))
        
    return {
        "student_id": student.student_id,
        "name": student.name,
        "program": student.program,
        "status": student.status,
        "version": student.version,
        "transcript": transcript
    }









@router.post("/api/students/{student_id}/grades")
def add_student_grade(student_id: int, request: AddGradeRequest, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    course = db.query(models.Course).filter(models.Course.course_id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    exam = db.query(models.Exam).filter(models.Exam.course_id == request.course_id, models.Exam.semester == request.semester).first()
    if not exam:
        exam = models.Exam(course_id=request.course_id, semester=request.semester)
        db.add(exam)
        db.commit()

    passed = request.grade <= 4.0
    existing = db.query(models.ExamResult).join(models.Exam).filter(models.ExamResult.student_id == student.student_id, models.Exam.course_id == exam.course_id).first()
    if existing:
        if request.grade < existing.grade:
            existing.grade = request.grade
            existing.passed = passed
            existing.exam_id = exam.exam_id
            db.commit()
    else:
        res = models.ExamResult(student_id=student.student_id, exam_id=exam.exam_id, grade=request.grade, passed=passed)
        db.add(res)
        db.commit()
    return {"status": "success"}





@router.put("/api/students/{student_id}/status")
def update_student_status(student_id: int, update: StudentStatusUpdate, db: Session = Depends(get_db)):
    s = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    s.status = update.status
    db.commit()
    return {"status": "success"}

