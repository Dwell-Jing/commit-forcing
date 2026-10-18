"""Render recorded fixed-latent committing propagation, without resampling.

The portable CSV contains the existing FLI means and prompt-bootstrap
intervals for cache lags 1--11. The intervention changes one committing
call; the directly affected entries leave the cache after 3 subsequent
commits. No generated-probe measurements are plotted here. The cache
boundary is explained in the manuscript, without an in-plot annotation.
"""

import csv

import numpy as np
from paper_style import apply_style, export, ROOT, GREEN, BLUE, INK, MUTED, RULE
import matplotlib.pyplot as plt


DATA = ROOT / "assets/source/kv_propagation.csv"


def read_records():
    with DATA.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    columns = {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}
    if not np.array_equal(columns["lag"], np.arange(1, 12)):
        raise ValueError("Expected recorded cache lags 1--11, without lag 0")
    for kind in ("k", "v"):
        if np.any(columns[f"self_only_{kind}"] != 0):
            raise ValueError("The recorded fixed-content self-only control is zero")
        mean = columns[f"recent_{kind}"]
        if not np.all((columns[f"recent_{kind}_low"] <= mean)
                      & (mean <= columns[f"recent_{kind}_high"])):
            raise ValueError("Invalid recorded interval")
    return columns


def main():
    apply_style()
    values = read_records()
    fig, ax = plt.subplots(figsize=(5.35, 2.12))
    fig.subplots_adjust(left=.137, right=.98, bottom=.265, top=.80)
    x = values["lag"]
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=RULE, linewidth=.5, alpha=.7)

    handles = []
    for kind, color, marker in (("k", GREEN, "o"), ("v", BLUE, "s")):
        mean = values[f"recent_{kind}"]
        lo, hi = values[f"recent_{kind}_low"], values[f"recent_{kind}_high"]
        handle = ax.errorbar(x, mean, yerr=np.vstack((mean - lo, hi - mean)),
                    color=color, marker=marker, markersize=3.8,
                    markeredgecolor="white", markeredgewidth=.45,
                    linewidth=1.5, elinewidth=.8, capsize=1.6,
                    label=f"Recent: {kind.upper()}", zorder=3)
        handles.append(handle)
    handle, = ax.plot(x, values["self_only_k"], color=MUTED,
            linestyle=(0, (4, 2)), linewidth=1.25,
            label="Self-only: K/V", zorder=4)
    handles.append(handle)
    ax.set_xlim(.7, 11.25)
    ax.set_ylim(-.013, .221)
    ax.set_xticks((1, 3, 5, 7, 9, 11))
    ax.set_yticks((0, .05, .10, .15, .20))
    ax.set_yticklabels(("0", "0.05", "0.10", "0.15", "0.20"))
    ax.set_xlabel("Blocks after committing intervention", fontsize=9.2, labelpad=5)
    ax.set_ylabel("Subsequent KV difference\n(relative L2)", fontsize=9.2, labelpad=6)
    ax.tick_params(labelsize=8.8, length=3, pad=3)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    fig.legend(handles=handles, loc="upper center",
               bbox_to_anchor=(.60, 1.015), ncol=3, fontsize=8.8,
               handlelength=2.0, columnspacing=1.6, handletextpad=.5)
    export(fig, "committing_impulse")


if __name__ == "__main__":
    main()
