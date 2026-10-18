#!/usr/bin/env python3
"""Plot the frozen historical-recency intervention, without new inference.

The main axis contains only the tested target lags 1, 2, 4, 8, and 16 blocks on a
base-2 logarithmic axis. Sink is a separate category on a shared-y mini-axis;
it has no fixed numerical lag and is never connected to the finite-lag curves.
Points are unrounded per-video Subject_c2c means from the original loader.
No fit, confidence intervals, resampling, or statistical tests are added here.
"""

import hashlib
import csv
import json
from pathlib import Path

from paper_style import apply_style, export, ROOT, FIG, BLUE, GREEN, INK, RULE
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
import numpy as np


SCORES = ROOT / "assets/source/committing_content_age_scores.csv"
DATA = ROOT / "assets/source/committing_content_age_data.json"
AGES = (1, 2, 4, 8, 16)
SERIES = (("SGF", "AGE", GREEN, "o", "-", -.15),
          ("LongLive", "LLA", BLUE, "s", (0, (4, 2.5)), .15))
EXPECTED_ROUNDED = {
    "SGF": (90.61, 90.53, 90.30, 90.02, 89.92, 78.62),
    "LongLive": (85.50, 85.16, 84.35, 83.68, 83.03, 78.28),
}


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
    data, source_files = load_points()
    width, height = 170 / 25.4, 58 / 25.4
    fig = plt.figure(figsize=(width, height))
    layout = fig.add_gridspec(1, 2, width_ratios=(5.0, 1.0), wspace=.13,
                             left=.105, right=.985, bottom=.25, top=.82)
    age_axis = fig.add_subplot(layout[0, 0])
    sink_axis = fig.add_subplot(layout[0, 1], sharey=age_axis)
    for axis in (age_axis, sink_axis):
        axis.set_ylim(77.4, 92.0)
        axis.set_yticks((78, 82, 86, 90))
        axis.grid(axis="y", color=RULE, linewidth=.5, zorder=0)
        axis.tick_params(axis="both", labelsize=9.2, length=3, pad=4)
        axis.spines["bottom"].set_color(RULE)
        axis.spines["left"].set_color(RULE)
    age_axis.set_xscale("log", base=2)
    age_axis.set_xlim(2 ** -.18, 2 ** 4.18)
    age_axis.xaxis.set_major_locator(FixedLocator(AGES))
    age_axis.xaxis.set_major_formatter(ScalarFormatter())
    age_axis.xaxis.set_minor_locator(NullLocator())
    age_axis.set_xlabel(r"Target temporal lag $d$ (blocks)", fontsize=10, labelpad=6)
    age_axis.set_ylabel("Subject c2c (×100)", fontsize=10, labelpad=7)
    sink_axis.set_xlim(-.55, .55)
    sink_axis.set_xticks((0,), ("Sink",))
    sink_axis.tick_params(axis="y", left=False, labelleft=False)
    sink_axis.tick_params(axis="x", length=0, pad=7)
    sink_axis.spines["left"].set_visible(False)

    legend_handles = []
    for label, _, color, marker, linestyle, sink_offset in SERIES:
        record = data[label]
        age_axis.plot(AGES, record["finite_age_subject_c2c_x100"],
                      color=color, marker=marker, linestyle=linestyle,
                      linewidth=1.6, markersize=4.9, markeredgecolor="white",
                      markeredgewidth=.65, zorder=3)
        sink_axis.plot(sink_offset, record["sink_category_subject_c2c_x100"],
                       color=color, marker=marker, linestyle="none",
                       markersize=5.8, markeredgecolor="white", markeredgewidth=.65, zorder=3)
        legend_handles.append(Line2D([], [], color=color, marker=marker,
                                     linestyle=linestyle, linewidth=1.6, markersize=4.9,
                                     label=label))
    fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(.56, 1.025),
               ncol=2, fontsize=10, handlelength=2.2, columnspacing=2.0)
    # A separator denotes a distinct categorical panel, never an axis break.
    x_separator = (age_axis.get_position().x1 + sink_axis.get_position().x0) / 2
    fig.add_artist(Line2D((x_separator, x_separator), (.25, .82),
                          transform=fig.transFigure, color=RULE, linewidth=.7))
    # Preserve the full 170 mm print width with the shared tight exporter.
    padding = .045
    fig.add_artist(Rectangle((padding / width, .5), 1 - 2 * padding / width, .01,
                             transform=fig.transFigure, facecolor="none",
                             edgecolor="none", clip_on=False))
    export(fig, "committing_content_age")
    provenance = {
        "figure": "committing_content_age",
        "experiment": "rollf200 prompts 0--99, 60 s, generation seed 0",
        "metric": "mean per-video Subject_c2c × 100",
        "data": data,
        "x_encoding": {"finite_age": "log2, target lags 1/2/4/8/16 blocks; actual source lag increases during startup until the target is available",
                       "sink": "separate source category with no fixed numerical lag; horizontally dodged by model"},
        "y_encoding": {"shared_limits": [77.4, 92.0], "axis_break": False},
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
