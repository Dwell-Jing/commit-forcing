#!/usr/bin/env python3
"""Paired committing effects on 200 rollf200 prompts at 60 seconds.

LongLive uses six latent frames during committing. Other rows retain their
reported configurations. Public CSV scores and ordered specs reproduce the
paired means and 4000-draw prompt-bootstrap intervals used by the paper.
The frozen data record checks numerical identity before plotting.
Run --check-only to validate values without importing Matplotlib.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / 'assets/source/commit_effects_data.json'
DATA = json.loads(DATA_PATH.read_text())
CONFIGURATIONS = tuple((row['label'],) for row in DATA['rows'])


def read_records():
    rows = list(csv.DictReader((ROOT / DATA['csv']).open()))
    scores = {}
    for row in rows:
        key = (int(row['seed']), row['label'], int(row['prompt']))
        if key in scores:
            raise ValueError(f'Duplicate scored key: {key}')
        scores[key] = {column: float(row[column]) for column, _ in DATA['metric_order'] if row.get(column, '') != ''}
    by_spec = {}
    for path in sorted({seed['spec'] for row in DATA['rows'] for seed in row['seeds']}):
        spec = json.loads((ROOT / path).read_text())
        if (ROOT / path).parent.joinpath(spec['scores']).resolve() != (ROOT / DATA['csv']).resolve():
            raise ValueError(f'Spec uses a different CSV: {path}')
        rng = np.random.default_rng(DATA['bootstrap_seed'])
        effects = {}
        for contrast in spec['contrasts']:
            a, b = contrast[2:4]
            keys_a = {prompt for seed, label, prompt in scores if seed == spec['seed'] and label == a}
            keys_b = {prompt for seed, label, prompt in scores if seed == spec['seed'] and label == b}
            if keys_a != set(range(DATA['num_prompts'])) or keys_b != keys_a:
                raise ValueError(f'Incomplete paired prompt coverage: {path}, {a}, {b}')
            record = {'a': a, 'b': b}
            for column, metric in DATA['metric_order']:
                d = 100 * np.array([scores[(spec['seed'], a, p)][column] - scores[(spec['seed'], b, p)][column]
                                    for p in sorted(keys_a)])
                indices = rng.integers(0, len(d), size=(DATA['bootstrap_draws'], len(d)))
                boot = d[indices].mean(axis=1)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                record[metric] = {'diff': float(d.mean()), 'ci': [float(lo), float(hi)],
                                  'n': len(d), 'sig': bool(lo > 0 or hi < 0)}
            effects[(a, b)] = record
        by_spec[path] = effects
    records = []
    for row in DATA['rows']:
        pair = []
        for seed in row['seeds']:
            actual = by_spec[seed['spec']][(seed['a'], seed['b'])]
            for metric, frozen in seed['reported'].items():
                values = actual[metric]
                if abs(values['diff'] - frozen['diff']) > 1e-10 or np.max(np.abs(np.array(values['ci']) - frozen['ci'])) > 1e-10:
                    raise ValueError(f'Replay differs from reported result: {row["label"]}, seed {seed["generation_seed"]}, {metric}: {values}, {frozen}')
                if values['n'] != frozen['n'] or values['sig'] != frozen['sig']:
                    raise ValueError('Pair count or significance mismatch')
            pair.append(actual)
        records.append(tuple(pair))
    return records


def write_provenance(records):
    sources = [DATA['csv'], str(DATA_PATH.relative_to(ROOT)),
               str(Path(__file__).resolve().relative_to(ROOT)), 'assets/source/commit_effects_style.py'] + sorted(
                   {s['spec'] for r in DATA['rows'] for s in r['seeds']})
    scientific = {
        'artifact': 'commit_effects', 'source': str(Path(__file__).resolve().relative_to(ROOT)),
        'protocol': {'prompt_set': 'rollf200', 'num_prompts': 200, 'duration_seconds': 60,
                     'generation_seeds': [0, 1], 'bootstrap_draws': 4000, 'bootstrap_seed': 0,
                     'resampling_unit': 'prompt', 'units': 'score points on the 0–100 presentation scale'},
        'longlive': {'committing_reads': '3 recent + 3 current latent frames', 'frame_count': 6,
                     'physical_cache_frames': 15, 'denoising_reads': 12},
        'metric_definitions': {'Quality': 'VBench-Long custom-input seven-component Quality',
                               'Subj_c2c': 'Clip-to-clip Subject Consistency, distinct from fused Subject'},
        'interval_replay': 'NumPy default_rng(0), public spec contrast order and metric order, 4000 paired prompt draws',
        'rows': [{'label': row['label'], 'generation_seeds': [
            {'seed': s['generation_seed'], 'a': s['a'], 'b': s['b'],
             'Quality': pair[i]['Quality'], 'Subj_c2c': pair[i]['Subj_c2c']}
            for i, s in enumerate(row['seeds'])]} for row, pair in zip(DATA['rows'], records)],
        'source_evidence': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in sources]
    }
    (ROOT / 'assets/commit_effects.provenance.json').write_text(json.dumps(scientific, indent=2) + '\n')


def main():
    from commit_effects_style import apply_style, export, INK, GREEN, BLUE, RULE
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle

    apply_style()
    records = read_records()
    fig, axes = plt.subplots(1, 2, figsize=(6.65, 3.62), sharey=True)
    fig.subplots_adjust(left=.235, right=.988, bottom=.16, top=.84, wspace=.18)

    rows = np.arange(len(CONFIGURATIONS), dtype=float)
    seed_styles = ((GREEN, "o", -.145), (BLUE, "s", .145))
    panels = (("Quality", "(a) ΔQuality", (-.43, 1.55), (0, .5, 1, 1.5)),
              ("Subj_c2c", "(b) ΔSubject (clip-to-clip)", (-.3, 6.1), (0, 2, 4, 6)))

    for axis, (metric, title, limits, ticks) in zip(axes, panels):
        axis.set_title(title, loc="left", fontsize=10, pad=12)
        axis.set_xlim(*limits)
        axis.set_xticks(ticks)
        axis.set_ylim(len(rows) - .5, -.5)
        axis.set_xlabel("Score points", labelpad=7)
        axis.set_axisbelow(True)
        axis.grid(axis="x", color=RULE, linewidth=.5, alpha=.7)
        axis.axvline(0, color=INK, linestyle=(0, (3, 3)), linewidth=.9, zorder=1)
        axis.spines["left"].set_visible(False)
        axis.spines["bottom"].set_color(RULE)
        axis.tick_params(axis="y", length=0, pad=9)
        axis.tick_params(axis="x", length=3, pad=4)

        for seed, (color, marker, offset) in enumerate(seed_styles):
            effects = [pair[seed][metric] for pair in records]
            means = np.array([effect["diff"] for effect in effects])
            intervals = np.array([effect["ci"] for effect in effects])
            axis.errorbar(means, rows + offset,
                          xerr=np.vstack((means - intervals[:, 0],
                                          intervals[:, 1] - means)),
                          fmt=marker, color=color, markerfacecolor=color,
                          markeredgecolor="white", markeredgewidth=.5,
                          markersize=4.9, elinewidth=1.1, capsize=2.4,
                          capthick=1.0, linestyle="none", zorder=3)

    axes[0].set_yticks(rows, [row[0] for row in CONFIGURATIONS], fontsize=9.5)
    axes[1].tick_params(axis="y", labelleft=False)
    legend = [Line2D([], [], color=color, marker=marker, markersize=4.9,
                     linewidth=1.1, label=f"Generation seed {seed}")
              for seed, (color, marker, _) in enumerate(seed_styles)]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(.60, .99),
               ncol=2, columnspacing=1.8, handlelength=1.7, handletextpad=.6)
    # Preserve the requested print width when the shared exporter crops tightly
    # and adds its .045-inch padding. This transparent artist carries no data.
    padding = .045
    fig.add_artist(Rectangle((padding / 6.65, .5), 1 - 2 * padding / 6.65, .01,
                             transform=fig.transFigure, facecolor="none",
                             edgecolor="none", clip_on=False))
    export(fig, "commit_effects")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Replay numerical inputs without rendering')
    args = parser.parse_args()
    if args.check_only:
        records = read_records()
        print('All 28 paired means and intervals match the paper; 200 paired prompts per arm and seed.')
    else:
        main()
        write_provenance(read_records())
