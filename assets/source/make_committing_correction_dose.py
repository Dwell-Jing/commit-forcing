#!/usr/bin/env python3
"""Reported LongLive correction-magnitude/effect ratios, with no fitted law.

The x coordinates are independently reported correction norms. They are not
inferred from either y series. Only the four reported spatial-averaging arms
are included. P/U lack reported x values and are deliberately not plotted.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

from paper_style import apply_style, ROOT, INK, MUTED, RULE, ACCENT
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter

SOURCE = ROOT / 'analysis/window_effects/summary.json'
FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
WIDTH_MM, HEIGHT_MM = 125, 80
EXPECTED = {
    'CG': (.36, .29, .37),
    'CM16': (.47, .47, .48),
    'SG16': (.48, .42, .61),
    'CM64': (.56, .55, .48),
}
LABEL_OFFSETS = {'CG': (-13, -15), 'CM16': (-34, 10),
                 'SG16': (10, -15), 'CM64': (9, 2)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_reported_data():
    summary = json.loads(SOURCE.read_text())
    rows = summary['pooling_arms']
    assert len(rows) == 4 and {row['code'] for row in rows} == set(EXPECTED)
    for row in rows:
        coordinates = (row['retained_correction'], row['retained_consistency_gain'],
                       row['retained_motion_suppression'])
        assert coordinates == EXPECTED[row['code']], row['code']
    return rows


def draw(rows):
    apply_style()
    fig, ax = plt.subplots(figsize=(WIDTH_MM/25.4, HEIGHT_MM/25.4))
    fig.subplots_adjust(left=.15, right=.97, bottom=.20, top=.94)
    ax.set_xlim(-.025, 1.045)
    ax.set_ylim(-.025, 1.045)
    ax.xaxis.set_major_locator(FixedLocator([0, .25, .5, .75, 1.]))
    ax.yaxis.set_major_locator(FixedLocator([0, .25, .5, .75, 1.]))
    formatter = FuncFormatter(lambda v, _: f'{v:g}')
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.tick_params(labelsize=9, length=3, pad=3)
    ax.spines['left'].set_color(MUTED)
    ax.spines['bottom'].set_color(MUTED)
    ax.set_xlabel('Retained correction', labelpad=5, fontsize=10)
    ax.set_ylabel('Retained effect', labelpad=5, fontsize=10)
    ref, = ax.plot([0, 1], [0, 1], color=MUTED, linewidth=.8,
                  linestyle=(0, (3.5, 3)), zorder=1)
    ref.set_gid('equal-fraction-reference-not-fit')
    # These are normalization definitions, not additional empirical observations.
    endpoint = ax.scatter([0, 1], [0, 1], marker='+', s=43, color=MUTED,
                          linewidths=1, zorder=2)
    endpoint.set_gid('normalization-endpoints-not-observations')
    labels = []
    actual_points = []
    for row in rows:
        x = row['retained_correction']
        y1 = row['retained_consistency_gain']
        y2 = row['retained_motion_suppression']
        circle = ax.scatter(x, y1, s=47, marker='o', facecolor='white',
                            edgecolor=INK, linewidths=1.1, zorder=4)
        circle.set_gid('consistency-' + row['code'])
        triangle = ax.scatter(x, y2, s=30, marker='^', facecolor=ACCENT,
                              edgecolor=ACCENT, linewidths=.7, zorder=5)
        triangle.set_gid('motion-suppression-' + row['code'])
        assert circle.get_offsets().tolist() == [[x, y1]]
        assert triangle.get_offsets().tolist() == [[x, y2]]
        actual_points.append({'code': row['code'], 'consistency': [x, y1],
                              'motion_suppression': [x, y2]})
        dx, dy = LABEL_OFFSETS[row['code']]
        lab = ax.annotate(row['code'], (x, y1), xytext=(dx, dy),
                          textcoords='offset points', fontsize=8.8, color=INK,
                          va='center', ha='left', annotation_clip=False)
        lab.set_gid('variant-label-' + row['code'])
        labels.append(lab)
    handles = [
        Line2D([], [], marker='o', markerfacecolor='white', markeredgecolor=INK,
               markeredgewidth=1.1, color=INK, linestyle='none', markersize=6.2,
               label='Consistency'),
        Line2D([], [], marker='^', markerfacecolor=ACCENT, markeredgecolor=ACCENT,
               color=ACCENT, linestyle='none', markersize=5.5,
               label='Motion suppression'),
    ]
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(.01, .99),
              fontsize=9, handletextpad=.5, borderaxespad=.2, labelspacing=.45)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for i, left in enumerate(labels):
        for right in labels[i+1:]:
            assert not left.get_window_extent(renderer).overlaps(right.get_window_extent(renderer)), (left.get_text(), right.get_text())
    return fig, actual_points


def main():
    rows = load_reported_data()
    stem = 'committing_correction_dose'
    FIG.mkdir(exist_ok=True, parents=True)
    fig, points = draw(rows)
    pdf, svg = (FIG / (stem + '.' + ext) for ext in ['pdf', 'svg'])
    try:
        fig.savefig(pdf, format='pdf', metadata={
            'Title':'Retained correction and retained effects',
            'CreationDate':None, 'ModDate':None})
        fig.savefig(svg, format='svg', metadata={
            'Title':'Retained correction and retained effects', 'Date':None})
    finally:
        plt.close(fig)
    subprocess.run(['pdftoppm', '-singlefile', '-png', '-scale-to', '2200',
                    str(pdf), str(FIG / stem)], check=True)
    record = {
        'artifact':stem,
        'source':'assets/source/make_committing_correction_dose.py',
        'source_sha256':sha(Path(__file__).resolve()),
        'aggregate_source':SOURCE.relative_to(ROOT).as_posix(),
        'aggregate_source_sha256':sha(SOURCE),
        'source_overleaf_commit':'85b6572eeaa51e55adb6fa153c69a8cb2a2fb313',
        'plotted_points':points,
        'correction_definition':'D = attention(q, current+previous K/V) - attention(q, current K/V), evaluated before the attention output projection. This is an attention-output correction, not a stored-KV difference.',
        'x_definition':'Reported ||pool(D)||_F / ||D||_F. This ratio is measured independently of outcome effects.',
        'norm_aggregation':'For each committing attention call, use current-token, head and channel dimensions. Average calls across 30 layers and 79 post-startup commits per video, then average the 100 video means.',
        'y_definition':'Reported retained fractions of recent-context versus self-only consistency gain and motion suppression.',
        'samples':{'variant_outcomes':'100 rollf200 prompts, 60 seconds, generation seed 0',
                   'effect_normalization':'Reported 200-prompt endpoints: self-only minus recent-context is Dynamic +3.63 and Subject c2c -1.00'},
        'precision':'Reported two-decimal ratios are preserved; no new norm measurements, intervals or outcome statistics are computed.',
        'reference':'The y=x line is an equal-fraction reference, not a fit. Plus signs at (0,0) and (1,1) define normalization and are not additional observations.',
        'scope':'Four spatial-averaging interventions and eight effect points on LongLive. No strict linear law or unique smoothing mechanism is established.',
        'excluded':'P and U have no reported horizontal norm ratio in this study and are not plotted.',
        'size_mm':[WIDTH_MM, HEIGHT_MM], 'minimum_font_pt':8.8,
        'exports':{ext:sha(FIG/f'{stem}.{ext}') for ext in ['pdf', 'svg']}}
    (FIG/f'{stem}.provenance.json').write_text(json.dumps(record, indent=2)+'\n')
    print(FIG/f'{stem}.png')


if __name__ == '__main__':
    main()
