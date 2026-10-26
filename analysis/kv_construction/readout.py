"""Check and print reported aggregate contrasts, without re-estimating statistics."""

import argparse
import json
import math
from pathlib import Path


def read_summary(path):
    summary = json.loads(path.read_text())
    if summary["statistics_recomputed"] or summary["per_prompt_values_included"]:
        raise ValueError("Expected an aggregate-only transcription")
    count = 0
    for experiment in summary["experiments"]:
        print(f"\n{experiment['id']} ({experiment['scale']})")
        for contrast in experiment["contrasts"]:
            print(contrast["label"])
            for metric, result in contrast["metrics"].items():
                delta = result["delta"]
                if not math.isfinite(delta):
                    raise ValueError(f"Non-finite delta: {metric}")
                interval = result["interval_95"]
                significant = result["reported_interval_excludes_zero"]
                if significant not in (True, False, None):
                    raise ValueError(f"Invalid reported decision: {metric}")
                suffix = ""
                if interval is not None:
                    if len(interval) != 2 or not all(math.isfinite(x) for x in interval):
                        raise ValueError(f"Invalid interval: {metric}")
                    lo, hi = interval
                    if not lo <= delta <= hi:
                        raise ValueError(f"Delta outside recorded interval: {metric}")
                    # Display rounding may turn a nonzero endpoint into 0.00.
                    if significant is True and lo < 0 < hi:
                        raise ValueError(f"Reported decision conflicts with interval: {metric}")
                    if significant is False and not lo <= 0 <= hi:
                        raise ValueError(f"Reported decision conflicts with interval: {metric}")
                    suffix = f" [{lo:+g}, {hi:+g}]"
                marker = "*" if significant is True else ""
                print(f"  {metric}: {delta:+g}{marker}{suffix}")
                count += 1
    print(f"\nChecked {count} reported aggregate values; no statistics recomputed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path(__file__).with_name("summary.json"))
    args = parser.parse_args()
    read_summary(args.summary)


if __name__ == "__main__":
    main()
