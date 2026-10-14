#!/usr/bin/env python3
"""Commit Forcing opening example: a paired SGF rollout with fixed denoising policy.

Only the committing queries' direct sink access changes. Sink KV stays stored.
The authentic result frames are unchanged. The previous multi-panel teaser is retained in assets/archive.
"""
from pathlib import Path
from html import escape
import base64
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

    def icon(self, filename, x, y, scale):
        root = ET.parse(ASSET / filename).getroot()
        self.items.append(f'<g transform="translate({x},{y}) scale({scale})">')
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

    def export(self, stem):
        final_svg = FIG / f"{stem}.svg"
        final_pdf = FIG / f"{stem}.pdf"
        final_png = PRE / f"{stem}.png"
        temporary_svg = FIG / f".{stem}.render.svg"
        temporary_pdf = FIG / f".{stem}.render.pdf"
        temporary_png = PRE / f".{stem}.render.png"
        temporary_svg.write_text("\n".join(self.items + ["</g></svg>"]))
        try:
            subprocess.run(["rsvg-convert", "-f", "pdf", "-o",
                            str(temporary_pdf), str(temporary_svg)], check=True)
            subprocess.run(["rsvg-convert", "-w", str(self.width), "-o",
                            str(temporary_png), str(temporary_svg)], check=True)
            temporary_svg.replace(final_svg)
            temporary_pdf.replace(final_pdf)
            temporary_png.replace(final_png)
        finally:
            for f in (temporary_svg, temporary_pdf, temporary_png):
                if f.exists():
                    f.unlink()



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


def layout():
    d=Drawing(2200,825,"Same denoising access, different committing context")
    d.text(30,65,"Same denoising access, different commits",44,bold=True)

    # This shared box represents the fixed access policy across two rollouts.
    # It does not claim equal recurrent KV or equal denoised blocks later on.
    d.text(380,135,"Denoising",42,INK,"middle",True)
    d.rect(30,157,700,563,RULE,2,"none",6)
    history_w=290
    history_h=history_w*240/416
    for source,x,cx,color,label in (
        ("initial",40,185,SAGE,"Sink"),
        ("nearby",410,555,BLUE,"Recent"),
    ):
        d.text(cx,220,label,38,color,"middle",True)
        d.memory(source,x,255,history_w,history_h,None)
    d.path("M185 439 V478 H365",SAGE,4)
    d.path("M555 439 V478 H365",BLUE,4)
    _arrow(d,365,478,365,550,INK,4)
    d.icon("eye_read.svg",250,540,1.28)
    _arrow(d,480,627,742,627,INK,4)
    d.path("M742 301 V656",INK,4)
    _arrow(d,742,301,793,301,INK,4)
    _arrow(d,742,656,793,656,INK,4)

    # Each committing context now leads directly to its own real SGF result.
    d.text(1880,135,"Long rollout",42,INK,"middle",True)
    case_w,case_h=500,500*240/416
    context_w,context_h=250,250*240/416
    for key,label,y,okay in (
        ("native","Base committing",157,False),
        ("commit","Commit Forcing",512,True),
    ):
        frame_color=GREEN if okay else MUTED
        d.text(1185,y-22,label,42,GREEN if okay else INK,"middle",True)
        d.rect(805,y,760,case_h,frame_color,2.5,
               "#F7FAF8" if okay else "#F9FAFA",6)
        source_y=y+54
        d.memory("initial",835,source_y,context_w,context_h,None)
        d.memory("nearby",1140,source_y,context_w,context_h,None)
        if okay:
            # The pale sink is excluded from this call, not erased from KV.
            # Keep its pin and border visible to preserve the storage cue.
            d.items.append(f'<rect x="835" y="{source_y}" '
                           f'width="{context_w}" height="{context_h}" '
                           'fill="white" fill-opacity="0.80"/>')
        # Every source card uses the same corner and size for access status.
        # Base reads both sources; Commit Forcing excludes only direct sink.
        for source_x,visible in ((835,not okay),(1140,True)):
            d.status(source_x+context_w-32,source_y+32,visible,30)
        d.text(960,y+239,"Sink",38,SAGE,"middle")
        d.text(1265,y+239,"Recent",38,BLUE,"middle")
        d.icon("pen_write.svg",1435,y+67,.7)
        _arrow(d,1577,y+case_h/2,1618,y+case_h/2,frame_color,4)
        d.rect(1625,y-5,case_w+10,case_h+10,
               GREEN if okay else RED,4,"white",4)
        d.photo(key,1630,y,case_w,case_h)
        d.status(1666,y+36,okay,34)
    d.export("teaser")


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    PRE.mkdir(parents=True, exist_ok=True)
    layout()
    print("Created committing-only Figure 1 SVG, PDF and preview.")
