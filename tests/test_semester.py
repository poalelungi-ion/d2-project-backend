"""
Tests for semester parsing, chronological comparison, and dashboard sorting (Ticket #99881).
"""
import pytest
from src.services.semester import parse_semester, semester_sort_key


def test_parse_semester_winter_and_summer():
    # WiSe23/24 starts in Oct 2023 -> year 2023, term 2
    assert parse_semester("WiSe23/24") == (2023, 2)
    assert parse_semester("WiSe 23/24") == (2023, 2)
    assert parse_semester("WISE_23") == (2023, 2)

    # SoSe24 starts in Apr 2024 -> year 2024, term 1
    assert parse_semester("SoSe24") == (2024, 1)
    assert parse_semester("SoSe 24") == (2024, 1)
    assert parse_semester("SOSE_24") == (2024, 1)

    # WiSe24/25
    assert parse_semester("WiSe24/25") == (2024, 2)
    assert parse_semester("WISE_24") == (2024, 2)

    # SOSE_25 and WISE_25
    assert parse_semester("SOSE_25") == (2025, 1)
    assert parse_semester("WISE_25") == (2025, 2)

    # SOSE_26 and WISE_26
    assert parse_semester("SOSE_26") == (2026, 1)
    assert parse_semester("WISE_26") == (2026, 2)


def test_chronological_sorting_resolves_alphabetical_anomaly():
    """
    Ticket #99881:
    Alphabetical sort erroneously places SoSe24 before WiSe23/24 ('S' < 'W').
    Chronological sort must place WiSe23/24 (starts Oct 2023) BEFORE SoSe24 (starts Apr 2024).
    """
    semesters = ["SOSE_25", "WISE_25", "SOSE_26", "WiSe23/24", "SoSe24", "WiSe24/25"]

    # Alphabetical sort (the bug):
    alpha_sorted = sorted(semesters)
    assert alpha_sorted == ['SOSE_25', 'SOSE_26', 'SoSe24', 'WISE_25', 'WiSe23/24', 'WiSe24/25']
    # In alphabetical sort, SoSe24 came before WiSe23/24!
    assert alpha_sorted.index("SoSe24") < alpha_sorted.index("WiSe23/24")

    # Chronological sort (the fix):
    chrono_sorted = sorted(semesters, key=semester_sort_key)
    assert chrono_sorted == [
        "WiSe23/24",  # Oct 2023
        "SoSe24",     # Apr 2024
        "WiSe24/25",  # Oct 2024
        "SOSE_25",    # Apr 2025
        "WISE_25",    # Oct 2025
        "SOSE_26",    # Apr 2026
    ]
    # WiSe23/24 is correctly before SoSe24!
    assert chrono_sorted.index("WiSe23/24") < chrono_sorted.index("SoSe24")


def test_empty_and_unknown_formats():
    assert parse_semester("") == (0, 0)
    assert parse_semester(None) == (0, 0)
    assert semester_sort_key("Unknown")[0] == 0
