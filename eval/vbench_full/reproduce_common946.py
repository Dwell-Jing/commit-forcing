#!/usr/bin/env python3
"""Validate current six-generator scores, or replay historical prompt statistics."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

QUALITY = ('subject_consistency', 'background_consistency', 'temporal_flickering',
           'motion_smoothness', 'dynamic_degree', 'aesthetic_quality', 'imaging_quality')
SEMANTIC = ('object_class', 'multiple_objects', 'human_action', 'color', 'spatial_relationship',
            'scene', 'appearance_style', 'temporal_style', 'overall_consistency')
DIMS = QUALITY + SEMANTIC
NORMALIZE = {
    'subject_consistency': (.1462, 1), 'background_consistency': (.2615, 1),
    'temporal_flickering': (.6293, 1), 'motion_smoothness': (.706, .9975),
    'dynamic_degree': (0, 1), 'aesthetic_quality': (0, 1), 'imaging_quality': (0, 1),
    'object_class': (0, 1), 'multiple_objects': (0, 1), 'human_action': (0, 1),
    'color': (0, 1), 'spatial_relationship': (0, 1), 'scene': (0, .8222),
    'appearance_style': (.0009, .2855), 'temporal_style': (0, .364),
    'overall_consistency': (0, .364),
}
MODELS = ('SGF', 'RF', 'CF', 'SGFP', 'LL', 'RS', 'IDFSF', 'IDFLL')
CURRENT_MODELS = MODELS[:6]


def require(value, message):
    if not value:
        raise ValueError(message)


def read_csv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def composites(raw):
    low = np.array([NORMALIZE[d][0] for d in DIMS])
    high = np.array([NORMALIZE[d][1] for d in DIMS])
    z = (raw - low) / (high - low)
    w = np.array([.5 if d == 'dynamic_degree' else 1 for d in QUALITY])
    q = 100 * (z[..., :7] @ w) / 6.5
    semantic = 100 * z[..., 7:].mean(axis=-1)
    return dict(quality=q, semantic=semantic, total=(4 * q + semantic) / 5)


def verify_close(actual, expected, name):
    require(np.allclose(actual, expected, rtol=0, atol=1e-8), f'Published value mismatch: {name}')


def reproduce(data, models=None):
    selected = MODELS if models is None else tuple(models)
    require(bool(selected) and len(set(selected)) == len(selected) and set(selected) <= set(MODELS),
            'Select distinct published models')
    sampled_arms = {m+s for m in selected for s in ('_N', '_W')}
    manifest = json.loads((data/'data_manifest.json').read_text())
    for name, digest in manifest['sha256'].items():
        require(Path(name).name == name, 'Unexpected data path')
        require(hashlib.sha256((data/name).read_bytes()).hexdigest() == digest, f'Changed data: {name}')
    protocol = json.loads((data/'protocol.json').read_text())
    require(protocol['bootstrap']['repetitions'] == 4000 and protocol['bootstrap']['seed'] == 20261011,
            'Unexpected bootstrap configuration')
    records = read_csv(data/'prompt_clusters.csv')
    require(len(records) == 946 and {int(r['global_idx']) for r in records} == set(range(946)),
            'Missing or duplicate metadata identity')
    names = sorted({r['original_prompt'] for r in records})
    require(len(names) == 944, 'Unexpected prompt clusters')
    index = {p:i for i,p in enumerate(names)}
    idxmap = {int(r['global_idx']):index[r['original_prompt']] for r in records}
    expected = {d:{int(r['global_idx']) for r in records if d in r['dimensions'].split(';')} for d in DIMS}
    arms = {m+s for m in MODELS for s in ('_N','_W')}
    points = read_csv(data/'full_scores.csv')
    require(len(points) == 16 and {r['arm'] for r in points} == arms, 'Unexpected arm coverage')
    points = {r['arm']:r for r in points}
    contribution = json.loads((data/'official_prompt_contributions.json').read_text())
    num = {a:np.zeros((944,16)) for a in arms}
    den = {a:np.zeros((944,16)) for a in arms}
    seen = set()
    coverage = {(a,d):set() for a in arms for d in DIMS}
    for row in contribution:
        a,d,i = row['arm'],row['dimension'],row['global_idx']
        key = a,d,i,row['sample_idx']
        require(a in arms and d in DIMS and i in expected[d] and row['sample_idx'] == 0,
                'Unexpected contribution identity')
        require(key not in seen, 'Duplicate prompt contribution')
        seen.add(key)
        require(np.isfinite(row['numerator']) and np.isfinite(row['denominator']) and row['denominator'] >= 0,
                'Invalid contribution')
        coverage[a,d].add(i)
        k,j = DIMS.index(d),idxmap[i]
        num[a][j,k] += row['numerator']
        den[a][j,k] += row['denominator']
    cells = read_csv(data/'coverage.csv')
    require(len(cells) == 256 and len({(r['arm'],r['dimension']) for r in cells}) == 256,
            'Incomplete coverage ledger')
    for cell in cells:
        a,d = cell['arm'],cell['dimension']
        require((a,d) in coverage and int(cell['input_prompts']) == len(expected[d]),
                'Unexpected coverage cell')
        actual = coverage[a,d]
        require(len(actual) == int(cell['scored_prompts']), 'Surviving-prompt count differs')
        if d in ('temporal_flickering','color'):
            require(bool(actual) and actual <= expected[d], 'Invalid official survivor set')
        else:
            require(actual == expected[d], 'Incomplete dimension coverage')
        require(den[a][:,DIMS.index(d)].sum() == int(cell['official_denominator']),
                'Official surviving-record denominator differs')
    weights = np.random.default_rng(20261011).multinomial(944, np.full(944,1/944),size=4000).astype(np.float64)
    estimates, boot = {}, {}
    for a in sorted(arms):
        require(np.all(den[a].sum(0) > 0), 'Zero official denominator')
        raw = num[a].sum(0)/den[a].sum(0)
        verify_close(raw*100, [float(points[a][d]) for d in DIMS], a+' components')
        estimates[a] = dict(components=raw*100, **composites(raw))
        for m in ('quality','semantic','total'):
            verify_close(estimates[a][m], float(points[a][m]), a+' '+m)
        if a in sampled_arms:
            with np.errstate(divide='ignore', invalid='ignore'):
                sampled = (weights @ num[a])/(weights @ den[a])
            boot[a] = dict(components=sampled*100, **composites(sampled))
    published_rows = [r for name in ('aggregate_paired_ci.csv', 'component_paired_ci.csv')
                      for r in read_csv(data/name)]
    published = {(r['model'], r['metric']): r for r in published_rows}
    expected_contrasts = {(m, metric) for m in MODELS for metric in ('quality', 'semantic', 'total')+DIMS}
    require(len(published_rows) == 152 and set(published) == expected_contrasts,
            'Missing or duplicate contrast rows')
    for m in MODELS:
        a,b = m+'_N',m+'_W'
        for metric in ('quality','semantic','total')+DIMS:
            if metric in DIMS:
                k = DIMS.index(metric)
                point = estimates[b]['components'][k]-estimates[a]['components'][k]
            else:
                point = estimates[b][metric]-estimates[a][metric]
            p = published[m,metric]
            verify_close(point, float(p['delta']), m+' '+metric+' delta')
            if m not in selected:
                continue
            if metric in DIMS:
                values = boot[b]['components'][:,k]-boot[a]['components'][:,k]
            else:
                values = boot[b][metric]-boot[a][metric]
            valid = values[np.isfinite(values)]
            require(len(valid) >= 3960, 'Too many ineligible bootstrap draws')
            verify_close(np.percentile(valid,[2.5,97.5]), [float(p['ci95_low']),float(p['ci95_high'])],
                         m+' '+metric+' interval')
            require(len(valid) == int(p['valid_draws']), 'Valid-draw count differs')
        if m in selected:
            print(f"{m:6s} Quality {estimates[a]['quality']:.4f} → {estimates[b]['quality']:.4f}; published contrasts verified")
    print(f'Verified all 16 arms, 16 dimensions, coverage and 152 paired point estimates; '
          f'{3*len(selected)} aggregate and {16*len(selected)} component intervals checked with 4,000 paired draws.')


def reproduce_current(data, models=None):
    """Validate frozen aggregate sources without claiming a new bootstrap replay."""
    selected = CURRENT_MODELS if models is None else tuple(models)
    require(bool(selected) and len(set(selected)) == len(selected)
            and set(selected) <= set(CURRENT_MODELS), 'Select current primary generators')
    manifest = json.loads((data/'data_manifest.json').read_text())
    require(manifest['profile'] == 'current6' and not manifest['per_prompt_data_included'],
            'Unexpected current release profile')
    for name, digest in manifest['sha256'].items():
        require(Path(name).name == name, 'Unexpected data path')
        require(hashlib.sha256((data/name).read_bytes()).hexdigest() == digest,
                'Changed current data: '+name)
    for name, digest in manifest['reference_package_sha256'].items():
        require(Path(name).name == name, 'Unexpected reference path')
        require(hashlib.sha256((data.parent/name).read_bytes()).hexdigest() == digest,
                'Changed historical reference: '+name)
    protocol = json.loads((data/'protocol.json').read_text())
    require(protocol['committing_context']['total_latent_frames'] == 6
            and protocol['committing_context']['previous_latent_frames'] == 3,
            'Current committing context must be current plus previous block')
    points = read_csv(data/'full_scores.csv')
    arms = {m+s for m in CURRENT_MODELS for s in ('_N', '_W')}
    require(len(points) == 12 and {r['arm'] for r in points} == arms,
            'Expected six complete current comparisons')
    points = {r['arm']:r for r in points}
    for arm, row in points.items():
        raw = np.array([float(row[d])/100 for d in DIMS])
        for metric, value in composites(raw).items():
            verify_close(value, float(row[metric]), arm+' '+metric)
    source = json.loads((data/'source_results.json').read_text())
    mapping = {'SGF':'SGF_W6', 'RF':'K_RFw6', 'SGFP':'SGFP_W6', 'RS':'RS_W6'}
    historical_points = {r['arm']:r for r in read_csv(data.parent/'full_scores.csv')}
    historical_stats = {(r['model'],r['metric']):r
                        for name in ('aggregate_paired_ci.csv','component_paired_ci.csv')
                        for r in read_csv(data.parent/name)}
    saved = [r for name in ('aggregate_paired_ci.csv','component_paired_ci.csv')
             for r in read_csv(data/name)]
    require(len(saved) == 114 and len({(r['model'],r['metric']) for r in saved}) == 114,
            'Expected 18 aggregate and 96 component contrasts')
    for model in CURRENT_MODELS:
        for suffix in ('_N','_W'):
            arm = model+suffix
            if model in mapping:
                src = source['summary'][model+'_N' if suffix == '_N' else mapping[model]]
                for metric in ('quality','semantic','total'):
                    verify_close(float(points[arm][metric]), src[metric], arm+' source')
                for metric in DIMS:
                    verify_close(float(points[arm][metric]), 100*src['components'][metric],
                                 arm+' component source')
            else:
                require(points[arm] == historical_points[arm], arm+' frozen reference changed')
    for row in saved:
        model, metric = row['model'], row['metric']
        require(model in CURRENT_MODELS and metric in ('quality','semantic','total')+DIMS,
                'Unexpected contrast identity')
        observed = float(points[model+'_W'][metric])-float(points[model+'_N'][metric])
        verify_close(observed, float(row['delta']), model+' '+metric+' difference')
        if model in mapping:
            family = 'component_delta_percent' if metric in DIMS else 'aggregate_delta'
            expected = source['comparisons'][mapping[model]+'_vs_'+model+'_N'][family][metric]
            values = [expected['delta'],*expected['ci95'],expected['valid_draws']]
        else:
            ref = historical_stats[model,metric]
            values = [float(ref[k]) for k in ('delta','ci95_low','ci95_high','valid_draws')]
        verify_close([float(row[k]) for k in ('delta','ci95_low','ci95_high','valid_draws')],
                     values, model+' '+metric+' frozen interval')
    decomposition = read_csv(data/'quality_decomposition.csv')
    require(len(decomposition) == 6, 'Missing Quality decomposition')
    for row in decomposition:
        model = row['model']
        terms = []
        for metric in QUALITY:
            difference = float(points[model+'_W'][metric])-float(points[model+'_N'][metric])
            term = (.5 if metric == 'dynamic_degree' else 1)*difference
            term /= (NORMALIZE[metric][1]-NORMALIZE[metric][0])*6.5
            verify_close(term, float(row[metric]), model+' weighted '+metric)
            terms.append(term)
        verify_close(sum(terms), float(row['quality_delta']), model+' seven-term sum')
    windows = read_csv(data/'window_comparisons.csv')
    expected_windows = {(m, metric) for m in mapping
                        for metric in ('quality', 'semantic', 'total')}
    require(len(windows) == 12
            and {(r['model'], r['metric']) for r in windows} == expected_windows,
            'Expected 12 current versus historical window contrasts')
    for row in windows:
        model, metric = row['model'], row['metric']
        require(int(row['new_context']) == 6
                and int(row['reference_context']) == (21 if model in ('RF','RS') else 9),
                'Unexpected window-comparison context')
        expected = source['comparisons'][mapping[model]+'_vs_'+model+'_W']['aggregate_delta'][metric]
        verify_close([float(row[k]) for k in ('delta','ci95_low','ci95_high','valid_draws')],
                     [expected['delta'], *expected['ci95'], expected['valid_draws']],
                     model+' '+metric+' window contrast')
    for model in selected:
        print(f"{model:6s} Quality {float(points[model+'_N']['quality']):.4f} -> "
              f"{float(points[model+'_W']['quality']):.4f}; current6 sources verified")
    print('Verified 12 arms, 16 dimensions, 114 saved contrasts, 12 window contrasts '
          'and six Quality decompositions. '
          'Current confidence intervals are checked against frozen reports; they are not '
          'recomputed from new per-prompt records. Use --profile historical for the public '
          'historical prompt-bootstrap replay.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('current6','historical'), default='current6')
    parser.add_argument('--data', type=Path, help='Override the selected profile directory')
    parser.add_argument('--models', nargs='+', choices=MODELS,
                        help='Select displayed models (current6) or interval replays (historical); '
                             'every arm and point estimate is still checked')
    args = parser.parse_args()
    suite = Path(__file__).resolve().parents[2]/'results/vbench_full/common946'
    data = args.data or (suite/'current6' if args.profile == 'current6' else suite)
    if args.profile == 'current6':
        reproduce_current(data, args.models)
    else:
        reproduce(data, args.models)
