"""Unit tests for numeric / absence-code pass-fail parsing. No database."""
import pytest

from src.services.grade_outcome import (
    OUTCOME_EXCUSED,
    OUTCOME_FAILED,
    OUTCOME_PASSED,
    UnrecognizedGrade,
    evaluate_grade,
    is_ignored_column,
    outcome_of,
)


def test_numeric_pass_and_fail():
    passed = evaluate_grade("2.3")
    assert passed.grade == 2.3
    assert passed.passed is True
    assert passed.outcome == OUTCOME_PASSED
    assert passed.absence_code is None

    failed = evaluate_grade(5.0)
    assert failed.passed is False
    assert failed.outcome == OUTCOME_FAILED
    assert failed.grade == 5.0


def test_pass_boundary_is_four():
    assert evaluate_grade("4.0").passed is True
    assert evaluate_grade("4.3").passed is False


def test_ne_and_ex_are_fails():
    for code in ("NE", "ne", "N.E.", "EX", "ex"):
        verdict = evaluate_grade(code)
        assert verdict.passed is False
        assert verdict.outcome == OUTCOME_FAILED
        assert verdict.grade == 5.0
        assert verdict.absence_code in {"NE", "EX"}


def test_at_is_excused_without_a_numeric_grade():
    verdict = evaluate_grade("AT")
    assert verdict.outcome == OUTCOME_EXCUSED
    assert verdict.passed is False
    assert verdict.grade is None
    assert verdict.absence_code == "AT"


def test_passed_failed_yes_no_are_never_results():
    for label in ("Passed", "Failed", "Yes", "No", "passed", "YES"):
        with pytest.raises(UnrecognizedGrade):
            evaluate_grade(label)


def test_outcome_of_prefers_excused_over_the_passed_flag():
    assert outcome_of("AT", passed=False) == OUTCOME_EXCUSED
    assert outcome_of(None, passed=True) == OUTCOME_PASSED
    assert outcome_of("NE", passed=False) == OUTCOME_FAILED


def test_passed_column_names_are_ignored():
    assert is_ignored_column("Passed")
    assert is_ignored_column("YES")
    assert is_ignored_column("failed")
    assert not is_ignored_column("Grade")
    assert not is_ignored_column("Note")
