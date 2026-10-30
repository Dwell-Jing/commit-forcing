#!/usr/bin/env python3
"""Native-vector reconstruction of the user-approved shared-history method figure.

Run this builder from any directory. The editable SVG is the source of the
vector PDF and PNG preview; the reference bitmap is not embedded.
"""
from pathlib import Path
import argparse
import os
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

from paper_palette import (
    INK, MUTED, RULE, BLUE, BLUE_LIGHT, ACCENT, ACCENT_LIGHT,
    NONRECENT_LIGHT, COMMIT_FILL, TENSOR_FILL,
)
from method_glyphs import _glyph


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
PREVIEW = OUT
STEM = 'method'
NS = 'http://www.w3.org/2000/svg'
Q = '{' + NS + '}'
ET.register_namespace('', NS)
W, H, WIDTH_MM = 2200, 1120, 178
FONT = 'Helvetica, Arial, sans-serif'


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _n(value):
    return format(float(value), '.12g')


def _el(parent, name, **attrs):
    return ET.SubElement(parent, Q + name, {
        key.replace('_', '-'): str(value) for key, value in attrs.items()
    })


def _text(parent, x, y, content, color=INK, size=38, anchor='middle', weight='normal'):
    element = _el(parent, 'text', x=_n(x), y=_n(y), fill=color,
                  font_family=FONT, font_size=size, text_anchor=anchor,
                  font_weight=weight)
    element.text = content
    return element


def render(draft=False):
    """Render the manuscript figure using the released vector glyph helper."""
    out = OUT
    preview = PREVIEW
    stem = STEM + ('_draft' if draft else '')
    root = ET.Element(Q + 'svg', {
        'width': f'{WIDTH_MM}mm', 'height': f'{WIDTH_MM * H / W:.6f}mm',
        'viewBox': f'0 0 {W} {H}',
    })
    _el(root, 'title').text = 'Shared denoising and recurrent committing dependencies'
    _el(root, 'desc').text = (
        'Above, all configurations follow the same SGF denoising context: stored '
        'sink and recent KV condition generation of a clean latent block. '
        'Below, consecutive committing calls separately receive their own clean '
        'blocks. Base additionally reads sink and two preceding KV entries; '
        'self-only has no historical committing inputs; Ours reads the immediately '
        'preceding KV. Crosses exclude sink only from committing access, not '
        'storage or denoising. Blue lower blocks are clean latents; rust lower '
        'blocks are newly constructed KV. These are schematic types, not a '
        'shared numerical latent across policies. Inputs before the displayed '
        'window are omitted; the first shown Ours call is not a cold start.'
    )
    defs = _el(root, 'defs')
    for name, color in (('ink', INK), ('muted', MUTED), ('accent', ACCENT)):
        marker = _el(defs, 'marker', id=f'sh-arrow-{name}', viewBox='0 0 10 10',
                     refX=9, refY=5, markerWidth=4.5, markerHeight=4.5, orient='auto')
        # Actual tip and reference coincide, so endpoints equal visible tips.
        _el(marker, 'path', d='M0 1 L9 5 L0 9 Z', fill=color)
    noise = _el(defs, 'pattern', id='draft-noise-hatch', width=8, height=8,
                patternUnits='userSpaceOnUse')
    _el(noise, 'path', d='M0 0 L8 8 M-4 4 L4 12 M4 -4 L12 4',
        fill='none', stroke=MUTED, stroke_width=1.6)
    _el(root, 'rect', width=W, height=H, fill='white')

    glyphs, edges, crosses, rows = [], [], [], []

    def glyph(parent, name, role, kind, x, y, w, h, color, fill, noise_opacity=None):
        record = _glyph(parent, name, role, kind, x, y, w, h, color, fill, noise_opacity)
        glyphs.append(record)
        return record

    def edge(parent, name, kind, source, target, start, end, path=None, color=MUTED):
        d = path or f'M{_n(start[0])} {_n(start[1])} L{_n(end[0])} {_n(end[1])}'
        marker_name = 'accent' if color == ACCENT else 'ink' if color == INK else 'muted'
        _el(parent, 'path', id=name, d=d, fill='none', stroke=color,
            stroke_width=3, stroke_linecap='round', stroke_linejoin='round',
            marker_end=f'url(#sh-arrow-{marker_name})', **{
                'class': 'typed-edge', 'data-kind': kind,
                'data-source': source, 'data-target': target,
            })
        edges.append({
            'id': name, 'kind': kind, 'source': source, 'target': target,
            'start': list(start), 'end': list(end), 'path': d,
            'visible_tip_equals_end': True,
        })

    upper = _el(root, 'g', id='common-denoising', **{
        'data-scope': 'shared-base-sgf-generation',
    })
    _text(upper, 1100, 43, 'Historical KV', size=42)
    _el(upper, 'rect', x=735, y=70, width=730, height=202, rx=5,
        fill=TENSOR_FILL, stroke=MUTED, stroke_width=2.4,
        **{'id': 'historical-kv-tray'})
    _text(upper, 849, 115, 'Sink', color=MUTED)
    _text(upper, 1197, 115, 'Recent', color=BLUE)
    _el(upper, 'path', d='M993 139 V135 Q993 128 1002 128 H1411 Q1420 128 1420 135 V139',
        fill='none', stroke=BLUE, stroke_width=2.2, stroke_linecap='round',
        **{'id': 'recent-pair-bracket'})
    for name, x, color, fill in (
        ('sink', 785, MUTED, NONRECENT_LIGHT),
        ('recent-1', 1005, BLUE, BLUE_LIGHT),
        ('recent-2', 1265, BLUE, BLUE_LIGHT),
    ):
        glyph(upper, f'sh-history-{name}', 'historical-kv', 'historical-kv',
              x, 160, 128, 96, color, fill)
    _el(upper, 'path', d='M770 279 V284 Q770 294 780 294 H1420 Q1430 294 1430 284 V279',
        fill='none', stroke=MUTED, stroke_width=2.4, stroke_linecap='round',
        **{'id': 'whole-history-bracket'})
    edge(upper, 'sh-history-to-denoising', 'base-denoising-history',
         'historical-kv-tray', 'base-denoising', (1100, 294), (1100, 327))

    glyph(upper, 'sh-noisy-current', 'noisy-current-latent', 'noisy-latent',
          390, 345, 152, 114, MUTED, TENSOR_FILL, 1)
    edge(upper, 'sh-noise-to-denoising', 'noisy-current-input',
         'draft-glyph-sh-noisy-current', 'base-denoising',
         (390 + 152 * 1.11, 402), (685, 402), color=INK)
    _el(upper, 'rect', id='base-denoising', x=685, y=327, width=825, height=150,
        rx=5, fill=TENSOR_FILL, stroke=RULE, stroke_width=2.4)
    _text(upper, 1100, 369, 'Denoising', size=42, weight='bold')
    denoising_x = (742, 950, 1168, 1376)
    for i, (x, opacity) in enumerate(zip(denoising_x, (1, .65, .25, 0)), 1):
        glyph(upper, f'sh-denoising-{i}', 'denoising-latent', 'latent',
              x, 398, 96, 72, MUTED, TENSOR_FILL, opacity)
        if i < 4:
            edge(upper, f'sh-denoising-step-{i}', 'next-denoising-state',
                 f'draft-glyph-sh-denoising-{i}', f'draft-glyph-sh-denoising-{i + 1}',
                 (x + 96 * 1.11, 434), (denoising_x[i], 434), color=INK)
    glyph(upper, 'sh-clean-current', 'clean-current-latent', 'clean-latent-not-kv',
          1625, 346, 144, 108, BLUE, BLUE_LIGHT)
    edge(upper, 'sh-denoising-to-clean', 'generated-clean-latent',
         'base-denoising', 'draft-glyph-sh-clean-current', (1510, 402), (1625, 402), color=INK)
    _text(upper, 1805, 405, 'Clean block', color=BLUE, anchor='start')
    edge(upper, 'sh-generation-to-committing-comparison', 'stage-continuation-not-tensor-broadcast',
         'draft-glyph-sh-clean-current', 'committing-comparison-region',
         (1697, 454), (1697, 523))
    _el(root, 'path', id='stage-divider', d='M30 535 H2170', fill='none',
        stroke=RULE, stroke_width=2)

    lower = _el(root, 'g', id='committing-comparison-region', **{
        'data-comparison': 'successive-sgf-committing-inputs',
    })
    sink_x, gw, gh = 215, 96, 72
    clean_x, call_x, kv_x = (367, 980, 1590), (520, 1130, 1740), (810, 1420, 2030)
    call_w, call_h = 245, 84
    for policy, title, cy in (('base', 'Base', 665), ('self-only', 'Self-only', 845), ('ours', 'Ours', 1025)):
        lane = _el(lower, 'g', id=f'sh-lane-{policy}', **{
            'class': 'comparison-lane', 'data-policy': policy, 'data-center-y': cy,
            'data-sink-stored': 'true',
        })
        if policy == 'ours':
            _text(lane, 35, cy - 10, 'Commit', size=42, anchor='start')
            _text(lane, 35, cy + 38, 'Forcing', size=42, anchor='start')
        else:
            _text(lane, 35, cy + 14, title, size=42, anchor='start')
        sink = glyph(lane, f'sh-{policy}-sink', 'stored-sink-kv', 'historical-kv',
                     sink_x, cy - gh / 2, gw, gh, MUTED, NONRECENT_LIGHT)
        rows.append({'policy': policy, 'center_y': cy, 'sink_x': sink_x,
                     'clean_x': list(clean_x), 'committing_x': list(call_x), 'kv_x': list(kv_x)})
        for i in range(3):
            call_id = f'sh-{policy}-committing-{i + 1}'
            call = _el(lane, 'g', id=call_id, **{'class': 'committing-call', 'data-shown-call': i + 1})
            glyph(call, f'sh-{policy}-clean-{i + 1}', 'current-clean-latent', 'clean-latent-not-kv',
                  clean_x[i], cy - gh / 2, gw, gh, BLUE, BLUE_LIGHT)
            _el(call, 'rect', x=call_x[i], y=cy - call_h / 2,
                width=call_w, height=call_h, rx=4, fill=COMMIT_FILL,
                stroke=MUTED, stroke_width=2.4, **{'class': 'committing-operator'})
            _text(call, call_x[i] + call_w / 2, cy + 13, 'Committing')
            glyph(call, f'sh-{policy}-kv-{i + 1}', 'new-committed-kv', 'kv',
                  kv_x[i], cy - gh / 2, gw, gh, ACCENT, ACCENT_LIGHT)
            edge(call, f'{call_id}-current', 'current-clean-input',
                 f'draft-glyph-sh-{policy}-clean-{i + 1}', call_id,
                 (clean_x[i] + gw * 1.11, cy), (call_x[i], cy))
            edge(call, f'{call_id}-new-kv', 'new-kv-output', call_id,
                 f'draft-glyph-sh-{policy}-kv-{i + 1}',
                 (call_x[i] + call_w, cy), (kv_x[i], cy), color=ACCENT)

        if policy == 'base':
            bus_y = cy - 100
            _el(lane, 'path', id='sh-base-sink-bus',
                d=f'M{_n(sink_x + gw * 1.11)} {cy} H340 V{bus_y} H{call_x[2] + call_w / 2}',
                fill='none', stroke=MUTED, stroke_width=3,
                stroke_linecap='round', stroke_linejoin='miter',
                **{'data-kind': 'shared-sink-input-bus', 'data-source': sink['id']})
            for i in range(3):
                x = call_x[i] + call_w / 2
                edge(lane, f'sh-base-sink-to-{i + 1}', 'sink-committing-input',
                     sink['id'], f'sh-base-committing-{i + 1}',
                     (x, bus_y), (x, cy - call_h / 2))
        else:
            # The stored Sink stays visible; X denotes direct-access exclusion.
            half = gw * .3
            cx = sink_x + gw / 2
            d = (f'M{_n(cx - half)} {_n(cy - half)} L{_n(cx + half)} {_n(cy + half)} '
                 f'M{_n(cx + half)} {_n(cy - half)} L{_n(cx - half)} {_n(cy + half)}')
            cross = _el(lane, 'g', id=f'sh-{policy}-sink-access-excluded', **{
                'data-meaning': 'not-read-by-committing-sink-still-stored',
            })
            _el(cross, 'path', d=d, fill='none', stroke='white', stroke_width=10,
                stroke_linecap='square')
            _el(cross, 'path', d=d, fill='none', stroke=ACCENT, stroke_width=6,
                stroke_linecap='square')
            crosses.append({'policy': policy, 'center': [cx, cy], 'width': 2 * half,
                            'placement': 'center of front Sink face',
                            'meaning': 'exclude direct committing access, not deletion'})

        if policy in ('base', 'ours'):
            color = ACCENT if policy == 'ours' else MUTED
            for i in (0, 1):
                sx, sy = kv_x[i] + gw / 2, cy + gh / 2
                tx, ty = call_x[i + 1] + 45, cy + call_h / 2
                d = (f'M{sx} {sy} C{sx + 77} {cy + 95} '
                     f'{tx - 70} {cy + 95} {tx} {ty}')
                edge(lane, f'sh-{policy}-previous-{i + 1}-to-{i + 2}', 'previous-kv-input',
                     f'draft-glyph-sh-{policy}-kv-{i + 1}', f'sh-{policy}-committing-{i + 2}',
                     (sx, sy), (tx, ty), path=d, color=color)
        if policy == 'base':
            sx, sy = kv_x[0] + gw / 2, cy + gh / 2
            tx, ty = call_x[2] + 80, cy + call_h / 2
            d = (f'M{sx} {sy} C{sx + 122} {cy + 140} '
                 f'{tx - 115} {cy + 140} {tx} {ty}')
            edge(lane, 'sh-base-older-1-to-3', 'older-direct-kv-input',
                 'draft-glyph-sh-base-kv-1', 'sh-base-committing-3',
                 (sx, sy), (tx, ty), path=d)

    assert len(glyphs) == 30  # 9 common-generation glyphs and 21 lower glyphs.
    assert len(lower.findall('.//' + Q + 'g[@class="draft-data-glyph"]')) == 21
    assert len(lower.findall('.//' + Q + 'g[@class="committing-call"]')) == 9
    assert len(crosses) == 2
    for policy, count in (('base', 6), ('self-only', 0), ('ours', 2)):
        historical = [e for e in edges if e['id'].startswith(f'sh-{policy}-') and
                      e['kind'] in ('sink-committing-input', 'previous-kv-input', 'older-direct-kv-input')]
        assert len(historical) == count
        assert all('committing' in e['target'] for e in historical)
    assert all(float(t.get('font-size')) >= 38 for t in root.iter(Q + 'text'))
    assert not root.findall('.//' + Q + 'image')
    assert not root.findall('.//' + Q + 'linearGradient')
    assert rows[0]['clean_x'] == rows[1]['clean_x'] == rows[2]['clean_x']
    assert rows[0]['committing_x'] == rows[1]['committing_x'] == rows[2]['committing_x']
    assert rows[0]['kv_x'] == rows[1]['kv_x'] == rows[2]['kv_x']

    out.mkdir(parents=True, exist_ok=True)
    preview.mkdir(parents=True, exist_ok=True)
    svg_path, pdf_path = out / f'{stem}.svg', out / f'{stem}.pdf'
    tmp_svg, tmp_pdf = out / f'.{stem}.svg', out / f'.{stem}.pdf'
    try:
        ET.ElementTree(root).write(tmp_svg, encoding='utf-8', xml_declaration=True)
        subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(tmp_pdf), str(tmp_svg)], check=True)
        subprocess.run(['pdftoppm', '-singlefile', '-png', '-scale-to', str(W),
                        str(tmp_pdf), str(preview / stem)], check=True)
        tmp_svg.replace(svg_path)
        tmp_pdf.replace(pdf_path)
    finally:
        tmp_svg.unlink(missing_ok=True)
        tmp_pdf.unlink(missing_ok=True)

    metadata = {
        'artifact': stem,
        'status': ('Independent draft; canonical and manuscript untouched' if draft else
                   'Canonical Figure 4; user-approved common denoising and recurrent committing comparison'),
        'authoring_source': 'assets/source/make_method.py',
        'authoring_source_sha256': _sha(Path(__file__).resolve()),
        'entrypoint': 'assets/source/make_method.py',
        'regenerate': 'python3 assets/source/make_method.py' + (' --draft' if draft else ''),
        'palette_source': 'assets/source/paper_palette.py',
        'glyph_helper': 'assets/source/method_glyphs.py',
        'glyph_helper_sha256': _sha(ROOT / 'assets/source/method_glyphs.py'),
        'manuscript_asset': {'version': '2026-10-30 manuscript assets', 'source': 'figures/method_overview.svg', 'source_svg_sha256': '3502f42da24cbd6df1e6e3042d124e39331fd908544cd041fc79cea1642741b6'},
        'canvas': [W, H], 'physical_size_mm': [WIDTH_MM, WIDTH_MM * H / W],
        'minimum_source_font_size': 38,
        'minimum_type_pt_at_178mm': 38 * WIDTH_MM / W * 72 / 25.4,
        'editable': 'Native live SVG text, vector grids/slabs/operators and typed connectors; no raster',
        'glyph_count': {'upper': 9, 'lower': 21, 'total': len(glyphs)},
        'glyphs': glyphs, 'rows': rows, 'edges': edges, 'sink_access_crosses': crosses,
        'caption_handoff': (
            'Top: common SGF generation. Sink and recent historical KV condition the '
            'base denoising process, producing a clean latent block. Bottom: direct '
            'committing dependencies across consecutive blocks. Blue inputs denote '
            'each call’s own clean latent, and rust outputs denote newly constructed KV; '
            'matching shapes indicate tensor types, not shared numerical values across '
            'methods. Base reads sink and two preceding KV entries; self-only reads no '
            'historical KV; Ours reads the immediately preceding KV. Large crosses '
            'exclude sink from committing access only: sink storage, base denoising '
            'and base cache updates remain unchanged. Inputs before the shown window '
            'are omitted, and the first shown Ours call is not a cold start. Slabs '
            'and front grid cells are symbolic, not literal frame or layer counts. '
            'Other backbones retain their own base denoising policies.'
        ),
        'scientific_boundaries': [
            'Shared top depicts the same denoising policy, not identical free-running latents',
            'Gray continuation arrow ends 12 source units above the divider, not on Base Sink bus',
            'All historical edges target committing operators, never clean inputs or output KV',
            'Base also recurs; recurrence is not exclusive to Ours',
            'Sink remains stored in all configurations despite committing-access crosses',
            'No automatic KV decay, drift magnitude, learned router or cache-cropping operator',
            ('No canonical artifact or manuscript modified' if draft else
             'Canonical figure exports only; TeX, caption and main-PDF integration are separate'),
        ],
        'export_sha256': {'svg': _sha(svg_path), 'pdf': _sha(pdf_path)},
    }
    provenance = out / f'{stem}.provenance.json'
    provenance.write_text(json.dumps(metadata, indent=2) + '\n')
    return {'svg': str(svg_path), 'pdf': str(pdf_path), 'provenance': str(provenance),
            'preview': str(preview / f'{stem}.png')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--draft', action='store_true')
    args = parser.parse_args()
    print(json.dumps(render(draft=args.draft), indent=2))
