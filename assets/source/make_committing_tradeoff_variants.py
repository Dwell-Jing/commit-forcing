#!/usr/bin/env python3
"""All 27 reported LongLive committing variants, at their original coordinates.

The reference line is fixed by two 200-prompt endpoints, not fitted to the
100-prompt variant means. Reported G intervals are preserved, not reconstructed
from rounded means. The renderer uses the released aggregate record only; set FIGURE_OUTPUT_DIR
to render into another directory.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from paper_style import apply_style, ROOT, INK, MUTED, RULE, ACCENT
import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator
import numpy as np

SOURCE = ROOT / 'analysis/committing_variants/summary.json'
FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
PRE = FIG
STEM = 'committing_tradeoff_variants'
WIDTH_MM, HEIGHT_MM = 168, 84
ENDPOINTS = {'six-frame': (0., 0.), 'self-only': (3.63, -1.)}
SLOPE = ENDPOINTS['self-only'][1] / ENDPOINTS['self-only'][0]
GROUPS = {
    'Scaling / attention': {'marker':'o', 'color':INK,
                            'codes':['U','T15','T2','T3','T4']},
    'Selection / noise': {'marker':'^', 'color':INK,
                          'codes':['M','Mr','KR','SF0','SF2','ALT2','ALT3','CN30','CN100']},
    'Alignment / averaging': {'marker':'s', 'color':INK,
                              'codes':['P','AL','AL2','ALr','ALL','ALLr','CM16','CM64','CG','SG16']},
    'Sink corrections': {'marker':'D', 'color':ACCENT,
                         'codes':['FR','FP16','SFP16']},
}
# Typographic offsets move labels only. No observed coordinate is displaced.
LABELS = {'FR':(7,5), 'FP16':(7,5), 'SFP16':(7,-14),
          'P':(-19,-12), 'CN30':(6,-14), 'T2':(7,8)}
EXPECTED_BELOW = {'P','CN30','FR','FP16','SFP16'}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_data():
    summary = json.loads(SOURCE.read_text())
    reference = summary['reference_line']
    assert reference['recent_context_endpoint'] == [0.0, 0.0]
    assert reference['self_only_endpoint'] == [3.63, -1.0]
    assert not reference['line_is_fit_to_discovery_points']
    groups = {code:name for name,spec in GROUPS.items() for code in spec['codes']}
    rows = []
    for variant in summary['discovery_variants']:
        code = variant['id']
        metrics = variant['metrics']
        interval = metrics['G']['interval_95']
        rows.append({'code':code, 'visual_family':groups[code],
                     'x':metrics['Dynamic Degree']['delta'],
                     'y':metrics['Subject c2c']['delta'],
                     'G_reported':{'mean':metrics['G']['delta'],'interval':interval},
                     'G_interval_excludes_zero':interval[0]>0 or interval[1]<0})
    assert len(rows) == 27 and {r['code'] for r in rows} == set(groups)
    assert {r['code'] for r in rows if r['G_interval_excludes_zero']} == EXPECTED_BELOW
    assert all(r['G_reported']['interval'][1] < 0 for r in rows if r['G_interval_excludes_zero'])
    assert sum(not r['G_interval_excludes_zero'] for r in rows) == 22
    return rows, reference


def draw(rows):
    apply_style()
    fig, ax = plt.subplots(figsize=(WIDTH_MM/25.4,HEIGHT_MM/25.4))
    fig.subplots_adjust(left=.105,right=.985,bottom=.18,top=.96)
    ax.set_xlim(-6.6,4.6);ax.set_ylim(-2.5,2.0)
    ax.xaxis.set_major_locator(FixedLocator([-6,-4,-2,0,2,4]))
    ax.yaxis.set_major_locator(FixedLocator([-2,-1,0,1,2]))
    ax.tick_params(labelsize=9,pad=3,length=3)
    ax.spines['left'].set_color(MUTED);ax.spines['bottom'].set_color(MUTED)
    ax.set_xlabel('Δ Dynamic Degree',fontsize=10,labelpad=6)
    ax.set_ylabel('Δ Subject c2c',fontsize=10,labelpad=6)
    ax.axhline(0,color=RULE,linewidth=.7,zorder=0)
    ax.axvline(0,color=RULE,linewidth=.7,zorder=0)
    xx=np.array(ax.get_xlim())
    reference,=ax.plot(xx,SLOPE*xx,color=MUTED,linewidth=1.1,
                      linestyle=(0,(4,3)),zorder=1)
    reference.set_gid('endpoint-reference-not-fit')
    ax.text(-5.9,SLOPE*(-5.9)+.16,'Endpoint reference',fontsize=8.8,color=MUTED,
            ha='left',va='bottom').set_gid('reference-label')
    observed_offsets = []
    for p in rows:
        spec=GROUPS[p['visual_family']]
        filled=p['G_interval_excludes_zero']
        size=43 if p['visual_family']=='Sink corrections' else 33
        artist=ax.scatter(p['x'],p['y'],s=size,marker=spec['marker'],
                          edgecolors=spec['color'],facecolors=spec['color'] if filled else 'none',
                          linewidths=1.,zorder=4 if filled else 3)
        artist.set_gid(f'variant-{p["code"]}')
        actual=artist.get_offsets().tolist()
        assert actual==[[p['x'],p['y']]]
        observed_offsets.append({'code':p['code'],'offset':actual[0],
                                 'marker':spec['marker'],'edgecolor':spec['color'],
                                 'filled':filled,'size_points_squared':size})
        if p['code'] in LABELS:
            dx,dy=LABELS[p['code']]
            label=ax.annotate(p['code'],(p['x'],p['y']),xytext=(dx,dy),
                              textcoords='offset points',fontsize=9.2,color=spec['color'],
                              ha='left',va='bottom',annotation_clip=False)
            label.set_gid(f'label-{p["code"]}')
    for name,(x,y) in ENDPOINTS.items():
        endpoint=ax.scatter(x,y,s=80,marker='+',color=INK,linewidths=1.7,zorder=6)
        endpoint.set_gid(f'endpoint-{name}-200-prompts')
        dx,dy,ha=(-9,24,'right') if name=='six-frame' else (-6,-21,'right')
        label=ax.annotate('Commit Forcing' if name=='six-frame' else 'Self-only',
                          (x,y),xytext=(dx,dy),textcoords='offset points',
                          fontsize=9.2,ha=ha,va='bottom',color=INK,
                          arrowprops={'arrowstyle':'-','color':MUTED,'linewidth':.55,
                                      'shrinkA':2,'shrinkB':4})
        label.set_gid(f'label-endpoint-{name}')
    handles=[Line2D([],[],marker=spec['marker'],color=spec['color'],linestyle='none',
                    markerfacecolor=spec['color'] if name=='Sink corrections' else 'none',
                    markeredgewidth=1,markersize=5.3,label=name)
             for name,spec in GROUPS.items()]
    ax.legend(handles=handles,loc='upper right',fontsize=8.7,labelspacing=.55,
              handletextpad=.6,borderaxespad=.4)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    labels=[a for a in ax.texts if a.get_gid()]
    for i,left in enumerate(labels):
        for right in labels[i+1:]:
            assert not left.get_window_extent(renderer).overlaps(right.get_window_extent(renderer)),(left.get_gid(),right.get_gid())
    return fig, observed_offsets


def main():
    rows, reference = load_data()
    fig, plotted = draw(rows)
    FIG.mkdir(parents=True,exist_ok=True)
    try:
        fig.savefig(FIG/f'{STEM}.pdf',format='pdf',metadata={
            'Title':'LongLive committing variants','CreationDate':None,'ModDate':None})
        fig.savefig(FIG/f'{STEM}.svg',format='svg',metadata={
            'Title':'LongLive committing variants','Date':None})
        subprocess.run(['pdftoppm','-singlefile','-png','-scale-to','2200',
                        str(FIG/f'{STEM}.pdf'),str(FIG/STEM)],check=True)
    finally:
        plt.close(fig)
    provenance = {
        'artifact':STEM,'source':'assets/source/make_committing_tradeoff_variants.py',
        'source_sha256':sha(Path(__file__).resolve()),
        'aggregate_source':SOURCE.relative_to(ROOT).as_posix(),
        'aggregate_source_sha256':sha(SOURCE),
        'source_overleaf_commit':json.loads(SOURCE.read_text())['overleaf_source_commit'],
        'physical_size_mm':[WIDTH_MM,HEIGHT_MM],
        'axes':{'x':'Delta Dynamic Degree','y':'Delta Subject c2c',
                'units':'points on 0-100 scales, relative to six-frame committing'},
        'reference':reference,'scatter_offsets':plotted,
        'reported_G_intervals_include_zero':22,
        'reported_G_intervals_below_zero':sorted(EXPECTED_BELOW),
        'encoding':{'open_symbols':'Reported G interval includes zero',
                    'filled_symbols':'Reported G interval excludes zero; all five below zero',
                    'clay':'Sink-derived corrections FR, FP16 and SFP16',
                    'shapes':'Intervention families; not pooled statistical groups'},
        'scope':'All 27 discovery means are shown at reported coordinates. The dashed endpoint reference is not a fit or a universal causal law. Confirmation-set sharpening and its costs are reported separately.',
        'exports':{ext:sha(FIG/f'{STEM}.{ext}') for ext in ['pdf','svg']}}
    (FIG/f'{STEM}.provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(FIG/f'{STEM}.png')


if __name__=='__main__':
    main()
