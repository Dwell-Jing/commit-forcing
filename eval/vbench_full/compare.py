#!/usr/bin/env python3
"""Full-VBench scores per label and paired contrasts, from the CSV files written by collect.py.

    python eval/vbench_full/compare.py --spec results/vbench_full/specs/sgf.json [--json out.json]
    python eval/vbench_full/compare.py --scores scores.csv --shards shards.csv --pair sgf+rule:sgf

Spec JSON: title, scores and shards (CSV paths relative to the spec), seed, labels {label: description}, contrasts
[[section, name, a, b], ...]. Quality / Semantic / Total follow VBench's cal_final_score.py."""
import argparse
import csv
import json
import os

import numpy as np

QUALITY = ["subject_consistency", "background_consistency", "temporal_flickering", "motion_smoothness",
           "aesthetic_quality", "imaging_quality", "dynamic_degree"]
SEMANTIC = ["object_class", "multiple_objects", "human_action", "color", "spatial_relationship", "scene",
            "appearance_style", "temporal_style", "overall_consistency"]
DIMS = QUALITY + SEMANTIC
NORM = {"subject_consistency": (0.1462, 1.0), "background_consistency": (0.2615, 1.0),
        "temporal_flickering": (0.6293, 1.0), "motion_smoothness": (0.706, 0.9975), "dynamic_degree": (0.0, 1.0),
        "aesthetic_quality": (0.0, 1.0), "imaging_quality": (0.0, 1.0), "object_class": (0.0, 1.0),
        "multiple_objects": (0.0, 1.0), "human_action": (0.0, 1.0), "color": (0.0, 1.0),
        "spatial_relationship": (0.0, 1.0), "scene": (0.0, 0.8222), "appearance_style": (0.0009, 0.2855),
        "temporal_style": (0.0, 0.364), "overall_consistency": (0.0, 0.364)}  # VBench scripts/constant.py
WEIGHT = {k: (0.5 if k == "dynamic_degree" else 1.0) for k in DIMS}
SHORT = {"subject_consistency": "Subject", "background_consistency": "Backgr", "temporal_flickering": "Flicker",
         "motion_smoothness": "MotionSm", "aesthetic_quality": "Aesth", "imaging_quality": "Imaging",
         "dynamic_degree": "Dynamic", "object_class": "Object", "multiple_objects": "MultiObj",
         "human_action": "Action", "color": "Color", "spatial_relationship": "Spatial", "scene": "Scene",
         "appearance_style": "AppStyle", "temporal_style": "TmpStyle", "overall_consistency": "OverallC"}
SPLITS = [("subject_inclip", "Subj_in"), ("subject_clip2clip", "Subj_c2c"), ("background_inclip", "Bg_in"),
          ("background_clip2clip", "Bg_c2c")]
BOOT = 4000


def load(scores, shards, seed):
    """per-video {label: {column: {prompt: score}}}, distinct prompts in list order, shard rows"""
    per_video, entries = {}, {}
    with open(scores) as f:
        for r in csv.DictReader(f):
            if int(r["seed"]) != seed:
                continue
            entries[int(r["index"])] = r["prompt"]
            cols = per_video.setdefault(r["label"], {})
            for c in DIMS + [c for c, _ in SPLITS]:
                if r[c] != "":
                    assert r["prompt"] not in cols.get(c, {}), (r["label"], c, r["prompt"])
                    cols.setdefault(c, {})[r["prompt"]] = float(r[c])
    assert sorted(entries) == list(range(946)), "scores must hold all 946 entries of VBench's list"
    prompts = list(dict.fromkeys(entries[i] for i in range(946)))
    shard = {}
    with open(shards) as f:
        for r in csv.DictReader(f):
            if int(r["seed"]) == seed:
                shard.setdefault((r["label"], r["dimension"]), []).append((int(r["shard"]), int(r["videos"]),
                                                                           float(r["overall"])))
    return per_video, prompts, shard


def official(rows, dim):
    """VBench's dimension score: shard scores weighted by video count, shards in result-folder order"""
    tot, n = 0.0, 0
    for _, videos, overall in sorted(rows, key=lambda r: str(r[0])):
        tot += overall * videos
        n += videos
    s = tot / n
    return s / 100.0 if (dim == "imaging_quality" and s > 1.5) else s


def composite(s):
    """(Quality, Semantic, Total) of cal_final_score.py from {dimension: score or array}"""
    z = {k: WEIGHT[k] * (s[k] - NORM[k][0]) / (NORM[k][1] - NORM[k][0]) for k in DIMS}
    q = sum(z[k] for k in QUALITY) / sum(WEIGHT[k] for k in QUALITY)
    se = sum(z[k] for k in SEMANTIC) / sum(WEIGHT[k] for k in SEMANTIC)
    return q, se, (4 * q + se) / 5


def interval(est, boots, percentile=np.nanpercentile):
    lo, hi = percentile(boots, [2.5, 97.5])
    return dict(diff=float(est), ci=[float(lo), float(hi)], sig=bool(lo > 0 or hi < 0))


def run(spec):
    S, prompts, shard = load(spec["scores"], spec["shards"], spec["seed"])
    labels = list(spec["labels"])
    print(f"{spec['title']}\nx100; Quality / Semantic / Total as VBench's cal_final_score.py\n")
    w = max(10, max(len(l) for l in labels))
    print(" " * (w + 1) + " ".join("%8s" % SHORT[k] for k in DIMS) + "   Quality Semantic    Total")
    table, off = {}, {}
    for a in labels:
        missing = [k for k in DIMS if (a, k) not in shard]
        if missing:
            print(f"%-{w}s missing dimensions: %s" % (a, ", ".join(missing)))
            continue
        off[a] = {k: official(shard[(a, k)], k) for k in DIMS}
        q, se, t = composite(off[a])
        table[a] = dict(dims={k: 100 * off[a][k] for k in DIMS}, quality=100 * q, semantic=100 * se, total=100 * t)
        print(f"%-{w}s " % a + " ".join("%8.2f" % (100 * off[a][k]) for k in DIMS) + "   %7.2f %8.2f %8.2f"
              % (100 * q, 100 * se, 100 * t))
    print("\ncheck: max over dimensions of |VBench score - mean of the per-video scores| x100")
    for a in off:
        dev = {k: 100 * abs(off[a][k] - np.mean(list(S[a][k].values()))) for k in DIMS}
        k = max(dev, key=dev.get)
        print(f"%-{w}s %.3f (%s)" % (a, dev[k], k))
    print("\nin-clip vs clip-to-clip consistency (x100, mean over videos)")
    print(" " * (w + 1) + " ".join("%9s" % s for _, s in SPLITS))
    for a in off:
        print(f"%-{w}s " % a + " ".join("%9.2f" % (100 * np.mean(list(S[a][c].values()))) for c, _ in SPLITS))
        table[a].update({s: 100 * float(np.mean(list(S[a][c].values()))) for c, s in SPLITS})

    rng = np.random.default_rng(0)
    idx = {p: i for i, p in enumerate(prompts)}
    weights = rng.multinomial(len(prompts), np.full(len(prompts), 1.0 / len(prompts)), size=BOOT).astype(float)
    print(f"\npaired contrasts (a - b) x100: per-video scores paired by prompt; {BOOT} joint resamples of the "
          f"{len(prompts)} distinct prompts; 95% CI ('*' = excludes 0)")
    res = {}
    for section, name, a, b in spec["contrasts"]:
        if a not in off or b not in off:
            continue
        row, means = {"a": a, "b": b}, {}
        for k in DIMS:
            common = sorted(set(S[a][k]) & set(S[b][k]))
            assert len(common) >= 10, (a, b, k, len(common))
            cols = np.array([idx[p] for p in common])
            xa, xb = np.array([S[a][k][p] for p in common]), np.array([S[b][k][p] for p in common])
            wk = weights[:, cols]
            ws = wk.sum(1)
            ws[ws == 0] = np.nan
            ba, bb = (wk @ xa) / ws, (wk @ xb) / ws
            means[k] = (xa.mean(), xb.mean(), ba, bb)
            row[SHORT[k]] = dict(interval(100 * (xa.mean() - xb.mean()), 100 * (ba - bb)), n=len(common))
        point = [composite({k: means[k][j] for k in DIMS}) for j in (0, 1)]
        boot = [composite({k: means[k][j] for k in DIMS}) for j in (2, 3)]
        for i, nm in enumerate(("Quality", "Semantic", "Total")):
            row[nm] = dict(interval(100 * (point[0][i] - point[1][i]), 100 * (boot[0][i] - boot[1][i])),
                           n=len(prompts))
        for c, s in SPLITS:
            common = sorted(set(S[a][c]) & set(S[b][c]))
            d = 100 * np.array([S[a][c][p] - S[b][c][p] for p in common])
            boots = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(BOOT)]
            row[s] = dict(interval(d.mean(), boots, np.percentile), n=len(common))
        print(f"\n[{section}] {name} ({a} - {b})")
        for m in ["Total", "Quality", "Semantic"] + [SHORT[k] for k in DIMS] + [s for _, s in SPLITS]:
            x = row[m]
            print("    %-9s %+7.2f [%+7.2f, %+7.2f]%s  n = %d" % (m, x["diff"], x["ci"][0], x["ci"][1],
                                                                 "*" if x["sig"] else " ", x["n"]))
        res[f"[{section}] {name}"] = row
    return dict(table=table, contrasts=res)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", help="spec JSON")
    p.add_argument("--scores", help="per-video CSV from collect.py (without --spec)")
    p.add_argument("--shards", help="per-shard CSV from collect.py (without --spec)")
    p.add_argument("--seed", type=int, default=0, help="generation seed (without --spec)")
    p.add_argument("--pair", action="append", default=[], help="a:b, repeatable (without --spec)")
    p.add_argument("--json", help="also write the table and contrasts to this JSON")
    args = p.parse_args()
    if args.spec:
        spec = json.load(open(args.spec))
        here = os.path.dirname(os.path.abspath(args.spec))
        spec["scores"], spec["shards"] = (os.path.join(here, spec[k]) for k in ("scores", "shards"))
    else:
        pairs = [x.split(":") for x in args.pair]
        spec = dict(title=f"{args.scores}, seed {args.seed}", scores=args.scores, shards=args.shards, seed=args.seed,
                    labels={l: "" for l in dict.fromkeys(l for ab in pairs for l in ab)},
                    contrasts=[["", f"{a} - {b}", a, b] for a, b in pairs])
    res = run(spec)
    if args.json:
        json.dump(res, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
