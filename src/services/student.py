"""
Student Domain Service.
Encapsulates business rules, data transformations, and transactional operations for students.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.database.models import Course, Exam, ExamResult, Student
from src.router.dto import (
    AddGradeRequest,
    StudentCreate,
    StudentStatusUpdate,
    StudentUpdate,
)


def get_all_students(db: Session):
    """
    Retrieves the complete student roster with aggregate performance metrics.
    """
    students = db.query(Student).all()
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
            "version": s.version,
        })
    return data


def create_student(db: Session, student_dto: StudentCreate):
    """
    Creates a new student profile in a transaction. Rejects duplicate IDs with 409 Conflict.
    """
    existing = db.query(Student).filter(Student.student_id == student_dto.student_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student ID already exists")

    new_student = Student(
        student_id=student_dto.student_id,
        name=student_dto.name,
        program=student_dto.program,
        status=student_dto.status,
    )
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return {"status": "success", "student_id": new_student.student_id}
    except Exception:
        db.rollback()
        raise


def update_student(db: Session, student_id: int, update_dto: StudentUpdate):
    """
    Updates an existing student profile under optimistic concurrency control.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if student.version != update_dto.version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")

    if update_dto.new_student_id and update_dto.new_student_id != student_id:
        existing = db.query(Student).filter(Student.student_id == update_dto.new_student_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student ID already exists")
        student.student_id = update_dto.new_student_id

    student.program = update_dto.program
    student.name = update_dto.name
    student.status = update_dto.status

    try:
        db.commit()
        return {"status": "success"}
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data modified by another user. Please refresh.")
    except Exception:
        db.rollback()
        raise


def update_student_status(db: Session, student_id: int, update_dto: StudentStatusUpdate):
    """
    Updates a student's active/graduated/failed status.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    student.status = update_dto.status
    try:
        db.commit()
        return {"status": "success"}
    except Exception:
        db.rollback()
        raise


def add_student_grade(db: Session, student_id: int, request: AddGradeRequest):
    """
    [REQ-TRANSACTION-01] Atomic Transaction for Student Grade Recording
    
    Demonstrates atomic transaction execution:
    1. Verifies student exists.
    2. Verifies course exists.
    3. Finds or provisions the Exam for the target semester.
    4. Finds or provisions the ExamResult, enforcing best-grade logic.
    5. Commits all operations atomically. If any error occurs, rolls back cleanly.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    course = db.query(Course).filter(Course.course_id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    try:
        # Atomic transaction block
        exam = (
            db.query(Exam)
            .filter(Exam.course_id == request.course_id, Exam.semester == request.semester)
            .first()
        )
        if not exam:
            exam = Exam(course_id=request.course_id, semester=request.semester)
            db.add(exam)
            db.flush()

        passed = request.grade <= 4.0
        existing = (
            db.query(ExamResult)
            .join(Exam)
            .filter(ExamResult.student_id == student.student_id, Exam.course_id == exam.course_id)
            .first()
        )

        if existing:
            if request.grade < existing.grade:
                existing.grade = request.grade
                existing.passed = passed
                existing.exam_id = exam.exam_id
        else:
            res = ExamResult(
                student_id=student.student_id,
                exam_id=exam.exam_id,
                grade=request.grade,
                passed=passed,
            )
            db.add(res)

        db.commit()
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction failed while adding student grade: {str(e)}",
        )
