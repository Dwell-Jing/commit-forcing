#!/usr/bin/env python3
"""LongLive committing-window curve and correction-magnitude controls.

Both panels read reported aggregate values. Their cohorts and y units remain
separate; no new generation, fitting, uncertainty or outcome statistics are run.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

from paper_style import apply_style, ROOT, INK, MUTED, RULE, ACCENT
from make_committing_correction_dose import load_reported_data
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter

SOURCE = ROOT / 'analysis/window_effects/summary.json'
FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
WIDTH_MM, HEIGHT_MM = 168, 78
EXPECTED_MEANS = [86.21, 87.21, 87.23, 86.93]
EXPECTED_DELTAS = [-1.0, 0.0, 0.02, -0.28]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_window():
    record = json.loads(SOURCE.read_text())['committing_window']
    rows, base = record['rows'], record['base']
    assert [r['h'] for r in rows] == [0, 1, 2, 3]
    assert [r['latent_frames'] for r in rows] == [3, 6, 9, 12]
    assert [r['subject_c2c_mean'] for r in rows] == EXPECTED_MEANS
    assert [r['change_from_h1'] for r in rows] == EXPECTED_DELTAS
    assert record['prompt_count'] == 200 and record['generation_seed'] == 0
    assert record['duration_seconds'] == 60
    assert record['h_excludes_current_block'] is True
    assert base['subject_c2c_mean'] == 86.01 and base['change_from_h1'] == -1.20
    assert base['sink_frames'] == 3
    assert base['latest_trajectory_frames_including_current'] == 9
    assert base['current_frames'] == 3 and base['physical_cache_frames'] == 15
    assert base['is_h_point'] is False and base['is_sink_only_intervention'] is False
    assert record['panels_pool_samples'] is False
    return rows, base


def draw_window(ax, rows, base):
    ax.set_title('Committing window', fontsize=10, weight='normal', pad=11)
    ax.set_xlim(-.18, 3.18); ax.set_ylim(-1.43, .30)
    ax.xaxis.set_major_locator(FixedLocator([0, 1, 2, 3]))
    ax.yaxis.set_major_locator(FixedLocator([-1.2, -.8, -.4, 0]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    ax.tick_params(labelsize=8.5, pad=3, length=3)
    ax.set_xlabel('Preceding blocks', fontsize=9.5, labelpad=6)
    ax.set_ylabel('Δ Subject c2c', fontsize=9.5, labelpad=5)
    ax.axhline(0, color=RULE, linewidth=.7, zorder=0)
    h = [r['h'] for r in rows]; y = [r['change_from_h1'] for r in rows]
    curve, = ax.plot(h, y, color=INK, linewidth=1.3, marker='o', markersize=4.5,
                     markerfacecolor='white', markeredgewidth=1.1, zorder=3)
    curve.set_gid('window-h0-h1-h2-h3')
    ax.scatter([1], [0], s=25, color=ACCENT, zorder=4).set_gid('current-plus-previous-h1')
    for row in rows:
        s = '0' if row['change_from_h1'] == 0 else f'{row["change_from_h1"]:+.2f}'.replace('-', '−')
        offset, align = ((11, 9), 'left') if row['h'] == 0 else ((0, 9), 'center')
        ax.annotate(s, (row['h'], row['change_from_h1']), xytext=offset,
                    textcoords='offset points', fontsize=8.5, ha=align, va='bottom',
                    color=ACCENT if row['h'] == 1 else INK).set_gid('window-value-h'+str(row['h']))
    line = ax.axhline(base['change_from_h1'], color=MUTED, linewidth=1.,
                      linestyle=(0, (4, 3)), zorder=1)
    line.set_gid('base-independent-reference-not-h4')
    ax.text(.13, base['change_from_h1']+.07, 'Base (sink + recent): −1.20',
            fontsize=8.5, color=MUTED, ha='left', va='bottom').set_gid('base-reference-label')
    return {'h': h, 'relative_subject_c2c': y, 'base_horizontal_reference': base['change_from_h1']}


def draw_dose(ax, rows):
    ax.set_title('Correction magnitude', fontsize=10, weight='normal', pad=11)
    ax.set_xlim(-.035, 1.045); ax.set_ylim(-.035, 1.045)
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_locator(FixedLocator([0, .5, 1]))
        axis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    ax.tick_params(labelsize=8.5, length=3, pad=3)
    ax.set_xlabel('Retained correction', fontsize=9.5, labelpad=6)
    ax.set_ylabel('Retained effect', fontsize=9.5, labelpad=5)
    line, = ax.plot([0, 1], [0, 1], color=MUTED, linewidth=.8,
                    linestyle=(0, (3.5, 3)), zorder=1)
    line.set_gid('equal-fraction-reference-not-fit')
    ax.scatter([0, 1], [0, 1], marker='+', s=32, color=MUTED, linewidths=1,
               zorder=2).set_gid('normalization-definitions-not-observations')
    # Codes annotate one of each pair; neither point is shifted.
    offsets = {'CG': (-12, -13), 'CM16': (-28, 13), 'SG16': (7, 7), 'CM64': (8, 1)}
    points = []
    for row in rows:
        code = row['code']; x = row['retained_correction']
        y1 = row['retained_consistency_gain']; y2 = row['retained_motion_suppression']
        a = ax.scatter(x, y1, s=35, marker='o', facecolor='white', edgecolor=INK,
                       linewidths=1.05, zorder=4)
        b = ax.scatter(x, y2, s=25, marker='^', facecolor=ACCENT, edgecolor=ACCENT,
                       linewidths=.6, zorder=5)
        a.set_gid('consistency-'+code); b.set_gid('motion-suppression-'+code)
        assert a.get_offsets().tolist() == [[x, y1]]
        assert b.get_offsets().tolist() == [[x, y2]]
        anchor = (x, y2) if code == 'SG16' else (x, y1)
        ax.annotate(code, anchor, xytext=offsets[code], textcoords='offset points',
                    fontsize=8.5, color=INK, va='center', ha='left').set_gid('dose-code-'+code)
        points.append({'code':code, 'consistency':[x,y1], 'motion_suppression':[x,y2]})
    handles = [Line2D([], [], marker='o', markerfacecolor='white', markeredgecolor=INK,
                      markeredgewidth=1.05, color=INK, linestyle='none', markersize=5.5,
                      label='Consistency'),
               Line2D([], [], marker='^', markerfacecolor=ACCENT, markeredgecolor=ACCENT,
                      color=ACCENT, linestyle='none', markersize=5., label='Motion suppression')]
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(-.02, 1.01),
               fontsize=8.5, handletextpad=.45, borderaxespad=.2, labelspacing=.35)
    return points


def main():
    window, base = load_window()
    dose = load_reported_data()
    summary = json.loads(SOURCE.read_text())
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_MM/25.4, HEIGHT_MM/25.4))
    fig.subplots_adjust(left=.085, right=.985, bottom=.21, top=.85, wspace=.41)
    for ax in axes:
        ax.spines['left'].set_color(MUTED)
        ax.spines['bottom'].set_color(MUTED)
    plotted_window = draw_window(axes[0], window, base)
    plotted_dose = draw_dose(axes[1], dose)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in axes:
        for text in [ax.title, ax.xaxis.label, ax.yaxis.label] + list(ax.texts):
            box = text.get_window_extent(renderer)
            assert (box.x0 >= -1 and box.x1 <= fig.bbox.x1+1 and
                    box.y0 >= -1 and box.y1 <= fig.bbox.y1+1), text.get_text()
    stem = 'committing_window_mechanisms'
    FIG.mkdir(exist_ok=True, parents=True)
    pdf, svg = [FIG / (stem+'.'+ext) for ext in ['pdf', 'svg']]
    try:
        fig.savefig(pdf, format='pdf', metadata={
            'Title':'LongLive committing-window evidence',
            'CreationDate':None, 'ModDate':None})
        fig.savefig(svg, format='svg', metadata={
            'Title':'LongLive committing-window evidence', 'Date':None})
    finally:
        plt.close(fig)
    subprocess.run(['pdftoppm', '-singlefile', '-png', '-scale-to', '2200',
                    str(pdf), str(FIG / stem)], check=True)
    record = {
        'artifact':stem,
        'source':'assets/source/make_committing_window_mechanisms.py',
        'source_sha256':sha(Path(__file__).resolve()),
        'aggregate_source':SOURCE.relative_to(ROOT).as_posix(),
        'aggregate_source_sha256':sha(SOURCE),
        'source_overleaf_commit':summary['overleaf_source_commit'],
        'window_rows':window,
        'base':base,
        'plotted_window':plotted_window,
        'dose_rows':dose,
        'plotted_dose':plotted_dose,
        'left_protocol':'LongLive, 200 rollf200 prompts, 60 seconds, generation seed 0. h counts preceding trajectory blocks, excluding the current block. h=0/1/2/3 correspond to 3/6/9/12 latent frames.',
        'left_y_definition':'Reported Subject c2c differences in percentage points from h=1. No new uncertainty is estimated or plotted.',
        'base_scope':'Base reads 3 sink plus latest 9 trajectory frames including the current 3, with 15-frame physical storage. It is a separate complete context, not h=4 and not an h=1-plus-sink-only intervention.',
        'right_protocol':{
            'variant_outcomes':'100 rollf200 prompts, 60 seconds, generation seed 0',
            'effect_normalization':'Reported 200-prompt endpoints: self-only minus recent-context is Dynamic +3.63 and Subject c2c -1.00'},
        'correction_definition':'D = attention(q, current+previous K/V) - attention(q, current K/V), evaluated before the attention output projection. This is an attention-output correction, not a stored-KV difference.',
        'correction_x_definition':'Reported ||pool(D)||_F / ||D||_F, measured independently of outcome scores.',
        'norm_aggregation':summary['norm_measurement']['aggregation'],
        'dose_normalization_formula':summary['effect_normalization']['formula'],
        'dose_reference':'Dashed y=x is an equal-fraction reference, not a fit. The 0/1 plus markers define normalization, not additional observations.',
        'panels_pool_samples':False,
        'SG16_departure':'Retained consistency gain 0.42 differs from retained motion suppression 0.61.',
        'size_mm':[WIDTH_MM, HEIGHT_MM],
        'minimum_font_pt':8.5,
        'no_new_generation_or_fitting_or_confidence_intervals':True,
        'exports':{ext:sha(FIG/(stem+'.'+ext)) for ext in ['pdf','svg']}}
    (FIG/(stem+'.provenance.json')).write_text(json.dumps(record, indent=2)+'\n')
    print(FIG/(stem+'.png'))


if __name__ == '__main__':
    main()
