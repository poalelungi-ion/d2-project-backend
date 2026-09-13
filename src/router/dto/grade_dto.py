"""
Grade Data Transfer Objects (DTOs).
"""
from typing import Optional
from pydantic import BaseModel, Field


class GradeUpdate(BaseModel):
    result_id: int
    version: int
    grade: float = Field(..., ge=1.0, le=5.0)
    # Ignored if sent. Pass/fail is always recomputed from the numeric grade.
    passed: Optional[bool] = None
