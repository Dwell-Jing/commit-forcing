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
Subject/Background are fused scores; `Subj_c2c`/`Bg_c2c` are unmapped clip-to-clip scores. The script prints all arm
means, replays 4,000-draw paired-prompt contrasts, and computes per-prompt least-squares trends against log2(lag),
with bootstrap seed 20261017 for trends. [reported_contrasts.json](data/reported_contrasts.json) preserves the original
15 contrasts; the verification option checks them against replay rather than replacing reported values.

Four additional historical reference arms are retained in the CSV and output: `SGF_W`, `SGF_N`, `LLS_c0` and `LLS_33`.
They differ in context geometry and/or original noise protocol and are not part of the fixed-six-frame lag scan.
In particular, LongLive base uses 12 committing frames and original sink positions. Sink versus lag-16 changes
content, provenance and realized age together. [provenance.json](data/provenance.json) records the original scored-file hashes.
