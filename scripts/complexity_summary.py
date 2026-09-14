"""Console summary for the ruff code quality report, and the gate for the job.

Only the complexity budgets fail the pipeline; other ruff findings are reported
but non-blocking.
"""

import json
import os
import sys

from report_table import table

COMPLEXITY_RULES = {"C901", "PLR0912", "PLR0913", "PLR0915"}


def load(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        print(f"Could not read {path}: {error}", file=sys.stderr)
        print("Did the ruff run crash before writing it?", file=sys.stderr)
        sys.exit(1)


def rule_of(finding):
    return finding.get("check_name", "")


def line_of(finding):
    location = finding.get("location", {})
    if "lines" in location:
        return location["lines"].get("begin", 0)
    return location.get("positions", {}).get("begin", {}).get("line", 0)


def counts(items, key):
    tally = {}
    for item in items:
        tally[key(item)] = tally.get(key(item), 0) + 1
    return sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))


def main():
    report_path = sys.argv[1] if len(sys.argv) > 1 else "gl-code-quality-report.json"
    findings = load(report_path)

    complexity = [f for f in findings if rule_of(f) in COMPLEXITY_RULES]
    other = [f for f in findings if rule_of(f) not in COMPLEXITY_RULES]

    print("\nComplexity report")

    if not complexity:
        print("No complexity budgets exceeded.")
    else:
        table(counts(complexity, rule_of), ["Rule", "Violations"])

        print("\nHotspots (files with the most violations):")
        table(counts(complexity, lambda f: f["location"]["path"])[:10], ["File", "Violations"])

        print("\nDetails:")
        for finding in sorted(complexity, key=lambda f: (f["location"]["path"], line_of(f))):
            print(f"  {finding['location']['path']}:{line_of(finding)}  {finding['description']}")

    files = {f["location"]["path"] for f in findings}
    print(f"\nTotal: {len(complexity)} complexity finding(s), "
          f"{len(other)} other lint finding(s) across {len(files)} file(s).")

    if other:
        print(f"Note: the {len(other)} other lint finding(s) are reported in the code quality "
              "report but do not fail this job.")

    # Only the complexity budgets gate the pipeline.
    if complexity:
        print(f"\nFAILED: {len(complexity)} complexity budget violation(s). Split the offending "
              "unit(s) or raise the budget in ruff.ci.toml.\n")
        sys.exit(1)

    print("\nPASSED: all complexity budgets met.\n")


if __name__ == "__main__":
    main()
