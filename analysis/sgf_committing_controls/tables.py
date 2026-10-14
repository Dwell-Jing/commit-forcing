#!/usr/bin/env python3
"""Display the reported pooled SGF contrasts without re-estimating intervals."""
import csv
from pathlib import Path


def main():
    source = Path(__file__).parent / "data" / "reported_contrasts.csv"
    with source.open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["seed"] == "pooled"]
    print("Reported pooled contrasts; scores ×100; *: paired interval excludes 0")
    print("contrast,metric,reported estimate [95% CI]")
    for row in rows:
        mark = "*" if row["significant"] == "true" else ""
        print(f'{row["contrast"]},{row["metric"]},{row["estimate"]}{mark} '
              f'[{row["ci95_low"]}, {row["ci95_high"]}]')


if __name__ == "__main__":
    main()
