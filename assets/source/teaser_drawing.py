"""Portable live-text vector primitives for the adopted Figure 1."""
from pathlib import Path
from html import escape
import base64
import subprocess
import xml.etree.ElementTree as ET
from paper_palette import INK, MUTED, RULE, BLUE, ACCENT, NONRECENT as SAGE, POSITIVE as GREEN, NEGATIVE as RED
ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "assets"
PRE = FIG
ASSET = ROOT / "assets/source/teaser_inputs"
FRAME = {"native": ASSET / "sgf_p000_s0_native_238s.png", "commit": ASSET / "sgf_p000_s0_commit_238s.png"}

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
            subprocess.run(["pdftoppm", "-singlefile", "-png", "-scale-to", "2200",
                            str(temporary_pdf), str(temporary_png.with_suffix(''))], check=True)
            temporary_svg.replace(final_svg)
            temporary_pdf.replace(final_pdf)
            temporary_png.replace(final_png)
        finally:
            for f in (temporary_svg, temporary_pdf, temporary_png):
                if f.exists():
                    f.unlink()


