"""Check and print the manuscript's current six-frame cost aggregates."""

import argparse
import json
import math
import re
from pathlib import Path


def read_summary(path):
    summary = json.loads(path.read_text())
    if summary["statistics_recomputed"] or summary["per_prompt_values_included"]:
        raise ValueError("Expected an aggregate-only transcription")
    if summary["source_snapshot"]["kind"] != "canonical manuscript working tree":
        raise ValueError("Expected a canonical working-tree source")
    for source, digest in summary["source_sha256"].items():
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid source hash: {source}")

    protocol = summary["protocol"]
    if protocol["committing_context_latent_frames"] != 6:
        raise ValueError("Expected six-frame timing adaptations")
    if protocol["timed_videos_per_condition"] != 1:
        raise ValueError("Expected one timed video per condition")
    if not protocol["all_rows_same_measurement_round"]:
        raise ValueError("Do not pool measurement rounds")
    measurements = summary["measurements"]
    names = [row["configuration"] for row in measurements]
    if len(names) != 8 or len(names) != len(set(names)):
        raise ValueError("Expected eight distinct configurations")

    print("Current six-frame timing round: one timed 60-second video per condition.")
    print("Configuration | Wall Base / Commit Forcing (s) | Peak device Base / Commit Forcing (GiB)")
    for row in measurements:
        values = []
        for measure in ("wall_seconds", "peak_device_memory_gib"):
            for arm in ("base", "commit_forcing"):
                value = row[measure][arm]
                if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                    raise ValueError(f"Invalid value: {row['configuration']} {measure} {arm}")
                values.append(value)
        print(f"{row['configuration']} | {values[0]:.1f} / {values[1]:.1f} | "
              f"{values[2]:.1f} / {values[3]:.1f}")
    print(protocol["id_forcing_scope"])
    print(protocol["comparison_scope"])
    print("Checked 32 reported values; no statistics recomputed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path,
                        default=Path(__file__).with_name("current6_aggregate.json"))
    args = parser.parse_args()
    read_summary(args.summary)


if __name__ == "__main__":
    main()
