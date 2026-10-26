# Committing variants and limited decoupling

This supplementary sweep accompanies the [window-effects analysis and correction-strength figure](../window_effects/README.md).
The original 27 points, full table and separate confirmations are retained below.

Changing committing can affect both long-range consistency and motion. This LongLive discovery sweep compares
27 variants with the line joining recent-context and self-only committing. Twenty-two reported intervals for
vertical departure from that reference include zero; five are below zero. Separate attention-sharpening
confirmations improve this comparison locally, with temporal-quality or motion costs.

[Scatter plot](../../assets/committing_tradeoff_variants.svg) · [PDF](../../assets/committing_tradeoff_variants.pdf)

## Discovery protocol and reference

All variants use the first 100 rollf200 prompts, 60-second videos and generation seed 0 on LongLive, preserving
base denoising. Changes below are relative to committing with the current and immediately preceding blocks
(6 latent frames). DD is Dynamic Degree, SC c2c is clip-to-clip Subject Consistency, and Q is Quality; values use
0–100 score points. Reported intervals use 4,000 paired prompt-bootstrap draws. An asterisk marks an interval
excluding zero. DD and SC stars are preserved even where the source table supplies no interval endpoints.

```text
G = Δ SC c2c − s × Δ DD
s = −1.00 / 3.63
```

The reference endpoints come from a separate 200-prompt comparison: self-only minus six-frame committing gives
Δ DD = +3.63 and Δ SC c2c = −1.00. The line is defined by these endpoints rather than fitted to the 27 discovery
means. An interval including zero does not establish equivalence or strict collinearity.

## All 27 discovery variants

| ID | Variant | Δ DD | Δ SC c2c | G [95% CI] | Δ Q [95% CI] |
|:---|:---|---:|---:|---:|---:|
| U | Uniform scaling | +0.50 | +0.03 | +0.17 [-0.27, +0.60] | +0.03 [-0.07, +0.13] |
| P | Frame averaging | -1.70 | -0.45* | -0.92 [-1.52, -0.35]* | -0.19 [-0.34, -0.06]* |
| M | Motion mask | -0.07 | -0.23 | -0.25 [-0.85, +0.34] | -0.07 [-0.21, +0.07] |
| Mr | Random mask | +0.43 | -0.11 | +0.01 [-0.52, +0.53] | +0.04 [-0.09, +0.16] |
| KR | Mixed K/V | -1.53 | +0.24 | -0.18 [-0.83, +0.44] | -0.09 [-0.25, +0.06] |
| SF0 | First frame only | -1.93* | +0.12 | -0.41 [-1.00, +0.14] | -0.16 [-0.30, -0.02]* |
| SF2 | Last frame only | +3.87* | -0.81* | +0.26 [-0.28, +0.79] | +0.08 [-0.07, +0.22] |
| ALT2 | Alternating 2 | +2.23* | -0.50* | +0.12 [-0.48, +0.74] | +0.04 [-0.10, +0.18] |
| ALT3 | Alternating 3 | +0.10 | -0.24 | -0.21 [-0.70, +0.28] | -0.07 [-0.18, +0.04] |
| CN30 | Commit noise 30 | +0.67 | -1.35* | -1.17 [-1.96, -0.40]* | +0.08 [-0.12, +0.27] |
| CN100 | Commit noise 100 | +1.03 | -0.71* | -0.42 [-1.01, +0.19] | -0.00 [-0.17, +0.17] |
| T15 | Sharpen 1.5 | -1.37 | +0.40* | +0.03 [-0.52, +0.59] | -0.11 [-0.25, +0.03] |
| T2 | Sharpen 2 | +1.63 | +0.08 | +0.53 [-0.20, +1.27] | -0.04 [-0.22, +0.14] |
| T3 | Sharpen 3 | +2.00 | -0.32 | +0.23 [-0.64, +1.08] | -0.12 [-0.34, +0.07] |
| T4 | Sharpen 4 | -0.23 | -0.95* | -1.01 [-2.03, +0.02] | -0.36 [-0.61, -0.11]* |
| AL | Global alignment | -0.33 | +0.07 | -0.02 [-0.46, +0.39] | -0.04 [-0.13, +0.06] |
| AL2 | Alignment 2x | +0.50 | -0.03 | +0.11 [-0.30, +0.53] | -0.03 [-0.13, +0.07] |
| ALr | Global random | +0.30 | +0.12 | +0.20 [-0.20, +0.59] | +0.03 [-0.06, +0.12] |
| ALL | Token alignment | -0.53 | +0.02 | -0.13 [-0.61, +0.39] | -0.08 [-0.20, +0.04] |
| ALLr | Token random | -0.17 | -0.10 | -0.15 [-0.67, +0.32] | -0.08 [-0.19, +0.03] |
| CM16 | 16 content regions | +1.90 | -0.53* | -0.01 [-0.61, +0.61] | -0.01 [-0.16, +0.14] |
| CM64 | 64 content regions | +1.87 | -0.45* | +0.06 [-0.56, +0.66] | -0.00 [-0.15, +0.15] |
| CG | Spatial mean per frame | +2.30 | -0.71* | -0.07 [-0.77, +0.62] | +0.02 [-0.15, +0.19] |
| SG16 | 16 spatial regions | +1.43 | -0.58* | -0.18 [-0.82, +0.44] | -0.04 [-0.19, +0.10] |
| FR | Sink correction | -5.87* | -2.07* | -3.69 [-4.70, -2.72]* | -0.64 [-0.90, -0.38]* |
| FP16 | Pooled sink correction | -4.37* | -1.76* | -2.97 [-3.92, -2.07]* | -0.42 [-0.68, -0.18]* |
| SFP16 | Self-only + pooled sink | -1.03 | -2.06* | -2.35 [-3.26, -1.43]* | -0.39 [-0.62, -0.16]* |

The five below-reference variants are P, CN30, FR, FP16 and SFP16. All observed coordinates and reported
G intervals are retained; the plot does not project points onto the reference line.

## Variant definitions

The recent-history correction is the difference between the outputs of recent-context and self-only committing.
The sink correction is the contribution introduced by sink access.

| ID | Intervention |
|:---|:---|
| U | Uniformly scale the recent-history correction to match the magnitude of frame averaging (P). |
| P | Average the recent-history correction across the current block's three frames. |
| M | Suppress the correction on the 30% of patches with greatest motion. |
| Mr | Suppress the correction on a random 30% of patches. |
| KR | Use K from recent-context committing and V from self-only committing. |
| SF0 | Allow history access only for the first frame of the current block. |
| SF2 | Allow history access only for the last frame of the current block. |
| ALT2 | Use self-only committing once every two blocks. |
| ALT3 | Use self-only committing once every three blocks. |
| CN30 | Commit at noise level 30 on the 0-1000 schedule. |
| CN100 | Commit at noise level 100 on the 0-1000 schedule. |
| T15 | Multiply historical attention logits by 1.5 while preserving total historical attention share. |
| T2 | Multiply historical attention logits by 2 while preserving total historical attention share. |
| T3 | Multiply historical attention logits by 3 while preserving total historical attention share. |
| T4 | Multiply historical attention logits by 4 while preserving total historical attention share. |
| AL | Apply the estimated global displacement to historical key positions. |
| AL2 | Apply twice the estimated global displacement to historical key positions. |
| ALr | Apply an equal-length displacement in a random direction. |
| ALL | Apply token-specific displacements to historical key positions. |
| ALLr | Apply matched token-specific displacements in random directions. |
| CM16 | Average the recent-history correction within 16 content regions in each frame. |
| CM64 | Average the recent-history correction within 64 content regions in each frame. |
| CG | Average the recent-history correction spatially within each frame. |
| SG16 | Average the recent-history correction in a 4x4 spatial grid. |
| FR | Add the sink-induced correction. |
| FP16 | Average the sink-induced correction within 16 content regions before adding it. |
| SFP16 | Add the regionally averaged sink-induced correction to self-only committing. |

FR and FP16 both remain below the reference. Averaging the sink correction within 16 content regions improves
G by +0.72 [+0.05, +1.37] relative to FR, but FP16 still has negative G. These regional interventions reduce
spatial detail while retaining regional information; they do not remove all geometry.

## Controls and separate confirmations

| Comparison | Protocol | Δ G [95% CI] |
|:---|:---|---:|
| Token relocation − random-direction control | LongLive, 100 prompts, seed 0 | +0.02 [−0.46, +0.51] |
| 16 content regions − 4×4 spatial regions | LongLive, 100 prompts, seed 0 | +0.17 [−0.16, +0.50] |
| Look-ahead windows − noise selection | LongLive, 40 prompts, seed 0 | −0.08 [−1.00, +0.88] |
| Attention sharpening, τ=2 − six-frame committing | LongLive, 200 prompts, new seeds 2 and 3 | +0.44* [+0.06, +0.81] |
| Attention sharpening, τ=2 − six-frame committing | CF, held-out prompts 100–199 | +0.97* [+0.29, +1.69] |

Look-ahead selection tests 3-, 6- and 12-frame windows by generating two future blocks and scoring DINO
consistency plus weighted RAFT motion. Its matched-compute control keeps a 6-frame window and chooses among
three noise samples with the same score. Both improve over the original six-frame rollout; their G difference
is not significant.

Attention sharpening multiplies historical logits while preserving total historical attention share. The
LongLive confirmation uses 400 paired videos across seeds 2 and 3; CF uses held-out prompts and its own
self-only–six-frame reference. These confirmations are separate from the discovery scatter.

| Sharpening comparison | Other reported changes (0–100 points) |
|:---|:---|
| LongLive confirmation | Quality −0.05 [−0.15, +0.05]; Temporal Flickering −0.29 |
| CF held-out confirmation | Quality −0.08 [−0.32, +0.18]; Dynamic Degree −3.17, significant |
| LongLive standard VBench suite | Total −0.06 [−0.22, +0.11]; Motion Smoothness −0.11 |

The costs here concern motion and temporal quality. No runtime cost estimate is supplied for sharpening in
these manuscript aggregates. The confirmation gains do not establish a general way to improve every measure.

## Extra old KV during denoising

The separate [extra-old-KV controls](../kv_construction/README.md#extra-old-kv-during-denoising) keep complete
Quality, Dynamic Degree, Subject c2c, Imaging and Aesthetic results and their recorded intervals. None has a
significant Subject c2c gain. A20 improves some quality components; other conditions have local quality losses.
These results remain separate from the 27 committing variants.

## Aggregate record

[`summary.json`](summary.json) transcribes the manuscript table and appendix at Overleaf commit
`6d6394380687d64fe505f050330f9118773a2e37`, with source SHA-256 hashes. Reported interval precision and
significance are preserved; unreported endpoints are `null`. It contains no per-prompt values, videos or
individual human responses.

```bash
python analysis/committing_variants/readout.py
```

The standard-library reader checks the aggregate schema, interval bounds, count of 27 unique variants and
22/5 interval split. It also checks G against the displayed means within their rounding precision. It does not
refit the reference, reconstruct confidence intervals or run generation, training or scoring.
