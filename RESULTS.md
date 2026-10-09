# Results

Scores ×100. **Base** is the original model; **+ Commit Forcing** applies Commit Forcing to the same model, with the
same initial noise. **Δ** is the paired difference over prompts, with its 95% bootstrap interval in brackets (4,000
resamples); `*` marks an interval that excludes 0. **Consistency** is VBench-Long's clip-to-clip subject consistency,
our measure of long-range consistency. † Our implementation of Recency Forcing's training-free reading.

[60 s videos](#60-s-videos) · [Full VBench](#full-vbench) · [Longer videos](#longer-videos) ·
[per-video data and commands](results/README.md) · [← Home](README.md)

## 60 s videos

VBench-Long, 200 [rollf200](eval/prompts/README.md) prompts, the protocol of Recency Forcing Tab. 3.

| Model | Base | + Commit Forcing | Δ Quality | Δ Consistency |
|:---|---:|---:|:---|:---|
| SGF | 83.58 | 84.62 | +1.04*&nbsp;[+0.67,&nbsp;+1.41] | +4.40*&nbsp;[+3.51,&nbsp;+5.27] |
| SGF + RF reading | 84.42 | 84.72 | +0.30*&nbsp;[+0.00,&nbsp;+0.61] | +3.35*&nbsp;[+2.55,&nbsp;+4.19] |
| SGF+ | 84.23 | 84.34 | +0.12&nbsp;[−0.26,&nbsp;+0.48] | +2.84*&nbsp;[+2.06,&nbsp;+3.59] |
| Recency Forcing, training-free † | 82.01 | 82.47 | +0.46*&nbsp;[+0.27,&nbsp;+0.65] | +3.86*&nbsp;[+3.22,&nbsp;+4.51] |
| LongLive | 82.23 | 82.65 | +0.42*&nbsp;[+0.27,&nbsp;+0.57] | +0.92*&nbsp;[+0.59,&nbsp;+1.26] |
| Context Forcing | 82.78 | 82.91 | +0.13&nbsp;[−0.10,&nbsp;+0.35] | +3.23*&nbsp;[+2.56,&nbsp;+3.94] |
| Rolling Sink | 82.61 | 82.72 | +0.11&nbsp;[−0.02,&nbsp;+0.24] | +0.67*&nbsp;[+0.18,&nbsp;+1.20] |
| ID-Forcing on Self-Forcing | 82.20 | 82.44 | +0.23*&nbsp;[+0.07,&nbsp;+0.40] | +2.53*&nbsp;[+1.99,&nbsp;+3.09] |
| ID-Forcing on LongLive | 82.54 | 82.45 | −0.09&nbsp;[−0.25,&nbsp;+0.06] | +2.05*&nbsp;[+1.46,&nbsp;+2.67] |

**Second generation seed.**

| Model | Base | + Commit Forcing | Δ Quality | Δ Consistency |
|:---|---:|---:|:---|:---|
| SGF | 83.85 | 84.71 | +0.86*&nbsp;[+0.52,&nbsp;+1.21] | +4.80*&nbsp;[+3.89,&nbsp;+5.79] |
| Recency Forcing, training-free † | 82.00 | 82.56 | +0.56*&nbsp;[+0.38,&nbsp;+0.73] | +4.30*&nbsp;[+3.64,&nbsp;+4.99] |
| LongLive | 82.19 | 82.67 | +0.48*&nbsp;[+0.33,&nbsp;+0.64] | +0.68*&nbsp;[+0.35,&nbsp;+1.01] |
| Context Forcing | 82.70 | 83.12 | +0.43*&nbsp;[+0.22,&nbsp;+0.64] | +3.53*&nbsp;[+2.83,&nbsp;+4.26] |
| Rolling Sink | 82.40 | 82.55 | +0.16*&nbsp;[+0.02,&nbsp;+0.30] | +0.98*&nbsp;[+0.58,&nbsp;+1.41] |
| ID-Forcing on Self-Forcing | 82.47 | 82.67 | +0.20*&nbsp;[+0.04,&nbsp;+0.37] | +2.27*&nbsp;[+1.70,&nbsp;+2.81] |

**Published entries of Recency Forcing Tab. 3**, and our evaluation of the same models:

| Method | Tab. 3 | Our evaluation |
|:---|--:|--:|
| Recency Forcing, trained | 84.02 | – |
| Recency Forcing, training-free | 82.63 | 82.01 † |
| Infinity-RoPE | 82.30 | – |
| Deep Forcing | 82.14 | – |
| LongLive | 81.98 | 82.23 |
| Rolling Forcing | 81.56 | – |
| Self-Forcing | 80.11 | 80.22 |
| Causal Forcing | 78.98 | – |

**Variants.** Each row compares a variant with the base model, unless the row names another reference. Late denoising passes: the last 2 of 4, layers 12–29.

| Model | Variant | Seed | Δ Quality | Δ Consistency |
|:---|:---|--:|:---|:---|
| SGF | + RF reading | 0 | +0.84*&nbsp;[+0.56,&nbsp;+1.14] | +1.17* |
| SGF | + Commit Forcing, compared with + RF reading | 0 | +0.20&nbsp;[−0.13,&nbsp;+0.55] | +3.23* |
| Context Forcing | no sink in the commit pass | 0 | +0.32*&nbsp;[+0.11,&nbsp;+0.54] | +1.80* |
| Context Forcing | no sink in the commit pass | 1 | +0.50*&nbsp;[+0.31,&nbsp;+0.69] | +1.61* |
| LongLive | commit pass reads only its own block | 0 | +0.49*&nbsp;[+0.29,&nbsp;+0.70] | +0.20 |
| LongLive | commit pass reads only its own block | 1 | +0.64*&nbsp;[+0.43,&nbsp;+0.85] | −0.11 |
| LongLive | commit pass reads the newest 6 frames | 0 | +0.49*&nbsp;[+0.33,&nbsp;+0.66] | +1.20* |
| LongLive | commit pass reads the newest 6 frames | 1 | +0.46*&nbsp;[+0.30,&nbsp;+0.64] | +1.06* |
| LongLive | commit pass reads the newest 9 frames | 0 | +0.48*&nbsp;[+0.33,&nbsp;+0.64] | +1.22* |
| Self-Forcing + sink | + Commit Forcing | 0 | +0.31&nbsp;[−0.30,&nbsp;+0.83] | +3.38* |
| Self-Forcing + sink | + Commit Forcing | 1 | +0.20&nbsp;[−0.28,&nbsp;+0.59] | +3.40* |
| Self-Forcing + sink | commit pass reads only its own block | 0 | −0.05&nbsp;[−0.71,&nbsp;+0.49] | −0.49 |
| Self-Forcing | far history in late denoising passes | 0 | −0.23&nbsp;[−0.92,&nbsp;+0.35] | +3.25* |
| Self-Forcing | far history in late denoising passes | 1 | +0.05&nbsp;[−0.43,&nbsp;+0.49] | +3.52* |
| Recency Forcing †, 2nd implementation | + Commit Forcing | 0 | +0.49*&nbsp;[+0.26,&nbsp;+0.72] | +4.71* |

<details>
<summary>All metrics, 60 s</summary>

<details>
<summary>Seed 0: Self-Forcing, Recency Forcing, LongLive, SGF, Context Forcing, Rolling Sink, ID-Forcing</summary>

Source: [`results/tables/vbl60_seed0.txt`](results/tables/vbl60_seed0.txt) · spec [`results/specs/vbl60_seed0.json`](results/specs/vbl60_seed0.json)

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

**Self-Forcing + sink + Commit Forcing** vs **Self-Forcing + sink**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.33 | 81.63 | +0.31&nbsp;[−0.30,&nbsp;+0.83] |
| Dynamic degree | 57.52 | 59.58 | +2.07&nbsp;[−0.38,&nbsp;+4.43] |
| Motion smoothness | 98.00 | 97.75 | −0.25&nbsp;[−0.77,&nbsp;+0.16] |
| Temporal flickering | 96.44 | 96.33 | −0.12&nbsp;[−0.51,&nbsp;+0.27] |
| Imaging quality | 67.08 | 68.03 | +0.95*&nbsp;[+0.29,&nbsp;+1.61] |
| Aesthetic quality | 57.61 | 58.41 | +0.80*&nbsp;[+0.32,&nbsp;+1.27] |
| Subject consistency | 96.72 | 96.87 | +0.15*&nbsp;[+0.01,&nbsp;+0.30] |
| Background consistency | 96.03 | 96.17 | +0.14*&nbsp;[+0.08,&nbsp;+0.20] |
| Subject, within clips | 96.27 | 96.19 | −0.08&nbsp;[−0.33,&nbsp;+0.16] |
| Subject, clip to clip (Consistency) | 75.18 | 78.56 | +3.38*&nbsp;[+2.73,&nbsp;+4.06] |
| Background, clip to clip | 80.64 | 83.31 | +2.66*&nbsp;[+2.24,&nbsp;+3.11] |

**Recency Forcing + Commit Forcing** vs **Recency Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.01 | 82.47 | +0.46*&nbsp;[+0.27,&nbsp;+0.65] |
| Dynamic degree | 63.20 | 63.93 | +0.73&nbsp;[−1.28,&nbsp;+2.83] |
| Motion smoothness | 98.19 | 98.12 | −0.07*&nbsp;[−0.13,&nbsp;−0.02] |
| Temporal flickering | 96.42 | 96.38 | −0.03&nbsp;[−0.12,&nbsp;+0.05] |
| Imaging quality | 68.11 | 68.91 | +0.80*&nbsp;[+0.38,&nbsp;+1.24] |
| Aesthetic quality | 57.99 | 59.58 | +1.59*&nbsp;[+1.20,&nbsp;+1.97] |
| Subject consistency | 96.59 | 96.83 | +0.24*&nbsp;[+0.15,&nbsp;+0.34] |
| Background consistency | 95.83 | 96.03 | +0.20*&nbsp;[+0.14,&nbsp;+0.25] |
| Subject, within clips | 96.01 | 96.05 | +0.04&nbsp;[−0.09,&nbsp;+0.17] |
| Subject, clip to clip (Consistency) | 75.02 | 78.88 | +3.86*&nbsp;[+3.22,&nbsp;+4.51] |
| Background, clip to clip | 80.79 | 83.51 | +2.72*&nbsp;[+2.31,&nbsp;+3.13] |

**ID-Forcing on Self-Forcing + Commit Forcing** vs **ID-Forcing on Self-Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.20 | 82.44 | +0.23*&nbsp;[+0.07,&nbsp;+0.40] |
| Dynamic degree | 61.95 | 60.78 | −1.17&nbsp;[−3.27,&nbsp;+0.98] |
| Motion smoothness | 97.90 | 98.01 | +0.11*&nbsp;[+0.07,&nbsp;+0.16] |
| Temporal flickering | 96.17 | 96.39 | +0.22*&nbsp;[+0.15,&nbsp;+0.29] |
| Imaging quality | 69.30 | 69.55 | +0.26&nbsp;[−0.06,&nbsp;+0.60] |
| Aesthetic quality | 59.32 | 59.86 | +0.54*&nbsp;[+0.27,&nbsp;+0.82] |
| Subject consistency | 97.03 | 97.22 | +0.19*&nbsp;[+0.11,&nbsp;+0.27] |
| Background consistency | 96.24 | 96.31 | +0.07*&nbsp;[+0.03,&nbsp;+0.12] |
| Subject, within clips | 96.39 | 96.50 | +0.11&nbsp;[−0.00,&nbsp;+0.24] |
| Subject, clip to clip (Consistency) | 79.07 | 81.60 | +2.53*&nbsp;[+1.99,&nbsp;+3.09] |
| Background, clip to clip | 84.42 | 86.21 | +1.79*&nbsp;[+1.44,&nbsp;+2.14] |

**Self-Forcing + sink, commit pass reads only its block** vs **Self-Forcing + sink**

| Metric | Self-Forcing + sink | Self-Forcing + sink, commit pass reads only its block | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.33 | 81.28 | −0.05&nbsp;[−0.71,&nbsp;+0.49] |
| Dynamic degree | 57.52 | 67.80 | +10.28*&nbsp;[+6.53,&nbsp;+13.88] |
| Motion smoothness | 98.00 | 97.30 | −0.70*&nbsp;[−1.19,&nbsp;−0.33] |
| Temporal flickering | 96.44 | 95.47 | −0.97*&nbsp;[−1.40,&nbsp;−0.61] |
| Imaging quality | 67.08 | 67.14 | +0.05&nbsp;[−0.85,&nbsp;+0.91] |
| Aesthetic quality | 57.61 | 57.45 | −0.16&nbsp;[−0.81,&nbsp;+0.45] |
| Subject consistency | 96.72 | 96.56 | −0.16&nbsp;[−0.36,&nbsp;+0.04] |
| Background consistency | 96.03 | 95.93 | −0.10*&nbsp;[−0.19,&nbsp;−0.01] |
| Subject, within clips | 96.27 | 96.01 | −0.26&nbsp;[−0.59,&nbsp;+0.07] |
| Subject, clip to clip (Consistency) | 75.18 | 74.69 | −0.49&nbsp;[−1.51,&nbsp;+0.55] |
| Background, clip to clip | 80.64 | 81.33 | +0.69*&nbsp;[+0.02,&nbsp;+1.41] |

**Self-Forcing + sink + Commit Forcing** vs **Self-Forcing + sink, commit pass reads only its block**

| Metric | Self-Forcing + sink, commit pass reads only its block | Self-Forcing + sink + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.28 | 81.63 | +0.36&nbsp;[−0.16,&nbsp;+0.81] |
| Dynamic degree | 67.80 | 59.58 | −8.22*&nbsp;[−11.67,&nbsp;−4.90] |
| Motion smoothness | 97.30 | 97.75 | +0.46*&nbsp;[+0.13,&nbsp;+0.75] |
| Temporal flickering | 95.47 | 96.33 | +0.85*&nbsp;[+0.50,&nbsp;+1.20] |
| Imaging quality | 67.14 | 68.03 | +0.90*&nbsp;[+0.23,&nbsp;+1.58] |
| Aesthetic quality | 57.45 | 58.41 | +0.96*&nbsp;[+0.41,&nbsp;+1.54] |
| Subject consistency | 96.56 | 96.87 | +0.32*&nbsp;[+0.11,&nbsp;+0.51] |
| Background consistency | 95.93 | 96.17 | +0.24*&nbsp;[+0.15,&nbsp;+0.33] |
| Subject, within clips | 96.01 | 96.19 | +0.18&nbsp;[−0.16,&nbsp;+0.51] |
| Subject, clip to clip (Consistency) | 74.69 | 78.56 | +3.87*&nbsp;[+2.82,&nbsp;+4.86] |
| Background, clip to clip | 81.33 | 83.31 | +1.97*&nbsp;[+1.32,&nbsp;+2.62] |

**LongLive + Commit Forcing** vs **LongLive**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.23 | 82.65 | +0.42*&nbsp;[+0.27,&nbsp;+0.57] |
| Dynamic degree | 42.98 | 49.38 | +6.40*&nbsp;[+4.43,&nbsp;+8.57] |
| Motion smoothness | 98.74 | 98.59 | −0.15*&nbsp;[−0.19,&nbsp;−0.12] |
| Temporal flickering | 97.61 | 97.37 | −0.24*&nbsp;[−0.30,&nbsp;−0.18] |
| Imaging quality | 68.69 | 69.39 | +0.69*&nbsp;[+0.45,&nbsp;+0.96] |
| Aesthetic quality | 61.53 | 61.68 | +0.15&nbsp;[−0.05,&nbsp;+0.34] |
| Subject consistency | 97.76 | 97.70 | −0.06*&nbsp;[−0.11,&nbsp;−0.02] |
| Background consistency | 96.54 | 96.49 | −0.05*&nbsp;[−0.09,&nbsp;−0.02] |
| Subject, within clips | 97.13 | 96.92 | −0.22*&nbsp;[−0.29,&nbsp;−0.15] |
| Subject, clip to clip (Consistency) | 86.01 | 86.93 | +0.92*&nbsp;[+0.59,&nbsp;+1.26] |
| Background, clip to clip | 88.40 | 89.17 | +0.77*&nbsp;[+0.56,&nbsp;+0.96] |

**ID-Forcing on LongLive + Commit Forcing** vs **ID-Forcing on LongLive**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.54 | 82.45 | −0.09&nbsp;[−0.25,&nbsp;+0.06] |
| Dynamic degree | 52.52 | 47.05 | −5.47*&nbsp;[−7.73,&nbsp;−3.33] |
| Motion smoothness | 98.50 | 98.65 | +0.15*&nbsp;[+0.10,&nbsp;+0.21] |
| Temporal flickering | 97.00 | 97.37 | +0.38*&nbsp;[+0.27,&nbsp;+0.50] |
| Imaging quality | 69.23 | 69.26 | +0.03&nbsp;[−0.32,&nbsp;+0.36] |
| Aesthetic quality | 60.93 | 61.10 | +0.17&nbsp;[−0.12,&nbsp;+0.46] |
| Subject consistency | 97.69 | 97.84 | +0.15*&nbsp;[+0.09,&nbsp;+0.23] |
| Background consistency | 96.46 | 96.61 | +0.15*&nbsp;[+0.10,&nbsp;+0.21] |
| Subject, within clips | 97.28 | 97.41 | +0.13*&nbsp;[+0.03,&nbsp;+0.23] |
| Subject, clip to clip (Consistency) | 82.83 | 84.88 | +2.05*&nbsp;[+1.46,&nbsp;+2.67] |
| Background, clip to clip | 86.21 | 87.83 | +1.62*&nbsp;[+1.24,&nbsp;+2.00] |

**LongLive, commit pass reads only its block** vs **LongLive**

| Metric | LongLive | LongLive, commit pass reads only its block | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.23 | 82.73 | +0.49*&nbsp;[+0.29,&nbsp;+0.70] |
| Dynamic degree | 42.98 | 53.03 | +10.05*&nbsp;[+7.28,&nbsp;+12.80] |
| Motion smoothness | 98.74 | 98.46 | −0.28*&nbsp;[−0.34,&nbsp;−0.22] |
| Temporal flickering | 97.61 | 97.11 | −0.50*&nbsp;[−0.60,&nbsp;−0.40] |
| Imaging quality | 68.69 | 69.18 | +0.49*&nbsp;[+0.15,&nbsp;+0.83] |
| Aesthetic quality | 61.53 | 61.66 | +0.13&nbsp;[−0.15,&nbsp;+0.40] |
| Subject consistency | 97.76 | 97.69 | −0.06&nbsp;[−0.13,&nbsp;+0.01] |
| Background consistency | 96.54 | 96.52 | −0.02&nbsp;[−0.07,&nbsp;+0.02] |
| Subject, within clips | 97.13 | 96.98 | −0.15*&nbsp;[−0.25,&nbsp;−0.05] |
| Subject, clip to clip (Consistency) | 86.01 | 86.21 | +0.20&nbsp;[−0.26,&nbsp;+0.69] |
| Background, clip to clip | 88.40 | 88.79 | +0.39*&nbsp;[+0.10,&nbsp;+0.70] |

**LongLive + Commit Forcing** vs **LongLive, commit pass reads only its block**

| Metric | LongLive, commit pass reads only its block | LongLive + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.73 | 82.65 | −0.08&nbsp;[−0.21,&nbsp;+0.06] |
| Dynamic degree | 53.03 | 49.38 | −3.65*&nbsp;[−5.50,&nbsp;−1.83] |
| Motion smoothness | 98.46 | 98.59 | +0.13*&nbsp;[+0.09,&nbsp;+0.17] |
| Temporal flickering | 97.11 | 97.37 | +0.26*&nbsp;[+0.19,&nbsp;+0.33] |
| Imaging quality | 69.18 | 69.39 | +0.20&nbsp;[−0.01,&nbsp;+0.42] |
| Aesthetic quality | 61.66 | 61.68 | +0.02&nbsp;[−0.17,&nbsp;+0.21] |
| Subject consistency | 97.69 | 97.70 | +0.00&nbsp;[−0.05,&nbsp;+0.06] |
| Background consistency | 96.52 | 96.49 | −0.03&nbsp;[−0.07,&nbsp;+0.01] |
| Subject, within clips | 96.98 | 96.92 | −0.07&nbsp;[−0.15,&nbsp;+0.01] |
| Subject, clip to clip (Consistency) | 86.21 | 86.93 | +0.72*&nbsp;[+0.32,&nbsp;+1.13] |
| Background, clip to clip | 88.79 | 89.17 | +0.38*&nbsp;[+0.15,&nbsp;+0.60] |

**SGF + Commit Forcing** vs **SGF**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.58 | 84.62 | +1.04*&nbsp;[+0.67,&nbsp;+1.41] |
| Dynamic degree | 54.92 | 68.30 | +13.38*&nbsp;[+8.73,&nbsp;+17.93] |
| Motion smoothness | 98.64 | 98.43 | −0.21*&nbsp;[−0.29,&nbsp;−0.13] |
| Temporal flickering | 97.32 | 96.88 | −0.44*&nbsp;[−0.59,&nbsp;−0.29] |
| Imaging quality | 70.83 | 71.19 | +0.36&nbsp;[−0.23,&nbsp;+0.91] |
| Aesthetic quality | 62.83 | 63.94 | +1.10*&nbsp;[+0.53,&nbsp;+1.67] |
| Subject consistency | 98.03 | 98.29 | +0.26*&nbsp;[+0.18,&nbsp;+0.33] |
| Background consistency | 96.71 | 96.84 | +0.13*&nbsp;[+0.05,&nbsp;+0.22] |
| Subject, within clips | 97.57 | 97.69 | +0.11&nbsp;[−0.00,&nbsp;+0.23] |
| Subject, clip to clip (Consistency) | 86.54 | 90.93 | +4.40*&nbsp;[+3.51,&nbsp;+5.27] |
| Background, clip to clip | 89.78 | 92.46 | +2.68*&nbsp;[+2.20,&nbsp;+3.17] |

**Recency Forcing, 2nd implementation + Commit Forcing** vs **Recency Forcing, 2nd implementation**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.89 | 82.38 | +0.49*&nbsp;[+0.26,&nbsp;+0.72] |
| Dynamic degree | 62.13 | 62.65 | +0.52&nbsp;[−1.78,&nbsp;+2.77] |
| Motion smoothness | 98.21 | 98.11 | −0.10*&nbsp;[−0.18,&nbsp;−0.03] |
| Temporal flickering | 96.42 | 96.38 | −0.04&nbsp;[−0.16,&nbsp;+0.08] |
| Imaging quality | 68.04 | 69.03 | +0.99*&nbsp;[+0.45,&nbsp;+1.53] |
| Aesthetic quality | 57.78 | 59.40 | +1.61*&nbsp;[+1.10,&nbsp;+2.11] |
| Subject consistency | 96.57 | 96.91 | +0.33*&nbsp;[+0.22,&nbsp;+0.45] |
| Background consistency | 95.80 | 96.07 | +0.27*&nbsp;[+0.20,&nbsp;+0.34] |
| Subject, within clips | 96.02 | 96.13 | +0.11&nbsp;[−0.04,&nbsp;+0.26] |
| Subject, clip to clip (Consistency) | 74.75 | 79.46 | +4.71*&nbsp;[+3.78,&nbsp;+5.64] |
| Background, clip to clip | 80.58 | 84.03 | +3.45*&nbsp;[+2.89,&nbsp;+4.04] |

**Context Forcing + Commit Forcing** vs **Context Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.78 | 82.91 | +0.13&nbsp;[−0.10,&nbsp;+0.35] |
| Dynamic degree | 60.62 | 59.57 | −1.05&nbsp;[−4.05,&nbsp;+1.92] |
| Motion smoothness | 98.40 | 98.28 | −0.12*&nbsp;[−0.20,&nbsp;−0.03] |
| Temporal flickering | 97.01 | 96.94 | −0.06&nbsp;[−0.20,&nbsp;+0.08] |
| Imaging quality | 67.81 | 68.50 | +0.69*&nbsp;[+0.27,&nbsp;+1.10] |
| Aesthetic quality | 60.60 | 61.21 | +0.61*&nbsp;[+0.21,&nbsp;+0.99] |
| Subject consistency | 97.36 | 97.65 | +0.30*&nbsp;[+0.21,&nbsp;+0.38] |
| Background consistency | 96.44 | 96.65 | +0.20*&nbsp;[+0.14,&nbsp;+0.27] |
| Subject, within clips | 97.15 | 97.33 | +0.19*&nbsp;[+0.04,&nbsp;+0.33] |
| Subject, clip to clip (Consistency) | 78.72 | 81.95 | +3.23*&nbsp;[+2.56,&nbsp;+3.94] |
| Background, clip to clip | 82.29 | 85.08 | +2.79*&nbsp;[+2.28,&nbsp;+3.29] |

**Context Forcing, sink out of the commit pass only** vs **Context Forcing**

| Metric | Context Forcing | Context Forcing, sink out of the commit pass only | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.78 | 83.11 | +0.32*&nbsp;[+0.11,&nbsp;+0.54] |
| Dynamic degree | 60.62 | 67.32 | +6.70*&nbsp;[+4.08,&nbsp;+9.20] |
| Motion smoothness | 98.40 | 98.18 | −0.22*&nbsp;[−0.29,&nbsp;−0.16] |
| Temporal flickering | 97.01 | 96.64 | −0.37*&nbsp;[−0.48,&nbsp;−0.25] |
| Imaging quality | 67.81 | 68.13 | +0.32&nbsp;[−0.03,&nbsp;+0.69] |
| Aesthetic quality | 60.60 | 60.80 | +0.20&nbsp;[−0.14,&nbsp;+0.57] |
| Subject consistency | 97.36 | 97.36 | +0.00&nbsp;[−0.08,&nbsp;+0.08] |
| Background consistency | 96.44 | 96.43 | −0.02&nbsp;[−0.07,&nbsp;+0.04] |
| Subject, within clips | 97.15 | 96.92 | −0.22*&nbsp;[−0.35,&nbsp;−0.11] |
| Subject, clip to clip (Consistency) | 78.72 | 80.52 | +1.80*&nbsp;[+1.20,&nbsp;+2.42] |
| Background, clip to clip | 82.29 | 84.09 | +1.80*&nbsp;[+1.36,&nbsp;+2.24] |

**Rolling Sink + Commit Forcing** vs **Rolling Sink**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.61 | 82.72 | +0.11&nbsp;[−0.02,&nbsp;+0.24] |
| Dynamic degree | 45.85 | 49.53 | +3.68*&nbsp;[+1.75,&nbsp;+5.58] |
| Motion smoothness | 98.69 | 98.57 | −0.12*&nbsp;[−0.15,&nbsp;−0.09] |
| Temporal flickering | 97.76 | 97.53 | −0.23*&nbsp;[−0.28,&nbsp;−0.18] |
| Imaging quality | 70.01 | 70.01 | −0.01&nbsp;[−0.28,&nbsp;+0.30] |
| Aesthetic quality | 60.58 | 60.78 | +0.20&nbsp;[−0.05,&nbsp;+0.50] |
| Subject consistency | 97.93 | 97.79 | −0.15*&nbsp;[−0.21,&nbsp;−0.09] |
| Background consistency | 96.74 | 96.64 | −0.10*&nbsp;[−0.14,&nbsp;−0.06] |
| Subject, within clips | 97.49 | 97.15 | −0.34*&nbsp;[−0.43,&nbsp;−0.25] |
| Subject, clip to clip (Consistency) | 86.00 | 86.67 | +0.67*&nbsp;[+0.18,&nbsp;+1.20] |
| Background, clip to clip | 88.82 | 89.39 | +0.57*&nbsp;[+0.25,&nbsp;+0.90] |

</details>

<details>
<summary>Seed 0: SGF and SGF + RF reading</summary>

Source: [`results/tables/vbl60_sgf_rf.txt`](results/tables/vbl60_sgf_rf.txt) · spec [`results/specs/vbl60_sgf_rf.json`](results/specs/vbl60_sgf_rf.json)

**SGF + Commit Forcing** vs **SGF**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.58 | 84.62 | +1.04*&nbsp;[+0.67,&nbsp;+1.40] |
| Dynamic degree | 54.92 | 68.30 | +13.38*&nbsp;[+8.70,&nbsp;+18.05] |
| Motion smoothness | 98.64 | 98.43 | −0.21*&nbsp;[−0.29,&nbsp;−0.13] |
| Temporal flickering | 97.32 | 96.88 | −0.44*&nbsp;[−0.59,&nbsp;−0.29] |
| Imaging quality | 70.83 | 71.19 | +0.36&nbsp;[−0.21,&nbsp;+0.93] |
| Aesthetic quality | 62.83 | 63.94 | +1.10*&nbsp;[+0.54,&nbsp;+1.70] |
| Subject consistency | 98.03 | 98.29 | +0.26*&nbsp;[+0.18,&nbsp;+0.34] |
| Background consistency | 96.71 | 96.84 | +0.13*&nbsp;[+0.05,&nbsp;+0.21] |
| Subject, within clips | 97.57 | 97.69 | +0.11*&nbsp;[+0.00,&nbsp;+0.22] |
| Subject, clip to clip (Consistency) | 86.54 | 90.93 | +4.40*&nbsp;[+3.54,&nbsp;+5.25] |
| Background, clip to clip | 89.78 | 92.46 | +2.68*&nbsp;[+2.19,&nbsp;+3.18] |

**SGF + RF reading** vs **SGF**

| Metric | SGF | SGF + RF reading | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.58 | 84.42 | +0.84*&nbsp;[+0.56,&nbsp;+1.14] |
| Dynamic degree | 54.92 | 66.67 | +11.75*&nbsp;[+8.25,&nbsp;+15.43] |
| Motion smoothness | 98.64 | 98.56 | −0.07*&nbsp;[−0.12,&nbsp;−0.03] |
| Temporal flickering | 97.32 | 97.07 | −0.25*&nbsp;[−0.34,&nbsp;−0.16] |
| Imaging quality | 70.83 | 71.03 | +0.21&nbsp;[−0.29,&nbsp;+0.71] |
| Aesthetic quality | 62.83 | 63.31 | +0.47&nbsp;[−0.07,&nbsp;+1.00] |
| Subject consistency | 98.03 | 97.97 | −0.06&nbsp;[−0.14,&nbsp;+0.02] |
| Background consistency | 96.71 | 96.62 | −0.09*&nbsp;[−0.16,&nbsp;−0.02] |
| Subject, within clips | 97.57 | 97.34 | −0.23*&nbsp;[−0.34,&nbsp;−0.12] |
| Subject, clip to clip (Consistency) | 86.54 | 87.71 | +1.17*&nbsp;[+0.33,&nbsp;+2.02] |
| Background, clip to clip | 89.78 | 90.39 | +0.61*&nbsp;[+0.18,&nbsp;+1.05] |

**SGF + RF reading + Commit Forcing** vs **SGF + RF reading**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 84.42 | 84.72 | +0.30*&nbsp;[+0.00,&nbsp;+0.61] |
| Dynamic degree | 66.67 | 69.52 | +2.85&nbsp;[−0.97,&nbsp;+6.53] |
| Motion smoothness | 98.56 | 98.49 | −0.08*&nbsp;[−0.13,&nbsp;−0.03] |
| Temporal flickering | 97.07 | 96.94 | −0.13*&nbsp;[−0.23,&nbsp;−0.03] |
| Imaging quality | 71.03 | 71.02 | −0.02&nbsp;[−0.57,&nbsp;+0.54] |
| Aesthetic quality | 63.31 | 63.84 | +0.53*&nbsp;[+0.02,&nbsp;+1.04] |
| Subject consistency | 97.97 | 98.23 | +0.26*&nbsp;[+0.18,&nbsp;+0.34] |
| Background consistency | 96.62 | 96.85 | +0.23*&nbsp;[+0.16,&nbsp;+0.31] |
| Subject, within clips | 97.34 | 97.57 | +0.23*&nbsp;[+0.12,&nbsp;+0.34] |
| Subject, clip to clip (Consistency) | 87.71 | 91.06 | +3.35*&nbsp;[+2.55,&nbsp;+4.19] |
| Background, clip to clip | 90.39 | 92.53 | +2.14*&nbsp;[+1.59,&nbsp;+2.70] |

**SGF + RF reading + Commit Forcing** vs **SGF + Commit Forcing**

| Metric | SGF + Commit Forcing | SGF + RF reading + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 84.62 | 84.72 | +0.10&nbsp;[−0.19,&nbsp;+0.39] |
| Dynamic degree | 68.30 | 69.52 | +1.22&nbsp;[−2.48,&nbsp;+5.02] |
| Motion smoothness | 98.43 | 98.49 | +0.06*&nbsp;[+0.00,&nbsp;+0.11] |
| Temporal flickering | 96.88 | 96.94 | +0.06&nbsp;[−0.04,&nbsp;+0.17] |
| Imaging quality | 71.19 | 71.02 | −0.17&nbsp;[−0.66,&nbsp;+0.31] |
| Aesthetic quality | 63.94 | 63.84 | −0.10&nbsp;[−0.57,&nbsp;+0.39] |
| Subject consistency | 98.29 | 98.23 | −0.05&nbsp;[−0.13,&nbsp;+0.03] |
| Background consistency | 96.84 | 96.85 | +0.01&nbsp;[−0.06,&nbsp;+0.09] |
| Subject, within clips | 97.69 | 97.57 | −0.12*&nbsp;[−0.23,&nbsp;−0.01] |
| Subject, clip to clip (Consistency) | 90.93 | 91.06 | +0.12&nbsp;[−0.53,&nbsp;+0.78] |
| Background, clip to clip | 92.46 | 92.53 | +0.07&nbsp;[−0.33,&nbsp;+0.46] |

**SGF + Commit Forcing** vs **SGF + RF reading**

| Metric | SGF + RF reading | SGF + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 84.42 | 84.62 | +0.20&nbsp;[−0.13,&nbsp;+0.55] |
| Dynamic degree | 66.67 | 68.30 | +1.63&nbsp;[−2.83,&nbsp;+5.90] |
| Motion smoothness | 98.56 | 98.43 | −0.13*&nbsp;[−0.21,&nbsp;−0.07] |
| Temporal flickering | 97.07 | 96.88 | −0.19*&nbsp;[−0.32,&nbsp;−0.07] |
| Imaging quality | 71.03 | 71.19 | +0.15&nbsp;[−0.31,&nbsp;+0.62] |
| Aesthetic quality | 63.31 | 63.94 | +0.63*&nbsp;[+0.11,&nbsp;+1.14] |
| Subject consistency | 97.97 | 98.29 | +0.31*&nbsp;[+0.23,&nbsp;+0.39] |
| Background consistency | 96.62 | 96.84 | +0.22*&nbsp;[+0.14,&nbsp;+0.30] |
| Subject, within clips | 97.34 | 97.69 | +0.34*&nbsp;[+0.23,&nbsp;+0.45] |
| Subject, clip to clip (Consistency) | 87.71 | 90.93 | +3.23*&nbsp;[+2.38,&nbsp;+4.09] |
| Background, clip to clip | 90.39 | 92.46 | +2.07*&nbsp;[+1.55,&nbsp;+2.59] |

</details>

<details>
<summary>Seed 0: SGF+</summary>

Source: [`results/tables/vbl60_sgf_plus.txt`](results/tables/vbl60_sgf_plus.txt) · spec [`results/specs/vbl60_sgf_plus.json`](results/specs/vbl60_sgf_plus.json)

**SGF+ + Commit Forcing** vs **SGF+**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 84.23 | 84.34 | +0.12&nbsp;[−0.26,&nbsp;+0.48] |
| Dynamic degree | 55.32 | 59.58 | +4.27&nbsp;[−0.85,&nbsp;+9.10] |
| Motion smoothness | 98.77 | 98.57 | −0.20*&nbsp;[−0.29,&nbsp;−0.12] |
| Temporal flickering | 97.80 | 97.49 | −0.30*&nbsp;[−0.45,&nbsp;−0.16] |
| Imaging quality | 71.47 | 71.15 | −0.32&nbsp;[−0.94,&nbsp;+0.32] |
| Aesthetic quality | 63.82 | 63.87 | +0.04&nbsp;[−0.51,&nbsp;+0.62] |
| Subject consistency | 98.28 | 98.44 | +0.16*&nbsp;[+0.07,&nbsp;+0.24] |
| Background consistency | 96.93 | 97.09 | +0.16*&nbsp;[+0.08,&nbsp;+0.24] |
| Subject, within clips | 97.78 | 97.87 | +0.09&nbsp;[−0.05,&nbsp;+0.22] |
| Subject, clip to clip (Consistency) | 89.83 | 92.66 | +2.84*&nbsp;[+2.06,&nbsp;+3.59] |
| Background, clip to clip | 91.85 | 94.02 | +2.17*&nbsp;[+1.69,&nbsp;+2.67] |

</details>

<details>
<summary>Seed 0: LongLive, commit window</summary>

Source: [`results/tables/vbl60_longlive_commit_window.txt`](results/tables/vbl60_longlive_commit_window.txt) · spec [`results/specs/vbl60_longlive_commit_window.json`](results/specs/vbl60_longlive_commit_window.json)

**LongLive, commit pass reads the newest 6 frames** vs **LongLive**

| Metric | LongLive | LongLive, commit pass reads the newest 6 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.23 | 82.73 | +0.49*&nbsp;[+0.33,&nbsp;+0.66] |
| Dynamic degree | 42.98 | 49.40 | +6.42*&nbsp;[+4.27,&nbsp;+8.58] |
| Motion smoothness | 98.74 | 98.61 | −0.14*&nbsp;[−0.18,&nbsp;−0.10] |
| Temporal flickering | 97.61 | 97.42 | −0.19*&nbsp;[−0.26,&nbsp;−0.12] |
| Imaging quality | 68.69 | 69.29 | +0.60*&nbsp;[+0.33,&nbsp;+0.88] |
| Aesthetic quality | 61.53 | 61.75 | +0.22&nbsp;[−0.01,&nbsp;+0.43] |
| Subject consistency | 97.76 | 97.82 | +0.06*&nbsp;[+0.01,&nbsp;+0.11] |
| Background consistency | 96.54 | 96.63 | +0.08*&nbsp;[+0.04,&nbsp;+0.12] |
| Subject, within clips | 97.13 | 97.14 | +0.01&nbsp;[−0.07,&nbsp;+0.09] |
| Subject, clip to clip (Consistency) | 86.01 | 87.21 | +1.20*&nbsp;[+0.84,&nbsp;+1.58] |
| Background, clip to clip | 88.40 | 89.53 | +1.13*&nbsp;[+0.90,&nbsp;+1.37] |

**LongLive, commit pass reads the newest 9 frames** vs **LongLive**

| Metric | LongLive | LongLive, commit pass reads the newest 9 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.23 | 82.72 | +0.48*&nbsp;[+0.33,&nbsp;+0.64] |
| Dynamic degree | 42.98 | 49.47 | +6.48*&nbsp;[+4.42,&nbsp;+8.52] |
| Motion smoothness | 98.74 | 98.62 | −0.13*&nbsp;[−0.17,&nbsp;−0.09] |
| Temporal flickering | 97.61 | 97.44 | −0.17*&nbsp;[−0.24,&nbsp;−0.11] |
| Imaging quality | 68.69 | 69.32 | +0.63*&nbsp;[+0.37,&nbsp;+0.89] |
| Aesthetic quality | 61.53 | 61.66 | +0.13&nbsp;[−0.07,&nbsp;+0.33] |
| Subject consistency | 97.76 | 97.77 | +0.01&nbsp;[−0.04,&nbsp;+0.06] |
| Background consistency | 96.54 | 96.57 | +0.03&nbsp;[−0.01,&nbsp;+0.07] |
| Subject, within clips | 97.13 | 97.04 | −0.10*&nbsp;[−0.17,&nbsp;−0.03] |
| Subject, clip to clip (Consistency) | 86.01 | 87.23 | +1.22*&nbsp;[+0.88,&nbsp;+1.56] |
| Background, clip to clip | 88.40 | 89.55 | +1.15*&nbsp;[+0.94,&nbsp;+1.37] |

**LongLive, commit pass reads the newest 6 frames** vs **LongLive, commit pass reads only its block**

| Metric | LongLive, commit pass reads only its block | LongLive, commit pass reads the newest 6 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.73 | 82.73 | +0.00&nbsp;[−0.12,&nbsp;+0.12] |
| Dynamic degree | 53.03 | 49.40 | −3.63*&nbsp;[−5.23,&nbsp;−2.03] |
| Motion smoothness | 98.46 | 98.61 | +0.15*&nbsp;[+0.11,&nbsp;+0.18] |
| Temporal flickering | 97.11 | 97.42 | +0.31*&nbsp;[+0.24,&nbsp;+0.37] |
| Imaging quality | 69.18 | 69.29 | +0.11&nbsp;[−0.09,&nbsp;+0.31] |
| Aesthetic quality | 61.66 | 61.75 | +0.09&nbsp;[−0.06,&nbsp;+0.25] |
| Subject consistency | 97.69 | 97.82 | +0.13*&nbsp;[+0.08,&nbsp;+0.17] |
| Background consistency | 96.52 | 96.63 | +0.11*&nbsp;[+0.07,&nbsp;+0.14] |
| Subject, within clips | 96.98 | 97.14 | +0.16*&nbsp;[+0.10,&nbsp;+0.22] |
| Subject, clip to clip (Consistency) | 86.21 | 87.21 | +1.00*&nbsp;[+0.68,&nbsp;+1.34] |
| Background, clip to clip | 88.79 | 89.53 | +0.74*&nbsp;[+0.56,&nbsp;+0.93] |

**LongLive, commit pass reads the newest 9 frames** vs **LongLive, commit pass reads the newest 6 frames**

| Metric | LongLive, commit pass reads the newest 6 frames | LongLive, commit pass reads the newest 9 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.73 | 82.72 | −0.01&nbsp;[−0.09,&nbsp;+0.07] |
| Dynamic degree | 49.40 | 49.47 | +0.07&nbsp;[−1.03,&nbsp;+1.20] |
| Motion smoothness | 98.61 | 98.62 | +0.01&nbsp;[−0.01,&nbsp;+0.03] |
| Temporal flickering | 97.42 | 97.44 | +0.02&nbsp;[−0.01,&nbsp;+0.05] |
| Imaging quality | 69.29 | 69.32 | +0.03&nbsp;[−0.08,&nbsp;+0.15] |
| Aesthetic quality | 61.75 | 61.66 | −0.09&nbsp;[−0.21,&nbsp;+0.04] |
| Subject consistency | 97.82 | 97.77 | −0.05*&nbsp;[−0.09,&nbsp;−0.01] |
| Background consistency | 96.63 | 96.57 | −0.05*&nbsp;[−0.08,&nbsp;−0.03] |
| Subject, within clips | 97.14 | 97.04 | −0.10*&nbsp;[−0.16,&nbsp;−0.05] |
| Subject, clip to clip (Consistency) | 87.21 | 87.23 | +0.02&nbsp;[−0.23,&nbsp;+0.27] |
| Background, clip to clip | 89.53 | 89.55 | +0.02&nbsp;[−0.13,&nbsp;+0.16] |

**LongLive + Commit Forcing** vs **LongLive, commit pass reads the newest 9 frames**

| Metric | LongLive, commit pass reads the newest 9 frames | LongLive + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.72 | 82.65 | −0.07&nbsp;[−0.15,&nbsp;+0.02] |
| Dynamic degree | 49.47 | 49.38 | −0.08&nbsp;[−1.25,&nbsp;+1.03] |
| Motion smoothness | 98.62 | 98.59 | −0.03*&nbsp;[−0.04,&nbsp;−0.01] |
| Temporal flickering | 97.44 | 97.37 | −0.07*&nbsp;[−0.09,&nbsp;−0.04] |
| Imaging quality | 69.32 | 69.39 | +0.07&nbsp;[−0.05,&nbsp;+0.18] |
| Aesthetic quality | 61.66 | 61.68 | +0.01&nbsp;[−0.11,&nbsp;+0.13] |
| Subject consistency | 97.77 | 97.70 | −0.07*&nbsp;[−0.11,&nbsp;−0.04] |
| Background consistency | 96.57 | 96.49 | −0.08*&nbsp;[−0.11,&nbsp;−0.06] |
| Subject, within clips | 97.04 | 96.92 | −0.12*&nbsp;[−0.17,&nbsp;−0.07] |
| Subject, clip to clip (Consistency) | 87.23 | 86.93 | −0.30*&nbsp;[−0.53,&nbsp;−0.08] |
| Background, clip to clip | 89.55 | 89.17 | −0.38*&nbsp;[−0.52,&nbsp;−0.24] |

</details>

<details>
<summary>Seed 0: LongLive, commit pass reads 6 vs 12 frames</summary>

Source: [`results/tables/vbl60_longlive_commit6_vs_12.txt`](results/tables/vbl60_longlive_commit6_vs_12.txt) · spec [`results/specs/vbl60_longlive_commit6_vs_12.json`](results/specs/vbl60_longlive_commit6_vs_12.json)

**LongLive, commit pass reads the newest 6 frames** vs **LongLive + Commit Forcing**

| Metric | LongLive + Commit Forcing | LongLive, commit pass reads the newest 6 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.65 | 82.73 | +0.08&nbsp;[−0.01,&nbsp;+0.17] |
| Dynamic degree | 49.38 | 49.40 | +0.02&nbsp;[−1.25,&nbsp;+1.30] |
| Motion smoothness | 98.59 | 98.61 | +0.02*&nbsp;[+0.00,&nbsp;+0.03] |
| Temporal flickering | 97.37 | 97.42 | +0.05*&nbsp;[+0.01,&nbsp;+0.08] |
| Imaging quality | 69.39 | 69.29 | −0.10&nbsp;[−0.23,&nbsp;+0.04] |
| Aesthetic quality | 61.68 | 61.75 | +0.07&nbsp;[−0.05,&nbsp;+0.19] |
| Subject consistency | 97.70 | 97.82 | +0.12*&nbsp;[+0.09,&nbsp;+0.16] |
| Background consistency | 96.49 | 96.63 | +0.14*&nbsp;[+0.11,&nbsp;+0.16] |
| Subject, within clips | 96.92 | 97.14 | +0.22*&nbsp;[+0.17,&nbsp;+0.28] |
| Subject, clip to clip (Consistency) | 86.93 | 87.21 | +0.28*&nbsp;[+0.02,&nbsp;+0.55] |
| Background, clip to clip | 89.17 | 89.53 | +0.36*&nbsp;[+0.20,&nbsp;+0.53] |

</details>

<details>
<summary>Seed 1: SGF, LongLive, ID-Forcing</summary>

Source: [`results/tables/vbl60_seed1_a.txt`](results/tables/vbl60_seed1_a.txt) · spec [`results/specs/vbl60_seed1_a.json`](results/specs/vbl60_seed1_a.json)

**SGF + Commit Forcing** vs **SGF**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.85 | 84.71 | +0.86*&nbsp;[+0.52,&nbsp;+1.21] |
| Dynamic degree | 57.27 | 70.58 | +13.32*&nbsp;[+9.05,&nbsp;+17.62] |
| Motion smoothness | 98.64 | 98.46 | −0.19*&nbsp;[−0.27,&nbsp;−0.11] |
| Temporal flickering | 97.33 | 96.90 | −0.43*&nbsp;[−0.57,&nbsp;−0.29] |
| Imaging quality | 71.24 | 70.88 | −0.37&nbsp;[−0.97,&nbsp;+0.24] |
| Aesthetic quality | 62.97 | 63.52 | +0.55&nbsp;[−0.11,&nbsp;+1.23] |
| Subject consistency | 98.03 | 98.28 | +0.26*&nbsp;[+0.17,&nbsp;+0.34] |
| Background consistency | 96.65 | 96.83 | +0.18*&nbsp;[+0.09,&nbsp;+0.26] |
| Subject, within clips | 97.55 | 97.63 | +0.07&nbsp;[−0.05,&nbsp;+0.19] |
| Subject, clip to clip (Consistency) | 86.60 | 91.41 | +4.80*&nbsp;[+3.89,&nbsp;+5.79] |
| Background, clip to clip | 89.36 | 92.78 | +3.42*&nbsp;[+2.78,&nbsp;+4.06] |

**LongLive + Commit Forcing** vs **LongLive**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.19 | 82.67 | +0.48*&nbsp;[+0.33,&nbsp;+0.64] |
| Dynamic degree | 42.03 | 50.20 | +8.17*&nbsp;[+6.23,&nbsp;+10.18] |
| Motion smoothness | 98.74 | 98.56 | −0.17*&nbsp;[−0.20,&nbsp;−0.14] |
| Temporal flickering | 97.59 | 97.31 | −0.28*&nbsp;[−0.33,&nbsp;−0.23] |
| Imaging quality | 68.83 | 69.51 | +0.68*&nbsp;[+0.47,&nbsp;+0.90] |
| Aesthetic quality | 61.67 | 61.61 | −0.06&nbsp;[−0.25,&nbsp;+0.12] |
| Subject consistency | 97.77 | 97.68 | −0.09*&nbsp;[−0.13,&nbsp;−0.05] |
| Background consistency | 96.54 | 96.47 | −0.08*&nbsp;[−0.12,&nbsp;−0.04] |
| Subject, within clips | 97.13 | 96.89 | −0.25*&nbsp;[−0.31,&nbsp;−0.18] |
| Subject, clip to clip (Consistency) | 86.02 | 86.70 | +0.68*&nbsp;[+0.35,&nbsp;+1.01] |
| Background, clip to clip | 88.20 | 88.84 | +0.64*&nbsp;[+0.43,&nbsp;+0.86] |

**ID-Forcing on Self-Forcing + Commit Forcing** vs **ID-Forcing on Self-Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.47 | 82.67 | +0.20*&nbsp;[+0.04,&nbsp;+0.37] |
| Dynamic degree | 65.23 | 62.98 | −2.25*&nbsp;[−4.45,&nbsp;−0.15] |
| Motion smoothness | 97.90 | 98.06 | +0.16*&nbsp;[+0.10,&nbsp;+0.21] |
| Temporal flickering | 96.11 | 96.41 | +0.29*&nbsp;[+0.21,&nbsp;+0.38] |
| Imaging quality | 69.38 | 69.52 | +0.15&nbsp;[−0.18,&nbsp;+0.50] |
| Aesthetic quality | 59.47 | 60.13 | +0.66*&nbsp;[+0.36,&nbsp;+0.96] |
| Subject consistency | 97.03 | 97.22 | +0.18*&nbsp;[+0.11,&nbsp;+0.25] |
| Background consistency | 96.20 | 96.27 | +0.07*&nbsp;[+0.03,&nbsp;+0.11] |
| Subject, within clips | 96.37 | 96.50 | +0.13*&nbsp;[+0.03,&nbsp;+0.24] |
| Subject, clip to clip (Consistency) | 79.29 | 81.56 | +2.27*&nbsp;[+1.70,&nbsp;+2.81] |
| Background, clip to clip | 84.30 | 85.81 | +1.51*&nbsp;[+1.20,&nbsp;+1.82] |

**LongLive, commit pass reads the newest 6 frames** vs **LongLive + Commit Forcing**

| Metric | LongLive + Commit Forcing | LongLive, commit pass reads the newest 6 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.67 | 82.66 | −0.02&nbsp;[−0.12,&nbsp;+0.08] |
| Dynamic degree | 50.20 | 48.65 | −1.55*&nbsp;[−2.88,&nbsp;−0.18] |
| Motion smoothness | 98.56 | 98.59 | +0.02&nbsp;[−0.00,&nbsp;+0.04] |
| Temporal flickering | 97.31 | 97.38 | +0.07*&nbsp;[+0.02,&nbsp;+0.11] |
| Imaging quality | 69.51 | 69.43 | −0.08&nbsp;[−0.23,&nbsp;+0.07] |
| Aesthetic quality | 61.61 | 61.70 | +0.09&nbsp;[−0.05,&nbsp;+0.23] |
| Subject consistency | 97.68 | 97.81 | +0.14*&nbsp;[+0.10,&nbsp;+0.17] |
| Background consistency | 96.47 | 96.62 | +0.16*&nbsp;[+0.13,&nbsp;+0.18] |
| Subject, within clips | 96.89 | 97.13 | +0.25*&nbsp;[+0.19,&nbsp;+0.30] |
| Subject, clip to clip (Consistency) | 86.70 | 87.09 | +0.38*&nbsp;[+0.11,&nbsp;+0.66] |
| Background, clip to clip | 88.84 | 89.36 | +0.52*&nbsp;[+0.36,&nbsp;+0.67] |

**LongLive, commit pass reads the newest 6 frames** vs **LongLive, commit pass reads only its block**

| Metric | LongLive, commit pass reads only its block | LongLive, commit pass reads the newest 6 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.83 | 82.66 | −0.17*&nbsp;[−0.30,&nbsp;−0.04] |
| Dynamic degree | 54.18 | 48.65 | −5.53*&nbsp;[−7.37,&nbsp;−3.80] |
| Motion smoothness | 98.45 | 98.59 | +0.13*&nbsp;[+0.10,&nbsp;+0.17] |
| Temporal flickering | 97.08 | 97.38 | +0.29*&nbsp;[+0.23,&nbsp;+0.36] |
| Imaging quality | 69.37 | 69.43 | +0.06&nbsp;[−0.12,&nbsp;+0.24] |
| Aesthetic quality | 61.69 | 61.70 | +0.01&nbsp;[−0.16,&nbsp;+0.19] |
| Subject consistency | 97.68 | 97.81 | +0.13*&nbsp;[+0.09,&nbsp;+0.17] |
| Background consistency | 96.50 | 96.62 | +0.13*&nbsp;[+0.09,&nbsp;+0.16] |
| Subject, within clips | 96.96 | 97.13 | +0.17*&nbsp;[+0.10,&nbsp;+0.24] |
| Subject, clip to clip (Consistency) | 85.91 | 87.09 | +1.18*&nbsp;[+0.86,&nbsp;+1.50] |
| Background, clip to clip | 88.49 | 89.36 | +0.87*&nbsp;[+0.67,&nbsp;+1.07] |

**LongLive, commit pass reads the newest 6 frames** vs **LongLive**

| Metric | LongLive | LongLive, commit pass reads the newest 6 frames | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.19 | 82.66 | +0.46*&nbsp;[+0.30,&nbsp;+0.64] |
| Dynamic degree | 42.03 | 48.65 | +6.62*&nbsp;[+4.53,&nbsp;+8.73] |
| Motion smoothness | 98.74 | 98.59 | −0.15*&nbsp;[−0.19,&nbsp;−0.12] |
| Temporal flickering | 97.59 | 97.38 | −0.21*&nbsp;[−0.27,&nbsp;−0.15] |
| Imaging quality | 68.83 | 69.43 | +0.60*&nbsp;[+0.35,&nbsp;+0.87] |
| Aesthetic quality | 61.67 | 61.70 | +0.03&nbsp;[−0.19,&nbsp;+0.25] |
| Subject consistency | 97.77 | 97.81 | +0.05&nbsp;[−0.01,&nbsp;+0.10] |
| Background consistency | 96.54 | 96.62 | +0.08*&nbsp;[+0.04,&nbsp;+0.12] |
| Subject, within clips | 97.13 | 97.13 | +0.00&nbsp;[−0.07,&nbsp;+0.07] |
| Subject, clip to clip (Consistency) | 86.02 | 87.09 | +1.06*&nbsp;[+0.72,&nbsp;+1.43] |
| Background, clip to clip | 88.20 | 89.36 | +1.16*&nbsp;[+0.91,&nbsp;+1.41] |

**LongLive, commit pass reads only its block** vs **LongLive**

| Metric | LongLive | LongLive, commit pass reads only its block | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.19 | 82.83 | +0.64*&nbsp;[+0.43,&nbsp;+0.85] |
| Dynamic degree | 42.03 | 54.18 | +12.15*&nbsp;[+9.42,&nbsp;+14.90] |
| Motion smoothness | 98.74 | 98.45 | −0.28*&nbsp;[−0.33,&nbsp;−0.24] |
| Temporal flickering | 97.59 | 97.08 | −0.51*&nbsp;[−0.60,&nbsp;−0.42] |
| Imaging quality | 68.83 | 69.37 | +0.54*&nbsp;[+0.23,&nbsp;+0.85] |
| Aesthetic quality | 61.67 | 61.69 | +0.02&nbsp;[−0.25,&nbsp;+0.28] |
| Subject consistency | 97.77 | 97.68 | −0.08*&nbsp;[−0.15,&nbsp;−0.02] |
| Background consistency | 96.54 | 96.50 | −0.05&nbsp;[−0.09,&nbsp;+0.00] |
| Subject, within clips | 97.13 | 96.96 | −0.17*&nbsp;[−0.26,&nbsp;−0.07] |
| Subject, clip to clip (Consistency) | 86.02 | 85.91 | −0.11&nbsp;[−0.58,&nbsp;+0.36] |
| Background, clip to clip | 88.20 | 88.49 | +0.28&nbsp;[−0.04,&nbsp;+0.61] |

</details>

<details>
<summary>Seed 1: Self-Forcing, Recency Forcing, Context Forcing, Rolling Sink</summary>

Source: [`results/tables/vbl60_seed1_b.txt`](results/tables/vbl60_seed1_b.txt) · spec [`results/specs/vbl60_seed1_b.json`](results/specs/vbl60_seed1_b.json)

**Recency Forcing + Commit Forcing** vs **Recency Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.00 | 82.56 | +0.56*&nbsp;[+0.38,&nbsp;+0.73] |
| Dynamic degree | 63.25 | 65.37 | +2.12*&nbsp;[+0.43,&nbsp;+3.82] |
| Motion smoothness | 98.23 | 98.17 | −0.07*&nbsp;[−0.12,&nbsp;−0.02] |
| Temporal flickering | 96.46 | 96.43 | −0.04&nbsp;[−0.12,&nbsp;+0.05] |
| Imaging quality | 67.93 | 68.78 | +0.85*&nbsp;[+0.44,&nbsp;+1.29] |
| Aesthetic quality | 58.01 | 59.48 | +1.48*&nbsp;[+1.10,&nbsp;+1.88] |
| Subject consistency | 96.52 | 96.78 | +0.27*&nbsp;[+0.18,&nbsp;+0.35] |
| Background consistency | 95.77 | 95.97 | +0.20*&nbsp;[+0.15,&nbsp;+0.25] |
| Subject, within clips | 95.93 | 95.93 | −0.00&nbsp;[−0.13,&nbsp;+0.12] |
| Subject, clip to clip (Consistency) | 74.42 | 78.72 | +4.30*&nbsp;[+3.64,&nbsp;+4.99] |
| Background, clip to clip | 80.22 | 83.35 | +3.13*&nbsp;[+2.75,&nbsp;+3.54] |

**Context Forcing, sink out of the commit pass only** vs **Context Forcing**

| Metric | Context Forcing | Context Forcing, sink out of the commit pass only | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.70 | 83.19 | +0.50*&nbsp;[+0.31,&nbsp;+0.69] |
| Dynamic degree | 60.27 | 67.45 | +7.18*&nbsp;[+4.87,&nbsp;+9.52] |
| Motion smoothness | 98.43 | 98.25 | −0.18*&nbsp;[−0.25,&nbsp;−0.11] |
| Temporal flickering | 97.09 | 96.78 | −0.31*&nbsp;[−0.41,&nbsp;−0.20] |
| Imaging quality | 67.44 | 68.35 | +0.92*&nbsp;[+0.44,&nbsp;+1.38] |
| Aesthetic quality | 60.30 | 60.49 | +0.18&nbsp;[−0.13,&nbsp;+0.49] |
| Subject consistency | 97.35 | 97.34 | −0.01&nbsp;[−0.09,&nbsp;+0.07] |
| Background consistency | 96.41 | 96.42 | +0.01&nbsp;[−0.05,&nbsp;+0.07] |
| Subject, within clips | 97.14 | 96.92 | −0.22*&nbsp;[−0.35,&nbsp;−0.10] |
| Subject, clip to clip (Consistency) | 78.63 | 80.24 | +1.61*&nbsp;[+1.02,&nbsp;+2.22] |
| Background, clip to clip | 81.93 | 84.04 | +2.10*&nbsp;[+1.64,&nbsp;+2.56] |

**Context Forcing + Commit Forcing** vs **Context Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.70 | 83.12 | +0.43*&nbsp;[+0.22,&nbsp;+0.64] |
| Dynamic degree | 60.27 | 61.60 | +1.33&nbsp;[−1.45,&nbsp;+4.13] |
| Motion smoothness | 98.43 | 98.32 | −0.11*&nbsp;[−0.18,&nbsp;−0.04] |
| Temporal flickering | 97.09 | 96.98 | −0.11&nbsp;[−0.24,&nbsp;+0.02] |
| Imaging quality | 67.44 | 68.90 | +1.46*&nbsp;[+0.87,&nbsp;+2.06] |
| Aesthetic quality | 60.30 | 60.92 | +0.62*&nbsp;[+0.27,&nbsp;+0.96] |
| Subject consistency | 97.35 | 97.69 | +0.34*&nbsp;[+0.25,&nbsp;+0.43] |
| Background consistency | 96.41 | 96.63 | +0.21*&nbsp;[+0.15,&nbsp;+0.28] |
| Subject, within clips | 97.14 | 97.39 | +0.25*&nbsp;[+0.12,&nbsp;+0.37] |
| Subject, clip to clip (Consistency) | 78.63 | 82.16 | +3.53*&nbsp;[+2.83,&nbsp;+4.26] |
| Background, clip to clip | 81.93 | 85.26 | +3.32*&nbsp;[+2.80,&nbsp;+3.87] |

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

**Rolling Sink + Commit Forcing** vs **Rolling Sink**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.40 | 82.55 | +0.16*&nbsp;[+0.02,&nbsp;+0.30] |
| Dynamic degree | 43.42 | 47.58 | +4.17*&nbsp;[+2.57,&nbsp;+5.88] |
| Motion smoothness | 98.62 | 98.52 | −0.09*&nbsp;[−0.12,&nbsp;−0.06] |
| Temporal flickering | 97.65 | 97.47 | −0.18*&nbsp;[−0.23,&nbsp;−0.13] |
| Imaging quality | 69.95 | 69.71 | −0.23&nbsp;[−0.55,&nbsp;+0.07] |
| Aesthetic quality | 60.96 | 61.13 | +0.17&nbsp;[−0.05,&nbsp;+0.40] |
| Subject consistency | 97.90 | 97.80 | −0.10*&nbsp;[−0.16,&nbsp;−0.05] |
| Background consistency | 96.79 | 96.73 | −0.06*&nbsp;[−0.10,&nbsp;−0.02] |
| Subject, within clips | 97.44 | 97.13 | −0.31*&nbsp;[−0.41,&nbsp;−0.21] |
| Subject, clip to clip (Consistency) | 86.34 | 87.32 | +0.98*&nbsp;[+0.58,&nbsp;+1.41] |
| Background, clip to clip | 88.79 | 89.45 | +0.66*&nbsp;[+0.39,&nbsp;+0.96] |

**Self-Forcing + sink + Commit Forcing** vs **Self-Forcing + sink**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.35 | 81.54 | +0.20&nbsp;[−0.28,&nbsp;+0.59] |
| Dynamic degree | 58.22 | 58.87 | +0.65&nbsp;[−2.00,&nbsp;+3.40] |
| Motion smoothness | 97.93 | 97.73 | −0.20&nbsp;[−0.60,&nbsp;+0.09] |
| Temporal flickering | 96.35 | 96.27 | −0.09&nbsp;[−0.43,&nbsp;+0.21] |
| Imaging quality | 67.14 | 67.95 | +0.81*&nbsp;[+0.26,&nbsp;+1.38] |
| Aesthetic quality | 58.01 | 58.68 | +0.68*&nbsp;[+0.23,&nbsp;+1.14] |
| Subject consistency | 96.62 | 96.74 | +0.12&nbsp;[−0.00,&nbsp;+0.24] |
| Background consistency | 95.96 | 96.14 | +0.18*&nbsp;[+0.12,&nbsp;+0.24] |
| Subject, within clips | 96.13 | 95.96 | −0.17&nbsp;[−0.40,&nbsp;+0.04] |
| Subject, clip to clip (Consistency) | 74.71 | 78.11 | +3.40*&nbsp;[+2.76,&nbsp;+4.07] |
| Background, clip to clip | 80.31 | 83.19 | +2.88*&nbsp;[+2.44,&nbsp;+3.32] |

</details>

</details>

## Full VBench

The 946 prompts of VBench's standard suite, one 60 s video each, all 16 dimensions; Total, Quality and Semantic as VBench computes them ([pipeline](eval/vbench_full/README.md)).

| Model | Base | + Commit Forcing | Δ Total | Δ Quality | Δ Semantic | Δ Consistency |
|:---|---:|---:|:---|:---|:---|:---|
| SGF | 83.84 | 84.93 | +1.08*&nbsp;[+0.53,&nbsp;+1.64] | +1.17* | +0.72 | +2.71* |
| Recency Forcing, training-free † | 82.23 | 83.08 | +0.85*&nbsp;[+0.56,&nbsp;+1.15] | +0.47* | +2.37* | +4.44* |
| Context Forcing | 82.23 | 82.68 | +0.43*&nbsp;[+0.09,&nbsp;+0.79] | +0.46* | +0.33 | +2.35* |

<details>
<summary>All 16 dimensions</summary>

**SGF** · Source: [`results/vbench_full/tables/sgf.txt`](results/vbench_full/tables/sgf.txt) · spec [`results/vbench_full/specs/sgf.json`](results/vbench_full/specs/sgf.json)

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Total | 83.84 | 84.93 | +1.08*&nbsp;[+0.53,&nbsp;+1.64] |
| Quality | 86.06 | 87.22 | +1.17*&nbsp;[+0.57,&nbsp;+1.79] |
| Semantic | 74.97 | 75.78 | +0.72&nbsp;[−0.73,&nbsp;+2.17] |
| Subject consistency | 98.26 | 98.43 | +0.17*&nbsp;[+0.05,&nbsp;+0.29] |
| Background consistency | 96.69 | 97.08 | +0.40*&nbsp;[+0.27,&nbsp;+0.53] |
| Temporal flickering | 98.95 | 98.78 | −0.15*&nbsp;[−0.24,&nbsp;−0.05] |
| Motion smoothness | 98.63 | 98.37 | −0.26*&nbsp;[−0.36,&nbsp;−0.16] |
| Dynamic degree | 67.45 | 81.81 | +14.35*&nbsp;[+6.93,&nbsp;+22.05] |
| Aesthetic quality | 67.06 | 67.52 | +0.46&nbsp;[−0.26,&nbsp;+1.19] |
| Imaging quality | 71.82 | 72.32 | +0.50&nbsp;[−0.29,&nbsp;+1.29] |
| Object class | 86.00 | 85.51 | −0.49&nbsp;[−4.20,&nbsp;+2.89] |
| Multiple objects | 71.24 | 77.01 | +5.76&nbsp;[−0.83,&nbsp;+12.11] |
| Human action | 92.33 | 91.83 | −0.50&nbsp;[−5.22,&nbsp;+4.08] |
| Color | 89.46 | 88.92 | −1.45&nbsp;[−6.83,&nbsp;+3.60] |
| Spatial relationship | 76.29 | 75.76 | −0.53&nbsp;[−5.73,&nbsp;+5.11] |
| Scene | 48.09 | 51.04 | +2.95&nbsp;[−1.45,&nbsp;+7.99] |
| Appearance style | 20.60 | 20.75 | +0.18&nbsp;[−0.04,&nbsp;+0.38] |
| Temporal style | 22.05 | 22.33 | +0.28&nbsp;[−0.10,&nbsp;+0.66] |
| Overall consistency | 24.84 | 24.37 | −0.47*&nbsp;[−0.93,&nbsp;−0.04] |
| Subject, within clips | 97.93 | 98.06 | +0.13&nbsp;[−0.04,&nbsp;+0.28] |
| Subject, clip to clip (Consistency) | 87.75 | 90.46 | +2.71*&nbsp;[+1.28,&nbsp;+4.08] |
| Background, within clips | 96.18 | 96.44 | +0.26*&nbsp;[+0.06,&nbsp;+0.47] |
| Background, clip to clip | 90.01 | 94.83 | +4.82*&nbsp;[+4.05,&nbsp;+5.64] |

**Recency Forcing, training-free †** · Source: [`results/vbench_full/tables/rf.txt`](results/vbench_full/tables/rf.txt) · spec [`results/vbench_full/specs/rf.json`](results/vbench_full/specs/rf.json)

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Total | 82.23 | 83.08 | +0.85*&nbsp;[+0.56,&nbsp;+1.15] |
| Quality | 84.77 | 85.24 | +0.47*&nbsp;[+0.17,&nbsp;+0.79] |
| Semantic | 72.08 | 74.43 | +2.37*&nbsp;[+1.64,&nbsp;+3.15] |
| Subject consistency | 96.73 | 96.98 | +0.26*&nbsp;[+0.08,&nbsp;+0.41] |
| Background consistency | 95.92 | 96.23 | +0.30*&nbsp;[+0.23,&nbsp;+0.37] |
| Temporal flickering | 98.88 | 99.02 | +0.15*&nbsp;[+0.10,&nbsp;+0.21] |
| Motion smoothness | 98.37 | 98.23 | −0.14*&nbsp;[−0.24,&nbsp;−0.05] |
| Dynamic degree | 70.28 | 70.56 | +0.28&nbsp;[−3.28,&nbsp;+3.97] |
| Aesthetic quality | 62.65 | 64.06 | +1.41*&nbsp;[+0.89,&nbsp;+1.94] |
| Imaging quality | 70.34 | 71.24 | +0.90*&nbsp;[+0.29,&nbsp;+1.52] |
| Object class | 88.05 | 89.04 | +1.00&nbsp;[−1.56,&nbsp;+3.52] |
| Multiple objects | 63.58 | 69.33 | +5.75*&nbsp;[+2.63,&nbsp;+8.99] |
| Human action | 92.83 | 94.17 | +1.33&nbsp;[−0.00,&nbsp;+2.72] |
| Color | 87.88 | 89.20 | +1.60&nbsp;[−0.40,&nbsp;+3.83] |
| Spatial relationship | 73.15 | 74.82 | +1.67&nbsp;[−1.36,&nbsp;+4.66] |
| Scene | 35.47 | 41.53 | +6.06*&nbsp;[+3.12,&nbsp;+9.06] |
| Appearance style | 20.64 | 20.55 | −0.12&nbsp;[−0.27,&nbsp;+0.02] |
| Temporal style | 21.96 | 22.62 | +0.66*&nbsp;[+0.29,&nbsp;+1.06] |
| Overall consistency | 24.59 | 25.03 | +0.44*&nbsp;[+0.17,&nbsp;+0.71] |
| Subject, within clips | 96.46 | 96.48 | +0.03&nbsp;[−0.19,&nbsp;+0.23] |
| Subject, clip to clip (Consistency) | 74.21 | 78.65 | +4.44*&nbsp;[+3.14,&nbsp;+5.67] |
| Background, within clips | 95.38 | 95.65 | +0.27*&nbsp;[+0.15,&nbsp;+0.39] |
| Background, clip to clip | 81.01 | 85.38 | +4.37*&nbsp;[+3.78,&nbsp;+4.97] |

**Context Forcing** · Source: [`results/vbench_full/tables/context_forcing.txt`](results/vbench_full/tables/context_forcing.txt) · spec [`results/vbench_full/specs/context_forcing.json`](results/vbench_full/specs/context_forcing.json)

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Total | 82.23 | 82.68 | +0.43*&nbsp;[+0.09,&nbsp;+0.79] |
| Quality | 84.79 | 85.25 | +0.46*&nbsp;[+0.10,&nbsp;+0.84] |
| Semantic | 72.01 | 72.39 | +0.33&nbsp;[−0.57,&nbsp;+1.20] |
| Subject consistency | 97.75 | 97.96 | +0.21*&nbsp;[+0.07,&nbsp;+0.38] |
| Background consistency | 96.63 | 96.92 | +0.29*&nbsp;[+0.18,&nbsp;+0.40] |
| Temporal flickering | 99.30 | 99.21 | −0.08*&nbsp;[−0.13,&nbsp;−0.03] |
| Motion smoothness | 98.55 | 98.43 | −0.12*&nbsp;[−0.22,&nbsp;−0.03] |
| Dynamic degree | 58.89 | 62.31 | +3.43&nbsp;[−1.26,&nbsp;+8.21] |
| Aesthetic quality | 65.41 | 65.82 | +0.41&nbsp;[−0.03,&nbsp;+0.85] |
| Imaging quality | 69.47 | 70.32 | +0.84*&nbsp;[+0.30,&nbsp;+1.45] |
| Object class | 88.63 | 87.23 | −1.40&nbsp;[−4.43,&nbsp;+1.15] |
| Multiple objects | 70.79 | 73.34 | +2.55&nbsp;[−1.16,&nbsp;+6.25] |
| Human action | 91.33 | 93.67 | +2.33*&nbsp;[+0.46,&nbsp;+4.58] |
| Color | 84.19 | 85.01 | +0.33&nbsp;[−2.71,&nbsp;+3.32] |
| Spatial relationship | 69.19 | 67.40 | −1.79&nbsp;[−4.91,&nbsp;+1.38] |
| Scene | 40.20 | 39.47 | −0.73&nbsp;[−3.92,&nbsp;+2.61] |
| Appearance style | 20.86 | 20.95 | +0.09&nbsp;[−0.07,&nbsp;+0.24] |
| Temporal style | 20.83 | 21.10 | +0.26&nbsp;[−0.00,&nbsp;+0.54] |
| Overall consistency | 23.60 | 23.89 | +0.29&nbsp;[−0.03,&nbsp;+0.60] |
| Subject, within clips | 97.70 | 97.87 | +0.17&nbsp;[−0.00,&nbsp;+0.37] |
| Subject, clip to clip (Consistency) | 80.92 | 83.27 | +2.35*&nbsp;[+1.22,&nbsp;+3.49] |
| Background, within clips | 96.51 | 96.82 | +0.32*&nbsp;[+0.13,&nbsp;+0.50] |
| Background, clip to clip | 83.90 | 87.26 | +3.35*&nbsp;[+2.56,&nbsp;+4.18] |

</details>

## Longer videos

**240 s, 32 MovieGen prompts** (the first 32 extended MovieGen prompts of Self-Forcing). Drift: imaging quality of the first 2 s clip minus that of the last one, the measure of TetherCache (lower is better).

| Model | Base | + Commit Forcing | Δ Quality | Δ Consistency | Δ Drift |
|:---|---:|---:|:---|:---|:---|
| SGF | 83.97 | 84.69 | +0.72*&nbsp;[+0.07,&nbsp;+1.37] | +5.07* | +0.28 |
| Context Forcing | 83.60 | 84.04 | +0.44&nbsp;[−0.08,&nbsp;+0.97] | +2.23* | −0.75 |
| TetherCache | 82.87 | 82.72 | −0.16&nbsp;[−1.16,&nbsp;+0.85] | +5.20* | −0.41 |
| TetherCache, FIFO memory | 80.70 | 82.49 | +1.79*&nbsp;[+1.26,&nbsp;+2.37] | +8.21* | −11.95* |

**Variants**, 240 s:

| Model | Variant | Δ Quality | Δ Consistency | Δ Drift |
|:---|:---|:---|:---|:---|
| Context Forcing | no sink in the commit pass | +0.50*&nbsp;[+0.06,&nbsp;+0.96] | +0.77 | −0.34 |
| Context Forcing | no slow memory or older frames in the commit pass | −0.19&nbsp;[−0.59,&nbsp;+0.21] | +0.08 | −1.88 |

**120 s and 240 s, ID-Forcing's 128 MovieGen prompts.**

| Model | Length | Base | + Commit Forcing | Δ Quality | Δ Consistency |
|:---|---:|---:|---:|:---|:---|
| LongLive | 120 s | 81.72 | 81.93 | +0.21*&nbsp;[+0.05,&nbsp;+0.37] | +1.09*&nbsp;[+0.62,&nbsp;+1.57] |
| LongLive | 240 s | 81.56 | 81.84 | +0.28*&nbsp;[+0.10,&nbsp;+0.46] | +1.96*&nbsp;[+1.49,&nbsp;+2.44] |
| ID-Forcing on Self-Forcing | 120 s | 81.62 | 81.68 | +0.06&nbsp;[−0.15,&nbsp;+0.26] | +3.05*&nbsp;[+2.33,&nbsp;+3.78] |
| ID-Forcing on Self-Forcing | 240 s | 81.32 | 81.65 | +0.34*&nbsp;[+0.05,&nbsp;+0.70] | +3.58*&nbsp;[+2.86,&nbsp;+4.30] |

<details>
<summary>All metrics, longer videos</summary>

<details>
<summary>240 s, MovieGen 32: SGF and TetherCache</summary>

Source: [`results/long_horizon/tables/moviegen32_240s_sgf_tethercache.txt`](results/long_horizon/tables/moviegen32_240s_sgf_tethercache.txt) · spec [`results/long_horizon/specs/moviegen32_240s_sgf_tethercache.json`](results/long_horizon/specs/moviegen32_240s_sgf_tethercache.json)

**SGF + Commit Forcing** vs **SGF**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.97 | 84.69 | +0.72*&nbsp;[+0.07,&nbsp;+1.37] |
| Dynamic degree | 49.11 | 59.69 | +10.57*&nbsp;[+2.24,&nbsp;+18.99] |
| Motion smoothness | 98.68 | 98.50 | −0.18*&nbsp;[−0.35,&nbsp;−0.04] |
| Temporal flickering | 97.38 | 96.96 | −0.42*&nbsp;[−0.79,&nbsp;−0.09] |
| Imaging quality | 73.45 | 73.05 | −0.40&nbsp;[−1.56,&nbsp;+0.67] |
| Aesthetic quality | 64.96 | 65.82 | +0.86&nbsp;[−0.88,&nbsp;+2.69] |
| Subject consistency | 98.26 | 98.53 | +0.28*&nbsp;[+0.10,&nbsp;+0.46] |
| Background consistency | 96.75 | 97.02 | +0.26*&nbsp;[+0.06,&nbsp;+0.47] |
| Subject, within clips | 97.92 | 98.05 | +0.13&nbsp;[−0.09,&nbsp;+0.34] |
| Subject, clip to clip (Consistency) | 87.34 | 92.41 | +5.07*&nbsp;[+2.98,&nbsp;+7.30] |
| Background, within clips | 96.29 | 96.38 | +0.09&nbsp;[−0.21,&nbsp;+0.41] |
| Background, clip to clip | 89.81 | 94.27 | +4.46*&nbsp;[+2.88,&nbsp;+6.15] |
| Drift, first vs last clip | -0.27 | 0.01 | +0.28&nbsp;[−0.94,&nbsp;+1.41] |
| Drift, first 5 vs last 5 clips | 0.42 | 0.10 | −0.31&nbsp;[−1.74,&nbsp;+0.81] |

**TetherCache, FIFO memory + Commit Forcing** vs **TetherCache, FIFO memory**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 80.70 | 82.49 | +1.79*&nbsp;[+1.26,&nbsp;+2.37] |
| Dynamic degree | 37.58 | 44.66 | +7.08*&nbsp;[+2.32,&nbsp;+12.84] |
| Motion smoothness | 98.28 | 98.24 | −0.04&nbsp;[−0.12,&nbsp;+0.04] |
| Temporal flickering | 97.24 | 97.15 | −0.09&nbsp;[−0.22,&nbsp;+0.03] |
| Imaging quality | 68.25 | 72.11 | +3.85*&nbsp;[+2.61,&nbsp;+5.18] |
| Aesthetic quality | 58.81 | 62.12 | +3.31*&nbsp;[+2.15,&nbsp;+4.51] |
| Subject consistency | 97.02 | 97.57 | +0.55*&nbsp;[+0.37,&nbsp;+0.72] |
| Background consistency | 96.07 | 96.55 | +0.48*&nbsp;[+0.33,&nbsp;+0.63] |
| Subject, within clips | 96.57 | 96.80 | +0.22*&nbsp;[+0.01,&nbsp;+0.41] |
| Subject, clip to clip (Consistency) | 76.62 | 84.82 | +8.21*&nbsp;[+6.47,&nbsp;+9.99] |
| Background, within clips | 95.67 | 95.99 | +0.31*&nbsp;[+0.11,&nbsp;+0.51] |
| Background, clip to clip | 81.27 | 89.22 | +7.95*&nbsp;[+6.67,&nbsp;+9.28] |
| Drift, first vs last clip | 12.20 | 0.25 | −11.95*&nbsp;[−15.80,&nbsp;−8.48] |
| Drift, first 5 vs last 5 clips | 12.46 | 0.66 | −11.79*&nbsp;[−15.48,&nbsp;−8.45] |

**TetherCache** vs **TetherCache, FIFO memory**

| Metric | TetherCache, FIFO memory | TetherCache | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 80.70 | 82.87 | +2.17*&nbsp;[+0.47,&nbsp;+3.64] |
| Dynamic degree | 37.58 | 68.52 | +30.94*&nbsp;[+21.02,&nbsp;+41.59] |
| Motion smoothness | 98.28 | 97.77 | −0.52&nbsp;[−1.64,&nbsp;+0.12] |
| Temporal flickering | 97.24 | 95.77 | −1.47*&nbsp;[−2.56,&nbsp;−0.65] |
| Imaging quality | 68.25 | 71.13 | +2.88*&nbsp;[+0.70,&nbsp;+4.82] |
| Aesthetic quality | 58.81 | 60.91 | +2.10*&nbsp;[+0.35,&nbsp;+3.77] |
| Subject consistency | 97.02 | 96.68 | −0.34&nbsp;[−1.02,&nbsp;+0.14] |
| Background consistency | 96.07 | 95.93 | −0.14&nbsp;[−0.41,&nbsp;+0.11] |
| Subject, within clips | 96.57 | 95.94 | −0.63&nbsp;[−1.76,&nbsp;+0.15] |
| Subject, clip to clip (Consistency) | 76.62 | 76.71 | +0.09&nbsp;[−2.62,&nbsp;+2.86] |
| Background, within clips | 95.67 | 95.26 | −0.41*&nbsp;[−0.83,&nbsp;−0.01] |
| Background, clip to clip | 81.27 | 82.69 | +1.42&nbsp;[−0.77,&nbsp;+3.52] |
| Drift, first vs last clip | 12.20 | 2.35 | −9.85*&nbsp;[−14.88,&nbsp;−4.72] |
| Drift, first 5 vs last 5 clips | 12.46 | 2.27 | −10.18*&nbsp;[−14.65,&nbsp;−5.39] |

**TetherCache + Commit Forcing** vs **TetherCache**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.87 | 82.72 | −0.16&nbsp;[−1.16,&nbsp;+0.85] |
| Dynamic degree | 68.52 | 75.29 | +6.77&nbsp;[−1.43,&nbsp;+16.15] |
| Motion smoothness | 97.77 | 97.16 | −0.61&nbsp;[−1.22,&nbsp;+0.04] |
| Temporal flickering | 95.77 | 95.11 | −0.66*&nbsp;[−1.32,&nbsp;−0.04] |
| Imaging quality | 71.13 | 70.39 | −0.74&nbsp;[−2.07,&nbsp;+0.62] |
| Aesthetic quality | 60.91 | 61.07 | +0.16&nbsp;[−1.01,&nbsp;+1.25] |
| Subject consistency | 96.68 | 96.51 | −0.16&nbsp;[−0.62,&nbsp;+0.26] |
| Background consistency | 95.93 | 96.10 | +0.17&nbsp;[−0.03,&nbsp;+0.38] |
| Subject, within clips | 95.94 | 95.07 | −0.87*&nbsp;[−1.52,&nbsp;−0.27] |
| Subject, clip to clip (Consistency) | 76.71 | 81.91 | +5.20*&nbsp;[+2.29,&nbsp;+8.37] |
| Background, within clips | 95.26 | 95.28 | +0.02&nbsp;[−0.34,&nbsp;+0.38] |
| Background, clip to clip | 82.69 | 86.44 | +3.74*&nbsp;[+2.13,&nbsp;+5.33] |
| Drift, first vs last clip | 2.35 | 1.94 | −0.41&nbsp;[−2.99,&nbsp;+2.53] |
| Drift, first 5 vs last 5 clips | 2.27 | 1.63 | −0.65&nbsp;[−3.39,&nbsp;+1.81] |

**TetherCache + Commit Forcing** vs **TetherCache, FIFO memory + Commit Forcing**

| Metric | TetherCache, FIFO memory + Commit Forcing | TetherCache + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 82.49 | 82.72 | +0.23&nbsp;[−1.20,&nbsp;+1.47] |
| Dynamic degree | 44.66 | 75.29 | +30.62*&nbsp;[+21.15,&nbsp;+41.04] |
| Motion smoothness | 98.24 | 97.16 | −1.09*&nbsp;[−1.78,&nbsp;−0.52] |
| Temporal flickering | 97.15 | 95.11 | −2.03*&nbsp;[−3.05,&nbsp;−1.19] |
| Imaging quality | 72.11 | 70.39 | −1.72*&nbsp;[−3.41,&nbsp;−0.33] |
| Aesthetic quality | 62.12 | 61.07 | −1.06&nbsp;[−2.32,&nbsp;+0.17] |
| Subject consistency | 97.57 | 96.51 | −1.05*&nbsp;[−1.79,&nbsp;−0.39] |
| Background consistency | 96.55 | 96.10 | −0.45*&nbsp;[−0.74,&nbsp;−0.16] |
| Subject, within clips | 96.80 | 95.07 | −1.72*&nbsp;[−3.02,&nbsp;−0.73] |
| Subject, clip to clip (Consistency) | 84.82 | 81.91 | −2.91*&nbsp;[−5.50,&nbsp;−0.60] |
| Background, within clips | 95.99 | 95.28 | −0.70*&nbsp;[−1.20,&nbsp;−0.23] |
| Background, clip to clip | 89.22 | 86.44 | −2.79*&nbsp;[−4.92,&nbsp;−0.84] |
| Drift, first vs last clip | 0.25 | 1.94 | +1.69&nbsp;[−0.29,&nbsp;+3.92] |
| Drift, first 5 vs last 5 clips | 0.66 | 1.63 | +0.96&nbsp;[−0.54,&nbsp;+2.44] |

</details>

<details>
<summary>240 s, MovieGen 32: Context Forcing</summary>

Source: [`results/long_horizon/tables/moviegen32_240s_context_forcing.txt`](results/long_horizon/tables/moviegen32_240s_context_forcing.txt) · spec [`results/long_horizon/specs/moviegen32_240s_context_forcing.json`](results/long_horizon/specs/moviegen32_240s_context_forcing.json)

**Context Forcing, memory out of the commit pass only** vs **Context Forcing**

| Metric | Context Forcing | Context Forcing, memory out of the commit pass only | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.60 | 83.41 | −0.19&nbsp;[−0.59,&nbsp;+0.21] |
| Dynamic degree | 58.46 | 48.83 | −9.64*&nbsp;[−14.06,&nbsp;−5.62] |
| Motion smoothness | 98.54 | 98.74 | +0.20*&nbsp;[+0.09,&nbsp;+0.33] |
| Temporal flickering | 97.32 | 97.79 | +0.47*&nbsp;[+0.26,&nbsp;+0.71] |
| Imaging quality | 69.93 | 70.92 | +0.99*&nbsp;[+0.18,&nbsp;+1.90] |
| Aesthetic quality | 62.26 | 62.40 | +0.14&nbsp;[−0.94,&nbsp;+1.06] |
| Subject consistency | 98.03 | 98.23 | +0.19*&nbsp;[+0.08,&nbsp;+0.31] |
| Background consistency | 96.78 | 97.00 | +0.23*&nbsp;[+0.14,&nbsp;+0.32] |
| Subject, within clips | 98.10 | 98.47 | +0.37*&nbsp;[+0.26,&nbsp;+0.50] |
| Subject, clip to clip (Consistency) | 81.83 | 81.91 | +0.08&nbsp;[−1.17,&nbsp;+1.34] |
| Background, within clips | 96.81 | 97.27 | +0.46*&nbsp;[+0.33,&nbsp;+0.59] |
| Background, clip to clip | 84.31 | 83.59 | −0.72&nbsp;[−1.74,&nbsp;+0.23] |
| Drift, first vs last clip | 0.70 | -1.18 | −1.88&nbsp;[−4.20,&nbsp;+0.20] |
| Drift, first 5 vs last 5 clips | 0.73 | -1.38 | −2.10*&nbsp;[−4.05,&nbsp;−0.49] |

**Context Forcing + Commit Forcing** vs **Context Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.60 | 84.04 | +0.44&nbsp;[−0.08,&nbsp;+0.97] |
| Dynamic degree | 58.46 | 59.64 | +1.17&nbsp;[−5.03,&nbsp;+7.40] |
| Motion smoothness | 98.54 | 98.57 | +0.03&nbsp;[−0.15,&nbsp;+0.24] |
| Temporal flickering | 97.32 | 97.43 | +0.11&nbsp;[−0.21,&nbsp;+0.47] |
| Imaging quality | 69.93 | 70.72 | +0.78&nbsp;[−0.46,&nbsp;+2.06] |
| Aesthetic quality | 62.26 | 63.05 | +0.79&nbsp;[−0.21,&nbsp;+1.79] |
| Subject consistency | 98.03 | 98.21 | +0.18*&nbsp;[+0.06,&nbsp;+0.31] |
| Background consistency | 96.78 | 96.87 | +0.10&nbsp;[−0.01,&nbsp;+0.20] |
| Subject, within clips | 98.10 | 98.17 | +0.08&nbsp;[−0.12,&nbsp;+0.26] |
| Subject, clip to clip (Consistency) | 81.83 | 84.06 | +2.23*&nbsp;[+0.51,&nbsp;+3.89] |
| Background, within clips | 96.81 | 96.87 | +0.05&nbsp;[−0.16,&nbsp;+0.25] |
| Background, clip to clip | 84.31 | 85.92 | +1.61*&nbsp;[+0.25,&nbsp;+3.00] |
| Drift, first vs last clip | 0.70 | -0.04 | −0.75&nbsp;[−3.59,&nbsp;+1.81] |
| Drift, first 5 vs last 5 clips | 0.73 | -0.31 | −1.04&nbsp;[−3.43,&nbsp;+1.12] |

**Context Forcing, sink out of the commit pass only** vs **Context Forcing**

| Metric | Context Forcing | Context Forcing, sink out of the commit pass only | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 83.60 | 84.10 | +0.50*&nbsp;[+0.06,&nbsp;+0.96] |
| Dynamic degree | 58.46 | 65.52 | +7.06*&nbsp;[+3.18,&nbsp;+11.61] |
| Motion smoothness | 98.54 | 98.48 | −0.05&nbsp;[−0.21,&nbsp;+0.15] |
| Temporal flickering | 97.32 | 97.17 | −0.15&nbsp;[−0.44,&nbsp;+0.18] |
| Imaging quality | 69.93 | 70.13 | +0.20&nbsp;[−0.97,&nbsp;+1.34] |
| Aesthetic quality | 62.26 | 62.55 | +0.30&nbsp;[−0.71,&nbsp;+1.18] |
| Subject consistency | 98.03 | 97.97 | −0.07&nbsp;[−0.21,&nbsp;+0.07] |
| Background consistency | 96.78 | 96.70 | −0.07&nbsp;[−0.19,&nbsp;+0.03] |
| Subject, within clips | 98.10 | 97.86 | −0.24*&nbsp;[−0.44,&nbsp;−0.07] |
| Subject, clip to clip (Consistency) | 81.83 | 82.60 | +0.77&nbsp;[−0.52,&nbsp;+2.03] |
| Background, within clips | 96.81 | 96.52 | −0.30*&nbsp;[−0.48,&nbsp;−0.12] |
| Background, clip to clip | 84.31 | 85.69 | +1.38*&nbsp;[+0.39,&nbsp;+2.37] |
| Drift, first vs last clip | 0.70 | 0.37 | −0.34&nbsp;[−2.61,&nbsp;+1.53] |
| Drift, first 5 vs last 5 clips | 0.73 | 0.73 | +0.00&nbsp;[−1.41,&nbsp;+1.53] |

**Context Forcing, memory out of the commit pass only** vs **Context Forcing, sink out of the commit pass only**

| Metric | Context Forcing, sink out of the commit pass only | Context Forcing, memory out of the commit pass only | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 84.10 | 83.41 | −0.69*&nbsp;[−1.20,&nbsp;−0.20] |
| Dynamic degree | 65.52 | 48.83 | −16.69*&nbsp;[−24.06,&nbsp;−9.84] |
| Motion smoothness | 98.48 | 98.74 | +0.25*&nbsp;[+0.13,&nbsp;+0.40] |
| Temporal flickering | 97.17 | 97.79 | +0.62*&nbsp;[+0.37,&nbsp;+0.90] |
| Imaging quality | 70.13 | 70.92 | +0.79&nbsp;[−0.17,&nbsp;+2.07] |
| Aesthetic quality | 62.55 | 62.40 | −0.16&nbsp;[−1.05,&nbsp;+0.66] |
| Subject consistency | 97.97 | 98.23 | +0.26*&nbsp;[+0.16,&nbsp;+0.37] |
| Background consistency | 96.70 | 97.00 | +0.30*&nbsp;[+0.18,&nbsp;+0.42] |
| Subject, within clips | 97.86 | 98.47 | +0.61*&nbsp;[+0.46,&nbsp;+0.78] |
| Subject, clip to clip (Consistency) | 82.60 | 81.91 | −0.69&nbsp;[−1.79,&nbsp;+0.43] |
| Background, within clips | 96.52 | 97.27 | +0.75*&nbsp;[+0.54,&nbsp;+0.97] |
| Background, clip to clip | 85.69 | 83.59 | −2.10*&nbsp;[−3.31,&nbsp;−0.98] |
| Drift, first vs last clip | 0.37 | -1.18 | −1.54&nbsp;[−3.50,&nbsp;+0.24] |
| Drift, first 5 vs last 5 clips | 0.73 | -1.38 | −2.11*&nbsp;[−3.92,&nbsp;−0.46] |

</details>

<details>
<summary>120 s, ID-Forcing's 128 prompts: LongLive and ID-Forcing on Self-Forcing</summary>

Source: [`results/long_horizon/tables/idf128_120s.txt`](results/long_horizon/tables/idf128_120s.txt) · spec [`results/long_horizon/specs/idf128_120s.json`](results/long_horizon/specs/idf128_120s.json)

**ID-Forcing on Self-Forcing + Commit Forcing** vs **ID-Forcing on Self-Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.62 | 81.68 | +0.06&nbsp;[−0.15,&nbsp;+0.26] |
| Dynamic degree | 64.27 | 60.49 | −3.78*&nbsp;[−6.39,&nbsp;−1.34] |
| Motion smoothness | 97.77 | 97.88 | +0.11&nbsp;[−0.00,&nbsp;+0.21] |
| Temporal flickering | 96.17 | 96.36 | +0.18*&nbsp;[+0.02,&nbsp;+0.33] |
| Imaging quality | 68.12 | 68.55 | +0.44*&nbsp;[+0.08,&nbsp;+0.79] |
| Aesthetic quality | 56.37 | 56.95 | +0.57*&nbsp;[+0.17,&nbsp;+0.97] |
| Subject consistency | 96.88 | 97.07 | +0.19*&nbsp;[+0.10,&nbsp;+0.28] |
| Background consistency | 96.06 | 96.19 | +0.12*&nbsp;[+0.07,&nbsp;+0.18] |
| Subject, within clips | 96.48 | 96.50 | +0.02&nbsp;[−0.13,&nbsp;+0.18] |
| Subject, clip to clip (Consistency) | 76.47 | 79.51 | +3.05*&nbsp;[+2.33,&nbsp;+3.78] |
| Background, clip to clip | 82.05 | 84.11 | +2.05*&nbsp;[+1.62,&nbsp;+2.50] |

**LongLive + Commit Forcing** vs **LongLive**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.72 | 81.93 | +0.21*&nbsp;[+0.05,&nbsp;+0.37] |
| Dynamic degree | 42.96 | 46.42 | +3.46*&nbsp;[+1.48,&nbsp;+5.56] |
| Motion smoothness | 98.74 | 98.59 | −0.15*&nbsp;[−0.19,&nbsp;−0.11] |
| Temporal flickering | 97.61 | 97.37 | −0.24*&nbsp;[−0.32,&nbsp;−0.17] |
| Imaging quality | 68.19 | 68.98 | +0.79*&nbsp;[+0.47,&nbsp;+1.11] |
| Aesthetic quality | 58.92 | 58.99 | +0.06&nbsp;[−0.20,&nbsp;+0.33] |
| Subject consistency | 97.69 | 97.62 | −0.06*&nbsp;[−0.13,&nbsp;−0.00] |
| Background consistency | 96.46 | 96.46 | −0.00&nbsp;[−0.05,&nbsp;+0.04] |
| Subject, within clips | 97.21 | 97.00 | −0.21*&nbsp;[−0.30,&nbsp;−0.12] |
| Subject, clip to clip (Consistency) | 84.16 | 85.25 | +1.09*&nbsp;[+0.62,&nbsp;+1.57] |
| Background, clip to clip | 87.17 | 88.36 | +1.19*&nbsp;[+0.92,&nbsp;+1.47] |

</details>

<details>
<summary>240 s, ID-Forcing's 128 prompts: LongLive and ID-Forcing on Self-Forcing</summary>

Source: [`results/long_horizon/tables/idf128_240s.txt`](results/long_horizon/tables/idf128_240s.txt) · spec [`results/long_horizon/specs/idf128_240s.json`](results/long_horizon/specs/idf128_240s.json)

**ID-Forcing on Self-Forcing + Commit Forcing** vs **ID-Forcing on Self-Forcing**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.32 | 81.65 | +0.34*&nbsp;[+0.05,&nbsp;+0.70] |
| Dynamic degree | 63.67 | 61.05 | −2.62*&nbsp;[−5.01,&nbsp;−0.34] |
| Motion smoothness | 97.68 | 97.86 | +0.18*&nbsp;[+0.02,&nbsp;+0.37] |
| Temporal flickering | 96.08 | 96.35 | +0.27*&nbsp;[+0.07,&nbsp;+0.51] |
| Imaging quality | 67.82 | 68.58 | +0.76*&nbsp;[+0.31,&nbsp;+1.27] |
| Aesthetic quality | 55.82 | 56.64 | +0.82*&nbsp;[+0.40,&nbsp;+1.25] |
| Subject consistency | 96.73 | 97.04 | +0.32*&nbsp;[+0.16,&nbsp;+0.53] |
| Background consistency | 96.02 | 96.17 | +0.15*&nbsp;[+0.09,&nbsp;+0.21] |
| Subject, within clips | 96.33 | 96.55 | +0.22&nbsp;[−0.03,&nbsp;+0.60] |
| Subject, clip to clip (Consistency) | 75.07 | 78.65 | +3.58*&nbsp;[+2.86,&nbsp;+4.30] |
| Background, clip to clip | 80.86 | 83.54 | +2.68*&nbsp;[+2.16,&nbsp;+3.22] |

**LongLive + Commit Forcing** vs **LongLive**

| Metric | Base | + Commit Forcing | Δ [95% CI] |
|:---|---:|---:|:---|
| Quality | 81.56 | 81.84 | +0.28*&nbsp;[+0.10,&nbsp;+0.46] |
| Dynamic degree | 41.56 | 45.98 | +4.41*&nbsp;[+2.16,&nbsp;+6.85] |
| Motion smoothness | 98.70 | 98.52 | −0.18*&nbsp;[−0.23,&nbsp;−0.13] |
| Temporal flickering | 97.56 | 97.27 | −0.29*&nbsp;[−0.39,&nbsp;−0.21] |
| Imaging quality | 68.03 | 69.09 | +1.06*&nbsp;[+0.66,&nbsp;+1.43] |
| Aesthetic quality | 59.07 | 58.92 | −0.16&nbsp;[−0.45,&nbsp;+0.13] |
| Subject consistency | 97.67 | 97.68 | +0.01&nbsp;[−0.05,&nbsp;+0.06] |
| Background consistency | 96.43 | 96.51 | +0.08*&nbsp;[+0.03,&nbsp;+0.13] |
| Subject, within clips | 97.26 | 97.09 | −0.17*&nbsp;[−0.26,&nbsp;−0.09] |
| Subject, clip to clip (Consistency) | 83.41 | 85.36 | +1.96*&nbsp;[+1.49,&nbsp;+2.44] |
| Background, clip to clip | 86.53 | 88.50 | +1.97*&nbsp;[+1.63,&nbsp;+2.30] |

</details>

</details>

[Per-video data, metric definitions and reproduction commands](results/README.md).
