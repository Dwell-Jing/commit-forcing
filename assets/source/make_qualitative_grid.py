#!/usr/bin/env python3
"""Render a paired 240-second case grid using only archived video frames.

The released 416 x 240 PNG cells preserve the decoded archived contact-sheet
pixels. Their source hashes and selection record accompany the frames. Neither frames nor evaluator
outputs are generated, retouched, or rescored. The figure's SVG retains live
text and twelve separate PNG images; PDF is exported from the same layout.

Run with a Python environment containing Pillow, numpy, and matplotlib.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "assets"
ASSET = FIG / "source/qualitative_grid_inputs"
PREVIEW = FIG
os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "commit-forcing-mpl"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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

CASES = (
    {
        "alias": "sgf", "pair": "SGF", "prompt_index": 19,
        "heading": "(a) SGF: church on the Amalfi Coast",
        "base_arm": "SGF_N", "commit_arm": "SGF_W",
        "configuration": "Native SGF denoising; committing reads the newest 9 trajectory frames, excluding the sink.",
        "visible_observation": "Base changes the church/coast composition across these samples; Commit Forcing retains a more similar church/coast layout.",
        "interpretation_limit": "The prompt requests a circling drone view. Composition stability alone does not establish motion quality or prompt adherence; initial rendered frames are visibly different.",
    },
    {
        "alias": "cf", "pair": "Context Forcing", "prompt_index": 10,
        "heading": "(b) CF (full rule): Zen garden in a glass sphere",
        "base_arm": "CF", "commit_arm": "CF_W",
        "configuration": "Native CF denoising; full committing rule excludes sink, slow memory, and stale frames, retaining fast FIFO/current context.",
        "visible_observation": "An external large hand is visible in Base at 120 s and multiple rake-like tools at 238 s; the Commit Forcing samples retain the small figure inside the sphere without that external hand.",
        "interpretation_limit": "The prompt requests the small figure raking sand inside the sphere; no external hand is requested. This readable visual contrast coincides with a negative per-video Quality change, not an overall metric improvement.",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return os.path.relpath(path, ROOT)


def render(frame_records: list[dict]) -> dict:
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 9.0, "text.color": INK,
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })
    width, height = 7.15, 5.70
    left, right, h_gap, v_gap = .66, .025, .035, .035
    frame_w = (width - left - right - 2 * h_gap) / 3
    frame_h = frame_w * CELL_H / CELL_W
    group_top = (.315, 3.14)
    fig = plt.figure(figsize=(width, height))
    by_key = {(r["case"], r["display_arm"], r["time_seconds"]): r for r in frame_records}
    positions = []

    def txt(x, y, text, **kwargs):
        fig.text(x / width, 1 - y / height, text, **kwargs)

    for case_index, case in enumerate(CASES):
        top = group_top[case_index]
        txt(.035, top - .245, case["heading"], fontsize=9.9, fontweight="bold", va="center")
        for col, sec in enumerate(TIMES):
            x = left + col * (frame_w + h_gap)
            txt(x + frame_w / 2, top - .075, f"{sec} s", fontsize=9.0,
                color=MUTED, ha="center", va="center")
        for row_index, (arm, label) in enumerate((("base", "Base"), ("commit", "+Commit\nForcing"))):
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
            destination = folder / f"qualitative_grid.{fmt}"
            temp = folder / f".qualitative_grid.render.{fmt}"
            temp_paths.append(temp)
            metadata = ({"Title": "Paired 240-second qualitative cases", "CreationDate": None,
                         "ModDate": None} if fmt == "pdf" else
                        {"Title": "Paired 240-second qualitative cases", "Date": None} if fmt == "svg" else None)
            fig.savefig(temp, format=fmt, dpi=300, metadata=metadata)
            temp.replace(destination)
    finally:
        plt.close(fig)
        for temp in temp_paths:
            temp.unlink(missing_ok=True)
    return {"figure_size_inches": [width, height], "frame_bounds": positions,
            "image_editability": "Twelve separately embedded raster frames; labels and frame borders are vector objects, SVG text is live.",
            "output_files": [rel(FIG / "qualitative_grid.pdf"), rel(FIG / "qualitative_grid.svg"),
                             rel(PREVIEW / "qualitative_grid.png")]}


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
    FIG.mkdir(exist_ok=True)
    render(frames)
    print("Created qualitative_grid.pdf/.svg/.png from twelve recorded frames")


if __name__ == "__main__":
    main()
