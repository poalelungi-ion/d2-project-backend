"""Console summary for the pytest run, and the gate for the job.

Reads the JUnit XML for pass/fail counts and coverage.json for coverage, so the
job log carries the same tables the frontend pipeline prints.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET

from report_table import table

# Floor, not a target: the job fails if coverage drops below this. Raise it as
# tests land so the number can only ratchet upwards.
COVERAGE_FLOOR = float(os.environ.get("COVERAGE_FLOOR", "65"))


def fail(path, error, hint):
    print(f"Could not read {path}: {error}", file=sys.stderr)
    print(hint, file=sys.stderr)
    sys.exit(1)


def load_junit(path):
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        fail(path, error, "Did the pytest run crash before writing it?")
    suites = [root] if root.tag == "testsuite" else list(root)
    cases = [case for suite in suites for case in suite.findall("testcase")]
    return suites, cases


def load_coverage(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        fail(path, error, "Was pytest run with --cov-report=json?")


def main():
    junit_path = sys.argv[1] if len(sys.argv) > 1 else "junit.xml"
    coverage_path = sys.argv[2] if len(sys.argv) > 2 else "coverage.json"

    suites, cases = load_junit(junit_path)
    coverage = load_coverage(coverage_path)

    total = sum(int(s.get("tests", 0)) for s in suites)
    failures = sum(int(s.get("failures", 0)) for s in suites)
    errors = sum(int(s.get("errors", 0)) for s in suites)
    skipped = sum(int(s.get("skipped", 0)) for s in suites)
    duration = sum(float(s.get("time", 0)) for s in suites)
    passed = total - failures - errors - skipped

    print("\nUnit test report")
    table(
        [
            ["Test files", len({c.get("file") or c.get("classname", "") for c in cases})],
            ["Tests", total],
            ["Passed", passed],
            ["Failed", failures],
            ["Errors", errors],
            ["Skipped", skipped],
            ["Test time", f"{duration:.2f}s"],
        ],
        ["Metric", "Value"],
    )

    broken = [c for c in cases if c.find("failure") is not None or c.find("error") is not None]
    if broken:
        print("\nFailing tests:")
        for case in broken:
            problem = case.find("failure")
            if problem is None:
                problem = case.find("error")
            print(f"  {case.get('classname')}::{case.get('name')}")
            print(f"    {(problem.get('message') or '').splitlines()[0][:160]}")

    totals = coverage.get("totals", {})
    covered = totals.get("covered_lines", 0)
    statements = totals.get("num_statements", 0)
    # coverage.py folds branches into percent_covered when --cov-branch is on,
    # so derive line coverage explicitly to keep the headline number honest.
    percent = (covered / statements * 100) if statements else 0.0

    branches = totals.get("num_branches", 0)
    covered_branches = totals.get("covered_branches", 0)
    branch_pct = f"{covered_branches / branches * 100:.2f}%" if branches else "n/a"

    print("\nCoverage")
    table(
        [
            ["lines", f"{percent:.2f}%", f"{covered}/{statements}"],
            ["branches", branch_pct, f"{covered_branches}/{branches}"],
        ],
        ["Metric", "Percent", "Covered/Total"],
    )
    print(f"Uncovered lines: {totals.get('missing_lines', 0)}")

    files = sorted(
        (
            (path, float(data["summary"]["percent_covered"]), data["summary"]["num_statements"])
            for path, data in coverage.get("files", {}).items()
            if data["summary"]["num_statements"] > 0
        ),
        key=lambda row: (row[1], -row[2]),
    )[:10]

    if files:
        print("\nLeast covered files:")
        table([[p, f"{pct:.2f}%", n] for p, pct, n in files], ["File", "Lines %", "Statements"])

    # This exact line is what the GitLab `coverage:` regex scrapes.
    print(f"\nTotal coverage: {percent:.2f}%")

    problems = []
    if failures or errors:
        problems.append(f"{failures + errors} failing test(s)")
    if percent < COVERAGE_FLOOR:
        problems.append(f"line coverage {percent:.2f}% is below the {COVERAGE_FLOOR:g}% floor")

    if problems:
        print(f"\nFAILED: {'; '.join(problems)}.\n")
        sys.exit(1)

    print(f"\nPASSED: {passed} test(s) green, coverage at or above the {COVERAGE_FLOOR:g}% floor.\n")


if __name__ == "__main__":
    main()
