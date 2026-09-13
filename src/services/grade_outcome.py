"""
Single source of truth for pass/fail.

Numeric German grades (1.0–5.0, pass is <= 4.0) and official absence codes in
the grade cell decide the outcome. Labels such as Passed/Failed/Yes/No are
never interpreted as a result — they are noise from source spreadsheets.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

OUTCOME_PASSED = "passed"
OUTCOME_FAILED = "failed"
OUTCOME_EXCUSED = "excused"

# NE = no show, EX = disqualified → fail. AT = medical note → excused.
FAIL_ABSENCE_CODES = frozenset({"NE", "EX"})
EXCUSED_ABSENCE_CODES = frozenset({"AT"})

# Spreadsheet columns or grade-cell labels the parser must never treat as a result.
IGNORED_RESULT_LABELS = frozenset({"PASSED", "FAILED", "YES", "NO"})
IGNORED_COLUMN_NAMES = frozenset({"passed", "failed", "yes", "no"})


@dataclass(frozen=True)
class GradeVerdict:
    """What the system stores and displays for one exam sitting."""

    grade: Optional[float]
    passed: bool
    outcome: str
    absence_code: Optional[str]


class UnrecognizedGrade(ValueError):
    """The cell was not a numeric grade and not NE/EX/AT."""


def _normalize_code(raw: str) -> str:
    return raw.strip().upper().replace(".", "").replace(" ", "")


def evaluate_grade(raw: object) -> GradeVerdict:
    """
    Interpret one grade cell.

    NE/EX → fail (recorded as 5.0). AT → excused (no numeric grade).
    A number in 1.0–5.0 → pass iff it is <= 4.0.
    Passed/Failed/Yes/No and anything else raise UnrecognizedGrade.
    """
    if raw is None:
        raise UnrecognizedGrade("Missing grade")

    text = str(raw).strip()
    if not text or text.lower() == "nan":
        raise UnrecognizedGrade("Missing grade")

    code = _normalize_code(text)
    if code in IGNORED_RESULT_LABELS:
        raise UnrecognizedGrade(
            "Pass/fail labels are ignored; provide a numeric grade or NE/EX/AT"
        )
    if code in FAIL_ABSENCE_CODES:
        return GradeVerdict(grade=5.0, passed=False, outcome=OUTCOME_FAILED, absence_code=code)
    if code in EXCUSED_ABSENCE_CODES:
        return GradeVerdict(grade=None, passed=False, outcome=OUTCOME_EXCUSED, absence_code=code)

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
