"""Unit tests for strict import header standardisation. No database."""
import pytest

from src.lib.column_names import (
    HeaderConflict,
    UnrecognizedHeaders,
    field_for_header,
    normalize_header,
    standardize_columns,
)


def test_normalize_header_trims_and_drops_trailing_dot():
    assert normalize_header("  Matrikelnr.  ") == "matrikelnr"
    assert normalize_header("Full  Name") == "full name"


def test_known_aliases_standardise_to_internal_fields():
    assert field_for_header("Name") == "name"
    assert field_for_header("note") == "grade"
    assert field_for_header("MatrNr") == "student_id"
    assert field_for_header("Study Program") == "program"


def test_unknown_header_is_rejected():
    with pytest.raises(UnrecognizedHeaders, match="Email"):
        standardize_columns(["Matrikelnr", "Name", "Grade", "Email"])


def test_two_columns_for_the_same_field_conflict():
    with pytest.raises(HeaderConflict, match="Name"):
        standardize_columns(["Name", "Full Name", "Grade", "Matrikelnr"])


def test_passed_and_unnamed_columns_are_skipped_when_marked_ignorable():
    rename = standardize_columns(
        ["Matrikelnr", "Name", "Grade", "Passed", "Unnamed: 0"],
        ignorable=["Passed"],
    )
    assert rename == {
        "Matrikelnr": "student_id",
        "Name": "name",
        "Grade": "grade",
    }


def test_note_and_grade_cannot_both_be_present():
    with pytest.raises(HeaderConflict, match="Note"):
        standardize_columns(["Matrikelnr", "Name", "Note", "Grade"])
