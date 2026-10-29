"""
Single source of truth for pass/fail.

Only numeric German grades (1.0–5.0, pass is <= 4.0) are tracked. Status codes
such as NE, EX, NA, TA and AT are not grades — they are filtered out of import
and rejected on save.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

OUTCOME_PASSED = "passed"
OUTCOME_FAILED = "failed"
OUTCOME_EXCUSED = "excused"

# Grade-cell values that must not enter tracking.
FILTERED_STATUS_CODES = frozenset({"NE", "EX", "NA", "TA", "AT"})

# Spreadsheet columns or grade-cell labels the parser must never treat as a result.
IGNORED_RESULT_LABELS = frozenset({"PASSED", "FAILED", "YES", "NO"})
IGNORED_COLUMN_NAMES = frozenset({"passed", "failed", "yes", "no"})

STATUS_CODE_MESSAGE = (
    "Status codes such as NE, EX, NA and TA are not grades; "
    "only numeric marks from 1.0 to 5.0 are tracked"
)


@dataclass(frozen=True)
class GradeVerdict:
    """What the system stores and displays for one exam sitting."""

    grade: Optional[float]
    passed: bool
    outcome: str
    absence_code: Optional[str]


class UnrecognizedGrade(ValueError):
    """The cell was not a numeric grade on the 1.0–5.0 scale."""


def _normalize_code(raw: str) -> str:
    return raw.strip().upper().replace(".", "").replace(" ", "")


def is_filtered_status_code(raw: object) -> bool:
    """True for NE/EX/NA/TA/AT (any punctuation or case). Empty cells are not status codes."""
    if raw is None:
        return False
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return False
    return _normalize_code(text) in FILTERED_STATUS_CODES


def evaluate_grade(raw: object) -> GradeVerdict:
    """
    Interpret one grade cell.

    A number in 1.0–5.0 → pass iff it is <= 4.0.
    Status codes (NE, EX, NA, TA, AT), Pass/Fail labels, and anything else
    raise UnrecognizedGrade.
    """
    if raw is None:
        raise UnrecognizedGrade("Missing grade")

    text = str(raw).strip()
    if not text or text.lower() == "nan":
        raise UnrecognizedGrade("Missing grade")

    code = _normalize_code(text)
    if code in IGNORED_RESULT_LABELS:
        raise UnrecognizedGrade(
            "Pass/fail labels are ignored; provide a numeric grade from 1.0 to 5.0"
        )
    if code in FILTERED_STATUS_CODES:
        raise UnrecognizedGrade(STATUS_CODE_MESSAGE)

    try:
        grade = float(text.replace(",", "."))
    except ValueError as exc:
        raise UnrecognizedGrade(f"Unrecognized grade {text!r}") from exc

    if not 1.0 <= grade <= 5.0:
        raise UnrecognizedGrade("Grade must be between 1.0 and 5.0")

    passed = grade <= 4.0
    return GradeVerdict(
        grade=grade,
        passed=passed,
        outcome=OUTCOME_PASSED if passed else OUTCOME_FAILED,
        absence_code=None,
    )


def outcome_of(absence_code: Optional[str], passed: bool) -> str:
    """Rebuild the display outcome from a stored result."""
    if (absence_code or "").upper() == "AT":
        return OUTCOME_EXCUSED
    return OUTCOME_PASSED if passed else OUTCOME_FAILED


def is_excused(absence_code: Optional[str]) -> bool:
    return (absence_code or "").upper() == "AT"


def is_ignored_column(name: object) -> bool:
    return str(name).strip().lower() in IGNORED_COLUMN_NAMES


def counted_attempts(results: Iterable) -> list:
    """Sittings that count toward pass rate and at-risk — medical notes do not."""
    return [r for r in results if not is_excused(getattr(r, "absence_code", None))]


def mean_grade(results: Iterable) -> float:
    grades = [r.grade for r in results if getattr(r, "grade", None) is not None]
    return sum(grades) / len(grades) if grades else 0.0


def result_outcome_fields(result) -> dict:
    """passed stays for compatibility; outcome is the display source of truth."""
    absence = getattr(result, "absence_code", None)
    passed = bool(getattr(result, "passed", False))
    return {
        "passed": passed,
        "outcome": outcome_of(absence, passed),
        "absence_code": absence,
    }
