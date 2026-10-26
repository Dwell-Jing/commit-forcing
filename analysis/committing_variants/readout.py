"""Check and print the reported aggregate committing-variant results."""

import argparse
import json
import math
from pathlib import Path


def check_metric(result, label):
    delta = result["delta"]
    if not math.isfinite(delta):
        raise ValueError(f"Non-finite aggregate: {label}")
    interval = result["interval_95"]
    decision = result["reported_interval_excludes_zero"]
    if decision not in (True, False, None):
        raise ValueError(f"Invalid significance decision: {label}")
    if interval is not None:
        if len(interval) != 2 or not all(math.isfinite(v) for v in interval):
            raise ValueError(f"Invalid recorded interval: {label}")
        lo, hi = interval
        if not lo <= delta <= hi:
            raise ValueError(f"Aggregate outside its recorded interval: {label}")
        if decision is not None and decision != (lo > 0 or hi < 0):
            raise ValueError(f"Recorded interval and decision disagree: {label}")
    return delta


def display(result):
    value = result.get("display", f'{result["delta"]:+.2f}')
    interval = result["interval_95"]
    if interval is not None:
        value += f" [{interval[0]:+.2f}, {interval[1]:+.2f}]"
    return value + ("*" if result["reported_interval_excludes_zero"] is True else "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path(__file__).with_name("summary.json"))
    summary = json.loads(parser.parse_args().summary.read_text())
    if summary["statistics_recomputed"] or summary["per_prompt_values_included"]:
        raise ValueError("Expected recorded aggregate values only")
    rows = summary["discovery_variants"]
    if len(rows) != 27 or len({row["id"] for row in rows}) != 27:
        raise ValueError("Expected 27 distinct discovery variants")
    reference = summary["reference_line"]
    slope = reference["slope_numerator"] / reference["slope_denominator"]
    if not math.isclose(slope, reference["slope"]):
        raise ValueError("Reference slope does not match its reported endpoints")
    negative, positive, including_zero = [], [], []
    count = 0
    print("ID\tDelta Dynamic\tDelta Subject c2c\tG [95% CI]\tDelta Quality [95% CI]")
    for row in rows:
        metrics = row["metrics"]
        for name, value in metrics.items():
            check_metric(value, f'{row["id"]}/{name}')
            count += 1
        # A rounding check, not a refit or a reconstruction of G intervals.
        g_rounded = metrics["Subject c2c"]["delta"] - slope * metrics["Dynamic Degree"]["delta"]
        if abs(g_rounded - metrics["G"]["delta"]) >= 0.008:
            raise ValueError(f'Recorded G inconsistent with rounded means: {row["id"]}')
        lo, hi = metrics["G"]["interval_95"]
        (negative if hi < 0 else positive if lo > 0 else including_zero).append(row["id"])
        print(row["id"] + "\t" + "\t".join(display(metrics[k]) for k in
              ("Dynamic Degree", "Subject c2c", "G", "Quality")))
    expected = summary["discovery_interval_summary"]
    if sorted(negative) != sorted(expected["below_zero_ids"]) or len(negative) != 5:
        raise ValueError("Below-zero discovery variants differ from the recorded set")
    if positive or len(including_zero) != 22:
        raise ValueError("Discovery interval counts differ from the recorded summary")
    for contrast in summary["additional_comparisons"]:
        print(f'\n{contrast["id"]}: {contrast["contrast"]}')
        for name, value in contrast["metrics"].items():
            check_metric(value, f'{contrast["id"]}/{name}')
            print(f"  {name}: {display(value)}")
            count += 1
    print(f"\nChecked {count} reported aggregate values; 22 G intervals include zero, 5 are below zero.")
    print("No generation, scoring or bootstrap reconstruction performed.")


if __name__ == "__main__":
    main()
