"""Shared print-size style and atomic exports for measured paper figures."""
from pathlib import Path
import os
import subprocess
from paper_palette import (INK, MUTED, RULE, BLUE, ACCENT, POSITIVE,
                           PLOT_PRIMARY, PLOT_SECONDARY, PLOT_CONTROL)

ROOT = Path(__file__).resolve().parents[2]
FIG = Path(os.environ.get('FIGURE_OUTPUT_DIR', ROOT / 'assets'))
PRE = FIG
os.environ.setdefault('MPLCONFIGDIR', str(Path(os.environ.get('TMPDIR', '/tmp')) / 'recent-context-mpl'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Compatibility name for archived plots and explicit positive-status badges.
GREEN = POSITIVE


def apply_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans'],
        'font.size': 9.5,
        'text.color': INK,
        'axes.labelcolor': INK,
        'axes.titlecolor': INK,
        'axes.titlesize': 10.5,
        'axes.titleweight': 'bold',
        'axes.labelsize': 9.5,
        'axes.linewidth': .8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'xtick.color': INK,
        'ytick.color': INK,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'xtick.major.width': .7,
        'ytick.major.width': .7,
        'legend.frameon': False,
        'legend.fontsize': 9,
        'grid.color': RULE,
        'grid.linewidth': .5,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
        'savefig.facecolor': 'white',
        'figure.facecolor': 'white',
        'mathtext.fontset': 'dejavusans',
    })


def export(fig, stem):
    """Retain SVG/PDF and one PNG preview from the same live-text figure."""
    FIG.mkdir(parents=True, exist_ok=True)
    PRE.mkdir(parents=True, exist_ok=True)
    candidates = []
    try:
        for fmt, folder in [('pdf', FIG), ('svg', FIG), ('png', PRE)]:
            temporary = folder / f'.{stem}.render.{fmt}'
            candidates.append((temporary, folder / f'{stem}.{fmt}'))
            metadata = ({'Title': stem.replace('_', ' '), 'CreationDate': None,
                         'ModDate': None} if fmt == 'pdf' else
                        {'Title': stem.replace('_', ' '), 'Date': None}
                        if fmt == 'svg' else None)
            fig.savefig(temporary, format=fmt, dpi=280, bbox_inches='tight',
                        pad_inches=.045, metadata=metadata)
        for temporary, target in candidates:
            temporary.replace(target)
    finally:
        for temporary, _ in candidates:
            temporary.unlink(missing_ok=True)
        plt.close(fig)
    subprocess.run(['pdftoppm', '-singlefile', '-png', '-scale-to', '2200', str(FIG / f'{stem}.pdf'), str(PRE / stem)], check=True)
    print(f'Created {stem}: PDF, editable SVG, actual-PDF PNG preview')
