"""Check and print reported window-effect aggregates without re-estimation."""

import argparse
import json
import math
from pathlib import Path


def check_metric(metric, name):
    delta = metric["delta"]
    if not math.isfinite(delta):
        raise ValueError(f"Non-finite aggregate: {name}")
    interval = metric["interval_95"]
    decision = metric["reported_interval_excludes_zero"]
    if decision not in (True, False, None):
        raise ValueError(f"Invalid reported decision: {name}")
    if interval is not None:
        if len(interval) != 2 or not all(math.isfinite(v) for v in interval):
            raise ValueError(f"Invalid interval: {name}")
        lo, hi = interval
        if not lo <= delta <= hi:
            raise ValueError(f"Aggregate outside interval: {name}")
        if decision is not None and decision != (lo > 0 or hi < 0):
            raise ValueError(f"Interval and reported decision disagree: {name}")
    precision = metric.get("display_decimals", 2)
    suffix = "" if interval is None else f" [{interval[0]:+.{precision}f}, {interval[1]:+.{precision}f}]"
    status = "unreported" if decision is None else "excludes zero" if decision else "includes zero"
    print(f"  {name}: {delta:+.{precision}f}{suffix} ({status})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path(__file__).with_name("summary.json"))
    summary = json.loads(parser.parse_args().summary.read_text())
    if summary["statistics_recomputed"] or summary["per_prompt_values_included"]:
        raise ValueError("Expected reported aggregate values only")
    rows = summary["pooling_arms"]
    if len(rows) != 4 or {row["code"] for row in rows} != {"CG", "CM16", "SG16", "CM64"}:
        raise ValueError("Expected four distinct spatial-pooling arms")
    norm = summary["norm_measurement"]
    if not norm["measured_independently_of_outcome_scores"] or norm["is_stored_KV_tensor_norm"] or norm["inferred_from_effect_fractions"]:
        raise ValueError("Correction norm has the wrong measurement meaning")
    if norm["dtype"] != "float32" or norm["layers"] != 30 or norm["post_startup_committing_passes_per_video"] != 79:
        raise ValueError("Correction measurement protocol differs from the recorded one")
    plot = summary["plot_semantics"]
    if plot["observed_arms"] != 4 or plot["observed_points"] != 8 or plot["normalization_endpoints_are_additional_observations"]:
        raise ValueError("Normalization endpoints must not count as observed effects")
    if summary["pooling_protocol"]["prompt_count"] != 100 or summary["effect_normalization"]["self_only_reference_prompt_count"] != 200:
        raise ValueError("Variant and normalization prompt counts must stay distinct")
    print("Arm\tCorrection\tConsistency gain\tMotion suppression")
    for row in rows:
        values = [row[key] for key in ("retained_correction", "retained_consistency_gain", "retained_motion_suppression")]
        if not all(math.isfinite(v) and 0 <= v <= 1 for v in values):
            raise ValueError(f"Invalid reported retention fraction: {row['code']}")
        print(row["code"] + "\t" + "\t".join(f"{value:.2f}" for value in values))
    print("\nPlateau comparison")
    for name, metric in summary["plateau"]["metrics"].items():
        check_metric(metric, name)
    print("\nDeep-layer KV mechanism control")
    for name, metric in summary["deep_KV_confirmation"]["metrics"].items():
        check_metric(metric, name)
    print("\nSelf-only minus full recent-context, same confirmation seeds 2/3")
    check_metric(summary["deep_KV_confirmation"]["self_only_minus_full_recent_context"], "Subject c2c")
    sink = summary["decline_controls"]["pooled_sink_variant"]
    print("\nFP16 minus recent-context")
    for name, metric in sink["metrics"].items():
        check_metric(metric, name)
    print("\nFP16 minus FR")
    for name, metric in sink["improvement_over_unaveraged_FR"].items():
        check_metric(metric, name)
    print("\nChecked 12 retention fractions and 10 reported comparison values.")
    print("No fractions, confidence intervals or evaluation statistics re-estimated.")


if __name__ == "__main__":
    main()
