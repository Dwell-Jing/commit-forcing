# Current six-frame method: custom-prompt results and window diagnostics

The main method constructs KV from the current and immediately preceding 3-frame blocks (6 latent frames).
These custom-prompt studies are separate from the [946-entry standard VBench suite](../vbench_full/common946/README.md).
The 60-second comparisons use all 200 rollf200 prompts with generation seeds 0 and 1. Six full-rule configurations
use 6-frame committing; the additional CF sink-exclusion row is a component control. The original
[9/21-frame supporting controls](../../RESULTS.md#committing-replication) retain their labels and values.

At 60 seconds, the six-frame SGF arm improves clip-to-clip Subject Consistency by 4.76 and 4.91 points with the two
seeds. At 240 seconds on the first 32 extended MovieGen prompts, the gain is 5.42 points. Its Quality change is
+0.90 [−0.002, +1.82], which is not significant. This differs from the archived nine-frame SGF control's +5.07
consistency and +0.72 Quality changes. The six-frame cases in the current figures use the current method.

A descriptive OLS adjustment of the seed-0 SGF 60-second paired consistency changes for paired Dynamic Degree
changes gives an intercept of +4.87 [+3.89, +5.95] with 2,000 prompt-bootstrap draws. This regression adjustment
does not hold motion fixed experimentally; the unadjusted Dynamic Degree increase is +11.33 points.

## Window boundaries

RF-TF reaches a 6–12-frame consistency plateau and Rolling Sink a 6–9-frame plateau in their 100-prompt scans;
their 21-frame contexts score lower. SF with a sink favors a wider 9–12-frame window: 9 minus 6 frames gives
+0.51 [+0.18, +0.84] in clip-to-clip Subject Consistency after averaging the two seed-specific differences within
each prompt. Its 21-frame window is lower than 9 frames by 1.42 points. The framewise SGF diagnostic instead uses
one latent frame per block. Its 3–6-frame plateau and lower scores at 9–17 frames concern temporal span;
2 frames, rather than 6, implement current-plus-previous-block committing on that model.

These tests retain base denoising and shared generation noise within their paired window comparisons. They
support generator-dependent window choices, rather than a universally optimal single preceding block.

## Data and reproduction

[`summary.json`](summary.json) freezes all reported aggregate rows from the manuscript tables, including their
original interval precision and source significance marks. Source file hashes refer to Overleaf commit
`6d6394380687d64fe505f050330f9118773a2e37`. Source tables are `rollf200_seed_results.tex`,
`committing_sources_240.tex`, `committing_window_plateaus.tex`, `sf_sink_committing_windows.tex`, and
`framewise_committing_windows.tex`; the descriptive adjustment and 240-second SGF Dynamic interval come from
`appendix/result-details.tex`. Scores and changes are on the 0–100 scale. Paired intervals use 4,000
prompt-bootstrap draws unless the OLS adjustment specifies 2,000. An asterisk in the tables below denotes an
interval excluding zero. Missing intervals are left absent, and reference rows use an em dash.

```bash
python results/current6_custom/reproduce.py
python results/current6_custom/reproduce.py --markdown
```

The reader checks the frozen values, coverage, rounding and recorded interval decisions. It does not reconstruct
bootstrap intervals from aggregate counts. This package contains no per-prompt numerical values, individual human
responses, participant identifiers or video files.

## Reported aggregate tables

### 60-second rollf200, generation seed 0

| Configuration | Quality: Base | Recent-context | Δ Quality | Subject c2c: Base | Recent-context | Δ Subject c2c | Δ Dynamic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SGF (6) | 83.58 | 84.51 | +0.93* [+0.55, +1.30] | 86.54 | 91.30 | +4.76* [+3.79, +5.73] | +11.33* [+6.53, +15.98] |
| RF-TF (6) | 82.01 | 82.43 | +0.42* [+0.18, +0.66] | 75.02 | 81.38 | +6.36* [+5.46, +7.24] | -3.92* [-6.75, -1.17] |
| LongLive (6 frames) | 82.23 | 82.73 | +0.49* [+0.33, +0.66] | 86.01 | 87.21 | +1.20* [+0.84, +1.58] | +6.42* [+4.27, +8.58] |
| CF, full rule | 82.78 | 82.91 | +0.13 [-0.10, +0.35] | 78.72 | 81.95 | +3.23* [+2.56, +3.94] | -1.05 [-4.05, +1.92] |
| Rolling Sink (6) | 82.61 | 82.68 | +0.07 [-0.13, +0.27] | 86.00 | 88.45 | +2.45* [+1.81, +3.17] | +2.02 [-0.83, +4.73] |
| SF with sink (6) | 81.33 | 81.64 | +0.31 [-0.15, +0.84] | 75.18 | 79.62 | +4.44* [+3.60, +5.25] | -0.93 [-3.92, +2.17] |
| CF, sink excluded | 82.78 | 83.11 | +0.32* [+0.11, +0.54] | 78.72 | 80.52 | +1.80* [+1.20, +2.42] | +6.70* [+4.08, +9.20] |

### 60-second rollf200, generation seed 1

| Configuration | Quality: Base | Recent-context | Δ Quality | Subject c2c: Base | Recent-context | Δ Subject c2c | Δ Dynamic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| SGF (6) | 83.85 | 84.42 | +0.57* [+0.24, +0.91] | 86.60 | 91.52 | +4.91* [+3.92, +5.90] | +8.55* [+3.98, +13.07] |
| RF-TF (6) | 82.00 | 82.69 | +0.69* [+0.46, +0.92] | 74.42 | 80.99 | +6.57* [+5.71, +7.46] | -0.05 [-2.35, +2.23] |
| LongLive (6 frames) | 82.19 | 82.66 | +0.46* [+0.30, +0.64] | 86.02 | 87.09 | +1.06* [+0.72, +1.43] | +6.62* [+4.53, +8.73] |
| CF, full rule | 82.70 | 83.12 | +0.43* [+0.22, +0.64] | 78.63 | 82.16 | +3.53* [+2.83, +4.26] | +1.33 [-1.45, +4.13] |
| Rolling Sink (6) | 82.40 | 82.66 | +0.26* [+0.07, +0.45] | 86.34 | 88.89 | +2.54* [+1.96, +3.18] | +4.05* [+1.83, +6.30] |
| SF with sink (6) | 81.35 | 81.57 | +0.23 [-0.42, +0.80] | 74.71 | 78.87 | +4.16* [+3.33, +4.96] | +0.68 [-2.67, +4.07] |
| CF, sink excluded | 82.70 | 83.19 | +0.50* [+0.31, +0.69] | 78.63 | 80.24 | +1.61* [+1.02, +2.22] | +7.18* [+4.87, +9.52] |

### 240-second MovieGen: absolute scores

| Generator | Committing configuration | Quality | Fused Subject | Fused Background | Dynamic |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CF | Base | 83.60 | 98.03 | 96.78 | 58.46 |
| CF | Exclude slow memory only | 83.41 | 98.23 | 97.00 | 48.83 |
| CF | Exclude sink only | 84.10 | 97.97 | 96.70 | 65.52 |
| CF | Recent-context | 84.04 | 98.21 | 96.87 | 59.64 |
| SGF | Base | 83.97 | 98.26 | 96.75 | 49.11 |
| SGF | Recent-context | 84.87 | 98.59 | 97.17 | 60.62 |

### 240-second MovieGen: recent-context minus Base

| Generator | Δ Quality | Δ Fused Subject | Δ Fused Background | Δ Subject c2c |
| :--- | :--- | :--- | :--- | :--- |
| CF | +0.44 [-0.08, +0.97] | +0.18* [+0.06, +0.31] | +0.10 [-0.01, +0.20] | +2.23* [+0.51, +3.89] |
| SGF | +0.90 [-0.002, +1.82] | +0.34* [+0.14, +0.55] | +0.42* [+0.22, +0.65] | +5.42* [+3.02, +8.09] |

SGF Dynamic Degree changes by +11.51* [+0.60, +23.44]. Its Quality interval includes zero, including the −0.002 lower endpoint.

### RF-TF and Rolling Sink window plateaus

| Generator | Window | Δ Quality | Δ Dynamic | Δ Subject c2c |
| :--- | :--- | :--- | :--- | :--- |
| RF-TF | 3 | -0.24* [-0.44, -0.03] | +4.20* [+1.93, +6.63] | -2.51* [-3.34, -1.74] |
| RF-TF | 6 | — | — | — |
| RF-TF | 9 | -0.08 [-0.19, +0.04] | +0.17 [-1.13, +1.53] | -0.29 [-0.69, +0.10] |
| RF-TF | 12 | -0.04 [-0.18, +0.10] | +0.83 [-0.73, +2.60] | -0.57 [-1.19, +0.03] |
| RF-TF | 21 | -0.16 [-0.33, +0.02] | +2.70* [+0.70, +5.03] | -2.27* [-2.98, -1.58] |
| Rolling Sink | 3 | +0.15 [-0.10, +0.38] | +6.00* [+2.97, +9.03] | -0.59* [-1.17, -0.0025] |
| Rolling Sink | 6 | — | — | — |
| Rolling Sink | 9 | +0.03 [-0.13, +0.17] | -0.33 [-2.33, +1.47] | -0.28 [-0.65, +0.05] |
| Rolling Sink | 12 | +0.03 [-0.17, +0.23] | +0.47 [-1.93, +3.07] | -0.70* [-1.28, -0.22] |
| Rolling Sink | 21 | +0.12 [-0.15, +0.40] | +2.57 [-0.77, +6.17] | -1.85* [-2.53, -1.23] |

Changes are relative to 6 frames, on rollf200 prompts 0–99 at 60 seconds with seed 0.

### SF with a sink: windows by seed

| Seed | Window | Quality | Dynamic | Subject c2c | Δ Quality | Δ Subject c2c |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | 3 | 81.28 | 67.80 | 74.69 | -0.36 [-1.00, +0.23] | -4.93* [-5.82, -4.07] |
| 0 | 6 | 81.64 | 56.58 | 79.62 | — | — |
| 0 | 9 | 81.54 | 56.68 | 80.09 | -0.09 [-0.56, +0.20] | +0.47* [+0.03, +0.90] |
| 0 | 12 | 81.77 | 58.08 | 79.97 | +0.14 [-0.40, +0.57] | +0.35 [-0.16, +0.86] |
| 0 | 21 | 81.63 | 59.58 | 78.56 | -0.00 [-0.57, +0.42] | -1.06* [-1.77, -0.31] |
| 1 | 6 | 81.57 | 58.90 | 78.87 | — | — |
| 1 | 9 | 81.80 | 60.58 | 79.42 | +0.22* [+0.07, +0.37] | +0.55* [+0.04, +1.02] |
| 1 | 12 | 81.69 | 61.02 | 79.29 | +0.11 [-0.16, +0.36] | +0.42 [-0.12, +0.94] |
| 1 | 21 | 81.54 | 58.87 | 78.11 | -0.03 [-0.48, +0.36] | -0.76* [-1.48, -0.05] |

Changes are relative to 6 frames within each seed; all 200 rollf200 prompts are used.

### SF with a sink: pooled window contrasts

| Window contrast | Δ Quality | Δ Dynamic | Δ Subject c2c |
| :--- | :--- | :--- | :--- |
| 9 minus 6 | +0.06 [-0.16, +0.23] | +0.89 [-0.45, +2.29] | +0.51* [+0.18, +0.84] |
| 12 minus 6 | +0.13 [-0.14, +0.36] | +1.81* [+0.25, +3.37] | +0.39 [-0.0005, +0.78] |
| 12 minus 9 | +0.06 [-0.11, +0.24] | +0.92 [-0.47, +2.33] | -0.12 [-0.44, +0.21] |
| 21 minus 9 | -0.08 [-0.36, +0.17] | +0.59 [-1.38, +2.58] | -1.42* [-1.86, -0.96] |
| 21 minus 6 | -0.02 [-0.31, +0.23] | +1.48 [-0.59, +3.52] | -0.91* [-1.47, -0.33] |

Each prompt contributes the average of its seed-0 and seed-1 differences before prompt resampling.

### Framewise SGF diagnostic

| Window | Quality | Dynamic | Subject c2c | Background c2c | Δ Quality | Δ Subject c2c |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Base (21, with sink) | 83.55 | 64.70 | 84.90 | 88.55 | -0.15 [-0.55, +0.26] | -7.12* [-8.72, -5.72] |
| w=1 | 83.51 | 76.50 | 90.37 | 92.98 | -0.19 [-0.62, +0.25] | -1.64* [-2.68, -0.77] |
| w=2 | 83.64 | 67.50 | 91.22 | 93.57 | -0.07 [-0.38, +0.23] | -0.80* [-1.72, -0.14] |
| w=3 | 83.71 | 64.53 | 91.76 | 94.04 | +0.01 [-0.13, +0.14] | -0.26 [-1.05, +0.29] |
| w=4 | 83.73 | 64.50 | 91.86 | 94.03 | +0.03 [-0.06, +0.12] | -0.16 [-0.93, +0.30] |
| w=6 | 83.71 | 63.97 | 92.02 | 94.14 | — | — |
| w=9 | 83.70 | 64.33 | 91.49 | 93.82 | -0.00 [-0.09, +0.09] | -0.53* [-0.83, -0.25] |
| w=12 | 83.79 | 66.20 | 91.05 | 93.48 | +0.08 [-0.03, +0.20] | -0.97* [-1.53, -0.51] |
| w=17 | 83.82 | 68.10 | 90.26 | 92.83 | +0.11 [-0.05, +0.30] | -1.76* [-2.37, -1.24] |

Changes are relative to the 6-frame diagnostic. This generator uses one latent frame per block:
2 frames implement current-plus-previous-block committing; 6 frames include five predecessors.
The study uses rollf200 prompts 0–99 at 60 seconds with seed 0.
