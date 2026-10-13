"""
Grade Data Transfer Objects (DTOs).
"""
from typing import Optional, Union
from pydantic import BaseModel, field_validator


class GradeUpdate(BaseModel):
    result_id: int
    version: int
    # Same cells as upload: 1.0–5.0, or NE/EX/AT. Pass/fail is never taken from
    # a client flag; evaluate_grade recomputes it.
    grade: Union[float, str]
    # Ignored if sent. Pass/fail is always recomputed from the grade cell.
    passed: Optional[bool] = None
    attempt_type: Optional[str] = None
    semester: Optional[str] = None

    @field_validator("grade", mode="before")
    @classmethod
    def same_rules_as_upload(cls, value: object) -> object:
        # Imported here to avoid a circular import through src.services.
        from src.services.grade_outcome import UnrecognizedGrade, evaluate_grade

        try:
            evaluate_grade(value)
        except UnrecognizedGrade as exc:
            raise ValueError(str(exc)) from exc
        return value
