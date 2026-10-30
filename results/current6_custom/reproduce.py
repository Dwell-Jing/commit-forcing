"""Validate and display the frozen custom-prompt aggregate results."""
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def metric(value):
    if value is None:
        return '—'
    result = value['reported_mean']
    if value.get('significant'):
        result += '*'
    if 'reported_ci' in value:
        result += ' [' + ', '.join(value['reported_ci']) + ']'
    return result


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join([':---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows])


def render_descriptive_adjustment(data):
    adjustment = data['six_generator_descriptive_adjustment']
    return '\n'.join([
        '### Six-generator descriptive Dynamic Degree adjustment', '',
        table(['Generator', 'Δ Dynamic Degree', 'Δ Subject c2c',
               'DD-adjusted Δ Subject c2c [95% CI]'],
              [[row['generator'], metric(row['dynamic_delta']),
                metric(row['subject_c2c_delta']), metric(row['subject_c2c_intercept'])]
               for row in adjustment['rows']]), '',
        'Commit Forcing minus Base on 200 rollf200 prompts at 60 seconds with generation seed 0.',
        'All six committing adaptations use 6 frames. OLS intercept intervals use 2,000 prompt-bootstrap draws.',
        'These are descriptive regression adjustments, not experiments with motion held fixed.',
        'This table includes SGF+; the original seed tables above retain the separate SF-with-sink configuration.',
        'It is separate from the 946-entry standard-suite scores.', ''])


def render_tables(data):
    parts = []
    roll = data['rollf200_60s']['rows']
    for seed in (0, 1):
        parts += [f'### 60-second rollf200, generation seed {seed}', '',
                  table(['Configuration', 'Quality: Base', 'Modified', 'Δ Quality',
                         'Subject c2c: Base', 'Modified', 'Δ Subject c2c', 'Δ Dynamic'],
                        [[r['configuration'], f"{r['quality_base']:.2f}", f"{r['quality_recent']:.2f}",
                          metric(r['quality_delta']), f"{r['subject_c2c_base']:.2f}",
                          f"{r['subject_c2c_recent']:.2f}", metric(r['subject_c2c_delta']),
                          metric(r['dynamic_delta'])] for r in roll if r['generation_seed'] == seed]), '']
    parts += [render_descriptive_adjustment(data)]
    long = data['moviegen32_240s']
    parts += ['### 240-second MovieGen: absolute scores', '',
              table(['Generator', 'Committing configuration', 'Quality', 'Fused Subject', 'Fused Background', 'Dynamic'],
                    [[r['generator'], r['configuration'], f"{r['quality']:.2f}",
                      f"{r['subject_fused']:.2f}", f"{r['background_fused']:.2f}",
                      f"{r['dynamic']:.2f}"] for r in long['absolute_scores']]), '',
              '### 240-second MovieGen: Commit Forcing minus Base', '',
              table(['Generator', 'Δ Quality', 'Δ Fused Subject', 'Δ Fused Background', 'Δ Subject c2c'],
                    [[r['generator']] + [metric(r[k]) for k in ('quality_delta', 'subject_fused_delta',
                      'background_fused_delta', 'subject_c2c_delta')] for r in long['paired_recent_minus_base']]), '',
              'SGF Dynamic Degree changes by ' + metric(long['sgf_dynamic_delta']) +
              '. Its Quality interval includes zero, including the −0.002 lower endpoint.', '',
              '### RF-TF and Rolling Sink window plateaus', '',
              table(['Generator', 'Window', 'Δ Quality', 'Δ Dynamic', 'Δ Subject c2c'],
                    [[r['generator'], r['window_frames']] + [metric(r[k]) for k in
                      ('quality_delta', 'dynamic_delta', 'subject_c2c_delta')]
                     for r in data['window_plateaus']['rows']]), '',
              'Changes are relative to 6 frames, on rollf200 prompts 0–99 at 60 seconds with seed 0.', '',
              '### SF with a sink: windows by seed', '',
              table(['Seed', 'Window', 'Quality', 'Dynamic', 'Subject c2c', 'Δ Quality', 'Δ Subject c2c'],
                    [[r['generation_seed'], r['window_frames'], f"{r['quality']:.2f}",
                      f"{r['dynamic']:.2f}", f"{r['subject_c2c']:.2f}", metric(r['quality_delta']),
                      metric(r['subject_c2c_delta'])] for r in data['sf_sink_windows']['rows']]), '',
              'Changes are relative to 6 frames within each seed; all 200 rollf200 prompts are used.', '',
              '### SF with a sink: pooled window contrasts', '',
              table(['Window contrast', 'Δ Quality', 'Δ Dynamic', 'Δ Subject c2c'],
                    [[r['contrast']] + [metric(r[k]) for k in
                      ('quality_delta', 'dynamic_delta', 'subject_c2c_delta')]
                     for r in data['sf_sink_windows']['pooled_seed_contrasts']]), '',
              'Each prompt contributes the average of its seed-0 and seed-1 differences before prompt resampling.', '',
              '### Framewise SGF diagnostic', '',
              table(['Window', 'Quality', 'Dynamic', 'Subject c2c', 'Background c2c', 'Δ Quality', 'Δ Subject c2c'],
                    [[r['configuration'], f"{r['quality']:.2f}", f"{r['dynamic']:.2f}",
                      f"{r['subject_c2c']:.2f}", f"{r['background_c2c']:.2f}", metric(r['quality_delta']),
                      metric(r['subject_c2c_delta'])] for r in data['framewise_sgf_windows']['rows']]), '',
              'Changes are relative to the 6-frame diagnostic. This generator uses one latent frame per block:',
              '2 frames implement current-plus-previous-block committing; 6 frames include five predecessors.',
              'The study uses rollf200 prompts 0–99 at 60 seconds with seed 0.', '']
    return '\n'.join(parts)


def check(data):
    counts = {'aggregate_metrics': 0}
    def visit(obj):
        if isinstance(obj, dict):
            if 'reported_mean' in obj:
                assert float(obj['reported_mean']) == obj['mean']
                assert math.isfinite(obj['mean'])
                counts['aggregate_metrics'] += 1
                if 'ci' in obj:
                    assert list(map(float, obj['reported_ci'])) == obj['ci']
                    lo, hi = obj['ci']
                    assert lo <= obj['mean'] <= hi
                    if 'significant' in obj:
                        assert obj['significant'] == (lo > 0 or hi < 0)
            for v in obj.values():
                visit(v)
        elif isinstance(obj, list):
            for v in obj:
                visit(v)
    visit(data)
    assert data['bootstrap_recomputed'] is False
    assert len(data['source_sha256']) == 6
    assert all(len(h) == 64 and all(c in '0123456789abcdef' for c in h)
               for h in data['source_sha256'].values())
    roll = data['rollf200_60s']['rows']
    assert len(roll) == 14
    assert len({(r['configuration'], r['generation_seed']) for r in roll}) == 14
    assert sum(r['component_only'] for r in roll) == 2
    assert all(r['committing_frames'] == 6 for r in roll if not r['component_only'])
    for r in roll:
        for stem in ('quality', 'subject_c2c'):
            # Published absolute means and paired deltas are independently rounded.
            assert abs(r[stem + '_recent'] - r[stem + '_base'] - r[stem + '_delta']['mean']) <= 0.011
    long = data['moviegen32_240s']
    assert len(long['absolute_scores']) == 6 and len(long['paired_recent_minus_base']) == 2
    sgf = next(r for r in long['paired_recent_minus_base'] if r['generator'] == 'SGF')
    assert sgf['quality_delta']['ci'] == [-0.002, 1.82]
    assert sgf['quality_delta']['significant'] is False
    assert sgf['subject_c2c_delta']['mean'] == 5.42
    assert len(data['window_plateaus']['rows']) == 10
    assert len(data['sf_sink_windows']['rows']) == 9
    assert len(data['sf_sink_windows']['pooled_seed_contrasts']) == 5
    assert len(data['framewise_sgf_windows']['rows']) == 9
    assert data['framewise_sgf_windows']['block_frames'] == 1
    assert data['framewise_sgf_windows']['current_plus_previous_frames'] == 2
    assert data['sgf60_descriptive_adjustment']['subject_c2c_intercept']['mean'] == 4.87
    adjustment = data['six_generator_descriptive_adjustment']
    assert adjustment['source_snapshot']['kind'] == 'canonical manuscript working tree'
    assert all(len(h) == 64 and all(c in '0123456789abcdef' for c in h)
               for h in adjustment['source_sha256'].values())
    assert adjustment['prompts'] == 200 and adjustment['seconds'] == 60
    assert adjustment['generation_seed'] == 0 and adjustment['committing_frames'] == 6
    assert adjustment['prompt_bootstrap_draws'] == 2000
    assert adjustment['statistics_recomputed'] is False
    names = [row['generator'] for row in adjustment['rows']]
    assert len(names) == 6 and len(set(names)) == 6
    assert set(names) == {'SGF', 'SGF+', 'RF-TF', 'Rolling Sink', 'LongLive', 'CF'}
    sgf_adjusted = next(row['subject_c2c_intercept'] for row in adjustment['rows']
                        if row['generator'] == 'SGF')
    legacy = data['sgf60_descriptive_adjustment']['subject_c2c_intercept']
    assert all(sgf_adjusted[key] == legacy[key]
               for key in ('mean', 'reported_mean', 'ci', 'reported_ci'))
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--markdown', action='store_true', help='Print the frozen aggregate tables.')
    args = parser.parse_args()
    data = json.loads((HERE / 'summary.json').read_text())
    counts = check(data)
    if args.markdown:
        print(render_tables(data))
    else:
        print(f"Validated {counts['aggregate_metrics']} reported aggregate means and their stored intervals; no bootstrap recomputed.")
        print(render_descriptive_adjustment(data))


if __name__ == '__main__':
    main()
