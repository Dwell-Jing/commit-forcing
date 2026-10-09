#!/usr/bin/env python3
"""Tables of the LongLive sink 2x2 from data/longlive_sink_48s.csv (one row per 48 s video).

    python analysis/longlive_sink/tables.py [--csv CSV]

--csv takes a CSV with the same columns, such as the output of analysis/metrics/compute.py.
Videos are paired with LLS_33; intervals: 95% bootstrap over prompts, 4000 draws; '*' = excludes 0."""
import argparse
import csv
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "longlive_sink_48s.csv")
REF = "LLS_33"
ARMS = {"LLS_33": ("yes", "yes"),  # (denoise, commit) reads the sink
        "LLS_c0": ("yes", "no"),
        "LLS_d0": ("no", "yes"),
        "LLS_00": ("no", "no")}
SECONDS = 48
BOOT = 4000
KEYS = ("ident", "sat", "bri", "dsat", "dbri", "m", "det")


def compute(path=CSV):
    rows = {}
    with open(path) as fh:
        for r in csv.DictReader(fh):
            rows.setdefault(r["arm"], {})[(int(r["prompt"]), int(r["seed"]))] = r
    have = {a: set(rows[a]) for a in ARMS}
    assert all(have[a] == have[REF] for a in ARMS), {a: len(have[a]) for a in ARMS}
    cells = [(p, s) for (p, s) in sorted(have[REF]) if any(p2 == p and s2 != s for (p2, s2) in have[REF])]
    n = len(cells)
    prom = np.array([p for p, _ in cells])
    up = np.unique(prom)

    def column(a, key):
        return np.array([float(rows[a][c][key]) for c in cells])

    def late_over_early(a, key):
        x = np.array([[float(rows[a][c][f"{key}_{t}"]) for t in range(SECONDS)] for c in cells])
        return np.array([np.nanmean(x[i, 38:48]) / np.nanmean(x[i, 4:8]) for i in range(n)])

    def timing(a):  # DiT ms per block, nan if the CSV lacks it
        ok = all(rows[a][c].get("dit_ms_per_block", "") != "" for c in cells)
        return float(np.median(column(a, "dit_ms_per_block"))) if ok else float("nan")

    M = {}
    for a in ARMS:
        x = M[a] = dict(ident=column(a, "dino_late_38_47"), early=column(a, "dino_early_4_8"),
                        m=np.log(column(a, "motion_late_38_47") / column(a, "motion_early_4_8")),
                        sat=late_over_early(a, "sat"), bri=late_over_early(a, "bri"), det=late_over_early(a, "det"),
                        ms=timing(a))
        x["dsat"], x["dbri"] = np.abs(x["sat"] - 1), np.abs(x["bri"] - 1)
        x["ret"], x["late"] = x["ident"].mean() / x["early"].mean(), x["ident"].mean()
        x["m_med"], x["static"] = np.exp(np.median(x["m"])), (np.exp(x["m"]) < 0.85).mean()
        x["det_low"] = (x["det"] < 0.5).mean()

    rng = np.random.default_rng(0)
    boots = [np.concatenate([np.where(prom == p)[0] for p in rng.choice(up, len(up))]) for _ in range(BOOT)]
    D = {}
    for a in list(ARMS)[1:]:
        D[a] = {}
        for k in KEYS:
            d = M[a][k] - M[REF][k]
            lo, hi = np.percentile([d[b].mean() for b in boots], [2.5, 97.5])
            D[a][k] = (d.mean(), lo, hi)
        dl, dm = M[a]["ident"] - M[REF]["ident"], M[a]["m"] - M[REF]["m"]
        D[a]["ancova"] = np.linalg.lstsq(np.stack([np.ones(n), dm], 1), dl, rcond=None)[0][0]
    return dict(n=n, prompts=len(up), M=M, D=D)


def main():
    parser = argparse.ArgumentParser(description="Tables of the LongLive sink 2x2")
    parser.add_argument("--csv", default=CSV, help="metrics CSV (default: data/longlive_sink_48s.csv)")
    R = compute(parser.parse_args().csv)
    M, D = R["M"], R["D"]
    print(f"LongLive sink 2x2, 48 s: {R['n']} videos per arm ({R['prompts']} prompts x {R['n'] // R['prompts']} seeds), "
          f"reference {REF}\n")
    print("%-7s %7s %6s  %5s %7s %6s %7s %6s %6s %7s %7s %6s %7s %6s" % (
        "arm", "denoise", "commit", "ret", "late", "m_med", "reduced", "sat_le", "bri_le", "|sat-1|", "|bri-1|",
        "det_le", "det<0.5", "ms/blk"))
    for a, (dn, cm) in ARMS.items():
        x = M[a]
        print("%-7s %7s %6s  %5.3f %7.4f %6.2f %7.2f %6.3f %6.3f %7.3f %7.3f %6.2f %7.2f %6.0f" % (
            a, dn, cm, x["ret"], x["late"], x["m_med"], x["static"], x["sat"].mean(), x["bri"].mean(),
            x["dsat"].mean(), x["dbri"].mean(), x["det"].mean(), x["det_low"], x["ms"]))
    print(f"\npaired differences vs {REF}, mean [95% CI]; ANCOVA: identity difference at equal motion (intercept of "
          "the identity difference regressed on the motion difference)\n")
    for a in D:
        cell = {k: "%s %+.4f [%+.4f,%+.4f]%s" % (k, *D[a][k], "*" if D[a][k][1] > 0 or D[a][k][2] < 0 else " ")
                for k in KEYS}
        print(f"{a} - {REF}:  {cell['ident']}  ANCOVA {D[a]['ancova']:+.4f}  {cell['m']}\n"
              f"    {cell['sat']}  {cell['bri']}  {cell['dsat']}  {cell['dbri']}  {cell['det']}")


if __name__ == "__main__":
    main()
