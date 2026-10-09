#!/usr/bin/env python3
"""Tables of the SGF boundary: a base with a sink does not use history outside its window.

    python analysis/boundaries/sgf/tables.py

Reads the CSVs in data/ (one row per video). Intervals: 95% bootstrap over prompts, 4000 draws; '*' = excludes 0."""
import csv
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
B = 4000
SEC = 48
STATIC = 0.85


def read(name):
    with open(os.path.join(DATA, name)) as fh:
        return list(csv.DictReader(fh))


def star(lo, hi):
    return "*" if lo > 0 or hi < 0 else ""


def units(rows, key, **match):
    return {(int(r["prompt"]), int(r["seed"])): float(r[key]) for r in rows if all(r[k] == v for k, v in match.items())}


def prompt_diffs(a, b, both_seeds=True):
    byp = defaultdict(list)
    for u in sorted(set(a) & set(b)):
        byp[u[0]].append(a[u] - b[u])
    return np.array([np.mean(v) for _, v in sorted(byp.items()) if len(v) == 2 or not both_seeds])


def boot_integers(x, rng):
    """Bootstrap with rng.integers; the caller passes a fresh default_rng(0) per contrast."""
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return x.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5), len(x)


def boot_choice(x, rng):
    """Bootstrap with rng.choice; one rng is shared by the metrics of a contrast."""
    m = x[rng.choice(len(x), size=(B, len(x)), replace=True)].mean(axis=1)
    return x.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5), len(x)


def motion_units(rows, arm):
    out = {}
    for r in rows:
        if r["arm"] == arm:
            e, late = float(r["motion_early_4_8"]), float(r["motion_late_38_47"])
            out[(int(r["prompt"]), int(r["seed"]))] = float(late / e < STATIC)
    return out


FAR_ARMS = [("SGF_RFW_ST1L20_NM", "extra", "stride 1, layers 20-29"),
            ("SGF_RFW_ST2L20_NM", "main", "stride 2, layers 20-29"),
            ("SGF_RFW_ST4L20_NM", "extra", "stride 4, layers 20-29"),
            ("SGF_RFW_ST4L12_NM", "extra", "stride 4, layers 12-29")]


def far_reads_vbench():
    rows = read("far_reads_vbench.csv")
    keys = ("subject_consistency", "subject_consistency_clip2clip", "dynamic_degree")
    base = {tag: {k: units(rows, k, arm="SGF_RFW", vbench_root=tag) for k in keys} for tag in ("main", "extra")}
    sm, se = base["main"]["subject_consistency"], base["extra"]["subject_consistency"]
    out = dict(rfw_rescore_maxdiff=max(abs(sm[u] - se[u]) for u in sorted(set(sm) & set(se))), rfw_rescore_n=len(sm),
               rfw_means={k: 100 * np.mean([v[u] for u in sorted(v)]) for k, v in base["main"].items()},
               rfw_static=np.mean(list(motion_units(rows, "SGF_RFW").values())), arms={})
    st0 = motion_units(rows, "SGF_RFW")
    for arm, tag, label in FAR_ARMS:
        d = dict(label=label)
        for k in ("subject_consistency", "subject_consistency_clip2clip", "dynamic_degree"):
            a = units(rows, k, arm=arm, vbench_root=tag)
            d[k + "_mean"] = 100 * np.mean([a[u] for u in sorted(a)])
            d[k] = [100 * v if i < 3 else v for i, v in
                    enumerate(boot_integers(prompt_diffs(a, base[tag][k]), np.random.default_rng(0)))]
        st = motion_units(rows, arm)
        d["static_mean"] = np.mean(list(st.values()))
        d["static"] = boot_integers(prompt_diffs(st, st0, both_seeds=False), np.random.default_rng(0))
        d["far_reads"] = np.mean([float(r["far_reads"]) for r in rows if r["arm"] == arm and r["vbench_root"] == tag])
        out["arms"][arm] = d
    return out


def pure_rf_vbench():
    rows = read("pure_rf_vbench.csv")
    a, b = "SGF_RF_ST1L20_NM", "SGF_RF"
    rng, rng_split, d = np.random.default_rng(0), np.random.default_rng(1), {}
    for k in ("subject_consistency", "dynamic_degree"):  # order matters (shared rng)
        d[k] = [100 * v if i < 3 else v for i, v in
                enumerate(boot_choice(prompt_diffs(units(rows, k, arm=a), units(rows, k, arm=b)), rng))]
    for k in ("subject_consistency_inclip", "subject_consistency_clip2clip"):
        d[k] = [100 * v if i < 3 else v for i, v in
                enumerate(boot_choice(prompt_diffs(units(rows, k, arm=a), units(rows, k, arm=b)), rng_split))]
    sa, sb = motion_units(rows, a), motion_units(rows, b)
    d["static_means"] = (np.mean(list(sb.values())), np.mean(list(sa.values())))
    d["static"] = boot_integers(prompt_diffs(sa, sb, both_seeds=False), np.random.default_rng(0))
    return d


class Screen:
    """Per-arm vectors over the cells (prompt, seed) that have a sibling seed, plus the prompt bootstrap."""

    def __init__(self, name, arms):
        rows = defaultdict(dict)
        for r in read(name):
            rows[r["arm"]][(int(r["prompt"]), int(r["seed"]))] = r
        have = {a: set(rows[a]) for a in arms}
        assert all(have[a] == have[arms[0]] for a in arms), {a: len(have[a]) for a in arms}
        self.cells = [(p, s) for (p, s) in sorted(have[arms[0]]) if any(q == p and t != s for (q, t) in have[arms[0]])]
        prom = np.array([p for p, _ in self.cells])
        self.n, self.prompts = len(self.cells), np.unique(prom)
        self.M = {}
        for a in arms:
            col = lambda k: np.array([float(rows[a][c][k]) for c in self.cells])

            def late_early(k):
                x = np.array([[float(rows[a][c][f"{k}_{t}"]) for t in range(SEC)] for c in self.cells])
                return np.array([np.nanmean(x[i, 38:48]) / np.nanmean(x[i, 4:8]) for i in range(self.n)])
            m = np.array([np.log(float(rows[a][c]["motion_late_38_47"]) / float(rows[a][c]["motion_early_4_8"]))
                          for c in self.cells])
            sat, bri = late_early("sat"), late_early("bri")
            self.M[a] = dict(ident=col("dino_late_38_47"), early=col("dino_early_4_8"), m=m, sat=sat, bri=bri,
                             dsat=np.abs(sat - 1), dbri=np.abs(bri - 1), det=late_early("det"),
                             ms=float(np.median(col("dit_ms_per_block"))))
        rng = np.random.default_rng(0)
        self.boot = [np.concatenate([np.where(prom == p)[0] for p in rng.choice(self.prompts, len(self.prompts))])
                     for _ in range(B)]

    def ci(self, f):
        return np.percentile([f(b) for b in self.boot], [2.5, 97.5])

    def diff(self, a, b, key="ident", c=None, d=None):
        """Mean and CI of key(a) - key(b), minus key(c) - key(d) when c is given."""
        x = self.M[a][key] - self.M[b][key]
        if c is not None:
            x = x - (self.M[c][key] - self.M[d][key])
        lo, hi = self.ci(lambda i: x[i].mean())
        return x.mean(), lo, hi

    def ancova(self, a, b):
        """Identity difference at equal motion: intercept of dIdent ~ 1 + dlog motion."""
        dl, dm = self.M[a]["ident"] - self.M[b]["ident"], self.M[a]["m"] - self.M[b]["m"]
        f = lambda i: np.linalg.lstsq(np.stack([np.ones(len(i)), dm[i]], 1), dl[i], rcond=None)[0][0]
        lo, hi = self.ci(f)
        return f(np.arange(self.n)), lo, hi

    def summary(self, a):
        x = self.M[a]
        return dict(ret=x["ident"].mean() / x["early"].mean(), late=x["ident"].mean(), m_med=np.exp(np.median(x["m"])),
                    static=(np.exp(x["m"]) < STATIC).mean(), sat=x["sat"].mean(), bri=x["bri"].mean(), ms=x["ms"])


SINK_ARMS = ["SGF_RFW", "SGF_RFW_ST1L20_NM_B0", "SGF_RFW_ST1L20_NM", "SGF_RFW_NS", "SGF_RFW_NS_ST1L20_NM_B0",
             "SGF_RFW_NS_ST1L20_NM"]


def screens():
    bias = Screen("far_bias_sink_screen.csv", ["SGF_RFW", "SGF_RFW_ST1L20_NM", "SGF_RFW_ST1L20_NM_B2",
                                               "SGF_RFW_ST1L20_NM_B0"])
    pos = Screen("far_position_screen.csv", ["SGF_RFW", "SGF_RFW_ST4L20", "SGF_RFW_ST4L20_PA", "SGF_RFW_ST4L20_PB"])
    sink = Screen("far_bias_sink_screen.csv", SINK_ARMS)
    early = Screen("early_sink_screen.csv", ["SGF_N", "SGF_W", "SGF_NL", "SGF_WL"])
    return bias, pos, sink, early


def fmt(t, p=4):
    m, lo, hi = t[:3]
    return f"{m:+.{p}f}{star(lo, hi):1s} [{lo:+.{p}f}, {hi:+.{p}f}]"


def main():
    F, P = far_reads_vbench(), pure_rf_vbench()
    bias, pos, sink, early = screens()
    print("Table 1. Far reads in the last two denoising passes, SGF + Recency Forcing reading + commit rule (SGF_RFW).")
    print("VBench-Long, 200 prompts x 2 seeds, 48 s; difference to the arm without far reads (x100 except reduced motion).")
    print(f"{'arm':20s} {'far read':24s} {'subject':27s} {'subject c2c':27s} {'dynamic':27s} {'reduced motion':27s}")
    for arm, d in F["arms"].items():
        print(f"{arm:20s} {d['label']:24s} {fmt(d['subject_consistency'], 3):27s} "
              f"{fmt(d['subject_consistency_clip2clip'], 3):27s} {fmt(d['dynamic_degree'], 3):27s} "
              f"{fmt(d['static']):27s}")
    print(f"{'SGF_RF_ST1L20_NM':20s} {'stride 1, no commit rule':24s} {fmt(P['subject_consistency'], 3):27s} "
          f"{fmt(P['subject_consistency_clip2clip'], 3):27s} {fmt(P['dynamic_degree'], 3):27s} {fmt(P['static']):27s}")
    m = F["rfw_means"]
    print(f"SGF_RFW: subject {m['subject_consistency']:.3f}, subject c2c {m['subject_consistency_clip2clip']:.2f}, "
          f"dynamic {m['dynamic_degree']:.2f}, reduced motion {F['rfw_static']:.3f}. "
          "Last row: difference to SGF_RF (Recency Forcing reading alone).")

    print("\nTable 2. Screens on SGF_RFW, DINOv2 identity at 38-47.5 s (48 s videos, 20 prompts), "
          "difference to no far read.")
    print(f"{'arm':22s} {'far read':44s} {'identity':29s} {'reduced':>7s} {'brightness':>10s}")
    rows2 = [(bias, "SGF_RFW", "none (3 seeds)"),
             (bias, "SGF_RFW_ST1L20_NM", "stride 1, layers 20-29, far bias -4 (TRB)"),
             (bias, "SGF_RFW_ST1L20_NM_B2", "stride 1, layers 20-29, far bias -2"),
             (bias, "SGF_RFW_ST1L20_NM_B0", "stride 1, layers 20-29, far bias 0"),
             (pos, "SGF_RFW", "none (4 seeds)"),
             (pos, "SGF_RFW_ST4L20", "stride 4 +ln4, true positions -37..2"),
             (pos, "SGF_RFW_ST4L20_PA", "(a) on the sink positions 0-2"),
             (pos, "SGF_RFW_ST4L20_PB", "(b) on positions 3-5, oldest block dropped")]
    for S, arm, label in rows2:
        s = S.summary(arm)
        idt = "-" if arm == "SGF_RFW" else fmt(S.diff(arm, "SGF_RFW"))
        print(f"{arm:22s} {label:44s} {idt:29s} {s['static']:7.2f} {s['bri']:10.3f}")

    print("\nTable 3. The sink in the denoising passes, DINOv2 identity at 38-47.5 s (48 s videos, 20 prompts).")
    print(f"{'contrast':52s} {'identity':29s} {'identity, motion-adjusted':29s} {'log motion':29s} {'reduced motion':>15s}")
    for a, b, label in [("SGF_RFW_NS", "SGF_RFW", "sink left out of the denoising passes"),
                        ("SGF_RFW_ST1L20_NM_B0", "SGF_RFW", "far read (bias 0), with the sink"),
                        ("SGF_RFW_NS_ST1L20_NM_B0", "SGF_RFW_NS", "far read (bias 0), without the sink"),
                        ("SGF_RFW_NS_ST1L20_NM", "SGF_RFW_NS", "far read (TRB), without the sink"),
                        ("SGF_RFW_NS_ST1L20_NM_B0", "SGF_RFW", "sink left out + far read (bias 0)")]:
        st = f"{sink.summary(b)['static']:.2f} / {sink.summary(a)['static']:.2f}"
        print(f"{label:52s} {fmt(sink.diff(a, b)):29s} {fmt(sink.ancova(a, b)):29s} "
              f"{fmt(sink.diff(a, b, 'm')):29s} {st:>11s}")
    inter = sink.diff("SGF_RFW_NS_ST1L20_NM_B0", "SGF_RFW_NS", "ident", "SGF_RFW_ST1L20_NM_B0", "SGF_RFW")
    loss, back = sink.diff("SGF_RFW_NS", "SGF_RFW")[0], sink.diff("SGF_RFW_NS_ST1L20_NM_B0", "SGF_RFW_NS")[0]
    print(f"{'interaction: far read without - with the sink':52s} {fmt(inter):29s}")
    print(f"identity retention late / early: with the sink {sink.summary('SGF_RFW')['ret']:.3f}, without "
          f"{sink.summary('SGF_RFW_NS')['ret']:.3f}; share of the loss that far reads restore {back / -loss:.3f}")
    print("Released cache (sink 3 + newest 9 frames, 2 seeds): sink also left out of denoising steps 0-1")
    for a, b, label in [("SGF_WL", "SGF_W", "with the commit rule (SGF_WL - SGF_W)"),
                        ("SGF_NL", "SGF_N", "without the commit rule (SGF_NL - SGF_N)")]:
        print(f"{label:52s} {fmt(early.diff(a, b)):29s} reduced motion {early.summary(b)['static']:.2f} / "
              f"{early.summary(a)['static']:.2f}")


if __name__ == "__main__":
    main()
