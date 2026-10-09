#!/usr/bin/env python3
"""Collect full-VBench results into one CSV row per video and one CSV row per scoring shard.

    python eval/vbench_full/collect.py --vbench VBench --work vbs_work --label sgf \
        --scores scores.csv --shards shards.csv [--append]

Reads <work>/results/<label>__<dimension>__s<j>/ from score.sh. scores.csv: one row per line of VBench's list (946).
shards.csv: per (dimension, shard) the overall score and video count, which compare.py uses to weight the shards."""
import argparse
import csv
import glob
import json
import os
import re

import numpy as np

QUALITY = ["subject_consistency", "background_consistency", "temporal_flickering", "motion_smoothness",
           "aesthetic_quality", "imaging_quality", "dynamic_degree"]
SEMANTIC = ["object_class", "multiple_objects", "human_action", "color", "spatial_relationship", "scene",
            "appearance_style", "temporal_style", "overall_consistency"]
DIMS = QUALITY + SEMANTIC
SPLITS = ["subject_inclip", "subject_clip2clip", "background_inclip", "background_clip2clip"]
SCORE_COLUMNS = ["label", "seed", "index", "prompt"] + DIMS + SPLITS
SHARD_COLUMNS = ["label", "seed", "dimension", "shard", "videos", "overall"]
SPLIT_CLIP = re.compile(r"/split_clip/([^/]+)-(\d+)/")
SHARD_DIR = re.compile(r"__s(\d+)$")


def full_info(vbench):
    rows = json.load(open(os.path.join(vbench, "vbench2_beta_long", "VBench_full_info.json")))
    assert len(rows) == 946, len(rows)
    return rows


def prompt_of(path):
    """prompt of a clip path: split_clip/<prompt>-0/... or <prompt>-0_<n>.mp4 (after the static filter)"""
    m = SPLIT_CLIP.search(path)
    if m:
        return m.group(1)
    name = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"-\d+$", "", re.sub(r"_\d+$", "", name))


def number(x):
    return float(x) if isinstance(x, (bool, int, float)) else None


def load(work, label):
    """clip scores {(dimension, prompt): [score]}, in-clip and clip-to-clip parts, shard rows"""
    clips, inclip, clip2clip, shards = {}, {}, {}, []
    for dim in DIMS:
        want = len(glob.glob(f"{work}/{label}/{dim}__s*.full_info.json"))
        files = sorted(glob.glob(f"{work}/results/{label}__{dim}__s*/results_*_eval_results.json"))
        dirs = [os.path.dirname(f) for f in files]
        assert len(dirs) == len(set(dirs)), f"more than one results file in a shard folder: {sorted(dirs)}"
        assert want and len(files) == want, f"{label} {dim}: {len(files)}/{want} shards scored"
        for f in files:
            r = json.load(open(f))[dim]
            assert isinstance(r, list) and len(r) >= 2 and number(r[0]) is not None, f"unexpected result in {f}"
            scored = set()
            for e in r[1]:
                if not (isinstance(e, dict) and "video_path" in e and number(e.get("video_results")) is not None):
                    continue
                p = prompt_of(e["video_path"])
                scored.add(p)
                x = number(e["video_results"])
                if dim == "imaging_quality" and x > 1.5:  # MUSIQ is 0-100
                    x /= 100.0
                clips.setdefault((dim, p), []).append(x)
                if dim in ("subject_consistency", "background_consistency") and "inclip_score" in e:
                    part = dim.split("_")[0]
                    inclip.setdefault((part, p), []).append(float(e["inclip_score"]))
                    clip2clip[(part, p)] = float(e["clip2clip_score"])
            shards.append(dict(dimension=dim, shard=int(SHARD_DIR.search(os.path.dirname(f)).group(1)),
                               videos=len(scored), overall=number(r[0])))
    return clips, inclip, clip2clip, shards


def rows(label, seed, info, clips, inclip, clip2clip):
    """one row per line of VBench's list; each (prompt, dimension) is on one line"""
    out = []
    for i, entry in enumerate(info):
        p, dims = entry["prompt_en"], entry["dimension"]
        row = dict(label=label, seed=seed, index=i, prompt=p)
        for dim in DIMS:
            if dim in dims and (dim, p) in clips:
                row[dim] = float(np.mean(clips[(dim, p)]))
        for part in ("subject", "background"):
            if f"{part}_consistency" in dims and (part, p) in inclip:
                row[f"{part}_inclip"] = float(np.mean(inclip[(part, p)]))
                row[f"{part}_clip2clip"] = clip2clip[(part, p)]
        out.append(row)
    return out


def write(path, columns, rows_, append):
    new = not (append and os.path.exists(path))
    with open(path, "a" if append else "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        if new:
            w.writeheader()
        for r in rows_:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})  # full float precision


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vbench", required=True, help="VBench checkout (commit 45e79ec)")
    p.add_argument("--work", required=True, help="the --work folder of prep.py / score.sh")
    p.add_argument("--label", required=True)
    p.add_argument("--seed", type=int, default=0, help="generation seed of the staged videos (for the CSV)")
    p.add_argument("--scores", required=True, help="per-video CSV")
    p.add_argument("--shards", required=True, help="per-shard CSV")
    p.add_argument("--append", action="store_true", help="append to existing CSV files")
    args = p.parse_args()
    info = full_info(args.vbench)
    clips, inclip, clip2clip, shards = load(args.work, args.label)
    video_rows = rows(args.label, args.seed, info, clips, inclip, clip2clip)
    shard_rows = [dict(label=args.label, seed=args.seed, **s) for s in shards]
    write(args.scores, SCORE_COLUMNS, video_rows, args.append)
    write(args.shards, SHARD_COLUMNS, shard_rows, args.append)
    n = sum(any(d in r for d in DIMS) for r in video_rows)
    print(f"{args.label}: {len(video_rows)} videos ({n} with a score), {len(shard_rows)} shards -> {args.scores}, "
          f"{args.shards}")


if __name__ == "__main__":
    main()
