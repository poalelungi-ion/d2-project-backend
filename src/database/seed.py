"""
Demonstration data seeding.

Populates an empty database with a representative roster, course catalogue,
exams and results so the dashboards have something to display on a fresh
deployment.
"""
import logging
import random

from src.database import config
from src.database.connection import get_db
from src.database.models import Course, Exam, ExamResult, Student, User
from src.lib.auth.passwords import hash_password
from src.router.dto.auth_dto import normalize_university_email

logger = logging.getLogger("uvicorn.error")


def seed_bootstrap_admin():
    """
    Creates the first account from BOOTSTRAP_ADMIN_EMAIL / _PASSWORD when the
    users table is empty.

    Optional by design: with registration open, a deployment can simply have
    its first user sign up. This exists so an automated deployment can come up
    with a known account without anyone writing a bcrypt hash by hand. The
    password is read from the environment and hashed immediately -- it is never
    stored or logged as given.
    """
    if not config.BOOTSTRAP_ADMIN_EMAIL or not config.BOOTSTRAP_ADMIN_PASSWORD:
        return

    db = next(get_db())
    try:
        if db.query(User).count() > 0:
            return
        email = normalize_university_email(config.BOOTSTRAP_ADMIN_EMAIL)
        db.add(User(
            email=email,
            name=config.BOOTSTRAP_ADMIN_NAME,
            password_hash=hash_password(config.BOOTSTRAP_ADMIN_PASSWORD),
        ))
        db.commit()
        logger.info("Bootstrap account created for %s.", email)
    except Exception as e:
        db.rollback()
        logger.warning("Bootstrap admin not created: %s", e)
    finally:
        db.close()


def seed_db():
    """Insert demonstration data, unless the students table is already populated."""
    db = next(get_db())
    try:
        if db.query(Student).count() > 0:
            return

        students = [
            Student(student_id=1001, name="Anna Chiriciuc", program="SE Master"),
            Student(student_id=1002, name="Ion Poalelungi", program="SE Master"),
            Student(student_id=1003, name="Jacqueline Denise", program="SE Master"),
            Student(student_id=1004, name="Max Mustermann", program="Data Science Master"),
            Student(student_id=1005, name="Erika Musterfrau", program="SE Master"),
            Student(student_id=1006, name="Lukas Schmidt", program="SE Master"),
            Student(student_id=1007, name="Sophie Wagner", program="SE Master"),
            Student(student_id=1008, name="Leon Becker", program="Data Science Master"),
            Student(student_id=1009, name="Marie Hoffmann", program="SE Master"),
            Student(student_id=1010, name="Julia Alumni", program="SE Master", status="graduated"),
            Student(student_id=1011, name="Tom Graduated", program="Data Science Master", status="graduated"),
            Student(student_id=1012, name="Markus Failed", program="SE Master", status="failed"),
        ]
        db.add_all(students)
        db.commit()

        course_names = [
            "Software Architecture", "Software Product Line Engineering",
            "Machine Learning", "Data Mining", "Advanced Databases",
            "Cloud Computing", "Requirements Engineering", "Project Management"
        ]
        courses = [Course(course_name=name) for name in course_names]
        courses.append(Course(course_name="Legacy Systems 2018", is_archived=True))
        courses.append(Course(course_name="Old Data Structures", is_archived=True))
        db.add_all(courses)
        db.commit()

        exams = []
        for c in courses:
            exams.append(Exam(course_id=c.course_id, semester="SOSE_25"))
            exams.append(Exam(course_id=c.course_id, semester="WISE_25"))
            exams.append(Exam(course_id=c.course_id, semester="SOSE_26"))
        db.add_all(exams)
        db.commit()

        results = []
        for s in students:
            sampled_exams = random.sample(exams, random.randint(8, 12))
            for e in sampled_exams:
                # 1st attempt: Exam 1
                grade1 = random.choices(
                    [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0],
                    weights=[5, 10, 15, 20, 15, 10, 5, 5, 5, 5, 20], k=1
                )[0]
                results.append(ExamResult(
                    student_id=s.student_id,
                    exam_id=e.exam_id,
                    grade=grade1,
                    passed=grade1 <= 4.0,
                    attempt_type="Exam 1",
                ))

                # If failed (5.0) or selected for retake: add 2nd attempt (Exam 2)
                if grade1 > 4.0 or random.random() < 0.35:
                    grade2 = random.choices(
                        [1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0],
                        weights=[10, 15, 25, 20, 10, 5, 5, 5, 3, 2], k=1
                    )[0]
                    results.append(ExamResult(
                        student_id=s.student_id,
                        exam_id=e.exam_id,
                        grade=grade2,
                        passed=grade2 <= 4.0,
                        attempt_type="Exam 2",
                    ))

        db.add_all(results)
        db.commit()
    except Exception as e:
        print("Seed error:", e)
    finally:
        db.close()
