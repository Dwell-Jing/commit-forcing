#!/usr/bin/env python3
"""SGF committing controls as two equal-size read-set schematics.

One card = one latent frame's K/V, not one token or one denoising forward.
Filled cards are directly attended during committing. Unselected historical
entries remain stored; sink access during base denoising is retained.
The sets represent the full-cache steady state, with original RoPE positions.
No outcome estimates, confidence intervals, axes, or success/failure symbols
are drawn. Results remain in the manuscript and its tables. Reported data
stay in the provenance for traceability, not as visible schematic content.
Rebuild the public SVG, vector PDF and PNG from the protocol and source records.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'analysis/sgf_committing_controls'
REPORT = EVIDENCE / 'data/READOUT.md'
PREREG = EVIDENCE / 'data/PREREG.md'
STAT_SOURCE = EVIDENCE / 'source/sgfcw_readout.py'
FIG = ROOT / 'assets'
PRE = FIG
STEM = 'sgf_committing_controls'
W, H = 1800, 470
WIDTH_MM = 168
INK, MUTED, RULE = '#202B33', '#67717A', '#D8DDE0'
SINK, SINK_LIGHT = '#607C68', '#DCE8DF'
RECENT, RECENT_LIGHT = '#557F9C', '#D7E6F0'
CURRENT, CURRENT_LIGHT = '#AD5036', '#F0D4C7'


def read_contrast(name):
    line = next(v for v in REPORT.read_text().splitlines()
                if v.startswith(f'| {name} | pooled |'))
    cells = [c.strip() for c in line.strip('|').split('|')]
    metrics = ['Subject c2c', 'Quality', 'Dynamic', 'Smoothness', 'Flickering',
               'Background c2c', 'Subject', 'Aesthetic', 'Imaging', 'Subject at equal motion']
    result = {}
    for metric, raw in zip(metrics, cells[2:]):
        match = re.fullmatch(r'([+-]?\d+\.\d+)(\*)? \[([+-]?\d+\.\d+), ([+-]?\d+\.\d+)\]', raw)
        if not match:
            raise ValueError(f'Unrecognized reported interval: {raw}')
        mean, star, lo, hi = match.groups()
        result[metric] = {'delta': float(mean), 'ci95': [float(lo), float(hi)],
                          'interval_excludes_zero': bool(star), 'reported': raw}
    return result


DATA = {'B - D': read_contrast('B - D'), 'B - C': read_contrast('B - C')}
ROWS = {
    'D': {'name': 'Sink + recent',
          'attended': [0, 1, 2, 6, 7, 8, 9, 10, 11]},
    'B': {'name': 'Recent',
          'attended': list(range(3, 12))},
    'C': {'name': 'Self-only',
          'attended': [9, 10, 11]},
}
for code, row in ROWS.items():
    assert len(row['attended']) == {'D': 9, 'B': 9, 'C': 3}[code]

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_MM}mm" height="{WIDTH_MM*H/W:.6f}mm" viewBox="0 0 {W} {H}">',
       '<title>SGF controlled committing read sets</title>',
       '<desc>Two parallel experimental-design panels with equal dimensions. Same-frame-count comparison: sink3 plus latest recent3 plus current3 versus recent6 plus current3, both nine frames. Recent-versus-self-only comparison: recent6 plus current3 versus current3, nine versus three frames. Each panel preserves the original sink3, older-to-newer recent6, current3 order. Unselected historical entries remain stored, physical cache capacity is twelve, denoising is unchanged, and current K/V is computed from the clean block. The sets depict the full-cache steady state. No measured outcomes or confidence intervals are drawn.</desc>',
       '<defs><pattern id="not-attended" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M0 10 L10 0 M-3 3 L3 -3 M7 13 L13 7" fill="none" stroke="#DEE3E6" stroke-width="1.1"/></pattern></defs>',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       f'<g font-family="Helvetica, Arial, sans-serif" fill="{INK}">']


def text(x, y, label, size=34, color=INK, anchor='start', weight='normal'):
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(label)}</text>')


def line(x1, y1, x2, y2, color=RULE, width=2, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ''
    svg.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{extra}/>')


def frame_card(x, y, source, selected, frame_index):
    color, fill = {'sink': (SINK, SINK_LIGHT), 'recent': (RECENT, RECENT_LIGHT),
                   'current': (CURRENT, CURRENT_LIGHT)}[source]
    stroke = color if selected else '#B8C0C6'
    interior = fill if selected else 'url(#not-attended)'
    svg.append(f'<g class="frame-kv" data-frame-index="{frame_index}" data-source="{source}" data-attended="{str(selected).lower()}">')
    svg.append(f'<path d="M{x} {y} L{x+5} {y-5} H{x+43} V{y+59} L{x+38} {y+64}Z" fill="white" stroke="{stroke}" stroke-width="1.8"/>')
    svg.append(f'<rect x="{x}" y="{y}" width="38" height="64" fill="{interior}" stroke="{stroke}" stroke-width="2.5"/>')
    if selected:
        line(x+19, y, x+19, y+64, color, 1.8)
        line(x, y+64/3, x+38, y+64/3, color, 1)
        line(x, y+128/3, x+38, y+128/3, color, 1)
    svg.append('</g>')


# Both panels use identical geometry, row glyphs, and source-column order.
PANELS = [
    {'id': 'a', 'x': 20, 'width': 860, 'title': 'Same frame count', 'rows': ['D', 'B']},
    {'id': 'b', 'x': 920, 'width': 860, 'title': 'Recent vs self-only', 'rows': ['B', 'C']},
]
XS = [240+46*i for i in range(3)] + [394+46*i for i in range(6)] + [686+46*i for i in range(3)]
for panel in PANELS:
    px = panel['x']
    svg.append(f'<g id="panel-{panel["id"]}" data-panel-width="{panel["width"]}" data-panel-height="350">')
    text(px, 46, f'({panel["id"]}) {panel["title"]}', 40, weight='bold')
    for cx, label, color in [(305, 'Sink', SINK), (528, 'Recent', RECENT), (751, 'Current', CURRENT)]:
        text(px+cx, 104, label, 36, color, 'middle')
    for code, cy in zip(panel['rows'], [175, 315]):
        row = ROWS[code]
        svg.append(f'<g id="read-set-{panel["id"]}-{code}" data-group="{code}" data-total-read="{len(row["attended"])}">')
        text(px, cy+1, row['name'], 36, weight='bold')
        text(px, cy+43, f'{len(row["attended"])} frames', 34, MUTED)
        for i, x in enumerate(XS):
            source = 'sink' if i < 3 else 'recent' if i < 9 else 'current'
            frame_card(px+x, cy-32, source, i in row['attended'], i)
        svg.append('</g>')
    # A short bracket marks the comparison, not data or computational flow.
    svg.append(f'<path d="M{px+842} 175 H{px+858} V315 H{px+842}" fill="none" stroke="{MUTED}" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round"/>')
    svg.append('</g>')
line(900, 25, 900, 360, RULE, 1.8)

# One compact shared key. These marks apply only to direct committing access.
frame_card(255, 397, 'recent', True, -1)
text(310, 438, 'Attended', 34)
frame_card(530, 397, 'recent', False, -1)
text(585, 438, 'Not attended', 34)
text(1010, 438, 'Cache capacity: 12 · same denoising', 32)
svg.append('</g></svg>')

manifest = {
    'artifact': STEM,
    'status': 'Paper Chapter 3 committing read-set schematic',
    'source': str(Path(__file__).resolve().relative_to(ROOT)),
    'physical_size_mm': [WIDTH_MM, WIDTH_MM*H/W],
    'minimum_text_pt_at_168mm': 32*WIDTH_MM/W*72/25.4,
    'source_colors': {'sink': SINK, 'recent': RECENT, 'current': CURRENT},
    'comparison_titles': {'B - D': 'Same frame count', 'B - C': 'Recent vs self-only'},
    'figure_kind': 'Pure controlled-read-set experimental-design schematic; no visible empirical results',
    'panels': PANELS,
    'topology': {'physical_cache_latent_frames': 12, 'card_means': 'one latent frame K/V',
        'frame_order': 'sink3, recent6 ordered older-to-newer, current3',
        'D': 'sink3 + latest recent3 + current3; 9 reads',
        'B': 'recent6 + current3; 9 reads; duplicated identically in both panels',
        'C': 'current3; 3 reads',
        'read_sets': 'Full-cache steady state; warmup has fewer available frames',
        'not_attended': 'Direct committing access only; unselected historical entries remain stored',
        'current': 'Current K/V is computed from the current clean block; current cards do not mean old history already stored before committing',
        'unchanged': ['12-frame physical cache', 'base denoising', 'original selected-slot RoPE positions'],
        'latest_recent3_evidence': 'D reads sink3 + latest recent3 + current3; data/PREREG.md specifies the 9-frame committing budget'},
    'contrasts': DATA,
    'displayed_principal_metrics': [],
    'secondary_metrics': {},
    'results_display': 'None; numerical results and intervals belong to manuscript prose/tables, retained here only as provenance',
    'selection_encoding': {'filled': 'Directly attended for committing',
        'hatch_outline': 'Not directly attended; historical entries remain stored',
        'bracket': 'Pair of experimental conditions; no causal-flow or outcome meaning',
        'representation': 'Historical sources and direct committing selection'},
    'protocol': {'generator': 'SGF released EMA', 'prompt_set': '200 rollf200 prompts',
        'duration_seconds': 60, 'generation_seeds': [0, 1], 'bootstrap_draws': 4000,
        'pooled': 'Average paired differences over seeds within prompt, then resample 200 prompts',
        'ci': '2.5 and 97.5 percentiles',
        'metrics': 'VBench-Long custom 7-component Quality; Subject c2c is separate from fused Subject',
        'not_standard_suite': 'Separate from the 946-entry suite',
        'outputs': 'A/B reused; C/D newly generated',
        'rng': 'Matched initial per-prompt noise seed and sampler protocol; intermediate device re-noise RNG is unfixed in every group, not identical full stochastic trajectories'},
    'interpretation': {'B-D': 'Beyond total read count; content, age and position not individually disentangled',
        'B-C': 'Quality and Subject c2c differences not established; not equivalence. Recent reduces Dynamic but improves Smoothness/Flickering scores'},
    'source_evidence': [
        {'path': str(REPORT.relative_to(ROOT)), 'sha256': hashlib.sha256(REPORT.read_bytes()).hexdigest()},
        {'path': str(PREREG.relative_to(ROOT)), 'sha256': hashlib.sha256(PREREG.read_bytes()).hexdigest()},
        {'path': str(STAT_SOURCE.relative_to(ROOT)), 'sha256': hashlib.sha256(STAT_SOURCE.read_bytes()).hexdigest()},
    ],
}
FIG.mkdir(parents=True, exist_ok=True)
PRE.mkdir(parents=True, exist_ok=True)
svg_path = FIG / f'{STEM}.svg'
pdf_path = FIG / f'{STEM}.pdf'
svg_path.write_text('\n'.join(svg)+'\n')
subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(pdf_path), str(svg_path)], check=True)
subprocess.run(['pdftoppm', '-singlefile', '-png', '-scale-to', '1800', str(pdf_path), str(PRE/STEM)], check=True)
(FIG/f'{STEM}.provenance.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(f'Exported {svg_path}, {pdf_path}, {PRE/STEM}.png')
