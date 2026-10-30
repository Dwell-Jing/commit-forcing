#!/usr/bin/env python3
"""LongLive committing-window means, using the released aggregate record.

The four means and separate Base reference match the manuscript main figure.
Spatial-averaging controls are exported separately for the appendix.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

from paper_style import apply_style, ROOT, INK, MUTED, RULE, ACCENT
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter

SOURCE = ROOT / 'analysis/window_effects/summary.json'
FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
WIDTH_MM, HEIGHT_MM = 86, 45.2
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
    ax.set_xlim(-.18, 3.18); ax.set_ylim(85.8, 87.45)
    ax.xaxis.set_major_locator(FixedLocator([0, 1, 2, 3]))
    ax.yaxis.set_major_locator(FixedLocator([86, 86.5, 87]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    ax.tick_params(labelsize=9.2, pad=4, length=3)
    ax.set_xlabel('Preceding blocks', fontsize=10, labelpad=6)
    ax.set_ylabel(r'Subject$_{\mathrm{c2c}}$', fontsize=10, labelpad=7)
    h = [r['h'] for r in rows]; y = [r['subject_c2c_mean'] for r in rows]
    curve, = ax.plot(h, y, color=INK, linewidth=1.3, marker='o', markersize=4.5,
                     markerfacecolor='white', markeredgewidth=1.1, zorder=3)
    curve.set_gid('window-h0-h1-h2-h3')
    ax.scatter([1], [y[1]], s=25, color=ACCENT, zorder=4).set_gid('current-plus-previous-h1')
    line = ax.axhline(base['subject_c2c_mean'], color=MUTED, linewidth=1.,
                      linestyle=(0, (4, 3)), zorder=1)
    line.set_gid('base-independent-reference-not-h4')
    ax.text(3.1, base['subject_c2c_mean']+.04, 'Base',
            fontsize=9.2, color=MUTED, ha='right', va='bottom').set_gid('base-reference-label')
    return {'h': h, 'subject_c2c': y, 'base_horizontal_reference': base['subject_c2c_mean']}


def main():
    window, base = load_window()
    apply_style()
    plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial',
                         'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold'})
    fig, ax = plt.subplots(figsize=(WIDTH_MM/25.4, HEIGHT_MM/25.4))
    fig.subplots_adjust(left=.19, right=.97, bottom=.27, top=.95)
    ax.spines['left'].set_color(MUTED); ax.spines['bottom'].set_color(MUTED)
    plotted_window = draw_window(ax, window, base)
    fig.canvas.draw(); renderer = fig.canvas.get_renderer()
    texts = [ax.xaxis.label, ax.yaxis.label] + list(ax.texts) + ax.get_xticklabels() + ax.get_yticklabels()
    for text in texts:
        if not text.get_text():
            continue
        box = text.get_window_extent(renderer)
        assert box.x0 >= -1 and box.x1 <= fig.bbox.x1+1 and box.y0 >= -1 and box.y1 <= fig.bbox.y1+1, text.get_text()
    stem = 'committing_window_mechanisms'
    FIG.mkdir(exist_ok=True, parents=True)
    try:
        fig.savefig(FIG/(stem+'.pdf'), format='pdf', metadata={'Title':'LongLive committing-window evidence','CreationDate':None,'ModDate':None})
        fig.savefig(FIG/(stem+'.svg'), format='svg', metadata={'Title':'LongLive committing-window evidence','Date':None})
    finally:
        plt.close(fig)
    subprocess.run(['pdftoppm','-singlefile','-png','-scale-to','2200',str(FIG/(stem+'.pdf')),str(FIG/stem)],check=True)
    record = {
        'artifact':stem, 'status':'Manuscript main-text window curve',
        'source':'assets/source/make_committing_window_mechanisms.py',
        'source_sha256':sha(Path(__file__).resolve()),
        'aggregate_source':SOURCE.relative_to(ROOT).as_posix(),
        'aggregate_source_sha256':sha(SOURCE),
        'manuscript_asset':{'version':'2026-10-30 manuscript assets','source':'figures/committing_window_mechanisms.svg','source_svg_sha256':'51746927c6ad6bc08b30e8ba277e973733bf1327f7b8a10e38aeb67ac949321f'},
        'window_rows':window, 'base':base, 'plotted_window':plotted_window,
        'protocol':'LongLive, 200 rollf200 prompts, 60 seconds, generation seed 0. h counts preceding trajectory blocks, excluding the current block. h=0/1/2/3 correspond to 3/6/9/12 latent frames.',
        'y_definition':'Mean clip-to-clip Subject Consistency on the 0-100 scale. No new uncertainty is estimated or plotted.',
        'base_scope':'Base reads 3 sink plus latest 9 trajectory frames including current 3, with 15-frame physical storage. It is a separate complete context, not h=4 and not an h=1-plus-sink-only intervention.',
        'averaging_controls':'assets/committing_correction_controls.pdf',
        'size_mm':[WIDTH_MM,HEIGHT_MM], 'minimum_font_pt':9,
        'no_new_generation_or_fitting_or_confidence_intervals':True,
        'exports':{ext:sha(FIG/(stem+'.'+ext)) for ext in ('pdf','svg')}}
    (FIG/(stem+'.provenance.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(FIG/(stem+'.png'))


if __name__ == '__main__':
    main()
