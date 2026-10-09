#!/usr/bin/env python3
"""Read locus on Self-Forcing: the README tables.

    python analysis/read_locus/tables.py [--vbench]

Reads data/read_locus_sf_48s.csv and data/far_mass_48s.csv; --vbench adds VBench-Long via specs/*.json.
Intervals: 95% bootstrap over prompts, 4000 draws from default_rng(0); '*' = excludes 0."""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
BANDS = ["L0_9", "L10_19", "L20_29"]
BLAB = {"L0_9": "0-9", "L10_19": "10-19", "L20_29": "20-29"}


def read_csv(name):
    out = {}
    with open(os.path.join(DATA, name)) as fh:
        for r in csv.DictReader(fh):
            out[(r["arm"], int(r["seed"]), int(r["prompt"]))] = r
    return out


SF, FM = read_csv("read_locus_sf_48s.csv"), read_csv("far_mass_48s.csv")
f = lambda r, k: float(r[k]) if r[k] != "" else np.nan


def load(rows, arms, seeds):
    """per arm: identity, log motion ratio, DiT time, late/early drift ratios over cells sorted by (prompt, seed)"""
    cells = sorted((p, s) for (a, s, p) in rows if a == arms[0] and s in seeds)
    assert all(sorted((p, s) for (a2, s, p) in rows if a2 == a and s in seeds) == cells for a in arms), arms
    D = {}
    for a in arms:
        rs = [rows[(a, s, p)] for p, s in cells]
        ratio = lambda k: np.array([np.nanmean(np.array([f(r, f"{k}_{t}") for t in range(38, 48)])) /
                                    np.nanmean(np.array([f(r, f"{k}_{t}") for t in range(4, 8)])) for r in rs])
        D[a] = dict(L=np.array([f(r, "dino_late_38_47") for r in rs]), E=np.array([f(r, "dino_early_4_8") for r in rs]),
                    lm=np.array([np.log(f(r, "motion_late_38_47") / f(r, "motion_early_4_8")) for r in rs]),
                    ms=float(np.median([f(r, "dit_ms_per_block") for r in rs])),
                    sat=ratio("sat"), bri=ratio("bri"), det=ratio("det"))
    prom = np.array([p for p, _ in cells])
    up = np.unique(prom)
    rng = np.random.default_rng(0)
    boot = [np.concatenate([np.where(prom == p)[0] for p in rng.choice(up, len(up))]) for _ in range(4000)]
    return D, cells, boot


def ci(boot, fn):
    return np.percentile([fn(b) for b in boot], [2.5, 97.5])


def star(lo, hi):
    return "*" if lo > 0 or hi < 0 else ""


def contrast(D, boot, a, b):
    dl, dm = D[a]["L"] - D[b]["L"], D[a]["lm"] - D[b]["lm"]

    def adj(i):
        X = np.stack([np.ones(len(i)), dm[i]], 1)
        return np.linalg.lstsq(X, dl[i], rcond=None)[0][0]
    lo, hi = ci(boot, lambda i: dl[i].mean())
    alo, ahi = ci(boot, adj)
    mlo, mhi = ci(boot, lambda i: dm[i].mean())
    st = lambda x: float((np.exp(x) < 0.85).mean())
    return dict(d=dl.mean(), lo=lo, hi=hi, adj=adj(np.arange(len(dl))), alo=alo, ahi=ahi, dm=dm.mean(), mlo=mlo,
                mhi=mhi, static=st(D[a]["lm"]), static_b=st(D[b]["lm"]), ms=D[a]["ms"],
                sat=float(D[a]["sat"].mean() - D[b]["sat"].mean()), coll=float((D[a]["det"] < 0.5).mean()))


def grid_tables(C, prefix, ref_rows, tables):
    for title, fmt in tables:
        print(f"### {title}\n\n| pass \\ layers | 0-9 | 10-19 | 20-29 |\n|---|---|---|---|")
        for s in range(4):
            print(f"| s{s} | " + " | ".join(fmt(C[f"{prefix}_S{s}_{b}"]) for b in BANDS) + " |")
        print("\nreferences: " + "; ".join(f"{lab} {fmt(C[a])}" for a, lab in ref_rows) + "\n")


def far_mass(arm, seeds):
    """{(pass, layer): [per-video share]} over the arm's videos"""
    mass = {}
    for (a, s, p), r in sorted(FM.items(), key=lambda kv: (kv[0][1], kv[0][2])):
        if a != arm or s not in seeds:
            continue
        for c in range(4):
            for layer in range(30):
                v = r[f"far_mass_s{c}_{layer}"]
                if v != "":
                    mass.setdefault((f"s{c}", layer), []).append(float(v))
    return mass


SF_ARMS = ["MM_R12", "MM_ALL", "MM_S23"] + [f"MM_S{s}_{b}" for s in range(4) for b in BANDS]


def sf_map():
    D, cells, boot = load(SF, SF_ARMS, (0, 1, 2))
    C = {a: contrast(D, boot, a, "MM_R12") for a in SF_ARMS if a != "MM_R12"}
    g_all = C["MM_ALL"]["d"]
    print(f"## Self-Forcing: far anchors read in one (denoising pass, layer band) cell ({len(cells)} cells, vs MM_R12)\n")
    print(f"Reading far history in every denoising pass and layer (MM_ALL): identity gain {g_all:+.4f}; "
          "'share of full gain' = the cell's gain / this gain.\n")
    refs = [("MM_ALL", "all passes x all layers"), ("MM_S23", "passes s2+s3 x all layers")]
    grid_tables(C, "MM", refs, [
        ("Identity gain [95% CI]", lambda c: "%+.4f%s [%+.4f,%+.4f]" % (c["d"], star(c["lo"], c["hi"]), c["lo"], c["hi"])),
        ("Motion-adjusted identity gain (ANCOVA)", lambda c: "%+.4f%s" % (c["adj"], star(c["alo"], c["ahi"]))),
        ("Share of the full-read gain", lambda c: "%.2f" % (c["d"] / g_all)),
        ("Motion change, d log(late / early motion) [CI]",
         lambda c: "%+.3f%s [%+.3f,%+.3f]" % (c["dm"], star(c["mlo"], c["mhi"]), c["mlo"], c["mhi"])),
        ("Reduced-motion cells (no far read = %.2f)" % ((np.exp(D["MM_R12"]["lm"]) < 0.85).mean()), lambda c: "%.2f" % c["static"]),
        ("Saturation drift difference (late / early)", lambda c: "%+.3f" % c["sat"])])
    print("DiT ms per block (median): " + ", ".join(f"{a} {D[a]['ms']:.0f}" for a in SF_ARMS) + "\n")
    mass = far_mass("MM_ALL", (0, 1, 2))
    print("### Share of attention on the far anchors (MM_ALL, +ln4 included; mean over videos)\n")
    print("| pass | " + " | ".join(f"L{l}" for l in range(0, 30, 3)) + " | 0-9 mean | 10-19 mean | 20-29 mean |")
    print("|---|" + "---|" * 13)
    for cls in ["s0", "s1", "s2", "s3"]:
        row = [np.mean(mass.get((cls, l), [np.nan])) for l in range(30)]
        band = [np.nanmean(row[0:10]), np.nanmean(row[10:20]), np.nanmean(row[20:30])]
        print(f"| {cls} | " + " | ".join("%.3f" % row[l] for l in range(0, 30, 3)) + " | " +
              " | ".join("%.3f" % x for x in band) + " |")
    print()
    return D, C


def sf_content():
    """M4: what the far anchors hold, at s3 x layers 20-29 (region A) and s2+s3 x layers 20-29 (region B)"""
    fmt = lambda t: "%+.4f%s [%+.4f,%+.4f]" % (t[0], "*" if t[1] > 0 or t[2] < 0 else "", t[1], t[2])
    for reg, ref, title in [("A", "MM_S3_L20_29", "pass s3 x layers 20-29"), ("B", "M4_B_NORMAL", "passes s2+s3 x layers 20-29")]:
        arms = ["MM_R12", ref, f"M4_{reg}_RECENT", f"M4_{reg}_RAND", f"M4_{reg}_MEAN"]
        X, cells, boot = load(SF, arms, (0, 1, 2))

        def diff(a, b, key="L"):
            d = X[a][key] - X[b][key]
            lo, hi = ci(boot, lambda i: d[i].mean())
            return d.mean(), lo, hi

        def adj(a, b):
            dl, dm = X[a]["L"] - X[b]["L"], X[a]["lm"] - X[b]["lm"]

            def fn(i):
                Xm = np.stack([np.ones(len(i)), dm[i]], 1)
                return np.linalg.lstsq(Xm, dl[i], rcond=None)[0][0]
            lo, hi = ci(boot, fn)
            return fn(np.arange(len(dl))), lo, hi
        st = lambda a: float((np.exp(X[a]["lm"]) < 0.85).mean())
        g_ref = X[ref]["L"].mean() - X["MM_R12"]["L"].mean()
        print(f"## Content controls, region {reg} ({title}; {len(cells)} cells)\n")
        print(f"Normal anchors vs no far read: identity gain {g_ref:+.4f}; 'kept' = the arm's gain / this gain.\n")
        print("| far anchors hold | identity vs no far | motion-adjusted | vs normal anchors | kept | "
              "motion d log (vs no far) | reduced motion | saturation drift (vs no far) |")
        print("|---|---|---|---|---|---|---|---|")
        for a, lab in [(ref, "old frames of this video (normal)"), (f"M4_{reg}_RECENT", "recent frames (no old content)"),
                       (f"M4_{reg}_RAND", "statistics-matched random (no content)"),
                       (f"M4_{reg}_MEAN", "temporal mean of the old frames")]:
            d0, dr, dm = diff(a, "MM_R12"), (diff(a, ref) if a != ref else None), diff(a, "MM_R12", "lm")
            sat = X[a]["sat"].mean() - X["MM_R12"]["sat"].mean()
            print(f"| {lab} | {fmt(d0)} | {fmt(adj(a, 'MM_R12'))} | {'-' if dr is None else fmt(dr)} | {d0[0] / g_ref:.2f} | "
                  f"{fmt(dm).replace('+0.', '+.').replace('-0.', '-.')} | {st(a):.2f} (no far {st('MM_R12'):.2f}) | {sat:+.3f} |")
        print()


def vbench():
    sys.path.insert(0, os.path.join(HERE, "..", "..", "eval", "vbench_long"))
    import compare
    for seed in (0, 1):
        path = os.path.join(HERE, "specs", f"vbl48_seed{seed}.json")
        spec = json.load(open(path))
        spec["scores"] = os.path.join(os.path.dirname(path), spec["scores"])
        compare.run(spec)
        print()


if __name__ == "__main__":
    print("# Where far history is read (Self-Forcing)\n")
    sf_map()
    sf_content()
    if "--vbench" in sys.argv:
        print("# VBench-Long, rollf200 x 48 s (eval/vbench_long/compare.py)\n")
        vbench()
