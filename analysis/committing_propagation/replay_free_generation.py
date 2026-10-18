#!/usr/bin/env python3
"""Replay archived free generation diagnostics with 4,000 prompt-cluster bootstrap draws (seed 0)."""
import glob
import json
import os
from pathlib import Path
import argparse

import numpy as np

O = str(Path(__file__).resolve().parent / "data" / "free_generation")
cells = [json.load(open(f)) for f in sorted(glob.glob(f"{O}/*.json"))]
if len(cells) != 40:
    raise ValueError("Expected 40 scalar diagnostic records")
rng = np.random.default_rng(0)
prom = np.array([c["prompt"] for c in cells])


def boot(vals, pr=prom):
    vals = np.asarray(vals, float)
    up = np.unique(pr)
    grp = {p: np.where(pr == p)[0] for p in up}
    bs = [vals[np.concatenate([grp[p] for p in rng.choice(up, len(up))])].mean() for _ in range(4000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    st = "*" if lo > 0 or hi < 0 else ""
    return f"{vals.mean():+.5f}{st} [{lo:+.5f}, {hi:+.5f}]"


L = [f"# Free-generation and fixed-content burst readout ({len(cells)} cells)\n",
     "Source pixel hashes are retained in cells; the source-video equality check is not replayed here.\n"]
WIN = [("during burst 16-31", 16, 31), ("right after stop 32-35", 32, 35), ("36-43", 36, 43), ("44-51", 44, 51),
       ("52-63", 52, 63)]
for name in ("burst", "single"):
    L += [f"## Free generation, {name} (vs control; mean over the blocks of each window)\n",
          "| blocks | d_sat [95% CI] | d_bri [95% CI] | mean abs pixel diff | latent rel diff |", "|---|---|---|---|---|"]
    wins = WIN if name == "burst" else [("before 0-19", 0, 19), ("block 20", 20, 20), ("21-23", 21, 23), ("24-31", 24, 31),
                                       ("32-43", 32, 43), ("44-63", 44, 63)]
    for lab, lo, hi in wins:
        rows = [[r for r in c[name] if lo <= r["j"] <= hi] for c in cells]
        ds = [np.mean([r["dsat"] for r in rr]) for rr in rows]
        db = [np.mean([r["dbri"] for r in rr]) for rr in rows]
        L.append(f"| {lab} | {boot(ds)} | {boot(db)} | {np.mean([np.mean([r['pix_abs'] for r in rr]) for rr in rows]):.2f} | "
                 f"{np.mean([np.mean([r['lat_rel'] for r in rr]) for rr in rows]):.3f} |")
    L.append("")
L += ["## Cache-only burst (content fixed = control latents; next block generated from caches A / B)\n",
      "| generated block | relation to the burst | d_sat [95% CI] | d_bri [95% CI] | mean abs pixel diff | later-block K rel diff |",
      "|---|---|---|---|---|---|"]
for i, b in enumerate(cells[0]["gen_at"]):
    rr = [c["cache_only_burst"][i] for c in cells]
    rel = "during" if b < 31 else ("first after stop" if b == 31 else f"{b - 31} blocks after stop")
    kv = [np.mean(r["kv"]["later_k"]) for r in rr if r["kv"] and r["kv"]["later_k"]]
    L.append(f"| {b + 1} | {rel} | {boot([r['dsat'] for r in rr])} | {boot([r['dbri'] for r in rr])} | "
             f"{np.mean([r['pix_abs'] for r in rr]):.2f} | {np.mean(kv):.4f} |" if kv else
             f"| {b + 1} | {rel} | {boot([r['dsat'] for r in rr])} | {boot([r['dbri'] for r in rr])} | "
             f"{np.mean([r['pix_abs'] for r in rr]):.2f} | — |")
L.append("\nFree-generation offsets at the same generated blocks (burst vs control):\n")
L += ["| block | d_sat [95% CI] | d_bri [95% CI] | mean abs pixel diff |", "|---|---|---|---|"]
for b in cells[0]["gen_at"]:
    rr = [c["burst"][b + 1] for c in cells]
    L.append(f"| {b + 1} | {boot([r['dsat'] for r in rr])} | {boot([r['dbri'] for r in rr])} | {np.mean([r['pix_abs'] for r in rr]):.2f} |")
parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path)
args = parser.parse_args()
if args.output:
    args.output.write_text("\n".join(L) + "\n")
print("\n".join(L))
