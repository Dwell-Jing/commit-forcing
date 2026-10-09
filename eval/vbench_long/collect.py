#!/usr/bin/env python3
"""Collect VBench-Long results into one CSV row per video.

    python eval/vbench_long/collect.py --work vb_work --label sgf_rule_on --out scores.csv [--append]

Reads <work>/results/<label>__k<j>_<dimset>/ from score.sh; scores are in [0, 1], averaged over the clips of a video.
Columns: quality, the 7 dimensions, and the in-clip / clip-to-clip parts of subject and background consistency."""
import argparse
import csv
import glob
import json
import os
import re

import numpy as np

# p<seed><prompt:03d>-0 as staged by prep.py
VIDEO_NAME = re.compile(r"/p(\d)(\d{3})-0(?:[/_.]|$)")
DIMS = ["dynamic_degree", "motion_smoothness", "temporal_flickering", "imaging_quality", "aesthetic_quality",
        "subject_consistency", "background_consistency"]
NORM = {"subject_consistency": (0.1462, 1.0), "background_consistency": (0.2615, 1.0),
        "temporal_flickering": (0.6293, 1.0), "motion_smoothness": (0.706, 0.9975), "dynamic_degree": (0.0, 1.0),
        "aesthetic_quality": (0.0, 1.0), "imaging_quality": (0.0, 1.0)}
WEIGHT = {d: (0.5 if d == "dynamic_degree" else 1.0) for d in DIMS}
SPLITS = ["subject_inclip", "subject_clip2clip", "background_inclip", "background_clip2clip"]
COLUMNS = ["label", "seed", "prompt", "quality"] + DIMS + SPLITS


def quality(row):
    num = sum(WEIGHT[d] * (row[d] - NORM[d][0]) / (NORM[d][1] - NORM[d][0]) for d in NORM)  # float sum in NORM order
    return num / sum(WEIGHT.values())


def result_files(work, label):
    jobs = [j for j in open(os.path.join(work, "jobs.txt")).read().split() if j.startswith(label + "__k")]
    assert jobs, f"no shard of {label} in {work}/jobs.txt"
    files = []
    for j in jobs:
        for dimset in ("q6", "bg"):
            out = os.path.join(work, "results", f"{j}_{dimset}")
            found = glob.glob(os.path.join(out, "results_*_eval_results.json"))
            assert os.path.exists(os.path.join(out, "done.txt")) and len(found) == 1, \
                f"{out}: not scored, or more than one results file"
            files += found
    return sorted(files)


def load(files, video_name=VIDEO_NAME):
    """{(seed, prompt): {column: score}} from VBench-Long result files"""
    per_video = {}
    for f in files:
        for dim, value in json.load(open(f)).items():
            if dim not in NORM or not isinstance(value, list) or len(value) < 2:
                continue
            scores, inclip, clip2clip = {}, {}, {}
            for entry in value[1]:
                m = video_name.search(entry.get("video_path", ""))
                if not m:
                    continue
                vid = (int(m.group(1) or 0), int(m.group(2)))
                s = entry.get("video_results", entry.get("score", entry.get("video_score")))
                if isinstance(s, (int, float, bool)):
                    scores.setdefault(vid, []).append(float(s) / (100.0 if dim == "imaging_quality" else 1.0))
                if "inclip_score" in entry:
                    inclip.setdefault(vid, []).append(float(entry["inclip_score"]))
                if "clip2clip_score" in entry:
                    clip2clip[vid] = float(entry["clip2clip_score"])
            for vid, xs in scores.items():
                per_video.setdefault(vid, {})[dim] = float(np.mean(xs))
            if dim in ("subject_consistency", "background_consistency"):
                part = dim.split("_")[0]
                for vid, xs in inclip.items():
                    per_video.setdefault(vid, {})[f"{part}_inclip"] = float(np.mean(xs))
                for vid, x in clip2clip.items():
                    per_video.setdefault(vid, {})[f"{part}_clip2clip"] = x
    for row in per_video.values():
        if all(d in row for d in DIMS):
            row["quality"] = quality(row)
    return per_video


def write(rows, out, append):
    new = not (append and os.path.exists(out))
    with open(out, "a" if append else "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})  # full float precision


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--work", required=True, help="the --work folder of prep.py / score.sh")
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True, help="CSV file")
    p.add_argument("--append", action="store_true", help="append to an existing CSV")
    args = p.parse_args()
    per_video = load(result_files(args.work, args.label))
    staged = {(int(n[1]), int(n[2:5])) for n in json.load(open(os.path.join(args.work, args.label, "videos.json")))}
    incomplete = sorted(v for v in staged if any(c not in per_video.get(v, {}) for c in COLUMNS[3:]))
    assert not incomplete and set(per_video) == staged, \
        f"{args.label}: {len(incomplete)} staged videos lack scores, first (seed, prompt): {incomplete[:3]}"
    rows = [dict(label=args.label, seed=s, prompt=i, **{c: v[c] for c in COLUMNS[3:]})
            for (s, i), v in sorted(per_video.items())]
    write(rows, args.out, args.append)
    print(f"{args.label}: {len(rows)} videos with all 7 dimensions -> {args.out}")


if __name__ == "__main__":
    main()
