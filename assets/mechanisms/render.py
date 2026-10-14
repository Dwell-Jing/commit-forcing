#!/usr/bin/env python3
"""Render assets/mechanisms/read_locus.{png,pdf,svg} from summary.json.

    python assets/mechanisms/render.py

Panels: (a) identity gain per (step, layer band) cell, (b) reduced-motion videos, (c) far-slot content control."""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "summary.json")))
BANDS = ["L0_9", "L10_19", "L20_29"]
BAND_LABEL = ["0–9", "10–19", "20–29"]
INK, MUTED, BLUE, ORANGE = "#1f2328", "#57606a", "#1f5aa6", "#c0672c"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})


def grid(key):
    C = S["read_locus"]["contrasts"]
    return [[C[f"MM_S{s}_{b}"][key] for b in BANDS] for s in range(4)], \
           [[C[f"MM_S{s}_{b}"]["lo"] > 0 or C[f"MM_S{s}_{b}"]["hi"] < 0 for b in BANDS] for s in range(4)]


def heatmap(ax, values, text, cmap, vmax, title, ylabel=True):
    ax.imshow(values, cmap=cmap, vmin=0, vmax=vmax, aspect="auto")
    for s in range(4):
        for b in range(3):
            v = values[s][b]
            ax.text(b, s, text(s, b), ha="center", va="center", fontsize=12,
                    color="white" if v > 0.6 * vmax else INK)
    ax.set_xticks(range(3), BAND_LABEL)
    ax.set_yticks(range(4), ["1", "2", "3", "4"])
    ax.set_xlabel("Layers")
    if ylabel:
        ax.set_ylabel("Denoising step  (early → late)")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK, pad=10)


fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.3), gridspec_kw=dict(width_ratios=[1, 1, 1.15], wspace=0.5))

gain, sig = grid("d")
heatmap(axes[0], gain, lambda s, b: f"{gain[s][b]:+.3f}" + ("*" if sig[s][b] else ""), "Blues", 0.05,
        "a   Identity gain from far history")
axes[0].add_patch(Rectangle((1.5, 2.5), 1, 1, fill=False, edgecolor=INK, linewidth=2.2))

static, _ = grid("static")
heatmap(axes[1], static, lambda s, b: f"{100 * static[s][b]:.0f}%", "Oranges", 1.0,
        "b   Videos with reduced motion", ylabel=False)
axes[1].set_xlabel(f"Layers   (no far history: {100 * S['read_locus']['static_reference']:.0f}%)")

ax = axes[2]
A = S["history_content"]["A"]["contrasts"]
rows = [("MM_S3_L20_29", "Old frames"), ("M4_A_MEAN", "Their mean"), ("M4_A_RECENT", "Recent frames"),
        ("M4_A_RAND", "Random")]
for i, (arm, label) in enumerate(rows):
    c = A[arm]
    significant = c["lo"] > 0 or c["hi"] < 0
    color = BLUE if i == 0 else MUTED
    ax.plot([c["lo"], c["hi"]], [i, i], color=color, linewidth=2.2, solid_capstyle="round")
    ax.plot(c["d"], i, "o", markersize=9, color=color, markerfacecolor=color if significant else "white",
            markeredgewidth=2)
ax.axvline(0, color=MUTED, linestyle="--", linewidth=1)
ax.set_yticks(range(len(rows)), [r[1] for r in rows])
ax.invert_yaxis()
ax.set_xlabel("Identity gain  (step 4, layers 20–29)")
ax.set_xlim(-0.04, 0.08)
ax.tick_params(length=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.set_title("c   What the far slots hold", loc="left", fontsize=13, fontweight="bold", color=INK, pad=10)

for ext in ("png", "pdf", "svg"):
    fig.savefig(os.path.join(HERE, f"read_locus.{ext}"), dpi=200, bbox_inches="tight", facecolor="white",
                metadata=None if ext != "pdf" else {"Creator": "assets/mechanisms/render.py"})
print("wrote read_locus.{png,pdf,svg}")
