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
from src.services.grade_outcome import (
    counted_attempts,
    evaluate_grade,
    mean_grade,
    result_outcome_fields,
)


def get_all_students(db: Session):
    """
    Retrieves the complete student roster with aggregate performance metrics.
    """
    students = db.query(Student).all()
    data = []
    for s in students:
        results = s.results
        graded = counted_attempts(results)
        passed_results = [r for r in graded if r.passed]
        passed = len(passed_results)
        avg_grade = mean_grade(passed_results)
        data.append({
            "student_id": s.student_id,
            "name": s.name,
            "program": s.program,
            "study_program": s.program,
            "status": s.status,
            "total_exams": len(results),
            "passed_exams": passed,
            "avg_grade": round(avg_grade, 2),
            "version": s.version,
        })
    return data


def get_student_details(db: Session, student_id: int):
    """
    Retrieves one student profile with their full transcript.

    Restored during the merge with the layered-architecture refactor, which
    dropped it: the client's student detail page and analytics both read it.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

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
            **result_outcome_fields(r),
            "attempt": course_attempts[c_name],
            # The sitting the lecturer tagged this batch with, as opposed to
            # `attempt`, which is this system counting results per course.
            "attempt_type": r.attempt_type,
            "version": r.version,
        })

    transcript.sort(key=lambda x: (x["course"], x["attempt"]))

    return {
        "student_id": student.student_id,
        "name": student.name,
        "program": student.program,
        "study_program": student.program,
        "status": student.status,
        "version": student.version,
        "transcript": transcript,
    }


def create_student(db: Session, student_dto: StudentCreate):
    """
    Creates a new student profile in a transaction. Rejects duplicate IDs with 409 Conflict.
    """
    existing = db.query(Student).filter(Student.student_id == student_dto.student_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student ID already exists")

    resolved_program = student_dto.study_program or student_dto.program or "SE Master"
    new_student = Student(
        student_id=student_dto.student_id,
        name=student_dto.name,
        program=resolved_program,
        status=student_dto.status or "active",
    )
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return {
            "status": "success",
            "student_id": new_student.student_id,
            "name": new_student.name,
            "program": new_student.program,
            "study_program": new_student.program,
            "version": new_student.version,
        }
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

    resolved_program = update_dto.study_program or update_dto.program
    if resolved_program:
        student.program = resolved_program
    if update_dto.name is not None:
        student.name = update_dto.name
    if update_dto.status is not None:
        student.status = update_dto.status

    try:
        db.commit()
        db.refresh(student)
        return {
            "status": "success",
            "student_id": student.student_id,
            "name": student.name,
            "program": student.program,
            "study_program": student.program,
            "version": student.version,
        }
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

        verdict = evaluate_grade(request.grade)
        attempt_type = request.attempt_type or "Exam 1"
        existing = (
            db.query(ExamResult)
            .filter(
                ExamResult.student_id == student.student_id,
                ExamResult.exam_id == exam.exam_id,
                ExamResult.attempt_type == attempt_type,
            )
            .first()
        )

        if existing:
            existing.grade = verdict.grade
            existing.passed = verdict.passed
            existing.absence_code = verdict.absence_code
        else:
            res = ExamResult(
                student_id=student.student_id,
                exam_id=exam.exam_id,
                grade=verdict.grade,
                passed=verdict.passed,
                absence_code=verdict.absence_code,
                attempt_type=attempt_type,
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
