"""
Demonstration data seeding.

Populates an empty database with a representative roster, course catalogue,
exams and results so the dashboards have something to display on a fresh
deployment.
"""
import random

from src.database.connection import get_db
from src.database.models import Course, Exam, ExamResult, Student


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

        results_dict = {}
        for s in students:
            sampled_exams = random.sample(exams, random.randint(8, 12))
            for e in sampled_exams:
                grade = random.choices(
                    [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0],
                    weights=[5, 10, 15, 20, 15, 10, 5, 5, 5, 5, 15], k=1
                )[0]
                key = (s.student_id, e.course_id)
                if key not in results_dict or grade < results_dict[key]['grade']:
                    results_dict[key] = {'exam_id': e.exam_id, 'grade': grade, 'passed': grade <= 4.0}

                if grade > 4.0:
                    retry_exam = next((ex for ex in exams if ex.course_id == e.course_id and ex.exam_id != e.exam_id), None)
                    if retry_exam:
                        retry_grade = random.choices([1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0], weights=[5,10,15,20,15,10,10,5,5,5], k=1)[0]
                        if retry_grade < results_dict[key]['grade']:
                            results_dict[key] = {'exam_id': retry_exam.exam_id, 'grade': retry_grade, 'passed': True}

        results = [
            ExamResult(student_id=k[0], exam_id=v['exam_id'], grade=v['grade'], passed=v['passed'])
            for k, v in results_dict.items()
        ]
        db.add_all(results)
        db.commit()
    except Exception as e:
        print("Seed error:", e)
    finally:
        db.close()
