#!/usr/bin/env python3
"""Render a paired 240-second case grid using only archived video frames.

The released PNG inputs are the unchanged 416 x 240 cells decoded from
archived contact sheets. The recorded hashes and source selection accompany
the inputs; no private contact sheets are required to rerender this layout. Neither frames nor evaluator
outputs are generated, retouched, or rescored. The figure's SVG retains live
text and twelve separate PNG images; PDF is exported from the same layout.

Run with a Python environment containing Pillow, numpy, and matplotlib.
"""

from __future__ import annotations

import csv
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIG = Path(os.environ.get("FIGURE_OUTPUT_DIR", ROOT / "assets"))
ASSET = ROOT / "assets/source/qualitative_grid_inputs"
PREVIEW = FIG
STEM = "qualitative_grid"
os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "recent-context-mpl"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import numpy as np
from PIL import Image

TIMES = (0, 120, 238)
SOURCE_TIMES = (0, 60, 120, 180, 238)
CELL_W, CELL_H = 416, 240
SHEET_MARGIN, SHEET_TOP = 90, 28
SHEET_SIZE = (2170, 508)
INK = "#202B33"
MUTED = "#67717A"
RULE = "#C6CDD1"
CALLOUT_YELLOW = "#FFD23F"
# Source-pixel coordinates: center x/y and radius x/y. These are transparent
# vector guides, not quantitative regions or edits to the archived frames.
CALLOUTS = {
    ("sgf", "base", 238): (313, 120, 82, 91),
    ("sgf", "commit", 238): (277, 122, 87, 102),
    ("cf", "base", 120): (357, 55, 48, 42),
    ("cf", "commit", 120): (357, 55, 48, 42),
}

CASES = (
    {
        "alias": "sgf", "pair": "SGF", "prompt_index": 19,
        "heading": "SGF",
        "base_arm": "SGF_N", "commit_arm": "SGF_W6",
        "configuration": "Native SGF denoising; committing reads the current 3 and immediately preceding 3 latent frames, excluding direct sink access.",
        "visible_observation": "Base changes the church/coast composition across these samples; Commit Forcing retains a more similar church/coast layout.",
        "interpretation_limit": "The prompt requests a circling drone view. Composition stability alone does not establish motion quality or prompt adherence; initial rendered frames are visibly different.",
    },
    {
        "alias": "cf", "pair": "Context Forcing", "prompt_index": 10,
        "heading": "CF",
        "base_arm": "CF", "commit_arm": "CF_W",
        "configuration": "Native CF denoising; committing reads the current 3 and immediately preceding 3 latent frames, excluding direct sink and earlier-memory access.",
        "visible_observation": "An external large hand is visible in Base at 120 s and multiple rake-like tools at 238 s; the Commit Forcing samples retain the small figure inside the sphere without that external hand.",
        "interpretation_limit": "The prompt requests the small figure raking sand inside the sphere; no external hand is requested. This readable visual contrast coincides with a negative per-video Quality change, not an overall metric improvement.",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return os.path.relpath(path, ROOT)


def write_json_atomic(path: Path, data: dict) -> None:
    temp = path.with_name("." + path.name + ".tmp")
    try:
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def render(frame_records: list[dict]) -> dict:
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 9.0, "text.color": INK,
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })
    width, height = 7.15, 5.28
    left, right, h_gap, v_gap = .91, .025, .035, .035
    frame_w = (width - left - right - 2 * h_gap) / 3
    frame_h = frame_w * CELL_H / CELL_W
    group_top = (.16, 2.82)
    fig = plt.figure(figsize=(width, height))
    by_key = {(r["case"], r["display_arm"], r["time_seconds"]): r for r in frame_records}
    positions = []

    def txt(x, y, text, **kwargs):
        fig.text(x / width, 1 - y / height, text, **kwargs)

    for case_index, case in enumerate(CASES):
        top = group_top[case_index]
        txt(.115, top + frame_h + v_gap / 2, case["heading"], fontsize=9.9,
            rotation=90, rotation_mode="anchor", ha="center", va="center")
        for col, sec in enumerate(TIMES):
            x = left + col * (frame_w + h_gap)
            txt(x + frame_w / 2, top - .075, f"{sec} s", fontsize=9.0,
                color=MUTED, ha="center", va="center")
        commit_label = "Commit\nForcing"
        for row_index, (arm, label) in enumerate((("base", "Base"), ("commit", commit_label))):
            y = top + row_index * (frame_h + v_gap)
            txt(left - .065, y + frame_h / 2, label, fontsize=9.0,
                ha="right", va="center", linespacing=1.20)
            for col, sec in enumerate(TIMES):
                x = left + col * (frame_w + h_gap)
                frame = by_key[(case["alias"], arm, sec)]
                axes = fig.add_axes((x / width, 1 - (y + frame_h) / height,
                                     frame_w / width, frame_h / height))
                with Image.open(ROOT / frame["asset"]) as im:
                    axes.imshow(np.asarray(im), interpolation="none", aspect="equal")
                callout = CALLOUTS.get((case["alias"], arm, sec))
                if callout is not None:
                    cx, cy, rx, ry = callout
                    for color, line_width in ((INK, 2.6), (CALLOUT_YELLOW, 1.65)):
                        axes.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry,
                                              fill=False, edgecolor=color,
                                              linewidth=line_width, zorder=5))
                axes.set_axis_off()
                # The stroke is outside the image; it does not alter frame pixels.
                fig.add_artist(Rectangle((x / width, 1 - (y + frame_h) / height),
                                         frame_w / width, frame_h / height,
                                         transform=fig.transFigure, fill=False,
                                         linewidth=.35, edgecolor=RULE))
                positions.append({"asset": frame["asset"], "bounds_inches": [x, y, frame_w, frame_h]})

    temp_paths = []
    try:
        for fmt, folder in (("pdf", FIG), ("svg", FIG), ("png", PREVIEW)):
            destination = folder / f"{STEM}.{fmt}"
            temp = folder / f".{STEM}.render.{fmt}"
            temp_paths.append(temp)
            metadata = ({"Title": "Commit Forcing: paired 240-second qualitative cases", "CreationDate": None,
                         "ModDate": None} if fmt == "pdf" else
                        {"Title": "Commit Forcing: paired 240-second qualitative cases", "Date": None} if fmt == "svg" else None)
            fig.savefig(temp, format=fmt, dpi=300, metadata=metadata)
            temp.replace(destination)
    finally:
        plt.close(fig)
        for temp in temp_paths:
            temp.unlink(missing_ok=True)
    return {"method_name": "Commit Forcing", "visible_method_label": "Commit Forcing",
            "visible_commit_row_labels": {"sgf": "Commit Forcing (6 frames)", "cf": "Commit Forcing (6 frames)"},
            "case_role": {"sgf": "Adopted current-plus-previous six-frame method, actual SGF_W6 output", "cf": "Adopted current-plus-previous committing"},
            "model_label_placement": "Left outer column, vertical, centered across each pair of rows",
            "figure_size_inches": [width, height], "frame_bounds": positions,
            "callouts": [{"case": case, "arm": arm, "time_seconds": sec,
                          "source_ellipse_cx_cy_rx_ry": list(ellipse)}
                         for (case, arm, sec), ellipse in CALLOUTS.items()],
            "callout_style": {"fill": "none", "color": CALLOUT_YELLOW,
                              "line_width_pt": 1.65, "halo_color": INK,
                              "halo_width_pt": 2.6,
                              "meaning": "Church structure at 238 s on SGF and the matched external-hand region at 120 s on CF; visual guides only, not a measured ROI."},
            "image_editability": "Twelve separately embedded raster frames; labels, frame borders, and transparent callouts are vector objects, SVG text is live.",
            "output_files": [f"assets/{STEM}.{ext}" for ext in ("pdf", "svg", "png")]}


def main() -> None:
    record = json.loads((ASSET / "source.json").read_text())
    frames = record["frames"]
    if len(frames) != 12:
        raise ValueError("Expected twelve recorded frames")
    for frame in frames:
        path = ROOT / frame["asset"]
        if sha256(path) != frame["asset_sha256"]:
            raise ValueError(f"Frame hash mismatch: {path.name}")
        with Image.open(path) as im:
            if im.size != (CELL_W, CELL_H):
                raise ValueError(f"Frame geometry mismatch: {path.name}")
    FIG.mkdir(parents=True, exist_ok=True)
    rendering = render(frames)
    subprocess.run(["pdftoppm", "-singlefile", "-png", "-scale-to", "2200", str(FIG / "qualitative_grid.pdf"), str(FIG / "qualitative_grid")], check=True)
    record["rendering"] = rendering
    record["label_edit"] = "Both SGF and CF use current plus previous (6 frames). Four transparent yellow circles with dark outlines highlight paired comparison regions."
    record["source"] = "assets/source/make_qualitative_grid.py"
    write_json_atomic(FIG / "qualitative_grid.provenance.json", record)
    print("Created qualitative_grid.pdf/.svg/.png from twelve recorded frames")

if __name__ == "__main__":
    main()
