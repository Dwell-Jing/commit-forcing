#!/usr/bin/env python3
"""Replay fixed-position recency scores, paired contrasts, and log2-lag trends."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
COLS = ['Quality', 'Dynamic', 'Subject', 'Background', 'Subj_in', 'Subj_c2c',
        'Bg_c2c', 'Imaging', 'Aesthetic', 'MotionSm', 'Flicker']
TREND_COLS = ['Subj_c2c', 'Bg_c2c', 'Quality', 'Dynamic', 'Subj_in', 'MotionSm', 'Flicker']
LAGS = [1, 2, 4, 8, 16]


def load(path):
    rows = {}
    with path.open() as source:
        for row in csv.DictReader(source):
            arm, prompt = row['arm'], int(row['prompt'])
            target = rows.setdefault(arm, {})
            if prompt in target:
                raise ValueError(f'Duplicate prompt {prompt} for {arm}')
            values = {key: float(row[key]) for key in COLS}
            if not all(np.isfinite(value) for value in values.values()):
                raise ValueError(f'Non-finite score: {arm}, {prompt}')
            target[prompt] = values
    for arm, values in rows.items():
        if set(values) != set(range(100)):
            raise ValueError(f'{arm}: expected exactly prompts 0–99')
    return rows


def bootstrap(values, rng):
    draws = [values[rng.integers(0, len(values), len(values))].mean() for _ in range(4000)]
    return [float(x) for x in np.percentile(draws, [2.5, 97.5])]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=HERE / 'data/per_prompt.csv')
    parser.add_argument('--verify-contrasts', action='store_true')
    args = parser.parse_args()
    scores = load(args.csv)
    reported = json.loads((HERE / 'data/reported_contrasts.json').read_text())
    print('Arm means ×100; 100 prompts, generation seed 0, 60 seconds')
    print('arm'.ljust(12) + ' '.join(key.rjust(10) for key in COLS))
    for arm, prompts in scores.items():
        values = [100 * np.mean([row[key] for row in prompts.values()]) for key in COLS]
        print(arm.ljust(12) + ' '.join(f'{value:10.2f}' for value in values))

    # Original contrast and metric iteration order and bootstrap seed are retained.
    rng = np.random.default_rng(0)
    max_error = 0.0
    for name, comparison in reported.items():
        a, b = comparison['a'], comparison['b']
        if set(scores[a]) != set(scores[b]):
            raise ValueError(f'Unpaired prompt coverage: {a}, {b}')
        print(f'\n{name}: {a} − {b}')
        for key in COLS:
            delta = 100 * np.array([scores[a][p][key] - scores[b][p][key] for p in sorted(scores[a])])
            ci = bootstrap(delta, rng)
            mean = float(delta.mean())
            old = comparison[key]
            max_error = max(max_error, abs(mean - old['diff']), *[abs(x-y) for x, y in zip(ci, old['ci'])])
            if old['n'] != len(delta):
                raise ValueError(f'Reported sample count differs: {name}, {key}')
            sig = ci[0] > 0 or ci[1] < 0
            if args.verify_contrasts and sig != old['sig']:
                raise ValueError(f'Significance flag differs: {name}, {key}')
            print(f'  {key:12s} {mean:+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}]')
    if args.verify_contrasts:
        if max_error > 1e-9:
            raise ValueError(f'Reported contrast mismatch: maximum absolute difference {max_error:g}')
        print(f'\nAll 15 reported contrasts verified; maximum absolute difference {max_error:.3g}.')

    rng = np.random.default_rng(20261017)
    x = np.log2(LAGS)
    x -= x.mean()
    for model, prefix in [('SGF', 'AGE_d'), ('LongLive', 'LLA_d')]:
        print(f'\n{model}: score points per doubling of target lag (sink excluded)')
        for key in TREND_COLS:
            values = np.array([[scores[f'{prefix}{d}'][p][key] for d in LAGS] for p in range(100)])
            slopes = (values - values.mean(1, keepdims=True)) @ x / (x @ x)
            ci = bootstrap(slopes, rng)
            print(f'  {key:12s} {100*slopes.mean():+.3f} [{100*ci[0]:+.3f}, {100*ci[1]:+.3f}]')


if __name__ == '__main__':
    main()
