#!/usr/bin/env python3
"""Verdict for PLAN.md "Rolling Sink 写入步预注册": RS_real - RS_off, paired by (prompt, seed), prompt bootstrap.
usage: rs_verdict.py ROOT DRIFT_JSON"""
import glob, json, os, re, sys
import numpy as np

ROOT, DRF = sys.argv[1], sys.argv[2]
ARMS = ["RS_off", "RS_real"]
ID, DR = json.load(open(os.path.join(ROOT, "ident2.json"))), json.load(open(DRF))
have = {a: {(int(re.match(r"(\d+)-", os.path.basename(v)).group(1)), int(re.search(r"_seed(\d+)\.vid", v).group(1)))
            for v in glob.glob(f"{ROOT}/{a}_seed*.vid/*-0_ema.mp4") if os.path.exists(v[:-4] + ".json")} for a in ARMS}
assert have["RS_off"] == have["RS_real"], {a: len(have[a]) for a in ARMS}
cells = [(p, s) for (p, s) in sorted(have["RS_off"]) if any(p2 == p and s2 != s for (p2, s2) in have["RS_off"])]
n = len(cells); prom = np.array([p for p, _ in cells]); up = np.unique(prom)


def lr(a, k):
    idx = {tuple(c): i for i, c in enumerate(DR[a]["cells"])}
    x = np.array(DR[a][k], dtype=float)
    return np.array([np.nanmean(x[idx[c], 38:48]) / np.nanmean(x[idx[c], 4:8]) for c in cells])


M = {}
for a in ARMS:
    js = [json.load(open(f"{ROOT}/{a}_seed{s}.vid/{p}-0_ema.json")) for p, s in cells]
    M[a] = dict(sat=lr(a, "sat"), bri=lr(a, "bri"), det=lr(a, "det"), ident=np.array(ID[a]["dino_late_38_47"]),
                early=np.array(ID[a]["dino_early_4_8"]),
                m=np.array([np.log(j["motion_late_38_47"] / j["motion_early_4_8"]) for j in js]),
                ms=float(np.median([j["dit_ms_per_block"] for j in js])))
    M[a]["dsat"], M[a]["dbri"] = np.abs(M[a]["sat"] - 1), np.abs(M[a]["bri"] - 1)
rng = np.random.default_rng(0)
BOOT = [np.concatenate([np.where(prom == p)[0] for p in rng.choice(up, len(up))]) for _ in range(4000)]
ci = lambda d: np.percentile([d[b].mean() for b in BOOT], [2.5, 97.5])
print(f"cells {n}  prompts {len(up)}")
for a in ARMS:
    x = M[a]
    print("%-8s ret %.3f late %.4f sat_le %.3f bri_le %.3f |sat-1| %.3f |bri-1| %.3f det_le %.2f m_med %.2f static %.2f ms/blk %.0f" % (
        a, x["ident"].mean() / x["early"].mean(), x["ident"].mean(), x["sat"].mean(), x["bri"].mean(), x["dsat"].mean(),
        x["dbri"].mean(), x["det"].mean(), np.exp(np.median(x["m"])), (np.exp(x["m"]) < 0.85).mean(), x["ms"]))
R = {}
for k in ("sat", "bri", "dsat", "dbri", "ident", "m", "det"):
    d = M["RS_real"][k] - M["RS_off"][k]; lo, hi = ci(d); R[k] = (d.mean(), lo, hi)
    print(f"RS_real - RS_off {k:6s} {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]  real>off {(d > 0).mean():.2f}")
mech = R["sat"][2] < 0 or R["bri"][1] > 0 or R["dsat"][2] < 0 or R["dbri"][2] < 0
print("MECH (less colour drift with real-history write step):", mech, "->", "supports H_content" if mech else "supports H_count")
print("APP  identity non-inferior (CI lower >= -0.02):", R["ident"][1] >= -0.02, " and less drift:", mech)
