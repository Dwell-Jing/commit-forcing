#!/usr/bin/env python3
"""SGF context contrasts from actual scored per-video CSV inputs.

Adapted from the original SGF readout. Metric/contrast order and sequential
NumPy RNG draws are retained. No input score is reconstructed from summaries.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

METRICS = (
    ("subject_clip2clip", "Subj_c2c"), ("quality", "Quality"),
    ("dynamic_degree", "Dynamic"), ("motion_smoothness", "MotionSm"),
    ("temporal_flickering", "Flicker"), ("background_clip2clip", "Bg_c2c"),
    ("subject_consistency", "Subject"), ("aesthetic_quality", "Aesthetic"),
    ("imaging_quality", "Imaging"),
)
PAIRS = (("B", "A"), ("B", "C"), ("B", "D"))
SEEDS = (0, 1)


def load_scores(path):
    data = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (row["group"], int(row["seed"]))
            if key[0] not in "ABCD" or len(key[0]) != 1 or key[1] not in SEEDS:
                raise ValueError(f"Unexpected group/seed: {key}")
            prompt = int(row["prompt"])
            arm = data.setdefault(key, {})
            if prompt in arm:
                raise ValueError(f"Duplicate group/seed/prompt: {key}, {prompt}")
            values = {short: float(row[column]) for column, short in METRICS}
            if not all(np.isfinite(v) for v in values.values()):
                raise ValueError(f"Nonfinite score: {key}, {prompt}")
            arm[prompt] = values
    for group in "ABCD":
        for seed in SEEDS:
            key = (group, seed)
            if set(data.get(key, {})) != set(range(200)):
                raise ValueError(f"Expected prompts 0–199 for {key}; found {len(data.get(key, {}))}")
    return data


def bootstrap(x, rng):
    draws = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(4000)]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return [float(x.mean()), float(lo), float(hi)]


def motion_adjusted(dynamic, consistency, prompts, rng):
    def fit(indices):
        design = np.vstack([np.ones(len(indices)), dynamic[indices]]).T
        return np.linalg.lstsq(design, consistency[indices], rcond=None)[0][0]
    ids = np.unique(prompts)
    rows = {prompt: np.flatnonzero(prompts == prompt) for prompt in ids}
    draws = [fit(np.concatenate([rows[p] for p in rng.choice(ids, len(ids))])) for _ in range(2000)]
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return [float(fit(np.arange(len(dynamic)))), float(lo), float(hi)]


def compute(data):
    rng = np.random.default_rng(0)
    results = []
    prompts = list(range(200))
    for a, b in PAIRS:
        differences = {}
        for seed in SEEDS:
            differences[seed] = {
                short: np.array([100 * (data[a, seed][p][short] - data[b, seed][p][short])
                                 for p in prompts])
                for _, short in METRICS
            }
            row = {short: bootstrap(differences[seed][short], rng) for _, short in METRICS}
            row["Subj_c2c at equal motion"] = motion_adjusted(
                differences[seed]["Dynamic"], differences[seed]["Subj_c2c"], np.array(prompts), rng)
            results.append({"contrast": f"{a} - {b}", "seed": str(seed), "metrics": row})
        row = {short: bootstrap(np.mean([differences[s][short] for s in SEEDS], axis=0), rng)
               for _, short in METRICS}
        row["Subj_c2c at equal motion"] = motion_adjusted(
            np.concatenate([differences[s]["Dynamic"] for s in SEEDS]),
            np.concatenate([differences[s]["Subj_c2c"] for s in SEEDS]),
            np.tile(prompts, len(SEEDS)), rng)
        results.append({"contrast": f"{a} - {b}", "seed": "pooled", "metrics": row})
    return results


def fmt(values):
    mean, lo, hi = values
    mark = "*" if lo > 0 or hi < 0 else ""
    return f"{mean:+.2f}{mark} [{lo:+.2f}, {hi:+.2f}]"


def check_reported(results, path):
    reported = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            mark = "*" if row["significant"] == "true" else ""
            reported[row["contrast"], row["seed"], row["metric"]] = (
                f'{row["estimate"]}{mark} [{row["ci95_low"]}, {row["ci95_high"]}]')
    actual = {(row["contrast"], row["seed"], metric): fmt(value)
              for row in results for metric, value in row["metrics"].items()}
    if actual.keys() != reported.keys():
        raise ValueError("Reported and computed contrast coverage differs")
    differences = [(key, reported[key], actual[key]) for key in actual if reported[key] != actual[key]]
    if differences:
        raise ValueError(f"Reported rounded contrasts differ: {differences}")
    print(f"Verified {len(actual)} reported metric contrasts.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", type=Path, required=True, help="Actual per-video scores in the documented CSV schema")
    parser.add_argument("--json", type=Path, help="Save unrounded computed contrasts")
    parser.add_argument("--check-reported", action="store_true", help="Verify rounded outputs against the published readout")
    args = parser.parse_args()
    if not args.scores.is_file():
        parser.error(f"Score CSV does not exist: {args.scores}")
    results = compute(load_scores(args.scores))
    print("SGF committing controls; scores ×100; 200 prompts; 2 generation seeds")
    for row in results:
        print(f'{row["contrast"]}, seed {row["seed"]}: ' +
              " | ".join(f"{metric} {fmt(value)}" for metric, value in row["metrics"].items()))
    if args.check_reported:
        check_reported(results, Path(__file__).parents[1] / "data" / "reported_contrasts.csv")
    if args.json:
        args.json.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
