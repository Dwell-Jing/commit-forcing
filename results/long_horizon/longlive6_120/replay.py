#!/usr/bin/env python3
"""Replay the original ordered 120-second paired statistics from per-video scores.

Reads the existing baseline CSV and this directory's additional scored arms.
No model inference or VBench scoring is performed. The complete contrast and
metric order is retained so the paired-bootstrap intervals can be reproduced.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent


def load_scores(paths, columns):
    scores = {}
    for path in paths:
        with path.open() as source:
            for row in csv.DictReader(source):
                key = (row['label'], int(row['seed']), int(row['prompt']))
                if key in scores:
                    raise ValueError(f'Duplicate scored key: {key}')
                values = {column: float(row[column]) for column in columns}
                if not np.all(np.isfinite(list(values.values()))):
                    raise ValueError(f'Nonfinite scores: {key}')
                scores[key] = values
    return scores


def replay():
    spec = json.loads((ROOT / 'spec.json').read_text())
    reported = json.loads((ROOT / spec['reported']).read_text())
    columns = [column for column, _ in spec['metric_order']]
    scores = load_scores([ROOT / spec['baseline_scores'], ROOT / spec['scores']], columns)
    expected_prompts = set(range(spec['num_prompts']))
    for label in spec['labels']:
        actual_prompts = {prompt for arm, seed, prompt in scores if arm == label and seed == spec['seed']}
        if actual_prompts != expected_prompts:
            raise ValueError(f'Incomplete prompt coverage: {label}')
    frozen = list(reported.values())
    if len(frozen) != len(spec['contrasts']):
        raise ValueError('Reported contrast count differs from the ordered protocol')
    original_names = {value: key for key, value in spec['source_label_map'].items()}
    rng = np.random.default_rng(spec['bootstrap_seed'])
    output = {}
    worst_error = 0.0
    for index, (section, name, a, b) in enumerate(spec['contrasts']):
        source = frozen[index]
        if (source['a'], source['b']) != (original_names[a], original_names[b]):
            raise ValueError('The original bootstrap contrast order has changed')
        record = {'a': a, 'b': b}
        for column, metric in spec['metric_order']:
            delta = 100.0 * np.array([scores[(a, spec['seed'], prompt)][column] -
                                      scores[(b, spec['seed'], prompt)][column]
                                      for prompt in sorted(expected_prompts)])
            draws = rng.integers(0, len(delta), size=(spec['bootstrap_draws'], len(delta)))
            boot = delta[draws].mean(axis=1)
            lo, hi = np.percentile(boot, [2.5, 97.5])
            result = {'diff': float(delta.mean()), 'ci': [float(lo), float(hi)],
                      'n': len(delta), 'sig': bool(lo > 0 or hi < 0)}
            expected = source[metric]
            error = max(abs(result['diff'] - expected['diff']),
                        float(np.max(np.abs(np.array(result['ci']) - expected['ci']))))
            worst_error = max(worst_error, error)
            if error > 1e-10 or result['n'] != expected['n'] or result['sig'] != expected['sig']:
                raise ValueError(f'Paired result differs from the source: {a} minus {b}, {metric}')
            record[metric] = result
        output[f'[{section}] {name}'] = record
    return output, worst_error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', help='Optionally write the replayed complete paired statistics')
    args = parser.parse_args()
    output, error = replay()
    print(f'PASS: {len(output)} contrasts × 11 metrics reproduce the complete source readout; '
          f'maximum mean/interval error {error:.3g}.')
    for title, record in output.items():
        if record['a'] != 'longlive+commit6':
            continue
        print(title)
        for metric in ('Quality', 'Subj_c2c', 'Dynamic'):
            value = record[metric]
            print(f"  {metric}: {value['diff']:+.5f} "
                  f"[{value['ci'][0]:+.5f}, {value['ci'][1]:+.5f}], n={value['n']}")
    if args.json:
        Path(args.json).write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
