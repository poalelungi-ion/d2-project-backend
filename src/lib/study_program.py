"""
Canonical study programs.

Lecturers pick from this list rather than typing a free-text Studiengang, so
imports and student records stay consistent. The client keeps an identical
STUDY_PROGRAMS array. A blank cell on upload is stored as UNASSIGNED_PROGRAM
instead of failing the row.
"""
from typing import Annotated, Literal, get_args

from pydantic import BeforeValidator

# Sorted for dropdown display. Change the Literal and the client list together.
StudyProgram = Literal[
    "Data Science Master",
    "Development Project",
    "Research Methods",
    "SE Master",
]

STUDY_PROGRAMS: tuple[str, ...] = get_args(StudyProgram)

UNASSIGNED_PROGRAM = "Unassigned / Unknown"

_NAMED = frozenset(STUDY_PROGRAMS)
_UPLOAD = _NAMED | {UNASSIGNED_PROGRAM}


def is_known_program(value: str) -> bool:
    """True for a named program or the upload placeholder."""
    return value in _UPLOAD


def _named_program(value: object) -> str:
    name = str(value).strip() if value is not None else ""
    if name not in _NAMED:
        raise ValueError("Study program must be chosen from the predefined list")
    return name


def _optional_named_program(value: object) -> str | None:
    if value is None:
        return None
    name = str(value).strip()
    if not name:
        return None
    return _named_program(name)


def _upload_program(value: object) -> str:
    name = str(value).strip() if value is not None else ""
    if not name:
        return UNASSIGNED_PROGRAM
    if not is_known_program(name):
        raise ValueError("Study program must be chosen from the predefined list")
    return name


NamedStudyProgram = Annotated[StudyProgram, BeforeValidator(_named_program)]
OptionalStudyProgram = Annotated[StudyProgram | None, BeforeValidator(_optional_named_program)]
UploadStudyProgram = Annotated[str, BeforeValidator(_upload_program)]
