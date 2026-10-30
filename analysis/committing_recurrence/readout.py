#!/usr/bin/env python3
"""Read the fixed-latent recurrence report without recomputing statistics."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_summary(report):
    require(report["schema_version"] == 1, "Unsupported schema")
    require(report["source_kind"] == "local manuscript working-tree snapshot", "Source kind changed")
    require(report["source_date"] == "2026-10-30", "Source date changed")
    require(report["export_scope"] == "reported aggregate values only", "Export scope changed")
    require(report["statistics_recomputed"] is False, "Statistics must remain reported values")
    require(report["per_prompt_values_included"] is False, "No per-prompt export is expected")
    require(report["latent_or_kv_arrays_included"] is False, "No latent or KV arrays are expected")
    for source in report["source_files"]:
        path = Path(source["path"])
        require(not path.is_absolute() and ".." not in path.parts, "Unsafe source path")
        digest = source["sha256"]
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "Invalid source hash")
    require(report["active_input"] == {"file": "main.tex", "input": "appendix/committing-recurrence"},
            "Active input relationship changed")
    protocol = report["protocol"]
    expected = {
        "prompt_count": 20, "generation_seed": 0, "duration_seconds": 60,
        "trajectory_blocks": 80, "layers": 30, "physical_cache_frames": 12,
        "committing_timestep": 0, "content_and_single_read_positions": [20, 40],
        "content_and_single_read_lags": [1, 32], "sink_change_blocks": [1, 79],
        "bootstrap_draws": 4000,
    }
    for key, value in expected.items():
        require(protocol[key] == value, "Protocol changed: " + key)
    require(protocol["prompt_indices"] == [i for i in range(21) if i != 5], "Prompt list changed")
    require(protocol["cache_slots"] == {"sink": 3, "recent": 6, "current": 3}, "Cache slots changed")
    counts = report["entry_comparisons"]
    require(counts["content_change_per_policy"] == 20 * 2 * 32 == 1280, "Content count mismatch")
    require(counts["sink_change_per_policy"] == 20 * 79 == 1580, "Sink count mismatch")
    require(counts["policies_per_counted_intervention"] == 3, "Policy count mismatch")
    require(counts["total"] == 3 * (1280 + 1580) == 8580, "Total count mismatch")
    require(counts["includes_single_sink_read"] is False, "8,580 must exclude single-sink-read curves")
    results = report["reported_results"]
    require(results["content_change"]["commit_forcing"]["exact_zero_from_lag"] == 30,
            "Content cutoff must be lag 30")
    require(results["content_change"]["base"]["lag32_mean_kv_difference"] == "0.0052",
            "Base content residual changed")
    require(results["sink_change"]["commit_forcing"]["means_by_block"] == {
        "1": "0.42", "5": "0.023", "10": "0.0088"}, "Sink-response means changed")
    require(results["sink_change"]["commit_forcing"]["exact_zero_from_block"] == 30,
            "Sink-change cutoff must be block 30")
    require(results["sink_change"]["base"]["mean_over_blocks_1_to_79"] == "0.29",
            "Base sink response changed")
    require(results["single_sink_read"]["commit_forcing"]["means_by_lag"] == {
        "1": "0.28", "2": "0.13", "3": "0.055", "4": "0.028"}, "Single-read means changed")
    require(results["single_sink_read"]["commit_forcing"]["exact_zero_from_lag"] == 29,
            "Single-read cutoff must be lag 29")
    require(results["single_sink_read"]["two_block_control"]["lag32_mean_v_difference"] == "0.007",
            "Two-block residual changed")
    require(results["self_only"]["all_subsequent_entries_exact_zero"] is True
            and len(results["self_only"]["interventions"]) == 3, "Self-only result changed")
    require(report["measurement"]["denominator_floor"] == "1e-12", "Normalization changed")
    require(report["measurement"]["comparison_dtype"] == "float32", "Comparison dtype changed")
    require(report["theorem"]["free_generation_forgetting_bound"] is False,
            "Fixed-block proposition cannot become a free-generation forgetting bound")


def read_columns(path):
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for key, value in row.items():
            row[key] = float(value)
            require(math.isfinite(row[key]) and row[key] >= 0, "Invalid aggregate value")
    return rows


def validate_plot_inputs(report):
    paths = {}
    for entry in report["aggregate_plot_inputs"]:
        relative = Path(entry["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe plot-input path")
        path = REPO / relative
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                "Aggregate input changed: " + entry["path"])
        paths[path.name] = path
    require(set(paths) == {"staircase_O.csv", "staircase_N.csv", "sink_curves.csv", "impulse6_own.csv"},
            "Unexpected plot-input set")
    for name, two_blocks in (("staircase_O.csv", False), ("staircase_N.csv", True)):
        with paths[name].open(newline="", encoding="utf-8") as stream:
            matrix = [[float(value) for value in row] for row in csv.reader(
                line for line in stream if not line.startswith("#"))]
        require(len(matrix) == 32 and all(len(row) == 30 for row in matrix), "Layer-map shape changed")
        for lag, row in enumerate(matrix, start=1):
            first_possible_layer = (lag + 1) // 2 if two_blocks else lag
            for layer, value in enumerate(row):
                require(math.isfinite(value) and value >= 0, "Invalid layer-map value")
                require((value == 0) == (layer < first_possible_layer),
                        "Aggregate layer-map zero boundary changed: " + name)
    sink = read_columns(paths["sink_curves.csv"])
    require([row["block"] for row in sink] == list(range(1, 80)), "Sink block coverage changed")
    for row in sink:
        require((row["O_mean"] == 0) == (row["block"] >= 30), "Sink-response cutoff changed")
        require(row["N_mean"] > 0, "Base sink response unexpectedly zero")
    impulse = read_columns(paths["impulse6_own.csv"])
    require([row["lag"] for row in impulse] == list(range(1, 33)), "Single-read lag coverage changed")
    for row in impulse:
        for policy in ("O", "R9"):
            mean, low, high = (row[policy + suffix] for suffix in ("_v", "_v_low", "_v_high"))
            require(low <= mean <= high, "Reported interval does not contain reported mean")
        require((row["O_v"] == 0) == (row["lag"] >= 29), "Single-read cutoff changed")
        if row["lag"] >= 29:
            require(row["O_v_low"] == row["O_v_high"] == 0, "Exact-zero endpoints changed")
        require(row["R9_v"] > 0, "Two-block single-read response unexpectedly zero")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=HERE / "summary.json")
    args = parser.parse_args()
    report = json.loads(args.summary.read_text(encoding="utf-8"))
    validate_summary(report)
    validate_plot_inputs(report)
    print("Fixed-latent recurrence: summary and four aggregate plot inputs validated.")
    print("Source: 2026-10-30 local manuscript working tree; 20 prompts, seed 0, 60 s, 30 layers.")
    print("8,580 reported entry comparisons: content change + sink change (single sink read is separate).")
    print()
    print("Intervention          Commit Forcing                      Control / base")
    print("Content change        exact 0 from lag 30                 base: 0.0052 at lag 32")
    print("Sink change           0.42 / 0.023 / 0.0088 at 1 / 5 / 10 base: mean 0.29 over blocks 1–79")
    print("Single sink read      0.28 / 0.13 / 0.055 / 0.028          two blocks: 0.007 at lag 32")
    print("                      exact 0 from lag 29")
    print("Self-only             all subsequent entries exactly 0 in all three interventions")
    print()
    print("Scales: dimensionless relative L2; single-sink-read curve measures V, not mean K/V.")
    print("The reader checks aggregate zero masks and stored intervals; it does not rerun the 8,580 raw comparisons.")
    print("No statistics or intervals recomputed. Fixed clean latents do not imply a free-generation forgetting bound.")


if __name__ == "__main__":
    main()
