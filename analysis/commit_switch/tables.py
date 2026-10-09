#!/usr/bin/env python3
"""Finding 1 (commit switch, Self-Forcing): the README tables from data/commit_switch_48s.csv.

    python analysis/commit_switch/tables.py

One row per video (arm, seed, prompt); 20 prompts x seeds 0-2 per arm, 48 s.
Intervals: 95% bootstrap over prompts, 4000 draws from default_rng(0), shared by all contrasts."""
import csv
import os

import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "commit_switch_48s.csv")
AGES = {"early_4_8": (4.0, 8.0), "mid_20_26": (20.0, 26.0), "late_38_47": (38.0, 47.5)}
DRIFT = ("sat", "con", "det", "bri")
EARLY = slice(4, 8)  # drift baseline, seconds 4-8


def load():
    rows = {}
    with open(DATA) as fh:
        for r in csv.DictReader(fh):
            rows.setdefault(r["arm"], []).append(r)
    arms = {}
    for arm, rs in rows.items():
        rs.sort(key=lambda r: (int(r["prompt"]), int(r["seed"])))
        col = lambda k: np.array([float(r[k]) if r[k] != "" else np.nan for r in rs])
        a = {k: col(k) for k in rs[0] if k not in ("arm", "seed", "prompt") and not k.split("_")[0] in DRIFT}
        for k in DRIFT:
            a[k] = np.array([[float(r[f"{k}_{t}"]) for t in range(48)] for r in rs])
        a["cells"] = [(int(r["prompt"]), int(r["seed"])) for r in rs]
        arms[arm] = a
    return arms


A = load()
CELLS = A["R12"]["cells"]
assert all(a["cells"] == CELLS for a in A.values())
PROM = np.array([p for p, _ in CELLS])


def bootstrap():
    """prompt-level resamples of the cell indices, the same 4000 for every contrast"""
    rng = np.random.default_rng(0)
    up = np.unique(PROM)
    return [np.concatenate([np.where(PROM == p)[0] for p in rng.choice(up, len(up))]) for _ in range(4000)]


BOOT = bootstrap()


def ci(f):
    return np.percentile([f(b) for b in BOOT], [2.5, 97.5])


def ident_table(arms):
    """identity per time window (mean +- s.e. over cells) and retention = ident(window) / ident(4-8 s)"""
    keys = list(AGES)
    for tag in ("clip", "dino"):
        print(f"--- {tag.upper()} ---")
        hdr = " ".join(f"{a + ' ' + str(AGES[a][0]) + '-' + str(AGES[a][1]):>20}" for a in keys)
        print(f"{'config':>11} | {hdr} | " + " ".join(f"{'ret ' + a:>12}" for a in keys[1:]))
        for arm in arms:
            base = A[arm][f"{tag}_{keys[0]}"].mean()
            cells, rets = [], []
            for k in keys:
                v = A[arm][f"{tag}_{k}"]
                cells.append(f"{v.mean():>11.4f}+-{v.std(ddof=1) / len(v) ** 0.5:<7.4f}")
            for k in keys[1:]:
                rets.append(f"{A[arm][f'{tag}_{k}'].mean() / base:>12.2f}")
            print(f"{arm:>11} | {' '.join(cells)} | {' '.join(rets)}")
        print()


def logm(arm):
    return np.log(A[arm]["motion_late_38_47"] / A[arm]["motion_early_4_8"])


def q3():
    """commit pass reading far history vs not, with the denoising passes reading it too (same-batch arms)"""
    arms = ["R12", "S123", "S123R", "S123C", "R160"]
    assert (A["S123C"]["commit_window_max"] == 160).all() and (A["S123R"]["commit_window_max"] == 12).all()
    print(f"cells {len(CELLS)} prompts {len(np.unique(PROM))}")
    print("%-6s %7s %6s %6s %7s %8s" % ("arm", "late", "ret", "m_med", "reduced", "ms/blk"))
    L = {a: A[a]["dino_late_38_47"] for a in arms}
    for a in arms:
        lm = logm(a)
        print("%-6s %7.4f %6.3f %6.2f %7.2f %8.0f" % (a, L[a].mean(), L[a].mean() / A[a]["dino_early_4_8"].mean(),
                                                    np.exp(np.median(lm)), (np.exp(lm) < 0.85).mean(),
                                                    float(np.nanmedian(A[a]["dit_ms_per_block"]))))
    res = {}
    for a, b in [("S123C", "S123R"), ("S123C", "S123"), ("S123R", "S123"), ("R160", "S123C")]:
        d = L[a] - L[b]
        lo, hi = ci(lambda i: d[i].mean())
        dm = logm(a) - logm(b)
        mlo, mhi = ci(lambda i: dm[i].mean())
        res[(a, b)] = (d.mean(), lo, hi, dm.mean())
        print(f"{a:6s}-{b:6s} dIdent {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]  dlog m {dm.mean():+.3f} [{mlo:+.3f},{mhi:+.3f}]"
              f"  cells a>b {(d > 0).mean():.2f}")
    verdict = lambda lo, hi: "HARMFUL" if hi < 0 else ("HELPFUL" if lo > 0 else "NEUTRAL")
    print("PRIMARY   S123C vs S123R (same batch):", verdict(*res[("S123C", "S123R")][1:3]))
    print("SECONDARY S123C vs S123 (archived):  ", verdict(*res[("S123C", "S123")][1:3]))
    lo, hi = res[("S123R", "S123")][1:3]
    print("EXCHANGEABILITY S123R vs S123:", "exchangeable" if lo <= 0 <= hi else "NOT exchangeable")
    return res


def paired(a, b, key):
    """relative drift r(t) = x(t) / mean(x, 4-7 s) of each video; returns r_a - r_b per cell"""
    xa, xb = A[a][key], A[b][key]
    return xa / xa[:, EARLY].mean(1, keepdims=True) - xb / xb[:, EARLY].mean(1, keepdims=True)


def dci(v):
    return ci(lambda i: v[i].mean())


def slope(d, t0, t1):
    """per-cell least-squares slope of d over seconds [t0, t1), per 10 s"""
    t = np.arange(t0, t1) + 0.5
    x = d[:, t0:t1]
    tc = t - t.mean()
    return 10.0 * (x - x.mean(1, keepdims=True)) @ tc / (tc @ tc)


def fmt_ci(v):
    lo, hi = dci(v)
    return f"{v.mean():+.4f} [{lo:+.4f},{hi:+.4f}]"


def summarize(a, b, key, lab=""):
    d = paired(a, b, key)
    s, e, l = slope(d, 8, 48), d[:, 8:16].mean(1), d[:, 38:48].mean(1)
    acc = slope(d, 28, 48) - slope(d, 8, 28)
    print(f"  {key} {a}-{b}: slope {fmt_ci(s)}/10s  early {fmt_ci(e)}  late {fmt_ci(l)}  accel {fmt_ci(acc)} {lab}".rstrip())
    return d, s, e, l


def drift():
    print("relative drift r(t) = x(t) / mean of x over seconds 4-8 of the same video; differences paired by cell")
    print("slope: per-cell least-squares slope over seconds 8-48, per 10 s; early: seconds 8-16; late: seconds 38-48;")
    print("accel: slope over seconds 28-48 minus slope over seconds 8-28\n")
    print("step 1: S123C - S123R (the commit pass also reads far history)")
    d, s, e, l = summarize("S123C", "S123R", "sat", "(primary)")
    lo, hi = dci(s)
    ratio = l.mean() / e.mean()
    verdict = "ACCUMULATING" if (lo > 0 and ratio >= 2) else ("ONE-SHOT" if lo <= 0 <= hi else "UNDECIDED")
    print(f"  late/early ratio {ratio:.2f} -> {verdict}")
    for k in ("con", "det", "bri"):
        summarize("S123C", "S123R", k)
    for a, b in [("C", "R12"), ("R160", "S123"), ("S123R", "S123")]:
        print(f"  reference {a} - {b}:")
        for k in DRIFT:
            summarize(a, b, k)
    print("step 2: switch arms (saturation)")
    sl = slope(paired("SWRC", "S123C", "sat"), 24, 34)
    lo, hi = dci(sl)
    main = "no history dependence" if lo <= 0 <= hi else ("history dependence: SWRC slower" if hi < 0 else
                                                          "SWRC faster (no compounding)")
    print(f"  slope(SWRC - S123C) 24-34 s: {sl.mean():+.4f}/10s [{lo:+.4f},{hi:+.4f}] -> {main}")
    for a, b in [("SWRC", "S123R"), ("S123C", "S123R")]:
        print(f"    slope({a} - {b}) 24-34 s {fmt_ci(slope(paired(a, b, 'sat'), 24, 34))}")
    sl2 = slope(paired("SWCR", "S123C", "sat"), 26, 48)
    lo2, hi2 = dci(sl2)
    print(f"  slope(SWCR - S123C) 26-47.5 s: {sl2.mean():+.4f} [{lo2:+.4f},{hi2:+.4f}] -> "
          f"{'drift stops growing when the commit pass stops reading' if hi2 < 0 else 'not shown'}")
    lp = paired("SWCR", "S123R", "sat")[:, 38:48].mean(1)
    lo3, hi3 = dci(lp)
    print(f"  late(SWCR - S123R) 38-47.5 s: {lp.mean():+.4f} [{lo3:+.4f},{hi3:+.4f}] -> "
          f"{'drift already written stays' if lo3 > 0 else 'not shown'}")
    for k in ("con", "det", "bri"):
        for a, b in [("SWCR", "S123R"), ("SWRC", "S123R")]:
            summarize(a, b, k)
    return e.mean(), l.mean()


def verdict_vs(ref, arms, pairs):
    """identity of each arm vs a reference arm: raw and motion-adjusted (ANCOVA on the log motion ratio)"""
    L = {c: A[c]["dino_late_38_47"] for c in arms}
    E = {c: A[c]["dino_early_4_8"] for c in arms}
    MR = {c: A[c]["motion_late_38_47"] / A[c]["motion_early_4_8"] for c in arms}
    n = len(CELLS)
    print(f"cells {n}  prompts {len(np.unique(PROM))}  ref {ref}\n")
    print("%-9s %7s %7s %6s %8s %8s  %-26s %-26s %4s" % ("arm", "early", "late", "ret", "ms/blk", "m_ratio",
                                                       "raw dL vs ref (CI)", "ANCOVA dL (CI)", "n_m"))
    for c in arms:
        ret, ms = L[c].mean() / E[c].mean(), float(np.nanmedian(A[c]["dit_ms_per_block"]))
        if c == ref:
            print("%-9s %7.4f %7.4f %6.3f %8.0f %8.2f  %-26s" % (c, E[c].mean(), L[c].mean(), ret, ms,
                                                                 np.nanmedian(MR[c]), "(reference)"))
            continue
        dy, dx = L[c] - L[ref], np.log(MR[c]) - np.log(MR[ref])

        def adj(i):
            X = np.stack([np.ones(len(i)), dx[i]], 1)
            return np.linalg.lstsq(X, dy[i], rcond=None)[0][0]
        r_lo, r_hi = ci(lambda i: dy[i].mean())
        a, (a_lo, a_hi) = adj(np.arange(n)), ci(adj)
        mm = np.where((MR[c] >= 0.8) & (MR[ref] >= 0.8))[0]
        print("%-9s %7.4f %7.4f %6.3f %8.0f %8.2f  %+.4f [%+.4f,%+.4f]  %+.4f [%+.4f,%+.4f] %4d" %
              (c, E[c].mean(), L[c].mean(), ret, ms, np.nanmedian(MR[c]), dy.mean(), r_lo, r_hi, a, a_lo, a_hi, len(mm)))
    for a_, b_ in pairs:
        d = L[a_] - L[b_]
        lo, hi = ci(lambda i: d[i].mean())
        print("pair %s - %s: late ident %+.4f [%+.4f,%+.4f]  cells a>b %.2f" % (a_, b_, d.mean(), lo, hi, (d > 0).mean()))


def supplement():
    """late (38-47.5 s) saturation drift of each reading schedule relative to reading no far history (R12)"""
    print("%-6s %-18s %s" % ("arm", "far read in", "late sat drift vs R12 [95% CI]"))
    where = {"S0": "s0", "S1": "s1", "S2": "s2", "S3": "s3", "S23": "s2 s3", "S123R": "s1 s2 s3",
             "S123C": "s1 s2 s3 + commit", "C": "commit only"}
    for a, w in where.items():
        print("%-6s %-18s %s" % (a, w, fmt_ci(paired(a, "R12", "sat")[:, 38:48].mean(1))))


if __name__ == "__main__":
    print("== Q3: identity (DINOv2 and CLIP), 60 cells\n")
    ident_table(["R12", "S123", "S123R", "S123C", "R160"])
    print("== Q3: the commit pass reads far history too (S123C) vs only the denoising passes (S123R)\n")
    res = q3()
    print("\n== Drift curves (saturation / contrast / detail / brightness relative to 4-8 s)\n")
    early, late = drift()
    print("\n== Switch arms: identity\n")
    ident_table(["R12", "S123R", "S123C", "SWCR", "SWRC"])
    verdict_vs("S123R", ["R12", "S123R", "S123C", "SWCR", "SWRC"],
               [("SWCR", "S123R"), ("SWRC", "S123R"), ("SWCR", "S123C"), ("SWRC", "S123C")])
    print("\n== Saturation drift of each reading schedule vs no far reading (R12), 38-47.5 s\n")
    supplement()
    d, lo, hi, dm = res[("S123C", "S123R")]
    st = {a: float((np.exp(logm(a)) < 0.85).mean()) for a in ("S123R", "S123C")}
    ms = {a: float(np.nanmedian(A[a]["dit_ms_per_block"])) for a in ("S123R", "S123C")}
    print("\n== Summary (S123C vs S123R)\n")
    print(f"identity {d:+.3f} [{lo:+.3f},{hi:+.3f}]; motion ratio x{np.exp(dm):.2f} ({100 * (np.exp(dm) - 1):+.0f}%); "
          f"reduced-motion cells {100 * st['S123R']:.0f}% -> {100 * st['S123C']:.0f}%; DiT {100 * (ms['S123C'] / ms['S123R'] - 1):+.0f}%; "
          f"saturation drift {100 * early:+.1f}% at 8-16 s -> {100 * late:+.1f}% at 38-47.5 s")
