#!/usr/bin/env python3
"""Replay archived fixed latent diagnostics with 4,000 prompt-cluster bootstrap draws (seed 0)."""
import glob
import json
import os
from pathlib import Path
import argparse

import numpy as np

O = str(Path(__file__).resolve().parent / "data" / "fixed_latent")
cells = [json.load(open(f)) for f in sorted(glob.glob(f"{O}/*.json"))]
if len(cells) != 20:
    raise ValueError("Expected 20 scalar diagnostic records")
rng = np.random.default_rng(0)
L = [f"# FLI readout: fixed-latent single-commit intervention on SGF ({len(cells)} cells)\n"]


def boot(vals, prom):
    vals, prom = np.asarray(vals, float), np.asarray(prom)
    up = np.unique(prom)
    grp = {p: np.where(prom == p)[0] for p in up}
    bs = [vals[np.concatenate([grp[p] for p in rng.choice(up, len(up))])].mean() for _ in range(4000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return vals.mean(), lo, hi


def fmt(m, lo, hi, d=4):
    st = "*" if lo > 0 or hi < 0 else ""
    return f"{m:+.{d}f}{st} [{lo:+.{d}f}, {hi:+.{d}f}]"


L.append("Source pixel hashes are retained in cells; the source-video equality check is not replayed here.\n")
det = [r["gen"]["det_ok"] for c in cells for run in c["runs"] for r in run["lags"] if "gen" in r]
L.append(f"Determinism (control generated twice, identical): {sum(det)} / {len(det)}.\n")
for base in ("R", "C"):
    L += [f"## Base commit policy {base} ({'newest 9 frames' if base == 'R' else 'self-only, the current block'})\n",
          "| k | b* stored | own K rel diff | own V rel diff | later K rel diff [95% CI] | later V rel diff [95% CI] |",
          "|---|---|---|---|---|---|"]
    rows = [(c["prompt"], run["bstar"], r) for c in cells for run in c["runs"] if run["base"] == base for r in run["lags"]]
    for k in range(cells[0]["kmax"] + 1):
        rk = [(p, r) for p, _, r in rows if r["k"] == k]
        prom = [p for p, _ in rk]
        own_k = [np.mean(r["own_k"]) for _, r in rk if r["own_k"]]
        own_v = [np.mean(r["own_v"]) for _, r in rk if r["own_v"]]
        lk = [np.mean(r["later_k"]) if r["later_k"] else np.nan for _, r in rk]
        lv = [np.mean(r["later_v"]) if r["later_v"] else np.nan for _, r in rk]
        stored = all(r["own_present"] for _, r in rk)
        ok = ~np.isnan(lk)
        sk = fmt(*boot(np.array(lk)[ok], np.array(prom)[ok])) if ok.any() else "—"
        sv = fmt(*boot(np.array(lv)[ok], np.array(prom)[ok])) if ok.any() else "—"
        L.append(f"| {k} | {'yes' if stored else 'no'} | {np.mean(own_k):.4f} | {np.mean(own_v):.4f} | {sk} | {sv} |"
                 if own_k else f"| {k} | {'yes' if stored else 'no'} | — | — | {sk} | {sv} |")
    if base == "C":
        mx = max([max(r["later_k"] + r["later_v"] + [0.0]) for _, _, r in rows if r["k"] >= 1] + [0.0])
        gx = max([r["gen"]["pix_abs"] for _, _, r in rows if "gen" in r and r["k"] >= 2] + [0.0])
        L.append(f"\nC null gate: max later-block KV difference at k >= 1 = {mx:.3g}; max generated |pixel diff| at k >= 2 "
                 f"= {gx:.3g} -> {'PASS (exact 0)' if mx == 0 and gx == 0 else 'FAIL'}\n")
    else:
        r3 = [r for _, _, r in rows if r["k"] == 3 and r["later_k"]]
        prof_k = np.mean([r["later_k"] for r in r3], 0)
        L.append("\nPer-layer later-block K rel diff at k = 3 (layers 0..29): " + " ".join(f"{x:.3f}" for x in prof_k) + "\n")
        r2 = [np.mean(r["later_k"]) for _, _, r in rows if r["k"] == 2 and r["later_k"]]
        r3m = [np.mean(r["later_k"]) for r in r3]
        L.append(f"Later-block K difference, first post-eviction (k = 3) / k = 2: {np.mean(r3m) / np.mean(r2):.3f}\n")
    L += [f"### Generated block (B - A), base {base}\n",
          "| k | b* read by this block's denoising? | latent rel diff | mean abs pixel diff (0-255) | d_sat [95% CI] | d_bri [95% CI] | sign share d_sat / d_bri |",
          "|---|---|---|---|---|---|---|"]
    for k in cells[0]["genk"]:
        rk = [(p, r["gen"]) for p, _, r in rows if r["k"] == k and "gen" in r]
        prom = [p for p, _ in rk]
        ds, db = [g["dsat"] for _, g in rk], [g["dbri"] for _, g in rk]
        share = lambda x: max(np.mean(np.array(x) > 0), np.mean(np.array(x) < 0))
        L.append(f"| {k} | {'yes' if k + 1 <= 2 else 'no (evicted)'} | {np.mean([g['lat_rel'] for _, g in rk]):.4f} | "
                 f"{np.mean([g['pix_abs'] for _, g in rk]):.3f} | {fmt(*boot(ds, prom), d=5)} | {fmt(*boot(db, prom), d=5)} | "
                 f"{share(ds):.2f} / {share(db):.2f} |")
    L.append("")
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path)
args = parser.parse_args()
if args.output:
    args.output.write_text("\n".join(L) + "\n")
print("\n".join(L))
