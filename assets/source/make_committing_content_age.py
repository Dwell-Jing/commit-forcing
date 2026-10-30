#!/usr/bin/env python3
"""Plot the frozen historical-recency intervention, without new inference.

The main axis contains only the tested target lags 1, 2, 4, 8, and 16 blocks on a
base-2 logarithmic axis. Sink remains a separate source control in the
manuscript text and appendix tables; it is not plotted on the recency axis.
Points are unrounded per-video Subject_c2c means from the original loader.
No fit, confidence intervals, resampling, or statistical tests are added here.
"""

import hashlib
import csv
import json
from pathlib import Path

from paper_style import (apply_style, export, ROOT, FIG, INK, RULE,
                        PLOT_PRIMARY, PLOT_SECONDARY)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
import numpy as np


SCORES = ROOT / "assets/source/committing_content_age_scores.csv"
DATA = ROOT / "assets/source/committing_content_age_data.json"
AGES = (1, 2, 4, 8, 16)
SERIES = (("SGF", "AGE", PLOT_PRIMARY, "o", "-"), ("LongLive", "LLA", PLOT_SECONDARY, "s", (0, (4, 2.5))))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_points():
    """Verify every plotted mean against the released per-video scores."""
    recorded = json.loads(DATA.read_text())
    rows = list(csv.DictReader(SCORES.open(newline="")))
    if len(rows) != 1200:
        raise ValueError("Expected 12 arms and 100 prompts per arm")
    for label, record in recorded.items():
        means = []
        for arm in record["arms"]:
            values = [r for r in rows if r["model"] == label and r["arm"] == arm]
            prompts = [int(r["prompt_index"]) for r in values]
            if len(prompts) != 100 or set(prompts) != set(range(100)):
                raise ValueError(f"Duplicate or missing prompt in {arm}")
            means.append(100.0 * float(np.mean([float(r["subject_c2c"]) for r in values])))
        expected = record["finite_age_subject_c2c_x100"] + [record["sink_category_subject_c2c_x100"]]
        if not np.allclose(means, expected, atol=1e-12, rtol=0):
            raise ValueError(f"Recorded mean mismatch in {label}")
    return recorded, {SCORES, DATA}


def main():
    apply_style()
    plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial',
                         'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold'})
    data, source_files = load_points()
    width, height = 86 / 25.4, 46 / 25.4
    fig = plt.figure(figsize=(width, height))
    age_axis = fig.add_axes((.215, .30, .77, .48))
    age_axis.set_ylim(82.0, 92.0)
    age_axis.set_yticks((82, 84, 86, 88, 90, 92))
    age_axis.grid(axis="y", color=RULE, linewidth=.5, zorder=0)
    age_axis.tick_params(axis="both", labelsize=9.2, length=3, pad=4)
    age_axis.spines["bottom"].set_color(RULE)
    age_axis.spines["left"].set_color(RULE)
    age_axis.set_xscale("log", base=2)
    age_axis.set_xlim(2 ** -.18, 2 ** 4.18)
    age_axis.xaxis.set_major_locator(FixedLocator(AGES))
    age_axis.xaxis.set_major_formatter(ScalarFormatter())
    age_axis.xaxis.set_minor_locator(NullLocator())
    age_axis.set_xlabel(r"Lag $d$ (blocks)", fontsize=10, labelpad=6)
    age_axis.set_ylabel(r"Subject$_{\mathrm{c2c}}$", fontsize=10, labelpad=7)
    legend_handles = []
    for label, _, color, marker, linestyle in SERIES:
        record = data[label]
        age_axis.plot(AGES, record["finite_age_subject_c2c_x100"],
                      color=color, marker=marker, linestyle=linestyle,
                      linewidth=1.6, markersize=4.9, markeredgecolor="white",
                      markeredgewidth=.65, zorder=3)
        legend_handles.append(Line2D([], [], color=color, marker=marker,
                                     linestyle=linestyle, linewidth=1.6, markersize=4.9,
                                     label=label))
    fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(.60, 1.025),
               ncol=2, fontsize=10, handlelength=2.2, columnspacing=2.0)
    # Preserve the compact 86 mm print width with the shared tight exporter.
    padding = .045
    fig.add_artist(Rectangle((padding / width, .5), 1 - 2 * padding / width, .01,
                             transform=fig.transFigure, facecolor="none",
                             edgecolor="none", clip_on=False))
    export(fig, "committing_content_age")
    provenance = {
        "figure": "committing_content_age",
        "experiment": "rollf200 prompts 0--99, 60 s, generation seed 0",
        "metric": "mean per-video Subject_c2c × 100",
        "axis_labels": {"x": "Lag d (blocks)", "y": r"Subject$_{\mathrm{c2c}}$",
                        "caption_definition": "Official clip-to-clip Subject Consistency on a 0–100 scale; target lag along the original trajectory"},
        "palette": {"SGF": PLOT_PRIMARY, "LongLive": PLOT_SECONDARY,
                    "source": "assets/source/paper_palette.py"},
        "data": data,
        "x_encoding": {"finite_age": "log2, target lags 1/2/4/8/16 blocks; actual source lag increases during startup until the target is available",
                       "sink": "not plotted; separate source category retained in manuscript text and Appendix A.8, without a numerical lag"},
        "y_encoding": {"shared_limits": [82.0, 92.0], "axis_break": False,
                       "scope": "Same linear scale for both generators; contains all ten plotted finite-lag means"},
        "display": {"panels": 1, "plotted_means": 10,
                    "sink_controls": "Both original sink means remain audited in data and unchanged in appendix tables; removed from this recency-only plot"},
        "statistics": "points only; original means, no new inference or confidence intervals",
        "sources": [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                    for path in sorted(source_files)],
        "script_sha256": sha256(Path(__file__).resolve()),
        "exports": {extension: sha256(FIG / f"committing_content_age.{extension}")
                    for extension in ("pdf", "svg")},
    }
    output = FIG / "committing_content_age.provenance.json"
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(provenance, indent=2) + "\n")
    temporary.replace(output)
    for label, record in data.items():
        print(label, json.dumps(record))


if __name__ == "__main__":
    main()
