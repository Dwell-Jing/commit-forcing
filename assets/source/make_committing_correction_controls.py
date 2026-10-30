#!/usr/bin/env python3
"""Render the manuscript appendix's twelve reported retained-fraction bars.

These spatial-averaging controls reuse released aggregate fractions. No new
normalization, fitting, uncertainty estimate or per-prompt data is exported.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

from paper_style import apply_style, ROOT, INK, MUTED, RULE, ACCENT
from make_committing_correction_dose import load_reported_data, SOURCE
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator

FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
WIDTH_MM, HEIGHT_MM = 125, 62
ORDER = ('CG', 'SG16', 'CM16', 'CM64')
LABELS = ('Frame', '4×4 grid', '16 regions', '64 regions')
SERIES = (
    ('retained_correction', 'Correction', '#D4D9DC', MUTED),
    ('retained_consistency_gain', 'Consistency', INK, INK),
    ('retained_motion_suppression', 'Motion suppression', ACCENT, ACCENT),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw(rows):
    apply_style()
    fig, ax = plt.subplots(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4))
    fig.subplots_adjust(left=.135, right=.98, bottom=.205, top=.81)
    xs, width = np.arange(4, dtype=float), .22
    handles, plotted = [], []
    for i, (field, label, fill, edge) in enumerate(SERIES):
        values = [100 * row[field] for row in rows]
        bars = ax.bar(xs + (i - 1) * width, values, width=width,
                      facecolor=fill, edgecolor=edge, linewidth=.65, zorder=3)
        for bar, row, value in zip(bars, rows, values):
            bar.set_gid(field + '-' + row['code'])
            assert bar.get_height() == value
            plotted.append({'code': row['code'], 'field': field,
                            'retained_fraction': row[field], 'plotted_percent': value})
        handles.append(Patch(facecolor=fill, edgecolor=edge, linewidth=.65, label=label))
    ax.set_xlim(-.57, 3.57)
    ax.set_ylim(0, 100)
    ax.set_xticks(xs, LABELS)
    ax.yaxis.set_major_locator(FixedLocator([0, 50, 100]))
    ax.set_ylabel('Retained (%)', fontsize=9.5, labelpad=5)
    ax.tick_params(labelsize=9, length=3, pad=3)
    ax.tick_params(axis='x', length=0, pad=6)
    ax.spines['left'].set_color(MUTED)
    ax.spines['bottom'].set_color(MUTED)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=RULE, linewidth=.5)
    legend = ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(.5, 1.045),
                       ncol=3, fontsize=9, handlelength=1, handleheight=.85,
                       handletextpad=.40, columnspacing=.85, borderaxespad=0)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = []
    texts = [ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()
    for item in texts:
        if not item.get_text():
            continue
        box = item.get_window_extent(renderer)
        assert box.x0 >= -1 and box.y0 >= -1 and box.x1 <= fig.bbox.x1 + 1 and box.y1 <= fig.bbox.y1 + 1, item.get_text()
        bounds.append({'text': item.get_text(), 'box_pixels': list(box.bounds)})
    box = legend.get_window_extent(renderer)
    assert box.x0 >= -1 and box.x1 <= fig.bbox.x1 + 1 and box.y1 <= fig.bbox.y1 + 1
    for left, right in zip(ax.get_xticklabels(), ax.get_xticklabels()[1:]):
        assert not left.get_window_extent(renderer).overlaps(right.get_window_extent(renderer))
    return fig, plotted, bounds


def main():
    summary = json.loads(SOURCE.read_text())
    by_code = {row['code']:row for row in load_reported_data()}
    rows = [by_code[code] for code in ORDER]
    fig, plotted, bounds = draw(rows)
    stem = 'committing_correction_controls'
    FIG.mkdir(exist_ok=True, parents=True)
    try:
        fig.savefig(FIG/(stem+'.pdf'),format='pdf',metadata={'Title':'Spatial-averaging controls','CreationDate':None,'ModDate':None})
        fig.savefig(FIG/(stem+'.svg'),format='svg',metadata={'Title':'Spatial-averaging controls','Date':None})
    finally:
        plt.close(fig)
    subprocess.run(['pdftoppm','-singlefile','-png','-scale-to','2200',str(FIG/(stem+'.pdf')),str(FIG/stem)],check=True)
    record = {
        'artifact':stem, 'status':'Manuscript appendix spatial-averaging controls',
        'source':'assets/source/make_committing_correction_controls.py',
        'source_sha256':sha(Path(__file__).resolve()),
        'aggregate_source':SOURCE.relative_to(ROOT).as_posix(),
        'aggregate_source_sha256':sha(SOURCE),
        'rows':rows, 'display_order':list(ORDER), 'plotted_bars':plotted,
        'scaling':'Each reported retained fraction is multiplied by 100 with no other change.',
        'samples':{'outcomes':summary['pooling_protocol'],'normalization_prompt_count':summary['effect_normalization']['self_only_reference_prompt_count']},
        'correction_definition':summary['norm_measurement']['correction'],
        'correction_output_definition':summary['norm_measurement']['O_definition'],
        'norm_aggregation':summary['norm_measurement']['aggregation'],
        'normalization_formula':summary['effect_normalization']['formula'],
        'series_definitions':{
            'Correction':'retained committing attention-output correction norm, not stored-KV difference',
            'Consistency':'retained consistency gain over self-only, not raw consistency',
            'Motion suppression':'retained motion suppression relative to self-only, not retained raw motion'},
        'scope':'These controls alter both correction magnitude and spatial structure; the bars do not establish a monotonic dose-response law.',
        'size_mm':[WIDTH_MM,HEIGHT_MM], 'minimum_font_pt':9,
        'no_new_measurement_fit_or_confidence_intervals':True,
        'exports':{ext:sha(FIG/(stem+'.'+ext)) for ext in ('pdf','svg')}}
    (FIG/(stem+'.provenance.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(FIG/(stem+'.png'))


if __name__ == '__main__':
    main()
