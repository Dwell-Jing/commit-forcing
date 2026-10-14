# SGF committing contexts: source and self-only controls

We compare four committing contexts on released SGF weights. At the same 9-frame read count, Commit Forcing improves
Quality by **1.25 points** and clip-to-clip Subject Consistency by **4.54 points** over a context retaining the sink.
Relative to self-only committing, neither Quality nor clip-to-clip Subject changes significantly; recent context
reduces Dynamic Degree while improving Motion Smoothness and Temporal Flickering.

![SGF committing controls](../../assets/sgf_committing_controls.png)

## Four contexts

| Group | Committing context | Latent frames read | Outputs |
|---|---|---:|---|
| A: Base SGF | 3 sink + 6 recent + 3 current | 12 | Existing seed-0/1 comparison |
| B: Commit Forcing | 6 recent + 3 current | 9 | Existing seed-0/1 comparison |
| C: Self-only | 3 current | 3 | Newly generated control |
| D: Sink retained, equal count | 3 sink + 3 recent + 3 current | 9 | Newly generated control |

All contexts retain the released EMA weights, 12-frame physical cache, denoising policy, top-aligned positions,
sampler, attention kernels, and number of model forwards. Selected entries retain their original RoPE positions.
We use 200 [rollf200 prompts](../../eval/prompts/rollf200.txt), 60-second videos, and generation seeds 0 and 1.
Each context uses the same per-prompt initial-noise seed convention. Intermediate device re-noising states are not
fixed, so these comparisons pair prompts and generation seeds rather than identical complete random trajectories.

## Paired results

Scores and changes are on a 0–100 scale. Pooled estimates average the two seeds within each prompt, then bootstrap
the 200 prompts. `*` denotes a paired 95% interval excluding zero.

| B minus context | Δ Quality [95% CI] | Δ Subject c2c [95% CI] | Δ Dynamic [95% CI] | Δ Motion Smoothness [95% CI] | Δ Temporal Flickering [95% CI] |
|---|---|---|---|---|---|
| A: Base | +0.95* [+0.66, +1.25] | +4.60* [+3.86, +5.34] | +13.35* [+9.54, +17.26] | −0.20* [−0.27, −0.13] | −0.43* [−0.57, −0.31] |
| C: Self-only | −0.10 [−0.30, +0.10] | −0.07 [−0.51, +0.39] | −2.85* [−5.48, −0.23] | +0.11* [+0.07, +0.16] | +0.16* [+0.08, +0.26] |
| D: Sink retained, equal count | +1.25* [+0.92, +1.57] | +4.54* [+3.84, +5.23] | +18.12* [+13.76, +22.48] | −0.26* [−0.33, −0.19] | −0.58* [−0.71, −0.44] |

| Group | Quality, seed 0 | Quality, seed 1 | Subject c2c, seed 0 | Subject c2c, seed 1 |
|---|---:|---:|---:|---:|
| A | 83.58 | 83.85 | 86.54 | 86.60 |
| B | 84.62 | 84.71 | 90.93 | 91.41 |
| C | 84.65 | 84.87 | 91.09 | 91.38 |
| D | 83.35 | 83.48 | 86.87 | 86.39 |

B−D excludes a smaller read count as the sole explanation for the SGF gain. It jointly changes historical content,
age, and position. B−C provides no clear Quality or continuity advantage for retaining recent frames on SGF; the
significant smoothness and flickering gains accompany reduced motion. Self-only committing is a context control,
distinct from the complete ID-Forcing procedure.

The motion-adjusted Subject c2c changes are +4.53* for B−A, −0.17 for B−C, and +4.48* for B−D. This adjustment is
the intercept of an OLS regression of paired consistency changes on paired Dynamic Degree changes, with prompt
bootstrap intervals. It is a descriptive adjustment rather than a matched-motion generation experiment.

## Protocol and available data

- [data/PREREG.md](data/PREREG.md) preserves the three contrasts and interpretation rules fixed before generating C and D.
- [data/READOUT.md](data/READOUT.md) contains all reported seed-specific and pooled contrasts, including additional metrics.
- [data/levels.csv](data/levels.csv) and [data/reported_contrasts.csv](data/reported_contrasts.csv) transcribe that completed readout.
- [data/per_video_scores.csv](data/per_video_scores.csv) contains the actual scored inputs for all 1,600 videos, with 200 prompts per context and seed.
- [source/sgfcw_readout.py](source/sgfcw_readout.py) retains its metric order, 4,000 prompt-bootstrap draws, and 2,000 regression-bootstrap draws, accepting a scored per-video CSV instead of an internal filesystem layout.
- [data/provenance.json](data/provenance.json) records source hashes and the distinction between reported summaries and input scores.

```bash
# Display the reported pooled contrasts without estimating new intervals.
python analysis/sgf_committing_controls/tables.py
# Recompute from the actual scored inputs and verify all reported rounded contrasts.
python analysis/sgf_committing_controls/source/sgfcw_readout.py \
    --scores analysis/sgf_committing_controls/data/per_video_scores.csv --check-reported
```

The input CSV schema is `group,seed,prompt,quality,subject_clip2clip,dynamic_degree,motion_smoothness,temporal_flickering,background_clip2clip,subject_consistency,aesthetic_quality,imaging_quality`.
Groups are A/B/C/D; metric inputs use their original 0–1 scale. Replaying the earlier two-arm specs uses a different
bootstrap contrast order, so its interval endpoints can differ slightly while the point estimates remain the same.
The reported summaries and actual scored inputs are identified separately in the provenance record.

The [SF and LongLive context comparisons](../commit_window/README.md) show that the effect of retaining recent
dependencies varies across generators. The [standard VBench results](../../RESULTS.md#full-vbench) use a separate
946-entry protocol.
