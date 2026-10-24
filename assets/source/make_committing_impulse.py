"""Render recorded fixed-latent committing propagation, without resampling.

The portable CSV contains the existing FLI means and prompt-bootstrap
intervals for cache lags 1--11. The intervention changes one committing
call; the directly affected entries leave the cache after 3 subsequent
commits. No generated-probe measurements are plotted here. The cache
boundary is explained in the manuscript, without an in-plot annotation.
"""

import argparse
import csv
import hashlib
import json
import subprocess

import numpy as np
from paper_style import (apply_style, export, ROOT, FIG, INK, MUTED, RULE,
                        PLOT_PRIMARY, PLOT_SECONDARY, PLOT_CONTROL)
import matplotlib.pyplot as plt


DATA = ROOT / "assets/source/kv_propagation.csv"


def export_draft(fig, values):
    """Independent review exports; leave canonical and the manuscript alone."""
    folder = FIG / "drafts"
    preview = folder
    stem = "committing_impulse_draft"
    folder.mkdir(parents=True, exist_ok=True)
    preview.mkdir(parents=True, exist_ok=True)
    for fmt in ("pdf", "svg"):
        metadata = ({"Title": "KV propagation after a single committing intervention",
                     "CreationDate": None, "ModDate": None} if fmt == "pdf" else
                    {"Title": "KV propagation after a single committing intervention", "Date": None})
        fig.savefig(folder / f"{stem}.{fmt}", format=fmt, dpi=280,
                    bbox_inches="tight", pad_inches=.045, metadata=metadata)
    plt.close(fig)
    subprocess.run(["pdftoppm", "-singlefile", "-png", "-scale-to", "1600",
                    str(folder / f"{stem}.pdf"), str(preview / stem)], check=True)
    write_provenance(folder, stem, values)
    print(f"Created independent {stem}: PDF, SVG, actual-PDF PNG, provenance")


def write_provenance(folder, stem, values):
    manifest = {
        "artifact": stem,
        "status": "Current shared-palette rendering with shortened axis labels",
        "source": "assets/source/make_committing_impulse.py",
        "data": {"path": "assets/source/kv_propagation.csv", "sha256": hashlib.sha256(DATA.read_bytes()).hexdigest()},
        "values": {key: value.tolist() for key, value in values.items()},
        "axis_labels": {"x": "Blocks after intervention", "y": "KV difference"},
        "palette": {"source": "assets/source/paper_palette.py", "K": PLOT_PRIMARY,
                    "V": PLOT_SECONDARY, "Self-only": PLOT_CONTROL},
        "legend": ["K", "V", "Self-only"],
        "removed": ["In-plot cache-removal text", "Vertical cache-removal line", "Pre-removal gray shading"],
        "preserved": ["All original K/V means and 95% intervals", "Self-only zero negative control",
                      "Axis limits/ticks", "All three series and their markers"],
        "scope": "Relative L2 differences in later-block KV under paired fixed clean inputs; not a video-quality or visible-drift score",
        "interpretation": "Recent-context reconstruction transmits differences that decay. Self-only reads no earlier blocks and transmits no later-KV difference under this controlled protocol. The plot does not rank generation quality.",
        "caption_handoff": "K and V are relative L2 differences in subsequent-block KV under recent-context committing with clean latents fixed. Keep the lag3 original-entry removal and 95% prompt-bootstrap intervals in the caption. Self-only K and V are zero; all means and intervals remain unchanged.",
        "exports": {extension: hashlib.sha256((folder / f'{stem}.{extension}').read_bytes()).hexdigest()
                    for extension in ('pdf', 'svg')},
    }
    (folder / f"{stem}.provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")


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


def main(draft=False):
    apply_style()
    values = read_records()
    fig, ax = plt.subplots(figsize=(5.35, 2.12))
    fig.subplots_adjust(left=.137, right=.98, bottom=.265, top=.80)
    x = values["lag"]
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=RULE, linewidth=.5, alpha=.7)

    handles = []
    for kind, color, marker, style in (("k", PLOT_PRIMARY, "o", "-"),
                                       ("v", PLOT_SECONDARY, "s", (0, (4, 2.5)))):
        mean = values[f"recent_{kind}"]
        lo, hi = values[f"recent_{kind}_low"], values[f"recent_{kind}_high"]
        handle = ax.errorbar(x, mean, yerr=np.vstack((mean - lo, hi - mean)),
                    color=color, marker=marker, linestyle=style, markersize=3.8,
                    markeredgecolor="white", markeredgewidth=.45,
                    linewidth=1.5, elinewidth=.8, capsize=1.6,
                    label=kind.upper(), zorder=3)
        handles.append(handle)
    handle, = ax.plot(x, values["self_only_k"], color=PLOT_CONTROL,
            linestyle=(0, (4, 1.5, 1, 1.5)), linewidth=1.25,
            label="Self-only", zorder=4)
    handles.append(handle)
    ax.set_xlim(.7, 11.25)
    ax.set_ylim(-.013, .221)
    ax.set_xticks((1, 3, 5, 7, 9, 11))
    ax.set_yticks((0, .05, .10, .15, .20))
    ax.set_yticklabels(("0", "0.05", "0.10", "0.15", "0.20"))
    ax.set_xlabel("Blocks after intervention", fontsize=9.2, labelpad=5)
    ax.set_ylabel("KV difference", fontsize=9.2, labelpad=6)
    ax.tick_params(labelsize=8.8, length=3, pad=3)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    fig.legend(handles=handles, loc="upper center",
               bbox_to_anchor=(.60, 1.015), ncol=3, fontsize=8.8,
               handlelength=2.0, columnspacing=1.6, handletextpad=.5)
    if draft:
        export_draft(fig, values)
    else:
        export(fig, "committing_impulse")
        write_provenance(FIG, "committing_impulse", values)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", action="store_true", help="Export an independent review draft")
    main(draft=parser.parse_args().draft)
