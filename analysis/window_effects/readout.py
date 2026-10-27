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
    window = summary["committing_window"]
    if (window["prompt_count"], window["duration_seconds"], window["generation_seed"], window["reference_h"]) != (200, 60, 0, 1):
        raise ValueError("Window protocol differs from the reported comparison")
    if not window["h_excludes_current_block"] or window["panels_pool_samples"] or window["error_bars_reconstructed"]:
        raise ValueError("Window and correction panels must retain their separate definitions")
    expected = [(0, 3, 86.21, -1.00), (1, 6, 87.21, 0.00), (2, 9, 87.23, 0.02), (3, 12, 86.93, -0.28)]
    actual = [(r["h"], r["latent_frames"], r["subject_c2c_mean"], r["change_from_h1"]) for r in window["rows"]]
    if actual != expected:
        raise ValueError("Window aggregates differ from the frozen reported means")
    base = window["base"]
    if (base["subject_c2c_mean"], base["change_from_h1"], base["sink_frames"],
        base["latest_trajectory_frames_including_current"], base["current_frames"], base["physical_cache_frames"]) != (86.01, -1.20, 3, 9, 3, 15):
        raise ValueError("Base is a separate sink-plus-recent configuration")
    if base["is_h_point"] or base["is_sink_only_intervention"]:
        raise ValueError("Base must not be interpreted as an h point or sink-only intervention")
    print("LongLive: preceding blocks / total frames / Subject c2c / change from h=1")
    for h, frames, mean, change in actual:
        print(f"  {h} / {frames} / {mean:.2f} / {change:+.2f}")
    print("  Separate Base: 86.01 / -1.20; sink 3 + latest 9, physical storage 15")
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
    print("\nSelf-only minus full Commit Forcing, same confirmation seeds 2/3")
    check_metric(summary["deep_KV_confirmation"]["self_only_minus_full_recent_context"], "Subject c2c")
    sink = summary["decline_controls"]["pooled_sink_variant"]
    print("\nFP16 minus Commit Forcing")
    for name, metric in sink["metrics"].items():
        check_metric(metric, name)
    print("\nFP16 minus FR")
    for name, metric in sink["improvement_over_unaveraged_FR"].items():
        check_metric(metric, name)
    print("\nChecked 12 retention fractions and 10 reported comparison values.")
    print("Also checked four window means and their contrasts, plus the separate Base configuration.")
    print("No fractions, confidence intervals or evaluation statistics re-estimated.")


if __name__ == "__main__":
    main()
