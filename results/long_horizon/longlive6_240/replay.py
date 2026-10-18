#!/usr/bin/env python3
"""Replay the reported 240-second six-frame contrasts from frozen video scores."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent


def replay():
    spec = json.loads((ROOT / 'spec.json').read_text())
    reported = json.loads((ROOT / spec['reported']).read_text())
    scores = {}
    with (ROOT / spec['scores']).open() as stream:
        for row in csv.DictReader(stream):
            key = (row['arm'], int(row['seed']), int(row['prompt']))
            if key in scores:
                raise ValueError(f'Duplicate scored video: {key}')
            scores[key] = {column: float(row[column]) for column, _ in spec['metric_order']}
            if not np.all(np.isfinite(list(scores[key].values()))):
                raise ValueError(f'Nonfinite scores: {key}')
    prompts = list(range(spec['num_prompts']))
    seed = spec['generation_seed']
    for arm in spec['labels']:
        if {p for a, s, p in scores if a == arm and s == seed} != set(prompts):
            raise ValueError(f'Incomplete prompt coverage: {arm}')
    rng = np.random.default_rng(spec['bootstrap_seed'])
    shape = (spec['bootstrap_draws'], len(prompts))
    # The original larger report uses one RNG stream across all its contrasts.
    for _ in range(spec['prior_bootstrap_draw_calls']):
        rng.integers(0, len(prompts), size=shape)
    output, worst = {}, 0.0
    for title, source in reported.items():
        a, b = source['a'], source['b']
        record = {'a': a, 'b': b}
        for column, metric in spec['metric_order']:
            delta = 100 * np.array([scores[(a, seed, p)][column] - scores[(b, seed, p)][column]
                                    for p in prompts])
            draws = rng.integers(0, len(prompts), size=shape)
            lo, hi = np.percentile(delta[draws].mean(axis=1), [2.5, 97.5])
            value = {'diff': float(delta.mean()), 'ci': [float(lo), float(hi)],
                     'n': len(delta), 'sig': bool(lo > 0 or hi < 0)}
            frozen = source[metric]
            error = max(abs(value['diff'] - frozen['diff']),
                        float(np.max(np.abs(np.array(value['ci']) - frozen['ci']))))
            worst = max(worst, error)
            if error > 1e-10 or value['n'] != frozen['n'] or value['sig'] != frozen['sig']:
                raise ValueError(f'Result differs from the original report: {title}, {metric}')
            record[metric] = value
        output[title] = record
    return output, worst


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', help='Optionally save all replayed statistics')
    args = parser.parse_args()
    output, error = replay()
    print(f'PASS: {len(output)} contrasts x 11 metrics reproduce the reported estimates and intervals; '
          f'maximum error {error:.3g}.')
    for title, record in output.items():
        print(title)
        for metric in ('Quality', 'Subj_c2c', 'Dynamic'):
            x = record[metric]
            print(f"  {metric}: {x['diff']:+.5f} [{x['ci'][0]:+.5f}, {x['ci'][1]:+.5f}], n={x['n']}")
    if args.json:
        Path(args.json).write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
