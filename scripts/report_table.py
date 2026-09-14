"""Shared console helpers for the CI summary scripts."""


def table(rows, headers):
    rows = [[str(cell) for cell in row] for row in rows]
    widths = [max(len(str(h)), *(len(r[i]) for r in rows)) if rows else len(str(h))
              for i, h in enumerate(headers)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    line = lambda r: "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(r)) + " |"
    print(sep)
    print(line([str(h) for h in headers]))
    print(sep)
    for row in rows:
        print(line(row))
    print(sep)
