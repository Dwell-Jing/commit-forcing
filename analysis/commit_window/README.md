# Recent-context and self-only committing

We compare committing with the current clean block alone (self-only) and with recent trajectory context, retaining
denoising, sink KV storage and cache-position rules within each framework. Recent context improves clip-to-clip
Subject Consistency over self-only committing on both SF with a sink and LongLive, while reducing Dynamic Degree.
In these historical 60-second controls, neither seed-0 Quality difference is significant. The comparison exposes a
continuity–motion tradeoff.

The tables below retain the historical window and self-only studies. The current LongLive main configuration
reads six frames during committing and stores 12 physical frames, matching Base storage; its separate standard-suite
evaluation is in [common946](../../results/vbench_full/common946/README.md).

## Current window scans

LongLive reaches its observed consistency plateau with the current and preceding blocks. Denser RF-TF and
Rolling Sink scans place their plateaus at 6–12 and 6–9 frames, respectively. SF with a sink favors 9–12 frames:
9 minus 6 improves clip-to-clip Subject Consistency by +0.51 [+0.18, +0.84] when the two seeds are averaged within
each prompt. Its 21-frame context scores lower than 9 frames.

Framewise SGF generates one latent frame per block. Two frames therefore implement current-plus-previous-block
committing; its separate temporal-span diagnostic has a 3–6-frame plateau and lower consistency at 9–17 frames.
On blockwise SGF, SGF+ and CF, the tested recent windows show no significant consistency gain over self-only.
[Recorded window levels, paired intervals and source summaries](../../results/current6_custom/README.md) retain
the distinct prompt sets and block sizes. These scans describe generator-dependent plateaus rather than a shared
optimal frame count.

## Historical controls

The core three-context comparison uses 200 `rollf200` prompts at 60 seconds, generation seed 0, and VBench-Long
scores ×100. Fused Subject is `subject_consistency`; Subject c2c is the separate clip-to-clip readout.

| Framework | Committing context | Quality | Dynamic | Fused Subject | Subject c2c |
|---|---|---:|---:|---:|---:|
| SF + sink | sink 3 + newest 18 | 81.33 | 57.52 | 96.72 | 75.18 |
| SF + sink | self-only (current 3) | 81.28 | 67.80 | 96.56 | 74.69 |
| SF + sink | newest 21 trajectory frames (Commit Forcing) | 81.63 | 59.58 | 96.87 | 78.56 |
| LongLive | sink 3 + newest 9 | 82.23 | 42.98 | 97.76 | 86.01 |
| LongLive | self-only (current 3) | 82.73 | 53.03 | 97.69 | 86.21 |
| LongLive | newest 12 trajectory frames (legacy control) | 82.65 | 49.38 | 97.70 | 86.93 |

| Recent − self-only, seed 0 | Δ Quality [95% CI] | Δ Dynamic | Δ Subject c2c | Δ Fused Subject | Δ Imaging |
|---|---|---:|---:|---:|---:|
| SF + sink | +0.36 [−0.16, +0.81] | −8.22\* | +3.87\* | +0.32\* | +0.90\* |
| LongLive | −0.08 [−0.21, +0.06] | −3.65\* | +0.72\* | +0.00 | +0.20 |

Differences use unrounded per-prompt scores. `*` means the paired 95% bootstrap interval excludes zero. On SF with a
sink, recent context also improves Motion Smoothness (+0.46\*) and Temporal Flickering (+0.85\*) over self-only. On
LongLive, these changes are +0.13\* and +0.26\*. Higher scores on these two dimensions indicate smoother motion and
less flickering; Dynamic Degree measures a different aspect of motion.

SF keeps a 24-frame physical cache in all three arms. The historical LongLive base-policy, self-only and recent-window
arms all store 15 frames (sink 3 + newest 12) and retain the base denoising read policy. These are matched-storage
window controls, distinct from the current common946 Base / six-frame pair, which both store 12 frames.
Self-only changes the committing read count as well as its historical
dependencies. Sink KV remains stored and accessible during denoising; recent and current representations can retain
indirect effects of earlier history.

These native-framework self-only arms are distinct from the complete ID-Forcing procedure, whose SF adaptation
also changes handover and recaching; see [ID-Forcing comparisons](../not_ood/README.md).
The [SGF four-context controls](../sgf_committing_controls/README.md) add a matched 9-frame sink control and a
self-only comparison. On SGF, recent and self-only committing have no significant Quality or clip-to-clip Subject
difference; recent context improves smoothness and flickering while reducing motion. Retaining recent dependencies
therefore has different effects across generators.

## Full recent-window results

On LongLive, the commit pass can read the newest 3, 6, 9 or 12 trajectory frames instead of the sink and the newest 9.
Every tested window raises Quality over the base model. The 3-frame window (self-only) has the highest Dynamic
Degree, and 6 frames give the highest clip-to-clip Subject Consistency among windows run on both seeds (9 frames,
run on seed 0 only, is close to 6). Quality differences between windows stay within ±0.17 in the reported contrasts
and can change sign between seeds.

VBench-Long, rollf200 × 60 s, ×100, generation seed 0 / seed 1 (`*`: the paired 95% bootstrap interval excludes 0).
Consistency: clip-to-clip subject consistency.

| Commit pass reads | Quality | Dynamic | Consistency | Background, clip to clip | Δ Quality to base |
|---|---|---|---|---|---|
| sink 3 + newest 9 (base) | 82.23 / 82.19 | 42.98 / 42.03 | 86.01 / 86.02 | 88.40 / 88.20 | |
| newest 3 (the block itself) | 82.73 / 82.83 | 53.03 / 54.18 | 86.21 / 85.91 | 88.79 / 88.49 | +0.49\* / +0.64\* |
| newest 6 | 82.73 / 82.66 | 49.40 / 48.65 | 87.21 / 87.09 | 89.53 / 89.36 | +0.49\* / +0.46\* |
| newest 9 | 82.72 / – | 49.47 / – | 87.23 / – | 89.55 / – | +0.48\* / – |
| newest 12 (legacy control) | 82.65 / 82.67 | 49.38 / 50.20 | 86.93 / 86.70 | 89.17 / 88.84 | +0.42\* / +0.48\* |

Between windows, Consistency: 6 − 3 +1.00\* / +1.18\*, 6 − 12 +0.28\* / +0.38\*, 9 − 6 +0.02 (seed 0); Dynamic: 6 − 3
−3.63\* / −5.53\*; Quality: 6 − 3 +0.00 / −0.17\*, 6 − 12 +0.08 / −0.02.

Self-Forcing with a 3-frame sink (`integrations/recency_forcing --trb off`), where every denoising pass reads
the sink and the newest 18 frames; seed 0 / seed 1:

| Commit pass reads | Quality | Dynamic | Consistency | Background, clip to clip |
|---|---|---|---|---|
| sink 3 + newest 18, as the denoising passes | 81.33 / 81.35 | 57.52 / 58.22 | 75.18 / 74.71 | 80.64 / 80.31 |
| newest 3 (the block itself) | 81.28 / – | 67.80 / – | 74.69 / – | 81.33 / – |
| newest 21 (Commit Forcing) | 81.63 / 81.54 | 59.58 / 58.87 | 78.56 / 78.11 | 83.31 / 83.19 |

The SF table uses seed 0 / seed 1. Commit Forcing − sink: Quality +0.31 [−0.30, +0.83] / +0.20 [−0.28, +0.59],
Consistency +3.38\* / +3.40\*, Dynamic +2.07 / +0.65. The SF self-only arm has only seed 0. LongLive has self-only and
recent arms for both seeds, but the existing published specs contain the recent-minus-self-only contrast only for
seed 0; no missing paired interval is inferred here. Reading only the block itself removes recent frames together
with the sink; Commit Forcing retains recent trajectory context while excluding direct sink access.

## Self-only confirmation beyond 60-second rollf200

On the standard 946-entry suite, self-only minus six-frame LongLive changes Quality by +0.18 [−0.07, +0.45] and
Total by +0.07 [−0.14, +0.31]. It increases Dynamic Degree by 5.32 points while reducing Subject, Background,
Motion Smoothness, Temporal Flickering and Aesthetic Quality. Both conditions store 12 physical frames.

On 128 MovieGen prompts at 120 and 240 seconds, six frames minus self-only improves clip-to-clip Subject by
1.30 and 1.31 points, but lowers Quality by 0.17 and 0.21 and Dynamic Degree by 6.32 and 6.07 points. All six of
these differences have intervals excluding zero. Those LongLive conditions retain 15-frame physical storage.
The [full self-only controls](data/window_controls/README.md) retain every paired interval and absolute score.

## Window changes across generators

A separate 60-second sweep uses rollf200 prompts 0–99, generation seed 0, on SGF, SGF+, RF-TF, Rolling Sink and
Context Forcing. All nine Quality changes from each model's fixed main context have intervals including zero.
Six frames versus 21 improves long-range Subject by 2.27 points on RF-TF and 1.85 on Rolling Sink; motion amount
has negative point changes. The effect of retaining recent context is not monotonic across models.
[All window contrasts](data/window_controls/README.md#cross-model-committing-window-sweep).

## Commands and score provenance

```bash
# Historical LongLive controls: newest 3 / 6 / 9 / 12 committing frames, with 15-frame physical storage.
python analysis/commit_window/generate.py --commit-frames 6 --code /path/to/LongLive \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window
# Self-Forcing + sink: the block itself (21 = integrations/recency_forcing --trb off --rule on)
python analysis/commit_window/generate_sf_sink.py --commit-frames 3 --code /path/to/Self-Forcing \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window
# score <out>/commit6 etc. with eval/vbench_long (prep.py --videos outputs/commit_window/commit6, score.sh, collect.py)
python analysis/commit_window/tables.py      # the tables above, from results/vbench_long_60s.csv
python eval/vbench_long/compare.py --spec results/specs/vbl60_longlive_commit_window.json
```

`tables.py` replays the specs `vbl60_seed0`, `vbl60_longlive_commit_window`, `vbl60_longlive_commit6_vs_12`,
`vbl60_seed1_a` and `vbl60_seed1_b` with `compare.py`, so every interval is the one in `results/tables/`. The source is
[results/vbench_long_60s.csv](../../results/vbench_long_60s.csv), paired by prompt with 4000 bootstrap draws.
The two seed-0 contrasts in the core table are in [vbl60_seed0.txt](../../results/tables/vbl60_seed0.txt). These public
specs fix the bootstrap contrast order and RNG stream; retain their intervals when replaying these repository
tables. Labels in
`results/`: `longlive`, `longlive+commit_self` (3), `longlive+commit6`, `longlive+commit9`, `longlive+rule` (12),
`sf_sink`, `sf_sink+commit_self`, `sf_sink+rule`. `generate.py` uses the per-pass control of
[`analysis/longlive_sink/generate.py`](../longlive_sink/generate.py).
The historical CSV label `longlive+rule` always denotes the 12-frame control; it is not an alias for the six-frame
arm. The public [LongLive integration](../../integrations/longlive/README.md) now defaults to six-frame committing
with 12-frame storage. Its explicit `--commit-profile legacy12` retains 12-frame committing and 15-frame storage.

<a id="quick-window-confirmation"></a>

## Independent quick59 window check

We additionally evaluate 59 held-out quick60 prompts at 48 seconds with generation seeds 0, 1, and 2. One prompt
overlapping the window-calibration set is excluded from every readout. The reference uses the existing 12-frame
recent committing context. Denoising, sampler, attention kernels, and RNG protocol are shared. All frame counts
include the current 3-frame block. Adaptive contexts use a static test based on the running mean latent motion of
committed blocks, with threshold 0.26105 fixed on 40 separate calibration prompts; otherwise they keep 12 frames.

| Context | Committing read when the static test is met | Otherwise |
|---|---|---|
| Reference (`LLS_c0`) | 12 recent/current frames | 12 |
| Adaptive 3 (`LLW_ad`) | 3 current frames | 12 |
| Adaptive 6 (`LLW_ad6`) | 6 recent/current frames | 12 |
| Adaptive heads (`LLW_adh6`) | 3 frames at the 180 selected local heads, 6 at the others | 12 |
| Fixed 6 (`LLW_w6`) | 6 recent/current frames, no static test | 6 |

Scores use the custom-input seven visual dimensions of VBench-Long. The pooled estimate averages three seeds within
each prompt, then resamples the 59 prompts. Each row below subtracts the 12-frame reference; `*` denotes a paired
95% interval excluding zero.

| Context | Δ Quality [95% CI] | Δ Subject c2c [95% CI] | Δ Dynamic [95% CI] | Δ Background c2c [95% CI] | Δ Subject within clips [95% CI] |
|---|---|---|---|---|---|
| Adaptive 3 | +0.27* [+0.13, +0.41] | −0.44* [−0.90, −0.01] | +3.51* [+1.55, +5.65] | −0.30 [−0.58, +0.01] | +0.04 [−0.01, +0.09] |
| Adaptive 6 | +0.12* [+0.05, +0.20] | +0.31* [+0.14, +0.50] | +0.45 [−0.45, +1.34] | +0.25* [+0.12, +0.41] | +0.12* [+0.09, +0.15] |
| Adaptive heads | +0.15* [+0.07, +0.24] | +0.08 [−0.16, +0.32] | +1.22* [+0.07, +2.38] | +0.20* [+0.02, +0.40] | +0.10* [+0.05, +0.14] |
| Fixed 6 | +0.16* [+0.05, +0.27] | +0.55* [+0.30, +0.81] | +0.99 [−0.47, +2.45] | +0.43* [+0.24, +0.64] | +0.21* [+0.16, +0.26] |

The Adaptive-3 consistency decrease has a negative mean in all three seeds (−0.40, −0.29, −0.62) and a negative pooled
interval. Its motion-adjusted change is −0.22 [−0.54, +0.10]. This descriptive regression adjustment leaves no clear
residual consistency change; it does not establish that motion accounts for the entire effect.

For Adaptive 6 minus Fixed 6, Quality changes by −0.03 [−0.14, +0.07], Subject c2c by −0.24* [−0.48, −0.04], Background
c2c by −0.18* [−0.35, −0.03], and Subject within clips by −0.09* [−0.15, −0.05]. The static test gives no advantage
over the fixed-6 control. Fixed 6 improves Quality and continuity relative to 12 frames without a significant
Dynamic Degree change in this separate prompt set.

The adaptive comparisons were specified before their quick60 videos were generated. The fixed-6 control was added
after the initial adaptive readout, with its contrast specified before generating fixed-6 videos. We preserve this
sequence in [data/quick59_prereg.md](data/quick59_prereg.md). Full seed-specific levels, contrasts, and subgroup
readouts remain in [data/quick59_readout.md](data/quick59_readout.md), with reported values in
[data/quick59_contrasts.csv](data/quick59_contrasts.csv) and source hashes in
[data/quick59_provenance.json](data/quick59_provenance.json).
The subgroup statistic retains the original fraction of recorded `commit_windows` entries equal to 3. This is a
historical marker statistic, rather than a common actual read count across adaptive contexts; adaptive 6 uses its
configured 6-frame context when narrowed.

[data/quick59_per_video_scores.csv](data/quick59_per_video_scores.csv) contains all 885 post-exclusion scored videos;
[data/quick59_prompts.csv](data/quick59_prompts.csv) supplies the actual prompt texts and their original quick60 IDs.
The excluded calibration-overlap ID is 43, with source hashes in
[data/quick59_metadata.json](data/quick59_metadata.json). The portable readout retains the original sequential
bootstrap stream, including subgroup computations before the fixed-control contrast:

```bash
python analysis/commit_window/source/quick59_readout.py \
    --scores analysis/commit_window/data/quick59_per_video_scores.csv --check-reported
```

This 59-prompt, 48-second check supplements the rollf200 window comparison. These scores retain their original
contexts and do not substitute for the separate [common946 test](../../results/vbench_full/common946/README.md).
The current standard-suite LongLive main row uses six-frame committing and 12-frame physical storage in both arms;
the earlier 12-frame/15-storage configuration remains a control.

The other core comparisons examine [sink access across stages](../longlive_sink/README.md) and
[committing sources on Rolling Sink](../committing_source/README.md).
