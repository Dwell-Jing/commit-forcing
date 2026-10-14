#!/usr/bin/env python3
"""Commit-window tables (both generation seeds side by side) from results/vbench_long_60s.csv.

    python analysis/commit_window/tables.py

Replays the specs in results/specs with eval/vbench_long/compare.py; intervals match results/tables/<spec>.txt."""
import contextlib
import importlib.util
import io
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_spec = importlib.util.spec_from_file_location("compare", os.path.join(REPO, "eval", "vbench_long", "compare.py"))
compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare)

SPECS = {0: ["vbl60_seed0", "vbl60_longlive_commit_window", "vbl60_longlive_commit6_vs_12"],
         1: ["vbl60_seed1_a", "vbl60_seed1_b"]}
LONGLIVE = [("longlive", "sink 3 + newest 9 (base)"), ("longlive+commit_self", "newest 3 (the block itself)"),
            ("longlive+commit6", "newest 6"), ("longlive+commit9", "newest 9"),
            ("longlive+rule", "newest 12 (commit rule)")]
SF_SINK = [("sf_sink", "sink 3 + newest 18 (as denoising passes)"),
           ("sf_sink+commit_self", "newest 3 (the block itself)"), ("sf_sink+rule", "newest 21 (commit rule)")]
COLUMNS = [("quality", "Quality"), ("dynamic_degree", "Dynamic"), ("subject_clip2clip", "Subj_c2c"),
           ("background_clip2clip", "Bg_c2c")]
CONTRASTS = [  # (row name, a, b)
    ("newest 3 - base", "longlive+commit_self", "longlive"),
    ("newest 6 - base", "longlive+commit6", "longlive"),
    ("newest 9 - base", "longlive+commit9", "longlive"),
    ("newest 12 - base", "longlive+rule", "longlive"),
    ("newest 6 - newest 3", "longlive+commit6", "longlive+commit_self"),
    ("newest 9 - newest 6", "longlive+commit9", "longlive+commit6"),
    ("newest 12 - newest 9", "longlive+rule", "longlive+commit9"),
    ("newest 6 - newest 12", "longlive+commit6", "longlive+rule"),
    ("newest 12 - newest 3", "longlive+rule", "longlive+commit_self"),
    ("SF+sink: newest 3 - sink", "sf_sink+commit_self", "sf_sink"),
    ("SF+sink: rule - sink", "sf_sink+rule", "sf_sink"),
    ("SF+sink: rule - newest 3", "sf_sink+rule", "sf_sink+commit_self")]


def replay(seed):
    """Means {label: {column: mean x100}} and contrasts {(a, b): row} of one generation seed."""
    means, pairs = {}, {}
    for name in SPECS[seed]:
        path = os.path.join(REPO, "results", "specs", name + ".json")
        spec = json.load(open(path))
        spec["scores"] = os.path.join(os.path.dirname(path), spec["scores"])
        with contextlib.redirect_stdout(io.StringIO()):
            res = compare.run(spec)
        for row in res.values():
            pairs.setdefault((row["a"], row["b"]), row)  # first spec wins
        scores = compare.load_scores(spec["scores"], seed)
        for label in spec["labels"]:
            if len(scores.get(label, {}).get("quality", {})) >= spec["num_prompts"]:
                means[label] = {col: compare.mean(scores[label], col) for col, _ in COLUMNS}
    return means, pairs


def main():
    R = {s: replay(s) for s in SPECS}
    for title, arms in (("LongLive, the commit pass reads", LONGLIVE),
                        ("Self-Forcing + 3-frame sink, the commit pass reads", SF_SINK)):
        print(f"{title} (VBench-Long, rollf200 x 60 s, x100; seed 0 / seed 1)")
        print("%-40s" % "" + "".join("%17s" % short for _, short in COLUMNS))
        for label, desc in arms:
            cells = []
            for col, _ in COLUMNS:
                v = [R[s][0].get(label, {}).get(col) for s in SPECS]
                cells.append(" / ".join("%6.2f" % x if x is not None else "    --" for x in v))
            print("%-40s" % desc + "".join("%17s" % c for c in cells))
        print()
    print("paired contrasts a - b by prompt (200 prompts, bootstrap 95% CI, '*' = excludes 0)")
    for name, a, b in CONTRASTS:
        out = []
        for s in SPECS:
            row = R[s][1].get((a, b))
            if row is None:
                out.append(f"seed {s}: --")
                continue
            q = row["Quality"]
            rest = "  ".join(f"{k} {row[k]['diff']:+.2f}{'*' if row[k]['sig'] else ''}"
                             for k in ("Dynamic", "Subj_c2c", "Bg_c2c"))
            out.append(f"seed {s}: Quality {q['diff']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]  {rest}")
        print(name + "\n" + "\n".join("    " + o for o in out))


if __name__ == "__main__":
    main()
