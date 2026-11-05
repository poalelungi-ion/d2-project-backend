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
    "Angewandte Informatik Bachelor",
    "Angewandte Informatik Master",
    "Data Science Master",
    "Development Project",
    "IMIT Bachelor",
    "IMIT Master",
    "Informatik",
    "Research Methods",
    "SE Master",
    "Wirtschaftsinformatik Master",
]

STUDY_PROGRAMS: tuple[str, ...] = get_args(StudyProgram)

UNASSIGNED_PROGRAM = "Unassigned / Unknown"

_NAMED = frozenset(STUDY_PROGRAMS)
_UPLOAD = _NAMED | {UNASSIGNED_PROGRAM}

PROGRAM_ALIASES = {
    # SE
    "m.sc. se": "SE Master",
    "m.sc. software engineering": "SE Master",
    "m.sc. software eng": "SE Master",
    "msc se": "SE Master",
    "se": "SE Master",
    "software engineering": "SE Master",
    "software engineering master": "SE Master",

    # Informatik & AINF
    "informatik": "Informatik",
    "inf": "Informatik",
    "b.sc. informatik": "Angewandte Informatik Bachelor",
    "bsc informatik": "Angewandte Informatik Bachelor",
    "informatik bachelor": "Angewandte Informatik Bachelor",
    "m.sc. informatik": "Angewandte Informatik Master",
    "msc informatik": "Angewandte Informatik Master",
    "informatik master": "Angewandte Informatik Master",
    "m.sc. ainf": "Angewandte Informatik Master",
    "m.sc. angewandte informatik": "Angewandte Informatik Master",
    "msc ainf": "Angewandte Informatik Master",
    "ainf master": "Angewandte Informatik Master",
    "ainf": "Angewandte Informatik Master",
    "angewandte informatik": "Angewandte Informatik Master",
    "b.sc. ainf": "Angewandte Informatik Bachelor",
    "bsc ainf": "Angewandte Informatik Bachelor",
    "angewandte informatik bachelor": "Angewandte Informatik Bachelor",

    # IMIT
    "m.sc. imit": "IMIT Master",
    "msc imit": "IMIT Master",
    "imit master": "IMIT Master",
    "imit": "IMIT Master",
    "informationsmanagement und informationstechnologie": "IMIT Master",
    "informationsmanagement": "IMIT Master",
    "b.sc. imit": "IMIT Bachelor",
    "bsc imit": "IMIT Bachelor",
    "imit bachelor": "IMIT Bachelor",

    # WiInf
    "m.sc. wiinf": "Wirtschaftsinformatik Master",
    "msc wiinf": "Wirtschaftsinformatik Master",
    "wiinf master": "Wirtschaftsinformatik Master",
    "wiinf": "Wirtschaftsinformatik Master",
    "m.sc. winf": "Wirtschaftsinformatik Master",
    "msc winf": "Wirtschaftsinformatik Master",
    "winf master": "Wirtschaftsinformatik Master",
    "winf": "Wirtschaftsinformatik Master",
    "wirtschaftsinformatik": "Wirtschaftsinformatik Master",
    "wirtschaftsinformatik master": "Wirtschaftsinformatik Master",

    # Data Science
    "m.sc. data science": "Data Science Master",
    "msc data science": "Data Science Master",
    "data science": "Data Science Master",
    "data analytics": "Data Science Master",
    "m.sc. data analytics": "Data Science Master",
    "m.sc. ds": "Data Science Master",
    "msc ds": "Data Science Master",
    "ds master": "Data Science Master",
    "ds": "Data Science Master",
}

_CANONICAL_LOWER = {p.lower(): p for p in _UPLOAD}


def normalize_study_program(value: str) -> str:
    """Normalizes study program name or resolves common aliases and abbreviations."""
    if not value:
        return UNASSIGNED_PROGRAM
    clean = str(value).strip()
    if not clean or clean.lower() == "nan":
        return UNASSIGNED_PROGRAM
    if clean in _UPLOAD:
        return clean
    lower = clean.lower()
    if lower in _CANONICAL_LOWER:
        return _CANONICAL_LOWER[lower]
    if lower in PROGRAM_ALIASES:
        return PROGRAM_ALIASES[lower]
    return clean


def is_known_program(value: str) -> bool:
    """True for a named program or the upload placeholder."""
    return normalize_study_program(value) in _UPLOAD


def _named_program(value: object) -> str:
    name = normalize_study_program(str(value) if value is not None else "")
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
    normalized = normalize_study_program(name)
    if normalized not in _UPLOAD:
        raise ValueError("Study program must be chosen from the predefined list")
    return normalized


NamedStudyProgram = Annotated[StudyProgram, BeforeValidator(_named_program)]
OptionalStudyProgram = Annotated[StudyProgram | None, BeforeValidator(_optional_named_program)]
UploadStudyProgram = Annotated[str, BeforeValidator(_upload_program)]
