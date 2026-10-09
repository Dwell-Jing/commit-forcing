#!/usr/bin/env python3
"""Per-arm means and paired contrasts from the CSV written by collect.py.

    python eval/vbench_long/compare.py --spec results/specs/vbl60_seed0.json [--json out.json]
    python eval/vbench_long/compare.py --scores scores.csv --seed 0 --pair sgf_rule_on:sgf_rule_off

Spec JSON: title, scores (CSV, relative to the spec), seed, num_prompts, labels {label: description}, contrasts
[[section, name, a, b], ...]; a fifth element "hidden" computes a contrast without printing it."""
import argparse
import csv
import json
import os

import numpy as np

# (CSV column, printed name); order fixes the bootstrap draws
SHOW = [("quality", "Quality"), ("dynamic_degree", "Dynamic"), ("subject_consistency", "Subject"),
        ("background_consistency", "Background"), ("subject_inclip", "Subj_in"), ("subject_clip2clip", "Subj_c2c"),
        ("background_clip2clip", "Bg_c2c"), ("imaging_quality", "Imaging"), ("aesthetic_quality", "Aesthetic"),
        ("motion_smoothness", "MotionSm"), ("temporal_flickering", "Flicker")]
BOOT = 4000
MIN_PROMPTS = 20


def load_scores(path, seed):
    """{label: {column: {prompt: score}}} for one generation seed"""
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if int(r["seed"]) != seed:
                continue
            per_label = out.setdefault(r["label"], {})
            for col, _ in SHOW:
                if r.get(col, "") != "":
                    per_label.setdefault(col, {})[int(r["prompt"])] = float(r[col])
    return out


def contrast(a, b, rng):
    prompts = sorted(set(a) & set(b))
    if len(prompts) < MIN_PROMPTS:
        return None
    d = 100.0 * np.array([a[p] - b[p] for p in prompts])
    boot = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(BOOT)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return dict(diff=float(d.mean()), ci=[float(lo), float(hi)], n=len(prompts), sig=bool(lo > 0 or hi < 0))


def mean(scores, col):
    return 100.0 * float(np.mean(list(scores[col].values()))) if scores.get(col) else None


def run(spec):
    S = load_scores(spec["scores"], spec["seed"])
    n = int(spec["num_prompts"])
    complete = {l for l in spec["labels"] if len(S.get(l, {}).get("quality", {})) >= n}
    print(f"{spec['title']}\nx100; Quality = Recency Forcing Tab. 3; labels with all {n} prompts scored\n")
    print("%-28s " % "label" + " ".join("%9s" % c for _, c in SHOW) + "   description")
    for label, desc in spec["labels"].items():
        if label in complete:
            cells = ("%.2f" % m if (m := mean(S[label], col)) is not None else "--" for col, _ in SHOW)
            print("%-28s " % label + " ".join("%9s" % c for c in cells) + "   " + desc)
        else:
            print("%-28s %d/%d prompts scored" % (label, len(S.get(label, {}).get("quality", {})), n))
    print(f"\npaired contrasts (a - b), by prompt, bootstrap {BOOT}, 95% CI ('*' = excludes 0)\n")
    rng = np.random.default_rng(0)
    res = {}
    for c in spec["contrasts"]:
        section, name, a, b = c[:4]
        if a not in complete or b not in complete:
            continue
        row = {"a": a, "b": b}
        for col, short in SHOW:
            x = contrast(S[a].get(col, {}), S[b].get(col, {}), rng)
            if x:
                row[short] = x
        if c[4:] == ["hidden"]:
            continue
        q = row.get("Quality")
        print(f"[{section}] {name} ({a} - {b})")
        if q:
            print(f"    Quality {q['diff']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]  n = {q['n']} prompts")
        print("    " + "  ".join(f"{c} {x['diff']:+.2f}{'*' if x['sig'] else ''}"
                                 for c, x in row.items() if c not in ("a", "b", "Quality")) + "\n")
        res[f"[{section}] {name}"] = row
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", help="spec JSON")
    p.add_argument("--scores", help="CSV from collect.py (without --spec)")
    p.add_argument("--seed", type=int, default=0, help="generation seed (without --spec)")
    p.add_argument("--num-prompts", type=int, default=200, help="(without --spec)")
    p.add_argument("--pair", action="append", default=[], help="a:b, repeatable (without --spec)")
    p.add_argument("--json", help="also write the contrasts to this JSON file")
    args = p.parse_args()
    if args.spec:
        spec = json.load(open(args.spec))
        spec["scores"] = os.path.join(os.path.dirname(os.path.abspath(args.spec)), spec["scores"])
    else:
        pairs = [x.split(":") for x in args.pair]
        labels = list(dict.fromkeys(l for ab in pairs for l in ab))
        spec = dict(title=f"{args.scores}, seed {args.seed}", scores=args.scores, seed=args.seed,
                    num_prompts=args.num_prompts, labels={l: "" for l in labels},
                    contrasts=[["", f"{a} - {b}", a, b] for a, b in pairs])
    res = run(spec)
    if args.json:
        json.dump(res, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
