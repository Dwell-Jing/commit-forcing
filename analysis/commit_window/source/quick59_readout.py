#!/usr/bin/env python3
"""Portable CSV adaptation of the original LongLive quick59 readout.

Retains the contrast/metric/subgroup order and shared NumPy RNG stream.
Scored inputs and sidecar-derived static fractions must be actual observations.
"""
import json
import argparse
import csv
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser(description="Recompute LongLive quick59 results from actual scored CSV inputs.")
parser.add_argument("--scores", type=Path, required=True)
parser.add_argument("--check-reported", action="store_true")
parser.add_argument("--out", type=Path, help="Optional destination for the recomputed report")
args = parser.parse_args()
if not args.scores.is_file():
    parser.error(f"Score CSV does not exist: {args.scores}")

BASE = "LLS_c0"
ARMS = {"LLW_ad": "static -> 3 frames", "LLW_ad6": "static -> 6 frames",
        "LLW_adh6": "static -> local heads 3, others 6", "LLW_w6": "every commit 6 frames (fixed control)"}
PICK = ("LLW_ad", "LLW_ad6", "LLW_adh6")   # Q2 candidates (PREREG); LLW_w6 is the fixed control of the addendum
SEEDS = (0, 1, 2)
COLS = ("Quality", "Dynamic", "Subj_c2c", "Bg_c2c", "Subj_in")
KEY = {"Quality": "quality", "Dynamic": "dynamic_degree", "Subj_c2c": "subj_c2c",
       "Bg_c2c": "bg_c2c", "Subj_in": "subj_in"}
CSV_KEYS = {"quality": "quality", "dynamic_degree": "dynamic_degree",
            "subj_c2c": "subject_clip2clip", "bg_c2c": "background_clip2clip",
            "subj_in": "subject_inclip"}
SCORES, STATIC = {}, {}
with args.scores.open(newline="") as f:
    for row in csv.DictReader(f):
        arm, seed, prompt = row["arm"], int(row["seed"]), int(row["prompt"])
        if arm not in (BASE, *ARMS) or seed not in SEEDS or prompt not in range(60):
            raise ValueError(f"Unexpected score identity: {arm}, {seed}, {prompt}")
        entry = SCORES.setdefault((arm, seed), {key: {} for key in CSV_KEYS})
        if prompt in entry["quality"]:
            raise ValueError(f"Duplicate score identity: {arm}, {seed}, {prompt}")
        for key, column in CSV_KEYS.items():
            value = float(row[column])
            if not np.isfinite(value):
                raise ValueError(f"Nonfinite {column}: {arm}, {seed}, {prompt}")
            entry[key][prompt] = value
        if arm in PICK:
            value = float(row["static_fraction"])
            if not np.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"Invalid static fraction: {arm}, {seed}, {prompt}")
            STATIC[arm, seed, prompt] = value
expected = set(SCORES.get((BASE, 0), {}).get("quality", {}))
if len(expected) != 59:
    raise ValueError(f"Expected 59 post-exclusion prompts, found {len(expected)}")
for arm in (BASE, *ARMS):
    for seed in SEEDS:
        if set(SCORES.get((arm, seed), {}).get("quality", {})) != expected:
            raise ValueError(f"Incomplete or unmatched prompts: {arm}, {seed}")
EXCL = set(range(60)) - expected
if len(EXCL) != 1:
    raise ValueError("Expected exactly one calibration-overlap exclusion")
rng = np.random.default_rng(0)


def load(arm, seed):
    return SCORES[arm, seed]


def static_frac(arm, seed, prompt):
    return STATIC[arm, seed, prompt]


def boot(x, groups=None):
    """mean and 95% CI; groups (cluster ids) resampled together when given"""
    if groups is None:
        m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(4000)]
    else:
        ids = np.unique(groups)
        rows = {g: np.flatnonzero(groups == g) for g in ids}
        m = []
        for _ in range(4000):
            pick = np.concatenate([rows[g] for g in rng.choice(ids, len(ids))])
            m.append(x[pick].mean())
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(x.mean()), float(lo), float(hi)


def eqm(dyn, con, groups):
    def fit(i):
        A = np.vstack([np.ones(len(i)), dyn[i]]).T
        return np.linalg.lstsq(A, con[i], rcond=None)[0][0]
    ids = np.unique(groups)
    rows = {g: np.flatnonzero(groups == g) for g in ids}
    b = [fit(np.concatenate([rows[g] for g in rng.choice(ids, len(ids))])) for _ in range(2000)]
    lo, hi = np.percentile(b, [2.5, 97.5])
    return float(fit(np.arange(len(dyn)))), float(lo), float(hi)


def fmt(t):
    m, lo, hi = t
    return f"{m:+.2f}{'*' if lo > 0 or hi < 0 else ''} [{lo:+.2f}, {hi:+.2f}]"


data = {(a, s): load(a, s) for a in (BASE, *ARMS) for s in SEEDS}
data = {k: v for k, v in data.items() if v is not None}
L = ["# LongLive quick59 window comparison\n",
     "LongLive, quick60 x 48 s x generation seeds 0-2, VBench-Long q6 + bg, x100; 59 prompts (the calibration-overlap "
     "prompt excluded). `*`: 95% CI excludes 0. Pooled = per-prompt mean over seeds, prompts resampled.\n",
     "## Levels\n", "| label | " + " | ".join(COLS) + " |", "|---|" + "---|" * len(COLS)]
for (a, s), d in sorted(data.items()):
    ps = [p for p in d[KEY["Quality"]] if p not in EXCL]
    L.append(f"| {a} seed {s} | " + " | ".join(f"{100 * np.mean([d[KEY[c]][p] for p in ps]):.2f}" for c in COLS) + " |")
L += ["", f"## Each arm - {BASE} (same seed)\n",
      "| arm | seed | " + " | ".join(COLS) + " | Subj_c2c at equal motion |", "|---|---|" + "---|" * (len(COLS) + 1)]
pooled = {}
for a, desc in ARMS.items():
    per, units = {}, []
    for s in SEEDS:
        if (a, s) not in data or (BASE, s) not in data:
            continue
        A, B = data[a, s], data[BASE, s]
        ps = sorted((set(A[KEY["Quality"]]) & set(B[KEY["Quality"]])) - EXCL)
        per[s] = {c: {p: 100 * (A[KEY[c]][p] - B[KEY[c]][p]) for p in ps} for c in COLS}
        dyn = np.array([per[s]["Dynamic"][p] for p in ps]); con = np.array([per[s]["Subj_c2c"][p] for p in ps])
        L.append(f"| {a} ({desc}) | {s} | " + " | ".join(fmt(boot(np.array(list(per[s][c].values())))) for c in COLS)
                 + f" | {fmt(eqm(dyn, con, np.array(ps)))} |")
        units += [(p, s) for p in ps]
    if len(per) >= 2:
        ps = sorted(set.intersection(*[set(per[s]["Quality"]) for s in per]))
        row = {c: boot(np.array([np.mean([per[s][c][p] for s in per]) for p in ps])) for c in COLS}
        dyn = np.array([per[s]["Dynamic"][p] for p, s in units]); con = np.array([per[s]["Subj_c2c"][p] for p, s in units])
        em = eqm(dyn, con, np.array([p for p, s in units]))
        pooled[a] = dict(row=row, seeds=sorted(per), means={s: float(np.mean(list(per[s]["Subj_c2c"].values()))) for s in per})
        L.append(f"| {a} ({desc}) | pooled {','.join(map(str, sorted(per)))} | "
                 + " | ".join(fmt(row[c]) for c in COLS) + f" | {fmt(em)} |")
L += ["", "## Where the differences sit (adaptive arms, pooled over seeds; units = prompt x seed)\n",
      "| arm | static commit passes | units | Quality | Dynamic | Subj_c2c |", "|---|---|---|---|---|---|"]
for a in PICK:
    rows = []
    for s in SEEDS:
        if (a, s) not in data or (BASE, s) not in data:
            continue
        A, B = data[a, s], data[BASE, s]
        for p in sorted((set(A[KEY["Quality"]]) & set(B[KEY["Quality"]])) - EXCL):
            rows.append((p, static_frac(a, s, p), *[100 * (A[KEY[c]][p] - B[KEY[c]][p]) for c in ("Quality", "Dynamic", "Subj_c2c")]))
    if not rows:
        continue
    r = np.array(rows)
    for name, m in (("never", r[:, 1] == 0), ("partly (<90%)", (r[:, 1] > 0) & (r[:, 1] < 0.9)), (">= 90%", r[:, 1] >= 0.9)):
        if m.sum() >= 5:
            g = r[m, 0]
            L.append(f"| {a} | {name} | {int(m.sum())} | " + " | ".join(fmt(boot(r[m, k], g)) for k in (2, 3, 4)) + " |")
        elif m.sum():
            L.append(f"| {a} | {name} | {int(m.sum())} | " + " | ".join(f"{r[m, k].mean():+.2f}" for k in (2, 3, 4)) + " |")
complete = all((a, s) in data for a in (BASE, *ARMS) for s in SEEDS)
L += ["", "## Verdicts (quick59_prereg.md)\n"]
if not complete:
    missing = [f"{a} s{s}" for a in (BASE, *ARMS) for s in SEEDS if (a, s) not in data]
    L.append(f"Not all labels scored yet; missing: {', '.join(missing)}")
else:
    q1 = pooled["LLW_ad"]
    rep = q1["row"]["Subj_c2c"][2] < 0 and sum(v < 0 for v in q1["means"].values()) >= 2
    L.append(f"- Q1: LLW_ad pooled Subj_c2c {fmt(q1['row']['Subj_c2c'])}, per-seed means "
             + ", ".join(f"s{s} {v:+.2f}" for s, v in sorted(q1["means"].items()))
             + f" -> the consistency drop {'replicates' if rep else 'does not replicate'}.")
    ok = [a for a, v in pooled.items() if a in PICK and v["row"]["Quality"][1] > 0 and not v["row"]["Subj_c2c"][2] < 0]
    if ok:
        best = max(ok, key=lambda a: pooled[a]["row"]["Quality"][0])
        near = [a for a in ok if pooled[best]["row"]["Quality"][0] - pooled[a]["row"]["Quality"][0] < 0.05]
        pick = max(near, key=lambda a: pooled[a]["row"]["Subj_c2c"][0])
        L.append(f"- Q2: qualifying arms {', '.join(ok)}; pick {pick} (Quality {fmt(pooled[pick]['row']['Quality'])}, "
                 f"Subj_c2c {fmt(pooled[pick]['row']['Subj_c2c'])}).")
    else:
        L.append("- Q2: no arm has Quality CI > 0 without a Subj_c2c CI below 0; LLW_ad stays the candidate (trade-off).")
# addendum (Q3): adaptive 6 vs fixed 6, paired by (prompt, seed)
L += ["", "## Addendum Q3: LLW_ad6 - LLW_w6 (does the static test add anything over a fixed 6-frame commit window?)\n",
      "| seed | " + " | ".join(COLS) + " | Subj_c2c at equal motion |", "|---|" + "---|" * (len(COLS) + 1)]
q3 = {}
for s_ in SEEDS:
    if ("LLW_ad6", s_) in data and ("LLW_w6", s_) in data:
        A, B = data["LLW_ad6", s_], data["LLW_w6", s_]
        ps = sorted((set(A[KEY["Quality"]]) & set(B[KEY["Quality"]])) - EXCL)
        q3[s_] = {c: {p: 100 * (A[KEY[c]][p] - B[KEY[c]][p]) for p in ps} for c in COLS}
        dyn = np.array([q3[s_]["Dynamic"][p] for p in ps]); con = np.array([q3[s_]["Subj_c2c"][p] for p in ps])
        L.append(f"| {s_} | " + " | ".join(fmt(boot(np.array(list(q3[s_][c].values())))) for c in COLS) + f" | {fmt(eqm(dyn, con, np.array(ps)))} |")
if len(q3) == 3:
    ps = sorted(set.intersection(*[set(q3[x]["Quality"]) for x in q3]))
    pr = {c: boot(np.array([np.mean([q3[x][c][p] for x in q3]) for p in ps])) for c in COLS}
    L.append("| pooled | " + " | ".join(fmt(pr[c]) for c in COLS) + " | |")
    adds = (pr["Quality"][1] > 0 or pr["Subj_c2c"][1] > 0) and not (pr["Quality"][2] < 0 or pr["Subj_c2c"][2] < 0)
    worse = pr["Quality"][2] < 0 or pr["Subj_c2c"][2] < 0
    L.append("- Q3: " + ("the static test adds value over a fixed 6-frame window" if adds else
                         "the fixed 6-frame window is better on Quality or Subj_c2c" if worse else
                         "no evidence that the static test adds value; the simpler fixed 6-frame commit window carries the gain"))
report = "\n".join(L) + "\n"
print(report)
if args.out:
    args.out.write_text(report)
if args.check_reported:
    def table_cells(text):
        records = {}
        section = None
        for line in text.splitlines():
            if line == "## Levels":
                section = "levels"
            elif line.startswith("## Each arm"):
                section = "against_reference"
            elif line.startswith("## Where the differences"):
                section = "subgroups"
            elif line.startswith("## Addendum Q3"):
                section = "adaptive6_minus_fixed6"
            elif line.startswith("## Verdicts"):
                section = None
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if section == "levels" and " seed " in cells[0] and cells[0].startswith(("LLS_c0 seed", "LLW_")):
                arm, seed = cells[0].split(" seed ")
                columns, values, subgroup = COLS, cells[1:], ""
            elif section == "against_reference" and cells[0].startswith("LLW_"):
                arm, seed, subgroup = cells[0].split(" (")[0], cells[1], ""
                columns, values = (*COLS, "Subj_c2c at equal motion"), cells[2:]
            elif section == "subgroups" and cells[0].startswith("LLW_"):
                arm, seed, subgroup = cells[0], "pooled", cells[1]
                columns, values = ("Quality", "Dynamic", "Subj_c2c"), cells[3:]
            elif section == "adaptive6_minus_fixed6" and cells[0] in ("0", "1", "2", "pooled"):
                arm, seed, subgroup = "LLW_ad6 - LLW_w6", cells[0], ""
                columns, values = (*COLS, "Subj_c2c at equal motion"), cells[1:]
            else:
                continue
            for metric, value in zip(columns, values):
                if value:
                    records[section, arm, seed, subgroup, metric] = value
        return records
    actual = table_cells(report)
    with (Path(__file__).parents[1] / "data" / "quick59_contrasts.csv").open(newline="") as f:
        reported = {(r["section"], r["arm"], r["seed"], r["subgroup"], r["metric"]): r["reported_value"]
                    for r in csv.DictReader(f)}
    if actual.keys() != reported.keys():
        raise ValueError("Computed and reported cell coverage differs")
    differences = [(key, reported[key], actual[key]) for key in actual if reported[key] != actual[key]]
    if differences:
        raise ValueError(f"Reported rounded readouts differ: {differences}")
    print(f"Verified {len(actual)} reported cells.")
