#!/usr/bin/env python3
"""Print frozen window-control statistics; does not rerun inference or scoring."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data' / 'window_controls'


def effect(value):
    if 'diff' in value:
        delta, interval = value['diff'], value['ci']
    else:
        delta, interval = value['delta'], value['ci95']
    star = '*' if interval[0] > 0 or interval[1] < 0 else ''
    return f'{delta:+.5f}{star} [{interval[0]:+.5f}, {interval[1]:+.5f}]'


def main():
    for seconds in (120, 240):
        table = json.loads((DATA / f'longlive{seconds}_summary.json').read_text())
        print(f'LongLive, {seconds} seconds: self-only controls')
        for title, record in table.items():
            if 'self only' not in title:
                continue
            print(title)
            for key, value in record.items():
                if isinstance(value, dict):
                    print(f'  {key}: {effect(value)}, n={value["n"]}')
    table = json.loads((DATA / 'longlive946_summary.json').read_text())
    print('LongLive, standard suite: self-only minus six frames')
    record = table['comparisons']['W946_CS_vs_W946_W6S']
    for field in ('aggregate_delta', 'component_delta_percent'):
        for key, value in record[field].items():
            print(f'  {key}: {effect(value)}')
    print('Cross-model window sweep: all original contrasts')
    table = json.loads((DATA / 'cross_model_summary.json').read_text())
    for title, record in table.items():
        print(title)
        for key, value in record.items():
            if isinstance(value, dict):
                print(f'  {key}: {effect(value)}, n={value["n"]}')


if __name__ == '__main__':
    main()
