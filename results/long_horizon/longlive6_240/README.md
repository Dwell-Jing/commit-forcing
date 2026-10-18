# LongLive: six-frame committing at 240 seconds

128 ID-Forcing MovieGen prompts, generation seed 0, 240 seconds (960 latent frames) per video.
Base, 6-frame and 12-frame committing retain base denoising and a **15-frame physical cache**. Denoising reads 12
frames; six-frame committing reads 3 preceding trajectory frames and the current 3-frame block. The common946
main comparison has a separate 12-frame physical cache in both arms.

## Arm means

Scores ×100. Quality is the seven-component VBench-Long custom-input aggregate.

| Configuration | Quality | Dynamic | Subject c2c | Background c2c |
|---|---:|---:|---:|---:|
| Base LongLive | 81.56 | 41.56 | 83.41 | 86.53 |
| Commit Forcing, 6 frames | 81.84 | 45.38 | 85.96 | 89.12 |
| Commit Forcing, 12-frame control | 81.84 | 45.98 | 85.36 | 88.50 |
| ID-Forcing on LongLive | 82.18 | 58.11 | 77.75 | 82.61 |

## Paired changes

| Metric | Six frames − base | Six frames − 12-frame control | Six frames − ID-Forcing |
|---|---|---|---|
| Quality | +0.28* [+0.08, +0.49] | +0.00 [-0.10, +0.11] | -0.34 [-0.71, +0.02] |
| Clip-to-clip Subject | +2.55* [+1.98, +3.15] | +0.60* [+0.32, +0.87] | +8.21* [+6.63, +9.91] |
| Clip-to-clip Background | +2.59* [+2.21, +2.98] | +0.62* [+0.42, +0.83] | +6.51* [+5.49, +7.64] |
| Dynamic Degree | +3.82* [+1.19, +6.52] | -0.59 [-1.99, +0.85] | -12.73* [-17.32, -8.36] |
| Motion Smoothness | -0.16* [-0.22, -0.10] | +0.02* [+0.00, +0.04] | +0.14* [+0.02, +0.27] |
| Temporal Flickering | -0.22* [-0.33, -0.12] | +0.07* [+0.03, +0.11] | +0.58* [+0.34, +0.85] |
| Fused Subject | +0.16* [+0.09, +0.23] | +0.16* [+0.10, +0.21] | +0.47* [+0.29, +0.66] |
| Fused Background | +0.24* [+0.18, +0.30] | +0.16* [+0.13, +0.19] | +0.48* [+0.36, +0.62] |
| Within-clip Subject | +0.08 [-0.03, +0.17] | +0.25* [+0.17, +0.32] | +0.08 [-0.14, +0.30] |
| Imaging Quality | +0.61* [+0.15, +1.02] | -0.45* [-0.64, -0.26] | +0.01 [-0.79, +0.79] |
| Aesthetic Quality | -0.05 [-0.33, +0.23] | +0.11 [-0.03, +0.25] | +0.89* [+0.19, +1.62] |

Each contrast contains 128 paired prompts; intervals use 4,000 paired prompt-bootstrap draws. `*` is determined
from unrounded endpoints. Six minus 12 frames changes Quality by +0.0042 [−0.1020, +0.1133]; the Motion Smoothness
interval is [+0.0019, +0.0442], whose lower endpoint rounds to zero above.

Six-frame committing improves Quality and long-range consistency over Base. Against 12 frames, consistency
improves without a significant Quality difference, while Imaging Quality decreases by 0.45 points. Against
complete ID-Forcing, consistency increases and Dynamic Degree decreases; Quality's interval includes zero.

## Authors' drift scores

These scores are separate from VBench Dynamic Degree and diagnostic saturation drift; higher is better.

| Configuration | Color drift | Motion drift | Symmetric motion | Static-to-moving |
|---|---:|---:|---:|---:|
| Base LongLive | 55.92 | 85.94 | 78.12 | 7.8% |
| 12-frame control | 68.66 | 92.19 | 85.16 | 7.0% |
| 6 frames | 68.95 | 90.62 | 85.16 | 5.5% |
| ID-Forcing on LongLive | 70.13 | 98.44 | 74.22 | 24.2% |

Six frames improves the two drift scores over Base, but neither exceeds complete ID-Forcing. Its motion-drift
score is below the 12-frame control. [Original readout](drift_scores.txt) and [per-video drift CSVs](drift/).

## Data and CPU replay

```bash
python results/long_horizon/longlive6_240/replay.py
# Optionally save all 33 estimates and intervals:
python results/long_horizon/longlive6_240/replay.py --json /tmp/longlive6_240_replay.json
```

[scores.csv](scores.csv) preserves 512 scored videos from the four arms, with prompt indices 0–127 exactly once
per arm. [source_summary.json](source_summary.json) retains all 33 six-frame effects from the completed report;
[paired_effects.csv](paired_effects.csv) retains its 18 core effects at full precision. The replay advances the
original RNG stream past the six earlier complete contrasts before checking every six-frame estimate and interval.
[spec.json](spec.json) records that order. [Coverage](coverage.json) and [provenance](provenance.json) retain counts,
configuration checks and source hashes. The existing [12-frame CSV](../vbench_long_240s_idf128.csv) is unchanged.

To regenerate the six-frame arm with the historical 15-frame cache:

```bash
python analysis/commit_window/generate.py --commit-frames 6 --code third_party/longlive \
    --prompts third_party/id_forcing/prompts/moviegenbench_128.txt --ids 0-127 \
    --seconds 240 --seed 0 --out outputs/longlive6_240
```

Score the generated videos with [VBench-Long](../../../eval/vbench_long/README.md).
