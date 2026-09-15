"""
Semester parsing and chronological sorting utilities.
Ensures semesters are sequenced chronologically (e.g., WiSe23/24 before SoSe24)
rather than by alphabetical string order.
"""
import re
from typing import Tuple


def parse_semester(s: str) -> Tuple[int, int]:
    """
    Parses a semester string into (calendar_year, term_order).

    Academic terms in Germany:
      - Sommersemester (SoSe / SS / Summer): starts in Spring (~April) -> term_order = 1
      - Wintersemester (WiSe / WS / Winter): starts in Fall (~October) of the given year -> term_order = 2

    Chronological timeline examples:
      - WiSe23/24 (starts Oct 2023) -> (2023, 2)
      - SoSe24    (starts Apr 2024) -> (2024, 1)  [comes AFTER WiSe23/24]
      - WiSe24/25 (starts Oct 2024) -> (2024, 2)
      - SOSE_25   (starts Apr 2025) -> (2025, 1)
      - WISE_25   (starts Oct 2025) -> (2025, 2)
      - SOSE_26   (starts Apr 2026) -> (2026, 1)
      - WISE_26   (starts Oct 2026) -> (2026, 2)
    """
    if not s:
        return (0, 0)

    clean = str(s).strip()
    upper = clean.upper()

    # Determine term: Winter (2) vs Summer (1)
    if upper.startswith("W") or "WISE" in upper or "WS" in upper or "WINTER" in upper:
        term_order = 2
    elif upper.startswith("S") or "SOSE" in upper or "SS" in upper or "SOMMER" in upper or "SUMMER" in upper:
        term_order = 1
    else:
        term_order = 0

    # Extract the starting calendar year
    numbers = re.findall(r"\d+", clean)
    if numbers:
        raw_year = int(numbers[0])
        # Two-digit year expansion: 23 -> 2023, 99 -> 1999
        if raw_year < 100:
            year = 2000 + raw_year if raw_year <= 70 else 1900 + raw_year
        else:
            year = raw_year
    else:
        year = 0

    return (year, term_order)


def semester_sort_key(s: str) -> Tuple[int, int, str]:
    """Sort key tuple enabling chronological comparisons."""
    year, term = parse_semester(s)
    return (year, term, str(s))
