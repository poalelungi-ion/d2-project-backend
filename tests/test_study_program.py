"""Study program list and API-boundary validation."""
import pytest
from pydantic import ValidationError

from src.lib.study_program import STUDY_PROGRAMS, UNASSIGNED_PROGRAM, is_known_program
from src.router.dto.course_dto import CourseCreate
from src.router.dto.create_student import StudentCreate
from src.router.dto.upload_dto import ConfirmRecord


def test_named_programs_are_sorted():
    assert list(STUDY_PROGRAMS) == sorted(STUDY_PROGRAMS)


def test_placeholder_is_known_but_not_a_named_program():
    assert UNASSIGNED_PROGRAM not in STUDY_PROGRAMS
    assert is_known_program(UNASSIGNED_PROGRAM)
    assert not is_known_program("Custom Degree")


def test_student_create_rejects_a_typed_in_program():
    with pytest.raises(ValidationError):
        StudentCreate(student_id=1, name="Ada", program="Custom Degree")


def test_student_create_accepts_a_listed_program():
    dto = StudentCreate(student_id=1, name="Ada", program="Data Science Master")
    assert dto.program == "Data Science Master"


def test_confirm_record_fills_a_blank_program():
    record = ConfirmRecord(student_id="1", grade="1.0")
    assert record.program == UNASSIGNED_PROGRAM


def test_confirm_record_empty_string_becomes_placeholder():
    record = ConfirmRecord(student_id="1", program="", grade="1.0")
    assert record.program == UNASSIGNED_PROGRAM


def test_confirm_record_rejects_a_typed_in_program():
    with pytest.raises(ValidationError):
        ConfirmRecord(student_id="1", program="CS", grade="1.0")


def test_course_create_rejects_a_typed_in_program():
    with pytest.raises(ValidationError):
        CourseCreate(course_name="Lab", study_program="Made Up Track")


def test_course_create_allows_omitting_program():
    dto = CourseCreate(course_name="Lab")
    assert dto.study_program is None
