"""
Grade Data Transfer Objects (DTOs).
"""
from pydantic import BaseModel, Field


class GradeUpdate(BaseModel):
    result_id: int
    version: int
    grade: float = Field(..., ge=1.0, le=5.0)
    passed: bool
