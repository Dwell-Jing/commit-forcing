# Historical recency at fixed committing positions

We vary the source-block lag while keeping committing-context size and assigned temporal positions fixed.
Clip-to-clip Subject and Background means decrease across the five tested target lags on both SGF and LongLive.
Dynamic Degree increases; Quality responses differ between generators.

![Historical recency](../../assets/committing_content_age.png)

| Model | Target lag (blocks) | Quality ↑ | Dynamic ↑ | Subject c2c ↑ | Background c2c ↑ |
|---|---:|---:|---:|---:|---:|
| SGF | 1 | 84.11 | 66.27 | 90.61 | 92.85 |
| SGF | 2 | 84.21 | 68.37 | 90.53 | 92.74 |
| SGF | 4 | 84.19 | 68.60 | 90.30 | 92.55 |
| SGF | 8 | 84.24 | 69.67 | 90.02 | 92.42 |
| SGF | 16 | 84.34 | 71.30 | 89.92 | 92.34 |
| SGF | Sink source | 83.14 | 72.53 | 78.62 | 83.52 |
| LongLive | 1 | 82.82 | 54.00 | 85.50 | 88.65 |
| LongLive | 2 | 82.78 | 55.13 | 85.16 | 88.37 |
| LongLive | 4 | 82.74 | 56.00 | 84.35 | 87.67 |
| LongLive | 8 | 82.75 | 57.93 | 83.68 | 86.91 |
| LongLive | 16 | 82.63 | 57.57 | 83.03 | 86.26 |
| LongLive | Sink source | 81.85 | 56.47 | 78.28 | 80.25 |

From lag 1 to 16, Subject c2c changes by −0.69 on SGF and −2.46 on LongLive; both paired intervals exclude zero.
Dynamic changes by +5.03 and +3.57, respectively. Quality changes by +0.23 and −0.19; the latter interval spans zero.
The small lag-2-minus-lag-1 Subject c2c intervals span zero on both models. Monotone arm means do not make every
adjacent-lag difference significant. Sink is a separate source control, not another fixed-lag point.

## Intervention

- First 100 `rollf200` prompts (indices 0–99), generation seed 0, 240 latent frames / nominal 60 seconds.
- Each committing pass after block 0 reads three historical frames plus the current three frames; denoising keeps
  each generator's base policy, including sink access.
- For nonsink route d and block b≥2, the source is block `max(1, b−d)`. Block 0 reads current only; block 1 uses block 0
  in every route. Realized age ramps up until the requested lag is available. Sink always reads block 0.
- All historical keys are assigned to the three positions immediately preceding the current block. SGF applies
  RoPE to the selected pre-RoPE K at those positions. LongLive re-rotates the temporal component of its stored K.
  V is unchanged. Each route retrieves the KV committed earlier in its own rollout, not a fresh forward of old latents.
- Active cache sizes are 12 frames on SGF and 15 on LongLive. An auxiliary diagnostic store retains evicted committed
  KV, up to 51 additional frames after cleanup (about 15 GB); this store is absent from Commit Forcing inference.

All six SGF conditions are fresh runs with per-video RNG resets before initial CPU noise. LongLive retains per-video
seeds and sampler call order; lag 1 reuses the existing six-frame outputs. A prompt-0 gate checks the fresh LongLive
lag-1 path against these outputs. Saved metadata does not independently fingerprint every intermediate noise tensor.
These are freely generated rollouts, unlike the [fixed-clean-latent propagation probe](../committing_propagation/README.md).

## Scores and replay

```bash
python analysis/committing_content_age/tables.py
python analysis/committing_content_age/tables.py --verify-contrasts
```

Requires NumPy. [per_prompt.csv](data/per_prompt.csv) contains the 11 scored readouts before ×100 display scaling.
`Quality` uses the seven-dimension min–max-normalized RF Table 3 definition, including Dynamic weight 0.5.
Subject/Background are fused scores; `Subj_c2c`/`Bg_c2c` are the interclip components before mapping and fusion.
VBench-Long maps these terms and combines them with within-clip consistency at equal weights to form the fused
scores. [Scoring details](../../eval/vbench_long/README.md). The script prints all arm
means, replays 4,000-draw paired-prompt contrasts, and computes per-prompt least-squares trends against log2(lag),
with bootstrap seed 20261017 for trends. [reported_contrasts.json](data/reported_contrasts.json) preserves the original
15 contrasts; the verification option checks them against replay rather than replacing reported values.

Four additional historical reference arms are retained in the CSV and output: `SGF_W`, `SGF_N`, `LLS_c0` and `LLS_33`.
They differ in context geometry and/or original noise protocol and are not part of the fixed-six-frame lag scan.
In particular, LongLive base uses 12 committing frames and original sink positions. Sink versus lag-16 changes
content, provenance and realized age together. [provenance.json](data/provenance.json) records the original scored-file hashes.

## Fixed-trajectory recency diagnostic

This separate diagnostic reconstructs SGF caches from identical clean latent trajectories before probing the next
block. It uses 20 prompts: zero-based indices 0–20 except 5 in Self-Forcing's released expanded MovieGen file,
generation seeds 0 and 1, and 48-second reference videos. The reference uses a six-frame context at target lag 1.
The prompt list and intervention differ from the [nine-frame fixed-clean propagation study](../committing_propagation/README.md).

For each target lag 1, 2, 4, 8 or 16, or the separate sink source, the same fixed blocks are committed in order into
an independent cache. Historical selection and assigned temporal positions follow the intervention above.
After blocks 20, 28, 36, 44 and 52, a copied cache generates the next block with matched initial noise and
intermediate re-noising across conditions. Denoising reads the base 12-frame context, including the sink.
The generated probes do not enter later cache reconstruction.

Opening similarity is full-frame DINOv2 cosine similarity to the reference opening, rather than the
own-minus-other-seed Consistency diagnostic or VBench Subject c2c. The generated block is sampled at decoded
frames 0, 5 and 11; the reference opening is sampled every 0.25 seconds from 0.5 to below 2 seconds.
Saturation and brightness readouts are absolute relative changes from the preceding fixed block.
The [aggregate record](fixed_trajectory_summary.json) defines all six metrics.

Each prompt contributes both seeds and all five probe positions before 4,000 paired prompt-bootstrap draws.
Slopes are fitted against log2(target lag) within each prompt before averaging. The tables retain the original
diagnostic scales: the first five metrics are dimensionless, and within-latent luma motion uses the 0–255 scale.
They are not multiplied by 100. An asterisk marks a reported interval excluding zero before rounding.

Opening similarity has a small negative slope whose interval excludes zero; its arm means are not strictly
monotonic. Older context increases latent distance and within-latent luma motion. Saturation and brightness
slope intervals include zero. Sink lowers both opening similarity and the luma boundary ratio, so the readouts
do not all move in the same direction.

### Condition means

| Metric | d=1 | d=2 | d=4 | d=8 | d=16 | Sink |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Opening similarity | 0.9347 | 0.9351 | 0.9344 | 0.9339 | 0.9338 | 0.9295 |
| Absolute saturation change | 0.0388 | 0.0394 | 0.0389 | 0.0389 | 0.0387 | 0.0378 |
| Absolute brightness change | 0.0256 | 0.0269 | 0.0271 | 0.0264 | 0.0270 | 0.0240 |
| Latent distance | 0.4511 | 0.4531 | 0.4557 | 0.4546 | 0.4563 | 0.4823 |
| Luma boundary ratio | 1.7313 | 1.7558 | 1.7704 | 1.7431 | 1.7439 | 1.3866 |
| Within-latent luma motion | 7.2064 | 7.2852 | 7.3132 | 7.3332 | 7.3330 | 7.3881 |

### Trajectory context contrasts

| Metric | d=2 minus d=1 | d=4 minus d=1 | d=8 minus d=1 | d=16 minus d=1 |
| :--- | :--- | :--- | :--- | :--- |
| Opening similarity | +0.0004 [-0.0001, +0.0009] | -0.0003 [-0.0011, +0.0003] | -0.0008 [-0.0019, +0.0001] | -0.0010* [-0.0020, -3.5e-5] |
| Absolute saturation change | +0.0006* [+0.000014, +0.0012] | +0.0001 [-0.0009, +0.0011] | +0.0001 [-0.0005, +0.0007] | -0.0001 [-0.0007, +0.0004] |
| Absolute brightness change | +0.0013* [+0.0003, +0.0026] | +0.0015* [+0.0001, +0.0036] | +0.0009 [-0.0004, +0.0028] | +0.0014 [-0.0003, +0.0038] |
| Latent distance | +0.0020* [+0.0001, +0.0039] | +0.0046* [+0.0025, +0.0069] | +0.0035* [+0.0017, +0.0053] | +0.0052* [+0.0037, +0.0068] |
| Luma boundary ratio | +0.0245 [-0.0080, +0.0603] | +0.0391* [+0.0015, +0.0825] | +0.0119 [-0.0186, +0.0424] | +0.0126 [-0.0166, +0.0428] |
| Within-latent luma motion | +0.0788* [+0.0427, +0.1163] | +0.1068* [+0.0606, +0.1564] | +0.1267* [+0.0787, +0.1775] | +0.1266* [+0.0479, +0.2039] |

### Sink contrasts and target-lag slopes

| Metric | Sink minus d=1 | Sink minus d=16 | Slope per doubling of d |
| :--- | :--- | :--- | :--- |
| Opening similarity | -0.0053* [-0.0072, -0.0034] | -0.0043* [-0.0063, -0.0025] | -0.0003* [-0.0006, -0.0001] |
| Absolute saturation change | -0.0011 [-0.0038, +0.0017] | -0.0009 [-0.0036, +0.0017] | -0.0001 [-0.0002, +0.0001] |
| Absolute brightness change | -0.0016 [-0.0059, +0.0026] | -0.0030 [-0.0091, +0.0015] | +0.0002 [-0.0002, +0.0008] |
| Latent distance | +0.0312* [+0.0250, +0.0374] | +0.0260* [+0.0198, +0.0321] | +0.0012* [+0.0008, +0.0016] |
| Luma boundary ratio | -0.3447* [-0.5114, -0.2185] | -0.3573* [-0.5317, -0.2204] | +0.0013 [-0.0061, +0.0082] |
| Within-latent luma motion | +0.1817 [-0.0516, +0.3940] | +0.0551 [-0.1176, +0.2216] | +0.0301* [+0.0124, +0.0475] |

### Aggregate record and reader

[`fixed_trajectory_summary.json`](fixed_trajectory_summary.json) transcribes all 36 condition means and 42 reported
contrasts or slopes from the current manuscript table, preserving decimal and scientific-notation precision.
In particular, the d=16 opening-similarity interval ends at −3.5e-5, rather than zero. The source is the local
2026-10-30 manuscript working-tree snapshot, identified by relative source paths and SHA-256 hashes; it is not
labelled as a newer Overleaf commit. No per-prompt values, latent tensors, videos or individual responses are included.

```bash
python analysis/committing_content_age/read_fixed_trajectory.py
python analysis/committing_content_age/read_fixed_trajectory.py --markdown
```

The standard-library reader validates coverage, finite values, preserved precision and the reported interval
decisions, then prints the frozen table. It does not reconstruct bootstrap intervals or run generation or scoring.
