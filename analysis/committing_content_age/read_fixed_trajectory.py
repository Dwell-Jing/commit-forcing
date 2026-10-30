"""Validate and display reported fixed-trajectory recency aggregates."""

import argparse
import json
import math
from pathlib import Path


def validate(summary):
    if summary["statistics_recomputed"] or summary["per_prompt_values_included"]:
        raise ValueError("Expected reported aggregate values only")
    protocol = summary["protocol"]
    if (protocol["prompt_count"], protocol["generation_seeds"],
        protocol["reference_duration_seconds"], protocol["probe_after_blocks"]) != (
            20, [0, 1], 48, [20, 28, 36, 44, 52]):
        raise ValueError("Fixed-trajectory protocol differs from the report")
    if not protocol["fixed_clean_latent_trajectory_across_conditions"]:
        raise ValueError("This is the fixed-trajectory recency diagnostic")
    conditions = ["d=1", "d=2", "d=4", "d=8", "d=16", "Sink"]
    if summary["condition_order"] != conditions:
        raise ValueError("Unexpected condition coverage")
    metrics = set(summary["metric_definitions"])
    if len(metrics) != 6:
        raise ValueError("Expected six diagnostic metrics")
    mean_count = contrast_count = 0
    if {row["metric"] for row in summary["condition_means"]} != metrics:
        raise ValueError("Condition means have incomplete metric coverage")
    for row in summary["condition_means"]:
        if list(row["means"]) != conditions:
            raise ValueError("Condition means have incomplete route coverage")
        for cell in row["means"].values():
            if not math.isfinite(cell["mean"]) or float(cell["reported_mean"]) != cell["mean"]:
                raise ValueError("Invalid reported condition mean")
            mean_count += 1
    groups = (
        ("trajectory_context_contrasts", [f"d={d} minus d=1" for d in (2, 4, 8, 16)]),
        ("sink_contrasts_and_target_lag_slopes", [
            "Sink minus d=1", "Sink minus d=16", "Slope per doubling of d"]),
    )
    for key, names in groups:
        rows = summary[key]
        if len(rows) != 6 or {row["metric"] for row in rows} != metrics:
            raise ValueError("Contrasts have incomplete metric coverage")
        for row in rows:
            if list(row["contrasts"]) != names:
                raise ValueError("Contrasts have incomplete comparison coverage")
            for cell in row["contrasts"].values():
                value = cell["mean"]
                lo, hi = cell["interval_95"]
                if not all(math.isfinite(x) for x in (value, lo, hi)) or not lo <= value <= hi:
                    raise ValueError("Invalid reported estimate or interval")
                if float(cell["reported_mean"]) != value:
                    raise ValueError("Reported estimate precision differs")
                if list(map(float, cell["reported_interval_95"])) != [lo, hi]:
                    raise ValueError("Reported interval precision differs")
                if cell["reported_interval_excludes_zero"] != (lo > 0 or hi < 0):
                    raise ValueError("Reported significance differs from the interval")
                contrast_count += 1
    if (mean_count, contrast_count) != (36, 42):
        raise ValueError("Unexpected aggregate coverage")
    opening = next(row for row in summary["trajectory_context_contrasts"]
                   if row["metric"] == "Opening similarity")
    upper = opening["contrasts"]["d=16 minus d=1"]
    if upper["reported_interval_95"][1] != "-3.5e-5":
        raise ValueError("Preserve the small negative interval endpoint")
    for digest in summary["source_sha256"].values():
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid source hash")
    return mean_count, contrast_count


def table(headers, rows):
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join([":---"] * len(headers)) + " |",
        *["| " + " | ".join(row) + " |" for row in rows],
    ])


def estimate(cell):
    star = "*" if cell["reported_interval_excludes_zero"] else ""
    lo, hi = cell["reported_interval_95"]
    return f"{cell['reported_mean']}{star} [{lo}, {hi}]"


def markdown(summary):
    conditions = summary["condition_order"]
    parts = [
        "### Condition means", "",
        table(["Metric"] + conditions, [
            [row["metric"]] + [row["means"][c]["reported_mean"] for c in conditions]
            for row in summary["condition_means"]]), "",
    ]
    for title, key in (
        ("Trajectory context contrasts", "trajectory_context_contrasts"),
        ("Sink contrasts and target-lag slopes", "sink_contrasts_and_target_lag_slopes"),
    ):
        rows = summary[key]
        names = list(rows[0]["contrasts"])
        parts += ["### " + title, "", table(["Metric"] + names, [
            [row["metric"]] + [estimate(row["contrasts"][name]) for name in names]
            for row in rows]), ""]
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path,
                        default=Path(__file__).with_name("fixed_trajectory_summary.json"))
    parser.add_argument("--markdown", action="store_true",
                        help="Print the frozen aggregate tables.")
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    means, contrasts = validate(summary)
    if args.markdown:
        print(markdown(summary))
    else:
        print(f"Validated {means} condition means and {contrasts} reported contrasts/slopes.")
        print("Original diagnostic scales; no generation, scoring or bootstrap reconstruction.")


if __name__ == "__main__":
    main()
