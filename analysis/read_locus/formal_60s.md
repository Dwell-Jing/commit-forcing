# Independent denoising study: 60 s SF comparison

This historical comparison belongs to the separate distant-history reading study. The route reads distant history
at s2+s3, layers 12–29, and also changes the recent-window configuration relative to base SF. Both configurations
already commit from recent context. It is distinct from the 48 s, s3 × layers 20–29 confirmation in [read_locus](README.md).

200 rollf200 prompts, generation seeds 0 and 1. Per-video data remain in
[`results/vbench_long_60s.csv`](../../results/vbench_long_60s.csv); the existing table specs and outputs retain all comparisons.

| Model | Variant | Seed | Δ Quality | Δ Consistency |
|:---|:---|--:|:---|:---|
| Self-Forcing | far history in late denoising passes | 0 | −0.23&nbsp;[−0.92,&nbsp;+0.35] | +3.25* |
| Self-Forcing | far history in late denoising passes | 1 | +0.05&nbsp;[−0.43,&nbsp;+0.49] | +3.52* |

## Generation seed 0

Source: [table](../../results/tables/vbl60_seed0.txt) · [spec](../../results/specs/vbl60_seed0.json).

**Self-Forcing + far history in late denoising** vs **Self-Forcing**

| Metric | Self-Forcing | Self-Forcing + far history in late denoising | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 80.22 | 79.99 | −0.23&nbsp;[−0.92,&nbsp;+0.35] |
| Dynamic degree | 34.58 | 47.75 | +13.17*&nbsp;[+8.65,&nbsp;+17.52] |
| Motion smoothness | 98.43 | 97.48 | −0.95*&nbsp;[−1.40,&nbsp;−0.54] |
| Temporal flickering | 97.68 | 96.32 | −1.36*&nbsp;[−1.91,&nbsp;−0.89] |
| Imaging quality | 66.65 | 67.36 | +0.71&nbsp;[−0.25,&nbsp;+1.62] |
| Aesthetic quality | 56.85 | 57.15 | +0.30&nbsp;[−0.44,&nbsp;+1.01] |
| Subject consistency | 96.99 | 95.99 | −1.01*&nbsp;[−1.32,&nbsp;−0.74] |
| Background consistency | 96.29 | 95.55 | −0.74*&nbsp;[−0.87,&nbsp;−0.62] |
| Subject, within clips | 96.89 | 94.54 | −2.35*&nbsp;[−2.86,&nbsp;−1.87] |
| Subject, clip to clip (Consistency) | 74.22 | 77.47 | +3.25*&nbsp;[+2.13,&nbsp;+4.30] |
| Background, clip to clip | 77.22 | 83.39 | +6.17*&nbsp;[+5.35,&nbsp;+6.96] |

## Generation seed 1

Source: [table](../../results/tables/vbl60_seed1_b.txt) · [spec](../../results/specs/vbl60_seed1_b.json).

**Self-Forcing + far history in late denoising** vs **Self-Forcing**

| Metric | Self-Forcing | Self-Forcing + far history in late denoising | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 80.30 | 80.35 | +0.05&nbsp;[−0.43,&nbsp;+0.49] |
| Dynamic degree | 35.30 | 49.82 | +14.52*&nbsp;[+10.57,&nbsp;+18.38] |
| Motion smoothness | 98.55 | 97.71 | −0.85*&nbsp;[−1.16,&nbsp;−0.61] |
| Temporal flickering | 97.81 | 96.63 | −1.18*&nbsp;[−1.55,&nbsp;−0.89] |
| Imaging quality | 66.42 | 67.01 | +0.59&nbsp;[−0.33,&nbsp;+1.44] |
| Aesthetic quality | 56.55 | 57.10 | +0.55&nbsp;[−0.12,&nbsp;+1.23] |
| Subject consistency | 97.00 | 96.03 | −0.98*&nbsp;[−1.21,&nbsp;−0.75] |
| Background consistency | 96.22 | 95.58 | −0.65*&nbsp;[−0.76,&nbsp;−0.53] |
| Subject, within clips | 97.00 | 94.65 | −2.35*&nbsp;[−2.73,&nbsp;−1.98] |
| Subject, clip to clip (Consistency) | 73.53 | 77.05 | +3.52*&nbsp;[+2.47,&nbsp;+4.54] |
| Background, clip to clip | 77.11 | 83.34 | +6.24*&nbsp;[+5.54,&nbsp;+6.95] |

