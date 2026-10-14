#!/usr/bin/env python3
"""Reproduce DINOv2 diagnostic components from saved opening/tail embeddings."""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
STUDIES = {
    "ll": ("LongLive stage interventions", "LLS_33", ("LLS_33", "LLS_c0", "LLS_d0", "LLS_00"), 2),
    "rs": ("Rolling Sink committing sources", "RS_off", ("RS_off", "RS_real"), 2),
    "sf": ("SF committing-context switches", "S123R", ("S123R", "S123C", "SWCR", "SWRC"), 3),
}


def reproduce(study):
    title, ref, arms, seeds = STUDIES[study]
    with np.load(ROOT / "data" / f"dino_{study}.npz", allow_pickle=False) as source:
        keys = [tuple(k.split("|")) for k in source["keys"].tolist()]
        assert len(keys) == len(set(keys)), "Duplicate feature keys"
        features = {(a, int(p), int(s)): {"open": source["open"][i], "tail": source["tail"][i]}
                    for i, (a, p, s) in enumerate(keys)}
    expected = {(a, p, s) for a in arms for p in range(20) for s in range(seeds)}
    assert set(features) == expected, "Feature coverage differs from the registered study"
    cells = [(p, s) for p in range(20) for s in range(seeds)]
    terms = {}
    for a in arms:
        own, sib = [], []
        for p, s in cells:
            tail = features[a, p, s]["tail"]
            own.append(float(tail @ features[a, p, s]["open"]))
            sib.append(float(np.mean([tail @ features[a, p, other]["open"]
                                      for other in range(seeds) if other != s])))
        own, sib = np.asarray(own), np.asarray(sib)
        terms[a] = {"own": own, "sib": sib, "cons": own - sib}
    groups = np.array([p for p, _ in cells])
    prompts = np.unique(groups)
    rows = {p: np.flatnonzero(groups == p) for p in prompts}
    rng = np.random.default_rng(0)
    draws = [np.concatenate([rows[p] for p in rng.choice(prompts, len(prompts))])
             for _ in range(4000)]

    def interval(values):
        lo, hi = np.percentile([values[i].mean() for i in draws], [2.5, 97.5])
        return [float(values.mean()), float(lo), float(hi)]

    result = {"study": study, "ref": ref, "cells": cells,
              "levels": {a: {k: float(v.mean()) for k, v in terms[a].items()} for a in arms},
              "changes": {a: {k: interval(terms[a][k] - terms[ref][k]) for k in ("cons", "own", "sib")}
                          for a in arms if a != ref}}
    saved = json.loads((ROOT / "data" / f"dino_{study}.json").read_text())
    for a in arms:
        for k in ("cons", "own", "sib"):
            np.testing.assert_allclose(result["levels"][a][k], saved["levels"][a][k], rtol=0, atol=2e-7)
    for a, values in result["changes"].items():
        for k, value in values.items():
            np.testing.assert_allclose(value, saved["changes"][a][k], rtol=0, atol=2e-7)
            assert (value[1] > 0 or value[2] < 0) == (saved["changes"][a][k][1] > 0 or saved["changes"][a][k][2] < 0)
    return title, result


def fmt(values):
    mean, lo, hi = values
    # Keep the positive Rolling Sink endpoint visible rather than rounding it to zero.
    digits = 5 if 0 < abs(lo) < 0.00005 else 4
    star = "*" if lo > 0 or hi < 0 else ""
    return f"{mean:+.4f}{star} [{lo:+.{digits}f}, {hi:+.4f}]"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", choices=("all", *STUDIES), default="all")
    parser.add_argument("--json", type=Path, help="Optional path for reproduced numerical results")
    args = parser.parse_args()
    results = {}
    for study in STUDIES if args.study == "all" else (args.study,):
        title, result = reproduce(study)
        results[study] = result
        print(f"## {title}\n")
        print("| Contrast | Consistency | Own | Sibling |")
        print("|---|---|---|---|")
        for a, values in result["changes"].items():
            print(f"| {a} − {result['ref']} | " + " | ".join(fmt(values[k]) for k in ("cons", "own", "sib")) + " |")
        print("\nSaved summary verified from the feature arrays.\n")
    if args.json:
        args.json.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
