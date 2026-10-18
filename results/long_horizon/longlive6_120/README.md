# LongLive: six-frame committing at 120 seconds

We evaluate the six-frame committing context on ID-Forcing's 128 MovieGen prompts at 120 seconds, with generation
seed 0. The context reads 3 recent and 3 current latent frames. Base denoising is retained. The base, six-frame and
12-frame committing conditions all use a **15-frame physical cache** in this long-horizon implementation.
The common946 main evaluation uses a separate 12-frame physical-cache implementation.

## Arm means

All scores are on a 0–100 presentation scale. Quality is the seven-component VBench-Long custom-input aggregate;
clip-to-clip consistency is distinct from fused consistency.

| Configuration | Quality | Dynamic | Subject c2c | Background c2c |
|---|---:|---:|---:|---:|
| Base LongLive | 81.72 | 42.96 | 84.16 | 87.17 |
| Commit Forcing, 6 frames | 82.05 | 46.37 | 86.03 | 89.06 |
| Commit Forcing, 12-frame control | 81.93 | 46.42 | 85.25 | 88.36 |
| ID-Forcing on LongLive | 82.27 | 57.37 | 78.72 | 83.57 |

## Paired changes

Six-frame Commit Forcing improves Quality and clip-to-clip Subject over both base committing and the 12-frame
committing control. Against ID-Forcing, the Quality interval spans zero; clip-to-clip Subject increases while
Dynamic Degree decreases. Relative to base LongLive, Motion Smoothness and Temporal Flickering scores decrease.

| Metric | Six frames − base | Six frames − 12-frame control | Six frames − ID-Forcing |
|---|---|---|---|
| Quality | +0.33* [+0.16, +0.50] | +0.12* [+0.03, +0.21] | −0.22 [−0.57, +0.12] |
| Dynamic Degree | +3.41* [+1.18, +5.70] | −0.05 [−1.35, +1.19] | −11.00* [−15.21, −6.91] |
| Fused Subject Consistency | +0.13* [+0.07, +0.20] | +0.20* [+0.15, +0.25] | +0.36* [+0.17, +0.54] |
| Fused Background Consistency | +0.15* [+0.09, +0.20] | +0.15* [+0.11, +0.18] | +0.35* [+0.24, +0.47] |
| In-clip Subject | +0.09 [−0.01, +0.20] | +0.30* [+0.23, +0.38] | −0.03 [−0.27, +0.20] |
| Clip-to-clip Subject | +1.87* [+1.39, +2.36] | +0.78* [+0.43, +1.14] | +7.31* [+5.88, +8.85] |
| Clip-to-clip Background | +1.89* [+1.57, +2.22] | +0.70* [+0.47, +0.92] | +5.49* [+4.52, +6.53] |
| Imaging Quality | +0.70* [+0.35, +1.05] | −0.09 [−0.28, +0.11] | +0.11 [−0.58, +0.80] |
| Aesthetic Quality | +0.31* [+0.02, +0.60] | +0.24* [+0.10, +0.38] | +0.71 [−0.02, +1.43] |
| Motion Smoothness | −0.13* [−0.18, −0.08] | +0.02* [+0.00, +0.04] | +0.19* [+0.08, +0.32] |
| Temporal Flickering | −0.18* [−0.28, −0.09] | +0.06* [+0.02, +0.10] | +0.63* [+0.40, +0.88] |

Each contrast contains 128 paired prompts. Intervals use 4,000 prompt-bootstrap draws. `*` is determined from
unrounded endpoints; the [source summary](source_summary.json) retains every estimate, interval, pair count and
significance decision at full precision. [Readable original score readout](source_readout.txt).

## Reproduce the paired statistics

Run from the repository root with Python and NumPy:

```bash
python results/long_horizon/longlive6_120/replay.py
# Optionally save the complete replayed statistics:
python results/long_horizon/longlive6_120/replay.py --json /tmp/longlive6_120_replay.json
```

The replay follows the complete original [spec](spec.json): 10 contrasts, 11 metrics per contrast, and one ordered
`default_rng(0)` bootstrap stream. It validates all 110 estimates and intervals against the frozen source summary,
including the 33 metrics in the three six-frame contrasts. Replaying only the new contrasts with a fresh RNG would
produce different bootstrap endpoints.

The inputs are the existing [baseline score CSV](../vbench_long_120s_idf128.csv) and this directory's
[additional scored arms](scores.csv). The latter contains 128 records each for `longlive+commit6`, `idf_longlive`
and `idf_longlive+rule`; the last arm supplies the original comparison context needed to replay the full bootstrap
order. The two existing LongLive arms' collected video-level scores agree with the baseline CSV within
2.3 × 10⁻¹⁶. The frozen interval replay agrees within 2.6 × 10⁻¹⁵.

## Score sources

The additional scores were collected from completed q6/background shards with the original evaluation loader.
Every arm covers prompt indices 0–127 exactly once with all seven components and both consistency splits.
[Provenance](provenance.json) records the original scorer and shard hashes, the frozen source reports, and the
public artifact hashes. [ID-Forcing drift score readout](drift_scores.txt).

The [six-frame 240-second evaluation](../longlive6_240/README.md) is complete. The existing 240-second
`longlive+rule` scores remain the 12-frame committing control.
