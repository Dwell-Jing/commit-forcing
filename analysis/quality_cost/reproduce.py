#!/usr/bin/env python3
"""Replay historical Quality contributions, costs and LongLive's four-repeat observations."""
import argparse
import csv
import io
import json
import hashlib
import math
import re
import statistics
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS = (
    ('SGF', 'SGF'), ('SGFP', 'SGF+'), ('RF', 'RF-TF'), ('CF', 'Context Forcing'),
    ('LL', 'LongLive'), ('RS', 'Rolling Sink'), ('IDFSF', 'IDF-SF'), ('IDFLL', 'IDF-LL'),
)
# VBench scripts/constant.py; score columns in full_scores.csv are already x100.
DIMENSIONS = (
    ('subject_consistency', 'Subject', .1462, 1., 1.),
    ('background_consistency', 'Background', .2615, 1., 1.),
    ('temporal_flickering', 'Flicker', .6293, 1., 1.),
    ('motion_smoothness', 'MotionSm', .706, .9975, 1.),
    ('dynamic_degree', 'Dynamic', 0., 1., .5),
    ('aesthetic_quality', 'Aesthetic', 0., 1., 1.),
    ('imaging_quality', 'Imaging', 0., 1., 1.),
)


def require(value, message):
    if not value:
        raise ValueError(message)


def number(value):
    result = float(value)
    require(math.isfinite(result), 'Non-finite input')
    return result


def read_csv(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def indexed(rows, fields):
    result = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        require(key not in result, f'Duplicate row: {key}')
        result[key] = row
    return result


def close(actual, expected, label):
    require(abs(actual - expected) < 1e-8, f'Mismatch in {label}: {actual} vs {expected}')


def quality_rows(suite):
    scores = indexed(read_csv(suite / 'full_scores.csv'), ('model', 'arm'))
    aggregate = indexed(read_csv(suite / 'aggregate_paired_ci.csv'), ('model', 'metric'))
    components = indexed(read_csv(suite / 'component_paired_ci.csv'), ('model', 'metric'))
    expected = {(model, model + suffix) for model, _ in MODELS for suffix in ('_N', '_W')}
    require(set(scores) == expected, 'Expected eight complete Base / +CF pairs')
    wide, long = [], []
    for model, label in MODELS:
        base, cf = scores[model, model + '_N'], scores[model, model + '_W']
        dq = number(cf['quality']) - number(base['quality'])
        aq = aggregate[model, 'quality']
        close(dq, number(aq['delta']), model + ' aggregate Quality')
        row = dict(model=model, label=label, base_quality=number(base['quality']),
                   cf_quality=number(cf['quality']), delta_quality=dq,
                   ci95_low=number(aq['ci95_low']), ci95_high=number(aq['ci95_high']))
        contributions = []
        for metric, _, low, high, weight in DIMENSIONS:
            raw_delta = number(cf[metric]) - number(base[metric])
            contribution = weight * raw_delta / (high - low) / 6.5
            component = components[model, metric]
            close(raw_delta, number(component['delta']), model + ' ' + metric)
            row[metric] = contribution
            contributions.append(contribution)
            long.append(dict(model=model, label=label, metric=metric,
                             base_score=number(base[metric]), cf_score=number(cf[metric]),
                             raw_delta=raw_delta, raw_ci95_low=number(component['ci95_low']),
                             raw_ci95_high=number(component['ci95_high']),
                             normalization_low=low, normalization_high=high,
                             quality_weight=weight, quality_contribution=contribution))
        close(sum(contributions), dq, model + ' seven-term sum')
        dt = number(cf['total']) - number(base['total'])
        ds = number(cf['semantic']) - number(base['semantic'])
        close(dt, .8 * dq + .2 * ds, model + ' Total decomposition')
        wide.append(row)
    # Keep the original report tied to its original 12-frame LongLive control.
    report = (HERE / 'data/QUALITY_DECOMP_report.md').read_text()
    report_labels = {'Context Forcing': 'CF'}
    report_rows = {parts[0]: parts for parts in markdown_rows(report) if len(parts) == 9}
    for row in wide:
        parts = report_rows[report_labels.get(row['label'], row['label'])]
        if row['model'] == 'LL':
            with zipfile.ZipFile(suite / 'ablation12/original_package.zip') as archive:
                old = indexed(list(csv.DictReader(io.StringIO(archive.read('full_scores.csv').decode()))),
                              ('model', 'arm'))
            old_base, old_cf = old['LL', 'LL_N'], old['LL', 'LL_W']
            values = [number(old_cf['quality']) - number(old_base['quality'])]
            values += [weight * (number(old_cf[metric]) - number(old_base[metric])) / (high - low) / 6.5
                       for metric, _, low, high, weight in DIMENSIONS]
            source = json.loads((suite / 'longlive6_source_results.json').read_text())
            new_case = source['comparisons']['W6S_vs_N']
            new_base, new_cf = scores['LL', 'LL_N'], scores['LL', 'LL_W']
            close(row['delta_quality'], new_case['aggregate_delta']['quality']['delta'],
                  'LongLive 6-frame source Quality')
            for metric, *_ in DIMENSIONS:
                component = new_case['component_delta_percent'][metric]
                close(number(new_cf[metric]) - number(new_base[metric]), component['delta'],
                      'LongLive 6-frame source ' + metric)
        else:
            values = [row['delta_quality']] + [row[metric] for metric, *_ in DIMENSIONS]
        for value, cell in zip(values, parts[1:]):
            published = re.match(r'[+-]?\d+\.\d+', cell)
            require(published is not None, 'Malformed archived Quality cell')
            close(float(f'{value:.2f}'), float(published.group()), 'archived Quality report')
    return wide, long


def markdown_rows(text):
    for line in text.splitlines():
        if line.startswith('|'):
            yield [cell.strip() for cell in line.strip().strip('|').split('|')]


def cost_rows():
    rows = []
    labels = {label: model for model, label in MODELS}
    labels['CF'] = 'CF'
    for parts in markdown_rows((HERE / 'data/COST_report.md').read_text()):
        if parts[0] not in labels:
            continue
        require(len(parts) == 8, 'Malformed cost report row')
        model = labels[parts[0]]
        row = dict(model=model, label=dict(MODELS)[model],
                   wall_base_s=parts[1], wall_cf_s=parts[2], reported_wall_ratio=parts[3],
                   device_peak_base_gib=parts[4], device_peak_cf_gib=parts[5],
                   torch_peak_alloc_base_gib='', torch_peak_alloc_cf_gib='',
                   clean_calls_base='', clean_calls_cf='', denoise_calls_base='', denoise_calls_cf='')
        for field in ('wall_base_s', 'wall_cf_s', 'reported_wall_ratio',
                      'device_peak_base_gib', 'device_peak_cf_gib'):
            require(number(row[field]) > 0, 'Invalid cost measurement')
        if parts[6] != '—':
            alloc = parts[6].split(' / ')
            require(len(alloc) == 2, 'Malformed allocated-memory pair')
            row['torch_peak_alloc_base_gib'], row['torch_peak_alloc_cf_gib'] = alloc
        if parts[7] != '—':
            calls = [int(value) for value in re.findall(r'\d+', parts[7])]
            require(len(calls) == 4, 'Malformed forward-call pair')
            row['clean_calls_base'], row['denoise_calls_base'], row['clean_calls_cf'], row['denoise_calls_cf'] = calls
        rows.append(row)
    require(len(rows) == 8 and {r['model'] for r in rows} == {m for m, _ in MODELS},
            'Incomplete cost report')
    # The source report above describes the previous committing-12 LongLive arm.
    # Override only that row with the four-repeat committing-6 JSON observations.
    repeats = longlive6_cost_repeats()
    native = [row for row in repeats if row['arm'] == 'LL_native']
    cf = [row for row in repeats if row['arm'] == 'LL_w6']
    base_mean = statistics.mean(row['wall_s'] for row in native)
    cf_mean = statistics.mean(row['wall_s'] for row in cf)
    ll = next(row for row in rows if row['model'] == 'LL')
    ll.update(wall_base_s=f'{base_mean:.1f}', wall_cf_s=f'{cf_mean:.1f}',
              reported_wall_ratio=f'{cf_mean / base_mean:.3f}',
              device_peak_base_gib=f"{statistics.mean(row['device_peak_gib'] for row in native):.1f}",
              device_peak_cf_gib=f"{statistics.mean(row['device_peak_gib'] for row in cf):.1f}",
              torch_peak_alloc_base_gib=f"{statistics.mean(row['torch_peak_alloc_gib'] for row in native):.1f}",
              torch_peak_alloc_cf_gib=f"{statistics.mean(row['torch_peak_alloc_gib'] for row in cf):.1f}",
              clean_calls_base=80, clean_calls_cf=80, denoise_calls_base=320, denoise_calls_cf=320)
    return rows


def longlive6_cost_repeats():
    source_dir = HERE / 'data' / 'longlive6_cost'
    metadata = json.loads((source_dir / 'retrieval.json').read_text())
    require(metadata['snapshot_id'] == 'second-completed-run' and metadata['stable_stat_check']
            and metadata['completion_marker_after_outputs'], 'Incomplete cost retrieval snapshot')
    retrieved = {entry['name']: entry for entry in metadata['files']}
    require(len(retrieved) == 25, 'Expected 8 timers, 8 memory logs, 8 stop records and completion marker')
    completion_time = retrieved['ALL_DONE']['mtime_ns']
    rows = []
    for arm, rule in (('LL_native', 'native'), ('LL_w6', 'cf-w6s')):
        for repeat in range(4):
            path = HERE / 'data' / 'longlive6_cost' / f'{arm}_r{repeat}.json'
            record = json.loads(path.read_text())
            require(record['model'] == 'LL' and record['rule'] == rule and record['repeat'] == repeat
                    and record['snapshot_id'] == 'second-completed-run',
                    'Unexpected LongLive cost identity')
            require(len(record['videos']) == 2 and record['videos'][0]['idx'] == 0 and record['videos'][1]['idx'] == 1,
                    'Expected warm-up prompt 0 and measured prompt 1')
            timer_meta = retrieved[path.name]
            require(record['original_source_sha256'] == timer_meta['sha256'],
                    'Timer original hash differs from stable retrieval metadata')
            memory_path = path.with_suffix('.mem')
            memory_bytes = memory_path.read_bytes()
            memory_meta = retrieved[memory_path.name]
            require(hashlib.sha256(memory_bytes).hexdigest() == memory_meta['sha256'],
                    'Memory log differs from stable retrieval metadata')
            require(timer_meta['mtime_ns'] <= completion_time and memory_meta['mtime_ns'] <= completion_time
                    and retrieved[path.with_suffix('.stop').name]['mtime_ns'] <= completion_time,
                    'Cost output postdates completion record')
            samples = [int(value) for value in memory_bytes.decode().splitlines() if value.strip()]
            require(samples and min(samples) > 0, 'Missing or invalid device-memory observations')
            device_peak = max(samples) / 1024
            measured = record['videos'][1]
            counts = measured['counters']
            require(counts['kv_cache_frames'] == 12 and counts['clean_model_calls'] == 80
                    and counts['denoise_model_calls'] == 320 and counts['blocks'] == 80,
                    'Unexpected LongLive cost cache or forward count')
            require(counts['sinkless_attention_calls'] == (0 if arm == 'LL_native' else 2400),
                    'Unexpected committing activation count')
            rows.append(dict(arm=arm, repeat=repeat, measured_prompt=1,
                             wall_s=number(measured['wall_s']),
                             torch_peak_alloc_gib=number(measured['peak_alloc_gib']),
                             torch_peak_reserved_gib=number(measured['peak_reserved_gib']),
                             device_peak_gib=device_peak,
                             physical_cache_frames=counts['kv_cache_frames'],
                             clean_calls=counts['clean_model_calls'], denoising_calls=counts['denoise_model_calls']))
    summary = json.loads((source_dir / 'summary.json').read_text())
    for arm in ('LL_native', 'LL_w6'):
        repeated = [row for row in rows if row['arm'] == arm]
        for field, summary_field in (('wall_s', 'mean_wall_s'), ('device_peak_gib', 'mean_device_peak_gib'),
                                    ('torch_peak_alloc_gib', 'mean_torch_peak_allocated_gib')):
            close(statistics.mean(row[field] for row in repeated), number(summary[arm][summary_field]),
                  arm + ' cost summary ' + field)
    base_mean = statistics.mean(row['wall_s'] for row in rows if row['arm'] == 'LL_native')
    cf_mean = statistics.mean(row['wall_s'] for row in rows if row['arm'] == 'LL_w6')
    close(cf_mean / base_mean, number(summary['wall_ratio']), 'LongLive cost ratio')
    return rows


def csv_text(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def verify_sources(suite):
    provenance = json.loads((HERE / 'provenance.json').read_text())
    for record in provenance['source_files']:
        path = suite / record['name'] if record['kind'] == 'public_suite' else HERE / record['name']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == record['sha256'], f'Source hash mismatch: {record["name"]}')


def display(quality, costs):
    print('| Model | Δ Quality | Subject | Background | Flicker | MotionSm | Dynamic | Aesthetic | Imaging |')
    print('|:---|' + '---:|' * 8)
    for row in quality:
        values = [row['delta_quality']] + [row[metric] for metric, *_ in DIMENSIONS]
        print('| ' + row['label'] + ' | ' + ' | '.join(f'{value:+.2f}' for value in values) + ' |')
    print('\n| Model | Wall Base (s) | Wall +CF (s) | Reported ratio | Device peak Base (GiB) | Device peak +CF (GiB) |')
    print('|:---|' + '---:|' * 5)
    for row in costs:
        fields = ('wall_base_s', 'wall_cf_s', 'reported_wall_ratio', 'device_peak_base_gib', 'device_peak_cf_gib')
        print('| ' + row['label'] + ' | ' + ' | '.join(row[field] or '—' for field in fields) + ' |')
    print('\nLongLive: four repeats of prompt 1, 6-frame committing, 12-frame physical cache; device peaks replayed from same-run memory logs.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, default=HERE.parents[1] / 'results/vbench_full/common946')
    parser.add_argument('--write', action='store_true', help='Regenerate the four derived CSV files')
    args = parser.parse_args()
    verify_sources(args.suite)
    quality, components = quality_rows(args.suite)
    costs = cost_rows()
    for name, rows in (('quality_decomposition.csv', quality), ('quality_components.csv', components),
                       ('cost_measurements.csv', costs), ('longlive6_cost_per_repeat.csv', longlive6_cost_repeats())):
        path = HERE / 'data' / name
        text = csv_text(rows)
        if args.write:
            path.write_text(text)
        else:
            require(path.read_text() == text, f'Derived CSV differs: {name}; inspect sources before rewriting')
    display(quality, costs)


if __name__ == '__main__':
    main()
