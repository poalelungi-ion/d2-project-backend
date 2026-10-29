"""Unit tests for numeric-only pass-fail parsing. No database."""
import pytest

from src.services.grade_outcome import (
    OUTCOME_EXCUSED,
    OUTCOME_FAILED,
    OUTCOME_PASSED,
    UnrecognizedGrade,
    evaluate_grade,
    is_filtered_status_code,
    is_ignored_column,
    is_valid_numeric_grade,
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


def test_status_codes_are_not_grades():
    for code in ("NE", "ne", "N.E.", "EX", "ex", "NA", "TA", "AT", "at"):
        assert is_filtered_status_code(code) is True
        with pytest.raises(UnrecognizedGrade, match="not grades"):
            evaluate_grade(code)


def test_empty_is_missing_not_a_status_code():
    assert is_filtered_status_code("") is False
    assert is_filtered_status_code(None) is False
    with pytest.raises(UnrecognizedGrade, match="Missing"):
        evaluate_grade("")


def test_passed_failed_yes_no_are_never_results():
    for label in ("Passed", "Failed", "Yes", "No", "passed", "YES"):
        with pytest.raises(UnrecognizedGrade):
            evaluate_grade(label)


def test_outcome_of_still_reads_stored_excused_sittings():
    assert outcome_of("AT", passed=False) == OUTCOME_EXCUSED
    assert outcome_of(None, passed=True) == OUTCOME_PASSED
    assert outcome_of("NE", passed=False) == OUTCOME_FAILED


def test_passed_column_names_are_ignored():
    assert is_ignored_column("Passed")
    assert is_ignored_column("YES")
    assert is_ignored_column("failed")
    assert not is_ignored_column("Grade")
    assert not is_ignored_column("Note")


def test_is_valid_numeric_grade_104085():
    """Ticket #104085: is_valid_numeric_grade correctly distinguishes 1.0-5.0 from missing/status/labels."""
    # Valid numeric German grades
    for val in ("1.0", 1.0, "1.3", 1.7, "2,3", "3.0", 4.0, "5.0", 5.0):
        assert is_valid_numeric_grade(val) is True, f"Expected {val} to be valid numeric grade"

    # Status / absence codes
    for code in ("NE", "ne", "N.E.", "EX", "ex", "NA", "TA", "AT", "at"):
        assert is_valid_numeric_grade(code) is False, f"Expected {code} to be excluded"

    # Missing / empty / NaN / None
    for empty in ("", "   ", None, "nan", "NaN", "None"):
        assert is_valid_numeric_grade(empty) is False, f"Expected {empty} to be excluded"

    # Ignored labels and arbitrary text
    for text in ("Passed", "Failed", "Yes", "No", "passed", "invalid", "abc", "-"):
        assert is_valid_numeric_grade(text) is False, f"Expected {text} to be excluded"

    # Out of range
    for out_of_range in (0.0, 0.9, "0.5", 5.1, "6.0", 10.0):
        assert is_valid_numeric_grade(out_of_range) is False, f"Expected {out_of_range} to be excluded"
