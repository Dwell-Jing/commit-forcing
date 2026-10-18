#!/usr/bin/env python3
"""Commit Forcing: generic historical-source/window selection and an SGF example.

The conceptual scheme preserves each generator's base denoising policy and
limits direct committing context to the current block and genuine recent KV.
Source categories and glyph counts are schematic, not shared physical caches.
The two authentic SGF output PNGs and their display geometry are unchanged.
"""
from pathlib import Path
from html import escape
import base64
import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "assets"
PRE = FIG
ASSET = FIG / "source/teaser_inputs"
INK, MUTED, RULE = "#202B33", "#67717A", "#D8DDE0"
SAGE, BLUE, ACCENT = "#607C68", "#527F9D", "#AD5036"
RED, GREEN = "#C93428", "#237C51"
FRAME = {"native": ASSET / "sgf_p000_s0_native_238s.png",
         "commit": ASSET / "sgf_p000_s0_commit_238s.png"}

class Drawing:
    def __init__(self, width, height, title):
        self.width, self.height = width, height
        self.items = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="178mm" '
            f'height="{178 * height / width:.6f}mm" viewBox="0 0 {width} {height}">',
            f"<title>{escape(title)}</title>",
            f'<rect width="{width}" height="{height}" fill="white"/>',
            f'<g font-family="Helvetica, Arial, sans-serif" fill="{INK}">',
        ]

    def text(self, x, y, label, size=40, color=INK, anchor="start", bold=False):
        self.items.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}">'
            f"{escape(label)}</text>"
        )

    def rect(self, x, y, w, h, color=RULE, width=2, fill="none", radius=0):
        self.items.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{width}"/>'
        )

    def path(self, d, color=INK, width=4):
        self.items.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )

    def photo(self, name, x, y, w, h):
        data = base64.b64encode(FRAME[name].read_bytes()).decode("ascii")
        self.items.append(
            f'<image x="{x}" y="{y}" width="{w}" height="{h}" '
            f'href="data:image/png;base64,{data}" preserveAspectRatio="xMidYMid meet"/>'
        )

    def status(self, x, y, okay, radius=42):
        color = GREEN if okay else RED
        self.items.append(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" '
            'stroke="white" stroke-width="5"/>'
        )
        if okay:
            self.path(
                f"M{x-radius*.47} {y} L{x-radius*.12} {y+radius*.31} "
                f"L{x+radius*.47} {y-radius*.36}", "white", radius*.15
            )
        else:
            d = radius * .36
            self.path(f"M{x-d} {y-d} L{x+d} {y+d} M{x+d} {y-d} L{x-d} {y+d}",
                      "white", radius * .15)

    def pin(self, x, y):
        # Gold cap + dark contour distinguishes the fixed-memory cue from
        # the red scene sign and the red/green phase-result badges.
        self.items.append(f'<g transform="translate({x},{y}) rotate(-20) scale(1.18)">')
        outline = (
            "M-24 -43 Q-29 -43 -29 -37 V-28 Q-29 -23 -23 -23 "
            "H-11 V1 L-30 19 H30 L11 1 V-23 H23 Q29 -23 29 -28 "
            "V-37 Q29 -43 24 -43 Z"
        )
        self.path("M0 19 L0 57", "white", 13)
        self.path("M0 19 L0 57", INK, 6)
        self.items.append(
            f'<path d="{outline}" fill="#E6B43B" stroke="white" '
            'stroke-width="10" stroke-linejoin="round"/>'
        )
        self.items.append(
            f'<path d="{outline}" fill="#E6B43B" stroke="{INK}" '
            'stroke-width="3.5" stroke-linejoin="round"/>'
        )
        self.path("M-18 -35 H18", "#FFE4A0", 3.5)
        self.items.append("</g>")

    def icon(self, filename, x, y, scale, mirror_x=False):
        root = ET.parse(ASSET / filename).getroot()
        if mirror_x:
            icon_width = float(root.attrib['viewBox'].split()[2])
            transform = f'translate({x+icon_width*scale},{y}) scale({-scale},{scale})'
        else:
            transform = f'translate({x},{y}) scale({scale})'
        self.items.append(f'<g data-icon="{filename}" data-mirror-x="{str(mirror_x).lower()}" transform="{transform}">')
        self.items.extend(ET.tostring(c, encoding="unicode") for c in root)
        self.items.append("</g>")

    def scene(self, name, x, y, w, h):
        """Editable original source-role scene, never an experimental frame."""
        filename = "scene_tokyo_sink.svg" if name == "initial" else "scene_tokyo_recent.svg"
        root = ET.parse(ASSET / filename).getroot()
        self.items.append(
            f'<svg x="{x}" y="{y}" width="{w}" height="{h}" '
            'viewBox="0 0 416 240" overflow="hidden">'
        )
        self.items.extend(ET.tostring(c, encoding="unicode") for c in root)
        self.items.append("</svg>")

    def memory(self, name, x, y, w, h, okay):
        color = SAGE if name == "initial" else BLUE
        if name == "nearby":
            self.rect(x + 18, y - 18, w, h, color, 3, "white", 3)
            self.rect(x + 9, y - 9, w, h, color, 3, "white", 3)
        self.rect(x - 5, y - 5, w + 10, h + 10, color, 4, "white", 4)
        self.scene(name, x, y, w, h)
        if name == "initial":
            self.pin(x + 44, y + 12)
        if okay is not None:
            self.status(x + w - 29, y + h - 29, okay, 47)

    def export(self, stem, figure_dir=None, preview_dir=None):
        fig_dir = figure_dir or FIG
        pre_dir = preview_dir or PRE
        fig_dir.mkdir(parents=True, exist_ok=True)
        pre_dir.mkdir(parents=True, exist_ok=True)
        final_svg = fig_dir / f"{stem}.svg"
        final_pdf = fig_dir / f"{stem}.pdf"
        final_png = pre_dir / f"{stem}.png"
        temporary_svg = fig_dir / f".{stem}.render.svg"
        temporary_pdf = fig_dir / f".{stem}.render.pdf"
        temporary_png = pre_dir / f".{stem}.render.png"
        temporary_svg.write_text("\n".join(self.items + ["</g></svg>"]))
        try:
            subprocess.run(["rsvg-convert", "-f", "pdf", "-o",
                            str(temporary_pdf), str(temporary_svg)], check=True)
            subprocess.run(["pdftoppm", "-singlefile", "-png", "-scale-to", str(self.width),
                            str(temporary_pdf), str(temporary_png.with_suffix(''))], check=True)
            temporary_svg.replace(final_svg)
            temporary_pdf.replace(final_pdf)
            temporary_png.replace(final_png)
        finally:
            for f in (temporary_svg, temporary_pdf, temporary_png):
                if f.exists():
                    f.unlink()

    def export_focus(self, stem, top):
        """Keep the current B/C preview synchronized with the native SVG."""
        svg=ET.parse(FIG/f"{stem}.svg")
        svg.getroot().set("viewBox",f"0 {top} {self.width} {self.height-top}")
        svg.getroot().set("width",str(self.width))
        svg.getroot().set("height",str(self.height-top))
        temporary_svg=PRE/f".{stem}_bc.render.svg"
        temporary_png=PRE/f".{stem}_bc.render.png"
        try:
            svg.write(temporary_svg,encoding="utf-8",xml_declaration=True)
            subprocess.run(["rsvg-convert","-w",str(self.width),"-o",
                            str(temporary_png),str(temporary_svg)],check=True)
            temporary_png.replace(PRE/f"{stem}_bc.png")
        finally:
            temporary_svg.unlink(missing_ok=True)
            temporary_png.unlink(missing_ok=True)


def _arrow(d, x1, y1, x2, y2, color=MUTED, width=4):
    d.path(f"M{x1} {y1} L{x2} {y2}", color, width)
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        d.items.append(
            f'<path d="M{x2} {y2} L{x2-13*direction} {y2-8} '
            f'L{x2-13*direction} {y2+8} Z" fill="{color}"/>'
        )
    else:
        direction = 1 if y2 >= y1 else -1
        d.items.append(
            f'<path d="M{x2} {y2} L{x2-8} {y2-13*direction} '
            f'L{x2+8} {y2-13*direction} Z" fill="{color}"/>'
        )


def _kv(d, x, y, w=76, h=96, color=BLUE, fill="#D7E6F0"):
    """Editable paired K/V glyph, not an experimental tensor visualization."""
    half = (w - 6) / 2
    for xx in (x, x + half + 6):
        d.rect(xx, y, half, h, color, 2.1, fill, 1)
        d.path(f"M{xx+half/2} {y} V{y+h}", color, 1)
        for frac in (1/3, 2/3):
            d.path(f"M{xx} {y+h*frac} H{xx+half}", color, 1)


def layout(draft=False, drawing_only=False):
    d = Drawing(2145, 825, "Historical-source and window selection during committing")
    purple = "#866E91"
    d.text(30, 65, "History for denoising and committing", 44, bold=True)
    d.text(1825, 65, "SGF example", 44, INK, "middle", True)
    d.path("M1515 105 V805", RULE, 2)

    # A generic source taxonomy. Availability and denoising access continue
    # to follow the base generator, rather than a new retrieval module.
    d.text(140, 172, "Sink", 42, SAGE, "middle", True)
    d.text(440, 151, "Nonrecent memory", 40, purple, "middle", True)
    d.text(440, 197, "/ replay", 39, purple, "middle")
    d.text(945, 172, "Recent trajectory", 42, BLUE, "middle", True)
    d.memory("initial", 50, 239, 180, 180*240/416, None)
    for off in (14, 7, 0):
        d.rect(340+off, 235-off, 200, 200*240/416,
               purple, 2.5, "white", 3)
    d.scene("initial", 345, 240, 190, 190*240/416)
    recent_x = [655 + 95*i for i in range(6)]
    for x in recent_x:
        _kv(d, x, 239)

    # All available historical classes can supply denoising under the base
    # policy. The lower blue bracket selects only a suffix for committing.
    d.path("M650 345 V362 H1230 V345", MUTED, 2.8)
    d.path("M140 352 V416 H650 V362", MUTED, 3.0)
    d.path("M440 363 V416", MUTED, 3.0)
    _arrow(d, 185, 416, 185, 545, MUTED, 3.2)
    d.path("M934 376 V398 H1230 V376", BLUE, 3.5)
    d.text(1082, 461, "w − c frames", 42, BLUE, "middle")
    d.path("M1230 398 H1280 V500 H1030 V545", BLUE, 3.5)
    _arrow(d, 1030, 520, 1030, 545, BLUE, 3.5)

    # The current clean block is distinct from historical KV and is always
    # an input to the committing forward. w counts it together with history.
    d.rect(50, 545, 270, 130, INK, 2.5, "#F5F7F8", 4)
    d.text(185, 601, "Denoising", 42, INK, "middle", True)
    d.text(185, 649, "Base policy", 39, MUTED, "middle")
    _arrow(d, 336, 610, 420, 610, INK, 3.5)
    d.rect(440, 527, 290, 290*240/416, INK, 3.0, "white", 4)
    d.scene("nearby", 445, 532, 280, 280*240/416)
    d.text(585, 748, "Current clean block", 40, INK, "middle", True)
    d.text(585, 793, "c frames", 39, MUTED, "middle")
    _arrow(d, 747, 610, 878, 610, INK, 3.5)
    d.rect(895, 545, 270, 130, ACCENT, 3.0, "#FCF5F0", 4)
    d.text(1030, 601, "Committing", 42, ACCENT, "middle", True)
    d.text(1030, 649, "w frames total", 39, ACCENT, "middle")
    _arrow(d, 1182, 610, 1277, 610, ACCENT, 3.5)
    _kv(d, 1295, 562, 90, 96, ACCENT, "#F0D4C7")
    d.text(1340, 716, "New KV", 40, ACCENT, "middle", True)

    # Preserve the existing two SGF frames, original PNG bytes, positions,
    # displayed dimensions, and result-status markers exactly.
    case_w, case_h = 500, 500*240/416
    for key, label, y, okay in (
        ("native", "Base SGF", 157, False),
        ("commit", "+ Commit Forcing", 512, True),
    ):
        d.text(1825, y-22, label, 42, INK, "middle", True)
        d.rect(1570, y-5, case_w+10, case_h+10,
               GREEN if okay else RED, 4, "white", 4)
        d.photo(key, 1575, y, case_w, case_h)
        d.status(1611, y+36, okay, 34)
    if drawing_only:
        return d
    stem = 'teaser_draft' if draft else 'teaser'
    output_dir = FIG/'drafts' if draft else FIG
    d.export(stem, output_dir, PRE/'redraw' if draft else PRE)
    manifest = {
        'status': 'Canonical generic source/window concept with unchanged SGF qualitative example' if not draft else 'Independent draft',
        'source': 'assets/source/make_teaser.py',
        'canvas': [d.width, d.height],
        'physical_size_mm': [178, 178*d.height/d.width],
        'typography': {'minimum_svg_units': 39,
                       'minimum_pt_at_162_96mm': 39*162.96/2145*72/25.4},
        'generic_scheme': {
            'sources': ['Sink', 'Nonrecent memory / replay', 'Recent trajectory'],
            'availability': 'Schematic source categories. Not every generator contains every source. This is not a new retrieval module.',
            'denoising': 'Base denoising policy unchanged. Historical-source arrows show availability under that policy, not mandatory access to all classes at every denoising step.',
            'selection': 'Direct committing context is current clean block plus genuine recent original-trajectory KV. Sink and other nonrecent sources are excluded from direct committing access.',
            'window': 'w includes current c latent frames. Blue bracket selects w-c historical frames. Six glyphs and the selected suffix are schematic, not universal budgets or physical cache capacity.',
            'construction': 'Current K/V is computed by the committing forward. New KV is not a copy of the selected history.',
            'indirect_history': 'Current latent and recent KV can retain older historical influence.',
            'illustrations': 'Editable source-role illustrations are not measured KV tensors or experimental frames.'
        },
        'layout': {'qualitative_frames': [[1575,157,case_w,case_h], [1575,512,case_w,case_h]],
                   'qualitative_borders': [[1570,152,case_w+10,case_h+10], [1570,507,case_w+10,case_h+10]],
                   'preserved_case_geometry': True},
        'illustrations': [{'asset': name, 'sha256': hashlib.sha256((ASSET/name).read_bytes()).hexdigest(),
                           'role': 'Original editable source-role illustration'}
                          for name in ['scene_tokyo_sink.svg', 'scene_tokyo_recent.svg']],
        'qualitative_outputs': [{'asset': FRAME[key].name, 'arm': arm, 'time_seconds': 238,
                                 'sha256': hashlib.sha256(FRAME[key].read_bytes()).hexdigest()}
                                for key,arm in [('native','SGF_N'), ('commit','SGF_W')]],
        'prompt_index': 0, 'generation_seed': 0,
        'sgf_instance': 'Base SGF committing uses 3 sink + 6 recent + 3 current frames. Commit Forcing uses 6 recent + 3 current, total w=9. Sink remains stored and the denoising policy is unchanged. SGF is not attributed slow memory or replay modules.',
        'display': 'Two original full-frame PNGs remain unchanged and are embedded byte-for-byte at the prior geometry. Normal vector-PDF export may resample image objects. No crop, retouching, or new case.',
        'rng': 'Shared prompt and initial-noise seed; no claim of identical intermediate stochastic streams.',
        'caption_handoff': 'Left: generic historical-source selection and a configurable recent window for committing, keeping base denoising. w includes current c, so selected history is w-c. Right: unchanged paired SGF example, p0 seed0 at238s. Generic source taxonomy does not imply all classes exist in SGF.'
    }
    suffix = '.json' if draft else '.provenance.json'
    (output_dir / f'{stem}{suffix}').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Render the current opening example.')
    parser.add_argument('--draft',action='store_true',help='Export independent review files only.')
    args = parser.parse_args()
    FIG.mkdir(parents=True, exist_ok=True)
    PRE.mkdir(parents=True, exist_ok=True)
    layout(draft=args.draft)
    print("Created source/window Figure 1 SVG, PDF, provenance and preview.")
