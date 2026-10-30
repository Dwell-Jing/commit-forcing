#!/usr/bin/env python3
"""Render the fixed-latent dependency map of committing as a recurrence (SGF, runs/chain).

Portable CSVs in assets/source/committing_recurrence_inputs/ hold the recorded means:
staircase_{O,N}.csv (rows lag 1..32, columns layer 0..29; mean (K+V)/2 relative
L2 of block b*+d's own KV after replacing the content of block b*), sink_curves.csv
(layer-mean difference of every later entry after replacing the sink block), and
impulse6_own.csv (one committing pass reads the sink; own-entry K/V differences
with prompt-bootstrap intervals). Exact zeros stay white in the maps.
"""

import csv
import os
import hashlib
import json
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(os.environ.get('TMPDIR', '/tmp')) / 'recent-context-mpl'))

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from paper_style import (apply_style, export, ROOT, INK, MUTED, RULE, BLUE,
                        PLOT_PRIMARY, PLOT_SECONDARY, PLOT_CONTROL)
import matplotlib.pyplot as plt

ASSETS = ROOT / "assets/source/committing_recurrence_inputs"
LAYERS = 30


def read_matrix(name):
    return np.loadtxt(ASSETS / name, delimiter=",", comments="#")


def read_columns(name):
    with (ASSETS / name).open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    return {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}


def heatmap(ax, values, vmin, vmax, cmap, bound):
    lags = values.shape[0]
    data = np.ma.masked_where(values.T <= 0, np.log10(np.where(values.T > 0, values.T, 1)))
    image = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax,
                      extent=(.5, lags + .5, -.5, LAYERS - .5), interpolation="nearest")
    d = np.arange(1, lags + 1)
    ax.step(d, np.minimum(bound(d), LAYERS) - .5, where="mid", color=PLOT_SECONDARY, linewidth=1.1)
    ax.set_xlim(.5, lags + .5)
    ax.set_ylim(-.5, LAYERS - .5)
    ax.set_xticks((1, 8, 16, 24, 32))
    ax.set_yticks((0, 10, 20, 29))
    ax.set_xlabel("Blocks after the changed block")
    ax.tick_params(length=2.5, pad=2)
    return image


def main():
    apply_style()
    ours, base = read_matrix("staircase_O.csv"), read_matrix("staircase_N.csv")
    sink = read_columns("sink_curves.csv")
    impulse = read_columns("impulse6_own.csv")
    positive = np.concatenate([ours[ours > 0], base[base > 0]])
    vmin, vmax = np.log10(positive.min()), np.log10(positive.max())
    cmap = LinearSegmentedColormap.from_list("chain", ["#EEF4F8", BLUE, INK])

    fig, axes = plt.subplots(2, 2, figsize=(6.9, 4.7))
    fig.subplots_adjust(left=.085, right=.9, bottom=.1, top=.94, wspace=.28, hspace=.55)
    image = heatmap(axes[0, 0], ours, vmin, vmax, cmap, lambda d: d)
    heatmap(axes[0, 1], base, vmin, vmax, cmap, lambda d: np.ceil(d / 2))
    axes[0, 0].set_ylabel("Layer")
    axes[0, 0].set_title("Commit Forcing", fontsize=10)
    axes[0, 1].set_title("Base", fontsize=10)
    cax = fig.add_axes([.915, .6, .014, .34])
    bar = fig.colorbar(image, cax=cax)
    bar.set_label("log$_{10}$ KV difference", fontsize=8.5)
    bar.ax.tick_params(labelsize=8, length=2)

    ax = axes[1, 0]
    block = sink["block"]
    keep = sink["O_mean"] > 0
    ax.plot(block, sink["N_mean"], color=PLOT_PRIMARY, linewidth=1.4, label="Base")
    ax.plot(block[keep], sink["O_mean"][keep], color=PLOT_SECONDARY, linewidth=1.4, label="Commit Forcing")
    ax.axvline(LAYERS, color=MUTED, linestyle=(0, (3, 2)), linewidth=.8)
    ax.set_yscale("log")
    ax.set_xlim(0, block.max() + 1)
    ax.set_xlabel("Block index")
    ax.set_ylabel("KV difference")
    ax.set_title("Changed sink block", fontsize=10)
    ax.legend(loc="lower right", fontsize=8.3, handlelength=1.8)
    ax.grid(axis="y", color=RULE, linewidth=.5, alpha=.7)

    ax = axes[1, 1]
    lag = impulse["lag"]
    for key, color, label in (("O", PLOT_SECONDARY, "Commit Forcing"), ("R9", PLOT_PRIMARY, "Two blocks")):
        mean, lo, hi = impulse[f"{key}_v"], impulse[f"{key}_v_low"], impulse[f"{key}_v_high"]
        keep = mean > 0
        ax.plot(lag[keep], mean[keep], color=color, linewidth=1.4, label=label)
        ax.fill_between(lag[keep], lo[keep], hi[keep], color=color, alpha=.18, linewidth=0)
    ax.axvline(LAYERS - 1, color=MUTED, linestyle=(0, (3, 2)), linewidth=.8)
    ax.set_yscale("log")
    ax.set_xlim(.5, lag.max() + .5)
    ax.set_xlabel("Blocks after intervention")
    ax.set_ylabel("V difference")
    ax.set_title("One committing pass reads the sink", fontsize=10)
    ax.legend(loc="lower left", fontsize=8.3, handlelength=1.8)
    ax.grid(axis="y", color=RULE, linewidth=.5, alpha=.7)
    for ax in axes.flat:
        ax.spines["left"].set_color(MUTED)
        ax.spines["bottom"].set_color(MUTED)
    export(fig, "committing_recurrence")
    from paper_style import FIG
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    record = {
        "artifact": "committing_recurrence",
        "source": "assets/source/make_committing_recurrence.py",
        "source_sha256": sha(Path(__file__).resolve()),
        "inputs": [{"path": path.relative_to(ROOT).as_posix(), "sha256":sha(path)}
                   for path in sorted(ASSETS.glob("*.csv"))],
        "input_scope": "Reported aggregate matrices and curves only; no latent, KV tensor, video or per-prompt records.",
        "layers": LAYERS,
        "matrix_shape": [32, 30],
        "display": "Top panels show log10 of positive aggregate own-entry K/V relative L2; exact zeros are masked white. Lower panels use the reported layer-mean sink response and own-entry V impulse means and intervals.",
        "new_statistics_computed": False,
        "exports": {extension:sha(FIG / ("committing_recurrence."+extension)) for extension in ("pdf","svg")},
    }
    (FIG / "committing_recurrence.provenance.json").write_text(json.dumps(record,indent=2)+"\n")


if __name__ == "__main__":
    main()
