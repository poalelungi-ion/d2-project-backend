"""
Canonical spreadsheet headers for exam import.

Lecturers must use this closed list (English or German). We standardise each
header to one internal field. Unknown names are rejected so a typo cannot
silently land in the wrong column.
"""
from __future__ import annotations

from typing import Iterable

# Display form → internal field. Keys are matched after normalize_header().
_HEADER_TO_FIELD: dict[str, str] = {
    "name": "name",
    "full name": "name",
    "fullname": "name",
    "first name": "first_name",
    "firstname": "first_name",
    "vorname": "first_name",
    "last name": "last_name",
    "lastname": "last_name",
    "nachname": "last_name",
    "matrikelnr": "student_id",
    "matrnr": "student_id",
    "matrikelnummer": "student_id",
    "student id": "student_id",
    "studentid": "student_id",
    "studiengang": "program",
    "program": "program",
    "study program": "program",
    "fachsemester": "semester",
    "semester": "semester",
    "note": "grade",
    "grade": "grade",
}

FIELD_LABEL: dict[str, str] = {
    "student_id": "Matrikelnr",
    "name": "Name",
    "first_name": "First Name",
    "last_name": "Last Name",
    "program": "Studiengang",
    "semester": "Fachsemester",
    "grade": "Note",
}

CANONICAL_HEADERS: tuple[str, ...] = (
    "Matrikelnr",
    "Name",
    "First Name",
    "Last Name",
    "Studiengang",
    "Fachsemester",
    "Note",
)

ALLOWED_HEADERS_MESSAGE = (
    "Use the standard names: Matrikelnr, Name, First Name, Last Name, "
    "Studiengang, Fachsemester, Note (Grade, Program, Study Program, "
    "Vorname, Nachname, MatrNr and Full Name are also accepted). "
    "Pass/Fail and course columns are ignored."
)


def normalize_header(name: object) -> str:
    """Trim, collapse spaces, drop a trailing dot, and case-fold for lookup."""
    text = " ".join(str(name).strip().split())
    text = text.rstrip(".:")
    return text.casefold()


def field_for_header(name: object) -> str | None:
    """Internal field for a known header, or None if the name is not allowed."""
    return _HEADER_TO_FIELD.get(normalize_header(name))


class HeaderConflict(ValueError):
    """Two file columns standardised onto the same field."""


class UnrecognizedHeaders(ValueError):
    """File columns that are not in the closed list and not ignorable."""


def standardize_columns(
    columns: Iterable[object],
    *,
    ignorable: Iterable[object] | None = None,
) -> dict[str, str]:
    """
    Map original header → internal field.

    Ignorable headers (Passed/Failed, course identifiers) are omitted.
    Raises UnrecognizedHeaders or HeaderConflict.
    """
    skip = {normalize_header(name) for name in (ignorable or ())}
    rename: dict[str, str] = {}
    claimed: dict[str, str] = {}
    unknown: list[str] = []

    for raw in columns:
        original = str(raw)
        key = normalize_header(original)
        if not key or key in skip:
            continue
        if key.startswith("unnamed"):
            continue
        field = _HEADER_TO_FIELD.get(key)
        if field is None:
            unknown.append(original.strip() or original)
            continue
        previous = claimed.get(field)
        if previous is not None:
            label = FIELD_LABEL.get(field, field)
            raise HeaderConflict(
                f"Columns '{previous}' and '{original.strip()}' both standardise "
                f"to {label}. Keep exactly one."
            )
        claimed[field] = original.strip() or original
        rename[original] = field

    if unknown:
        shown = ", ".join(unknown)
        raise UnrecognizedHeaders(
            f"Unrecognized column(s): {shown}. {ALLOWED_HEADERS_MESSAGE}"
        )
    return rename
