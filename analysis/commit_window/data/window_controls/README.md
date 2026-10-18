# Self-only and cross-model window controls

These are frozen scorer readouts for the additional window controls. All estimates and intervals are copied
from the completed reports. The new arms' video-level scoring inputs are not included in this snapshot;
these summaries do not provide a per-video bootstrap replay. Protocols and source hashes are in
[protocol.json](protocol.json) and [provenance.json](provenance.json).

## LongLive self-only at 120 and 240 seconds

128 ID-Forcing MovieGen prompts, generation seed 0. Base, self-only and recent-context LongLive use 15 physical
cache frames and the same denoising access. Self-only committing reads the current clean 3-frame block. Complete
ID-Forcing is a separate cache-construction framework.

| Duration | Contrast | Δ Quality [95% CI] | Δ Dynamic [95% CI] | Δ Subject c2c [95% CI] | Δ Background c2c [95% CI] |
|---|---|---|---|---|---|
| 120 s | Self-only − Base | +0.50* [+0.27, +0.72] | +9.73* [+6.91, +12.79] | +0.56 [-0.11, +1.23] | +0.88* [+0.49, +1.26] |
| 120 s | 6 frames − self-only | -0.17* [-0.31, -0.03] | -6.32* [-8.40, -4.32] | +1.30* [+0.89, +1.75] | +1.01* [+0.75, +1.28] |
| 120 s | Self-only − complete ID-Forcing | -0.05 [-0.37, +0.27] | -4.69* [-8.37, -1.11] | +6.01* [+4.60, +7.42] | +4.48* [+3.59, +5.40] |
| 240 s | Self-only − Base | +0.49* [+0.24, +0.74] | +9.89* [+6.61, +13.35] | +1.24* [+0.57, +1.91] | +1.47* [+0.98, +1.95] |
| 240 s | 6 frames − self-only | -0.21* [-0.34, -0.08] | -6.07* [-8.09, -4.21] | +1.31* [+0.99, +1.67] | +1.12* [+0.82, +1.43] |
| 240 s | Self-only − complete ID-Forcing | -0.13 [-0.46, +0.20] | -6.66* [-10.74, -2.87] | +6.89* [+5.38, +8.37] | +5.39* [+4.47, +6.35] |

Self-only absolute scores (Quality, Dynamic, Subject c2c, Background c2c) are 82.22 / 52.68 / 84.73 / 88.05 at
120 seconds and 82.05 / 51.45 / 84.65 / 88.00 at 240 seconds. Retaining six frames improves clip-to-clip consistency
and lowers both Dynamic Degree and Quality relative to self-only at these durations. Motion Smoothness and
Temporal Flickering improve with six frames: +0.15 / +0.33 at 120 seconds and +0.15 / +0.34 at 240 seconds.

Full original statistics: [120 seconds](longlive120_summary.json), [240 seconds](longlive240_summary.json).
The reports include the historical 12-frame and ID-Forcing contrasts.

## LongLive self-only on the standard suite

946 entries, nominal 60 seconds, generation seed 0, 12 physical cache frames in both conditions. Differences
are **self-only minus six-frame committing**. Official aggregation is retained; intervals use 4,000 bootstrap
draws over 944 original-prompt clusters. `*` marks an interval excluding zero.

| Metric | 6 frames | Self-only | Δ [95% CI] |
|---|---:|---:|---|
| Quality | 84.99 | 85.17 | +0.18 [-0.07, +0.45] |
| Semantic | 76.84 | 76.49 | -0.35 [-0.74, +0.03] |
| Total | 83.36 | 83.43 | +0.07 [-0.14, +0.31] |
| Subject consistency | 98.00 | 97.84 | -0.16* [-0.26, -0.08] |
| Background consistency | 97.23 | 97.05 | -0.18* [-0.25, -0.12] |
| Temporal flickering | 99.28 | 99.21 | -0.07* [-0.12, -0.02] |
| Motion smoothness | 98.55 | 98.46 | -0.09* [-0.14, -0.05] |
| Dynamic degree | 54.81 | 60.14 | +5.32* [+1.97, +8.95] |
| Aesthetic quality | 66.71 | 66.32 | -0.39* [-0.57, -0.21] |
| Imaging quality | 70.46 | 70.26 | -0.19 [-0.44, +0.06] |
| Object class | 88.52 | 88.10 | -0.42 [-1.61, +0.55] |
| Multiple objects | 79.91 | 79.76 | -0.15 [-1.33, +1.23] |
| Human action | 95.50 | 95.50 | +0.00 [-0.79, +0.80] |
| Color | 92.04 | 91.79 | -0.25 [-1.54, +0.95] |
| Spatial relationship | 76.30 | 74.20 | -2.10* [-3.74, -0.60] |
| Scene | 45.71 | 45.56 | -0.15 [-1.93, +1.58] |
| Appearance style | 20.73 | 20.76 | +0.03 [-0.04, +0.10] |
| Temporal style | 22.65 | 22.64 | -0.02 [-0.11, +0.08] |
| Overall consistency | 25.09 | 25.06 | -0.04 [-0.12, +0.05] |

Self-only gives more motion without a significant Quality or Total difference. Six-frame committing improves
Subject, Background, smoothness, flickering and aesthetics. The main LongLive configuration remains six frames.
[Original full summary](longlive946_summary.json) and [score readout](longlive946_readout.md).

## Cross-model committing-window sweep

rollf200 prompts 0–99, 60 seconds, generation seed 0. Context changes apply only during committing, with direct
sink access excluded in every compared context. Counts include the current 3-frame block. Each model retains
its denoising and physical storage. These development comparisons retain their own prompt set and do not replace
the common946 main pair.

| Model | New context − main context | Δ Quality [95% CI] | Δ Dynamic [95% CI] | Δ Subject c2c [95% CI] | Δ Background c2c [95% CI] | Δ Smoothness [95% CI] | Δ Flickering [95% CI] |
|---|---|---|---|---|---|---|---|
| SGF | 6 - default 9 | -0.13 [-0.46, +0.19] | -2.20 [-6.20, +1.77] | +0.20 [-0.77, +1.11] | +0.08 [-0.50, +0.67] | -0.02 [-0.12, +0.07] | -0.03 [-0.19, +0.14] |
| SGF | self-only - default 9 | -0.03 [-0.40, +0.34] | +1.87 [-2.87, +6.60] | -0.29 [-1.29, +0.73] | -0.18 [-0.84, +0.52] | -0.11* [-0.19, -0.03] | -0.14 [-0.30, +0.04] |
| SGF+ | 6 - default 9 | -0.10 [-0.55, +0.34] | -0.70 [-6.23, +4.37] | +0.40 [-0.47, +1.30] | +0.13 [-0.45, +0.66] | -0.00 [-0.09, +0.08] | +0.03 [-0.13, +0.18] |
| SGF+ | self-only - default 9 | -0.02 [-0.42, +0.36] | +2.53 [-2.40, +7.00] | +0.82 [-0.09, +1.77] | +0.02 [-0.49, +0.57] | -0.16* [-0.26, -0.07] | -0.22* [-0.39, -0.05] |
| RF-TF | 6 - default 21 | +0.16 [-0.02, +0.34] | -2.70* [-5.00, -0.63] | +2.27* [+1.57, +2.98] | +2.17* [+1.66, +2.70] | -0.00 [-0.07, +0.06] | +0.05 [-0.07, +0.15] |
| RF-TF | self-only - default 21 | -0.08 [-0.35, +0.18] | +1.50 [-1.13, +4.17] | -0.24 [-1.22, +0.74] | +0.55 [-0.13, +1.24] | -0.15* [-0.27, -0.05] | -0.29* [-0.45, -0.14] |
| Rolling Sink | 6 - default 21 | -0.12 [-0.40, +0.14] | -2.57 [-6.17, +0.63] | +1.85* [+1.24, +2.56] | +1.67* [+1.22, +2.19] | -0.08 [-0.17, +0.00] | -0.02 [-0.13, +0.08] |
| Rolling Sink | self-only - default 21 | +0.03 [-0.34, +0.39] | +3.43 [-1.17, +7.97] | +1.26* [+0.37, +2.27] | +1.64* [+1.01, +2.30] | -0.31* [-0.48, -0.16] | -0.36* [-0.56, -0.17] |
| CF | self-only - default 6 | +0.03 [-0.17, +0.22] | +1.03 [-1.07, +3.23] | -0.06 [-0.63, +0.52] | +0.13 [-0.24, +0.49] | -0.04 [-0.13, +0.03] | -0.02 [-0.14, +0.11] |

All nine Quality intervals include zero; their point changes have magnitude below 0.17. Shortening RF-TF and
Rolling Sink from 21 to six frames improves long-range consistency. Dynamic decreases by 2.70 and 2.57 points,
respectively, with only the RF-TF interval excluding zero. Self-only has higher Dynamic point estimates and often
lower smoothness/flickering. [Complete summary](cross_model_summary.json) and
[original score readout](cross_model_readout.txt) retain all ten contrasts, including Rolling Sink's original
released-policy reference.

Print all frozen readouts without inference or scoring:

```bash
python analysis/commit_window/source/window_controls_readout.py
```
