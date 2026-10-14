#!/usr/bin/env python3
"""Print reported Rolling Sink contrasts; this does not recompute confidence intervals.

Original per-video inputs are not included. See README.md and data/provenance.json.
"""
import csv
from pathlib import Path


def main():
    path = Path(__file__).resolve().parent / "data" / "reported_contrasts.csv"
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    print("Rolling Sink, 48 s: reported RS_real - RS_off contrasts (40 pairs, 20 prompts x 2 seeds)")
    print("Original diagnostic scales; intervals transcribed, not re-estimated.\n")
    for row in rows:
        print(f"{row['metric']}: {row['estimate']} [{row['ci_low']}, {row['ci_high']}]")
        print(f"  {row['reported_significance']}; source: {row['source']}")


if __name__ == "__main__":
    main()
