#!/usr/bin/env python3
"""Imaging-quality drift (TetherCache protocol) and the 240 s tables of results/long_horizon.

    python results/long_horizon/quality_drift.py collect --work vb_work --label sgf --out drift.csv [--append]
    python results/long_horizon/quality_drift.py table --spec results/long_horizon/specs/moviegen32_240s_sgf_tethercache.json

collect: dDrift<k> per video = imaging quality of the first k 2 s clips minus the last k (k = 1, 5).
table: a spec as for eval/vbench_long/compare.py plus "drift" (the CSV of collect); prints means and contrasts."""
import argparse
import csv
import glob
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "eval", "vbench_long"))
from compare import contrast  # noqa: E402

CLIP = re.compile(r"/p(\d)(\d{3})-0_(\d+)\.mp4")  # clip files p<seed><prompt:03d>-0_<clip>.mp4
KS = (1, 5)
DIMS = [("dynamic_degree", "Dynamic"), ("motion_smoothness", "MotionSm"), ("temporal_flickering", "Flicker"),
        ("imaging_quality", "Imaging"), ("aesthetic_quality", "Aesthetic"), ("subject_consistency", "Subject"),
        ("background_consistency", "Background")]
SPLITS = [("subject_inclip", "Subj_in"), ("subject_clip2clip", "Subj_c2c"), ("background_inclip", "Bg_in"),
          ("background_clip2clip", "Bg_c2c")]
DRIFT = [(f"dDrift{k}", f"dDrift{k}") for k in KS]
METRICS = [("quality", "Quality")] + DIMS + DRIFT + SPLITS  # bootstrap stream order within a contrast
COLUMNS = ["label", "seed", "prompt"] + [c for c, _ in DRIFT]


def imaging_clips(files, clip=CLIP):
    """{(seed, prompt): {clip index: imaging quality in [0, 1]}} from VBench-Long result files"""
    out = {}
    for f in files:
        for e in json.load(open(f)).get("imaging_quality", [None, []])[1]:
            m = clip.search(e.get("video_path", ""))
            s = e.get("video_results")
            if m and isinstance(s, (int, float)) and not isinstance(s, bool):
                out.setdefault((int(m.group(1) or 0), int(m.group(2))), {})[int(m.group(3))] = float(s) / 100.0
    return out


def drift(clips, k):
    """first k clips minus last k clips; None for fewer than 2k clips or a gap in the clip indices"""
    idx = sorted(clips)
    if len(idx) < 2 * k or idx != list(range(len(idx))):
        return None
    return float(np.mean([clips[i] for i in idx[:k]]) - np.mean([clips[i] for i in idx[-k:]]))


def collect_rows(label, files, clip=CLIP):
    rows = []
    for (s, i), c in sorted(imaging_clips(files, clip).items()):
        row = dict(label=label, seed=s, prompt=i)
        for k in KS:
            if (x := drift(c, k)) is not None:
                row[f"dDrift{k}"] = x
        rows.append(row)
    return rows


def write(rows, out, append):
    new = not (append and os.path.exists(out))
    with open(out, "a" if append else "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})


def load(paths, seed):
    """{label: {column: {prompt: value}}} from CSV files with label, seed, prompt columns"""
    out = {}
    for path in paths:
        with open(path) as f:
            for r in csv.DictReader(f):
                if int(r["seed"]) != seed:
                    continue
                for col, _ in METRICS:
                    if r.get(col, "") != "":
                        out.setdefault(r["label"], {}).setdefault(col, {})[int(r["prompt"])] = float(r[col])
    return out


def mean(scores, col):
    return 100.0 * float(np.mean(list(scores[col].values()))) if scores.get(col) else None


def table(spec):
    S = load([spec["scores"], spec["drift"]], spec["seed"])
    n = int(spec["num_prompts"])
    labels = [l for l in spec["labels"] if len(S.get(l, {}).get("quality", {})) >= n]
    w = max(8, max(len(l) for l in spec["labels"]))
    print(f"{spec['title']}\nx100; dDrift<k> = imaging quality of the first k 2 s clips - of the last k clips; "
          f"labels with all {n} prompts scored\n")
    print(f"%-{w}s " % "label" + " ".join("%10s" % s for _, s in METRICS[:1] + DIMS + DRIFT) + "   description")
    res = {"labels": {}, "contrasts": {}}
    for l in spec["labels"]:
        if l not in labels:
            print(f"%-{w}s %d/%d prompts scored" % (l, len(S.get(l, {}).get("quality", {})), n))
            continue
        res["labels"][l] = {s: mean(S[l], c) for c, s in METRICS}
        print(f"%-{w}s " % l + " ".join("%10s" % (("%+.2f" if c.startswith("dDrift") else "%.2f") % m
                                                  if (m := mean(S[l], c)) is not None else "--")
                                        for c, _ in METRICS[:1] + DIMS + DRIFT) + "   " + spec["labels"][l])
    print("\nin-clip vs clip-to-clip consistency (x100)")
    print(f"%-{w}s " % "label" + " ".join("%9s" % s for _, s in SPLITS))
    for l in labels:
        print(f"%-{w}s " % l + " ".join("%9.2f" % mean(S[l], c) for c, _ in SPLITS))
    print("\npaired contrasts (a - b) x100, by prompt, bootstrap 4000, 95% CI ('*' = excludes 0)")
    rng = np.random.default_rng(0)
    for section, name, a, b in spec["contrasts"]:
        if a not in labels or b not in labels:
            continue
        row = {"a": a, "b": b}
        print(f"\n[{section}] {name} ({a} - {b})")
        for col, short in METRICS:
            x = contrast(S[a].get(col, {}), S[b].get(col, {}), rng)
            if x:
                row[short] = x
                print("    %-10s %+7.2f [%+7.2f, %+7.2f]%s  n = %d" % (short, x["diff"], x["ci"][0], x["ci"][1],
                                                                     "*" if x["sig"] else " ", x["n"]))
        res["contrasts"][f"[{section}] {name}"] = row
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect", help="dDrift1 / dDrift5 per video of one label")
    c.add_argument("--work", required=True, help="--work folder of eval/vbench_long/score.sh")
    c.add_argument("--label", required=True)
    c.add_argument("--out", required=True, help="CSV file")
    c.add_argument("--append", action="store_true")
    t = sub.add_parser("table", help="print a table from a spec")
    t.add_argument("--spec", required=True)
    t.add_argument("--json", help="also write means and contrasts to this JSON")
    args = p.parse_args()
    if args.cmd == "collect":
        files = sorted(glob.glob(f"{args.work}/results/{args.label}__k*_q6/results_*_eval_results.json"))
        rows = collect_rows(args.label, files)
        write(rows, args.out, args.append)
        print(f"{args.label}: {len(rows)} videos -> {args.out}")
        return
    spec = json.load(open(args.spec))
    here = os.path.dirname(os.path.abspath(args.spec))
    spec["scores"], spec["drift"] = (os.path.join(here, spec[k]) for k in ("scores", "drift"))
    res = table(spec)
    if args.json:
        json.dump(res, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
