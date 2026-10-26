# KV construction and committing pathways

The SGF split-cache control separates KV directly read by denoising from the history used by later committing.
In this experiment, the larger Quality and clip-to-clip Subject losses follow construction of the denoising-facing
KV. [Recursive KV propagation](../committing_propagation/README.md) remains a separate supplementary observation.

## Two synchronized SGF caches

- **D** stores the KV directly read by denoising, with its base read policy.
- **C** stores the history used to construct new entries in both caches.
- Both physical caches use the native 12-frame geometry and roll together. For each clean block, two diagnostic
  committing passes read the same preceding C cache, construct the D and C entries under independently chosen
  policies, and then update the two caches.
- **N12:** 3 sink + 6 recent + 3 current frames; **R9:** 6 recent + 3 current; **S3:** current 3 only.

```text
clean_block = base_denoising(noise, D)
new_D = construct_KV(clean_block, previous_C, D_policy)
new_C = construct_KV(clean_block, previous_C, C_policy)
D, C = roll(D, new_D), roll(C, new_C)
```

The extra committing pass belongs to this diagnostic. The main current-plus-previous-block method reuses one
existing committing pass. This R9 reference also predates the six-frame main method.

All contrasts below are relative to D=R9, C=R9, on rollf200 prompts 0–99 at 60 seconds with generation seed 0.
Scores use 0–100 points. Quality brackets show reported 95% paired prompt-bootstrap intervals from 4,000 draws;
asterisks retain the source's decisions for intervals excluding zero.

| D construction | C construction | Δ Quality [95% CI] | Δ Dynamic Degree | Δ Subject c2c |
|:---|:---|---:|---:|---:|
| N12 | N12 | −0.59* [−1.04, −0.16] | −10.37* | −3.98* |
| N12 | R9 | −1.12* [−1.58, −0.69] | −13.83* | −5.67* |
| R9 | N12 | −0.07 [−0.24, +0.08] | −1.63 | −0.09 |
| R9 | S3 | −0.05 [−0.28, +0.20] | +2.10 | −2.99* |

Native construction of C alone has no significant Quality or Subject c2c change. It nevertheless changes other
components: Aesthetic Quality −0.22, Motion Smoothness +0.10 and Temporal Flickering +0.13 points. Self-only C
construction significantly reduces Subject c2c by 2.99 points. The nonsignificant aggregate changes are not an
estimate of zero effect or equivalence.

This comparison changes **construction of D**, while denoising continues to use its base read policy, including
sink access. It does not identify denoising's direct use of the sink as harmful, or establish one pathway for all drift.

## Extra old KV during denoising

On LongLive, denoising retains the base 3 sink and newest 9 trajectory frames, including the current 3 frames.
From block b=4, we add self-only KV from the distinct trajectory blocks `{1, floor((b−2)/2), b−3}`, retaining their
original temporal positions. Each source block supplies 4,680 tokens.

- **A:** extra reads at denoising steps 3–4 of 4, layers 20–29.
- **B:** extra reads at all four denoising steps, layers 15–29.
- **A20:** A with each source block averaged over a 5×4 spatial grid and its three frames, giving 20 summary tokens.
  Keys are averaged after removing RoPE and positioned at the grid-cell and middle-frame positions. Each token is
  repeated 234 times to preserve the original token multiplicity.
- **A+R6:** A added to six-frame committing, with source KV obtained through separate self-only passes.

Blocks and layers are zero-indexed. A, B and A20 use self-only committing (S3); R6 reads the current and preceding
three-frame blocks. All videos last 60 seconds with generation seed 0. A uses all 200 rollf200 prompts; the other
contrasts use prompts 0–99. The following changes are in 0–100 points.

| Contrast | Prompts | Δ Quality | Δ Dynamic Degree | Δ Subject c2c | Δ Imaging | Δ Aesthetic |
|:---|---:|---:|---:|---:|---:|---:|
| A − S3 | 200 | −0.03 | +0.78 | +0.03 | −0.39* | −0.24* |
| B − S3 | 100 | +0.05 | +2.03 | +0.09 | −0.55* | −0.38* |
| A20 − S3 | 100 | +0.11* | +1.63* | −0.23 | +0.15* | −0.07 |
| (A+R6) − R6 | 100 | −0.12* | −0.43 | +0.07 | −0.50* | −0.21* |

No condition has a significant Subject c2c gain. A20 improves Quality, Dynamic Degree and Imaging Quality;
A, B and the add-on lower Imaging and Aesthetic Quality. The complete reported intervals remain in
[`summary.json`](summary.json), including the rounded-zero lower Imaging endpoint for A20; the asterisk uses
the original unrounded interval decision.

In an attention probe of A on prompts 3 and 41 at blocks 5, 15, …, 75, mean attention shares are 0.187 for extra
old KV, 0.106 for sink, 0.216 for recent history and 0.491 for the current block, averaged over A's steps and layers.
The added KV is attended but does not reproduce the 1.00-point Subject c2c gain of R6 over self-only committing.
Attention share is not a measurement of causal utility.

## Aggregate record

[`summary.json`](summary.json) transcribes the supplied manuscript's aggregate values and reported intervals.
It records the source commit and SHA-256 hashes of the two table sources and explanatory appendix. Missing
interval endpoints are stored as `null`; component changes reported only in prose retain no invented significance
label. No per-prompt measurements are added by this export.

```bash
python analysis/kv_construction/readout.py
```

The standard-library reader checks the aggregate schema and recorded interval bounds, then prints the readout.
It performs no generation, scoring or bootstrap reconstruction.
