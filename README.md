<div align="center">

<h1>What Helps Denoising Can Hurt Memory:<br>Rethinking History in Long Video Generation</h1>

**Commit Forcing: construct new KV from the current and immediately preceding blocks.**

[![Paper](https://img.shields.io/badge/Paper-coming%20soon-b31b1b.svg)](#news)&nbsp;
[![Models](https://img.shields.io/badge/models-6-orange.svg)](integrations/)&nbsp;
[![Videos](https://img.shields.io/badge/videos-60%E2%80%93240%20s-orange.svg)](RESULTS.md)&nbsp;
[![Code](https://img.shields.io/badge/code-Apache--2.0-blue.svg)](LICENSE)

</div>

## News

<table>
<tr><td><img src="https://img.shields.io/badge/2026--10--09-released-2ea44f" alt="2026-10-09, released"></td><td><b>Initial release</b>: Code and evaluation results are available.</td></tr>
<tr><td><img src="https://img.shields.io/badge/coming-soon-lightgrey" alt="coming soon"></td><td><b>arXiv preprint</b></td></tr>
</table>

<p align="center">
  <img src="assets/teaser.png" width="92%" alt="Historical sources and the committing window: preserve base denoising while choosing which trajectory context constructs new KV.">
</p>

<sub>Historical context has different effects when a block is denoised and when it is committed to the KV cache.</sub>

---

Autoregressive video diffusion uses historical context to denoise the current block and to construct clean KV for
future blocks. SGF shows that future-prediction losses in Self-Forcing supervise denoising but not clean committing.
On LongLive and SGF, sink access helps denoising but can increase drift during committing.
At fixed context size and temporal positions, mean clip-to-clip Subject Consistency decreases with older
trajectory content on SGF and LongLive. Across five configurations supporting longer histories, consistency
rises, plateaus and then falls as the committing context expands.

Based on these findings, we propose **Commit Forcing**, a training-free rule for long video generation.
It preserves the base denoising policy and constructs new clean KV using the current
block and the immediately preceding block from the original generated trajectory. The current block supplies clean
latents; the preceding block is accessed through its stored KV. With 3 latent frames per block, the committing
context contains 6 frames after startup (3 at the first block). Direct access to other history, including sink KV, is
excluded during committing. Base cache storage and update remain in place; earlier history can still affect new KV
indirectly through the generated current block and the preceding block's KV. Commit Forcing requires no retraining or additional inference computation and can be directly applied to
KV-cached autoregressive video generators.

## Contributions

- **Stage effects.** Controlled interventions show that the same historical context can have opposing effects
  during denoising and committing. On LongLive, the harm persists even though committing uses that context
  during training.
  ([stage interventions](analysis/longlive_sink/README.md), [KV construction](analysis/kv_construction/README.md))
- **Recency and window size.** At fixed context size and temporal positions, older history lowers consistency.
  Window scans reveal a rise, plateau and decline, with generator-dependent plateaus. We relate these patterns
  to temporal smoothing, indirect historical influence through recent KV, and outdated context.
  ([historical recency](analysis/committing_content_age/README.md), [window effects](analysis/window_effects/README.md))
- **Commit Forcing.** The training-free rule uses the current and immediately preceding blocks. On 60-second
  VBench, Quality and Total improve on all six generators, significantly on 5 of 6. Clip-to-clip Subject
  Consistency gains extend to 240-second videos, reaching 5.42 points on SGF
  (32 extended MovieGen prompts, seed 0), with favorable human judgments on 120-second LongLive videos.
  ([results](#results))

<p align="center">
  <img src="assets/method.png" width="92%" alt="Commit Forcing: construct new KV from the current and immediately preceding blocks while preserving base denoising and storage.">
</p>

<sub>The clean committing pass reads the current block and stored KV of the immediately preceding block: 3 + 3
latent frames. Base denoising and cache storage remain in place.</sub>

## Results

**Main evaluation: full VBench, 60 s**, the common 946-entry suite, one video per entry (generation seed 0), all 16 dimensions.
Each row compares the same released weights with and without Commit Forcing. Every adapted generator
uses the current and immediately preceding blocks (6 latent frames after startup). Native denoising, sampler and
physical-storage settings remain model-specific; prompts and scoring protocol are shared.

<table>
<thead>
<tr><th rowspan="2" align="left">Model</th><th colspan="3">Quality</th><th colspan="3">Total</th></tr>
<tr><th>Base</th><th>Commit Forcing</th><th>Δ</th><th>Base</th><th>Commit Forcing</th><th>Δ</th></tr>
</thead>
<tbody>
<tr><td>Context Forcing</td><td align="right">84.79</td><td align="right">85.25</td><td align="right"><b>+0.46</b></td><td align="right">82.24</td><td align="right">82.68</td><td align="right"><b>+0.44</b></td></tr>
<tr><td>Rolling Sink</td><td align="right">84.84</td><td align="right">85.25</td><td align="right"><b>+0.41</b></td><td align="right">82.90</td><td align="right">83.26</td><td align="right"><b>+0.36</b></td></tr>
<tr><td>Recency Forcing, training-free †</td><td align="right">84.77</td><td align="right">85.42</td><td align="right"><b>+0.65</b></td><td align="right">82.24</td><td align="right">83.34</td><td align="right"><b>+1.10</b></td></tr>
<tr><td>LongLive</td><td align="right">84.70</td><td align="right">84.99</td><td align="right"><b>+0.29</b></td><td align="right">83.05</td><td align="right">83.36</td><td align="right"><b>+0.31</b></td></tr>
<tr><td>SGF+</td><td align="right">86.32</td><td align="right">86.63</td><td align="right">+0.32</td><td align="right">84.30</td><td align="right">84.64</td><td align="right">+0.34</td></tr>
<tr><td>SGF</td><td align="right">86.06</td><td align="right">87.33</td><td align="right"><b>+1.27</b></td><td align="right">83.85</td><td align="right">84.82</td><td align="right"><b>+0.98</b></td></tr>
</tbody>
</table>

Rows follow ascending Total with Commit Forcing. Scores ×100; differences are computed before rounding.
Bold Δ marks a paired 95% prompt-cluster interval excluding 0. Quality combines seven visual dimensions; Total
also includes nine semantic dimensions. † RF-TF applies Recency Forcing's Temporal Response Bias to released
Self-Forcing weights; it uses no RF-trained checkpoint.
On the 60-second standard suite, Quality and Total improve significantly on 5 of 6 generators. RF-TF has the
largest Total gain, +1.10 points, and SGF has the largest Quality gain, +1.27. On the separate 200-prompt rollf200
evaluation, SGF's raw clip-to-clip Subject gain is +4.76 points; the estimate is +4.87 after descriptive regression adjustment for
paired Dynamic Degree differences. This estimate comes from the paired videos, rather than an experiment with
motion held fixed. In the standard-suite Quality decomposition, Dynamic Degree contributes +1.01 points;
Motion Smoothness decreases by 0.29 points.
[All dimensions, intervals and protocol records](results/vbench_full/common946/README.md).
The two 9-frame ID-Forcing adaptations are [separate framework comparisons](RESULTS.md#id-forcing-framework-comparisons).

**MovieGen, 60 s videos**, 200 fixed [MovieGen prompts](eval/prompts/README.md), generation seed 0.
Quality combines VBench's seven visual dimensions using its official normalization and weights.

| Configuration | Base | Commit Forcing, 6 frames | Δ Quality | Δ Consistency |
|:---|--:|--:|--:|--:|
| SGF | 83.58 | 84.51 | **+0.93** | **+4.76** |
| RF-TF † | 82.01 | 82.43 | **+0.42** | **+6.36** |
| LongLive | 82.23 | 82.73 | **+0.49** | **+1.20** |
| Context Forcing | 82.78 | 82.91 | +0.13 | **+3.23** |
| Rolling Sink | 82.61 | 82.68 | +0.07 | **+2.45** |
| Self-Forcing with sink | 81.33 | 81.64 | +0.31 | **+4.44** |

Every adapted row uses the current and preceding blocks. All six Consistency gains reproduce with generation
seed 1. This custom-prompt comparison includes SF with a sink; the standard-suite main table instead includes SGF+.
Consistency is the interclip component of VBench-Long Subject Consistency; bold changes have paired intervals
excluding zero. [Mapping and fusion with within-clip consistency](eval/vbench_long/README.md).
[Both seeds, motion changes and recorded intervals](results/current6_custom/README.md).

<details>
<summary>Historical wider-context and sink-exclusion controls</summary>

| Model | Base | Recent-context control | Δ Quality | Δ Consistency |
|:---|--:|--:|--:|--:|
| SGF, 9 frames | 83.58 | 84.62 | **+1.04** | **+4.40** |
| RF-TF †, 21 frames | 82.01 | 82.47 | **+0.46** | **+3.86** |
| LongLive | 82.23 | 82.73 | **+0.49** | **+1.20** |
| Context Forcing, sink exclusion | 82.78 | 83.11 | **+0.32** | **+1.80** |
| Context Forcing, full rule | 82.78 | 82.91 | +0.13 | **+3.23** |
| Rolling Sink, 21 frames | 82.61 | 82.72 | +0.11 | **+0.67** |
| Self-Forcing with sink, 21 frames | 81.33 | 81.63 | +0.31 | **+3.38** |

These supporting studies retain their original contexts: 9 frames on SGF, 21 on RF-TF, Rolling Sink and
Self-Forcing with sink, and 6 on LongLive and CF's full rule. The CF sink-exclusion row is a separate control.
They do not evaluate the updated 6-frame SGF, RF-TF or Rolling Sink method arms.
Consistency: VBench-Long's clip-to-clip subject consistency, our measure of long-range consistency.
**bold Δ**: the paired 95% bootstrap interval excludes 0. All seven clip-to-clip Subject gains reproduce with generation
seed 1. [Both seeds and all metrics](RESULTS.md#committing-replication). SGF+, ID-Forcing and SGF + RF compatibility
comparisons remain in [RESULTS.md](RESULTS.md).

</details>

The standard suite scores dimension-specific subsets and applies VBench's static filter for Flickering.
The MovieGen evaluation scores all seven visual dimensions on each prompt and leaves Flickering unfiltered.
Each Base / adapted pair shares its inputs and scoring settings.
LongLive uses 6-frame committing: 3 recent frames and the current 3-frame block.

**Longer videos, 120–240 s**, VBench-Long Quality. Compare within each prompt set:

| Model | Length | Prompts | Base | Adapted | Δ Quality | Δ Consistency |
|:---|:---|:---|--:|--:|--:|--:|
| SGF, 6 frames | 240 s | 32 MovieGen | 83.97 | 84.87 | +0.90 | **+5.42** |
| SGF, 9-frame control | 240 s | 32 MovieGen | 83.97 | 84.69 | **+0.72** | **+5.07** |
| Context Forcing | 240 s | 32 MovieGen | 83.60 | 84.04 | +0.44 | **+2.23** |
| LongLive, 6 frames | 120 s | 128 of ID-Forcing | 81.72 | 82.05 | **+0.33** | **+1.87** |
| LongLive, 6 frames | 240 s | 128 of ID-Forcing | 81.56 | 81.84 | **+0.28** | **+2.55** |
| ID-Forcing on Self-Forcing, 9-frame adaptation | 240 s | 128 of ID-Forcing | 81.32 | 81.65 | **+0.34** | **+3.58** |

SGF's 6-frame arm, CF and LongLive use the current and preceding blocks. The SGF 9-frame row is a separate
supporting control; the ID-Forcing adaptation uses 9 frames within its own framework. SGF's 6-frame Quality
interval includes zero. Intervals and full scores: **[RESULTS.md](RESULTS.md)**.
The 240-second LongLive six-frame results are complete; the [12-frame control](results/long_horizon/README.md) remains available.

## Human evaluation

Blinded pairwise comparisons; win rates exclude ties. Durations and sampling protocols are reported separately.

| Comparison | Duration | Subject and scene consistency | Overall preference |
|:---|:---:|--:|--:|
| LongLive + Commit Forcing vs. LongLive | 60 s | 43% | 45% |
| LongLive + Commit Forcing vs. LongLive | 120 s | **83.5%** | **82.9%** |
| LongLive + Commit Forcing vs. ID-Forcing | 60 s | **90%** | **88%** |

The 60-second study uses 18 rollf200 pairs per comparison and 3 response units from 5 people, including one joint
response. The separate 120-second study uses 30 pairs from ID-Forcing's 128 MovieGen prompts, answered independently
by 5 non-project assessors. The studies use different prompts and sampling; their difference does not isolate duration.
All rows use current-plus-previous-block LongLive committing. The earlier SGF 9-frame evaluation remains a
[supporting reference with its original counts and protocol](results/human_evaluation/README.md#60-second-study).

## Qualitative comparisons

<p align="center">
  <img src="assets/qualitative_grid.png" width="100%" alt="Paired SGF and Context Forcing frames at 0, 120 and 238 seconds, with Base and Commit Forcing rows.">
</p>

Paired 240-second examples use the same prompt and initial-noise seed. Both SGF and Context Forcing use the
current and preceding blocks (6 frames). SGF retains church and coastline details; Context Forcing
retains the requested figure inside a glass sphere. The CF example has a lower
Quality score (−0.40 points). [Selection and source frames](assets/README.md) · [More examples and videos](assets/qualitative/README.md).

## Quickstart

### 1. Fetch the code

```bash
git clone https://github.com/Dwell-Jing/commit-forcing.git && cd commit-forcing
bash setup/fetch.sh sgf     # upstream code at the tested commit, with our patch, in third_party/sgf
```

Install the [tested environment](setup/README.md) and download the weights from the
[SGF integration guide](integrations/sgf/README.md).

### 2. Generate

The default rule uses the current and immediately preceding blocks (6 latent frames after startup). Historical
9-frame SGF controls use `--commit-profile legacy`; see the [integration settings](integrations/sgf/README.md).

```bash
python integrations/sgf/generate.py --code third_party/sgf --reading native --rule on \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf
```

- Run it again with `--rule off` for the base model; videos go to `outputs/sgf/native/rule_<on|off>/seed0/`.
- Each video has a JSON sidecar with the activation counters, the motion of the frames and `frames_md5`, the md5 of
  the frames before mp4 encoding.
- The noise of prompt `i` under seed `s` comes from `torch.manual_seed(s * 100003 + i)`.

### 3. Evaluate

```bash
python eval/vbench_long/prep.py --vbench VBench --videos outputs/sgf/native/rule_off --label sgf --work vb_work
python eval/vbench_long/prep.py --vbench VBench --videos outputs/sgf/native/rule_on --label sgf+rule --work vb_work
bash eval/vbench_long/score.sh VBench vb_work 0     # start one copy per GPU
python eval/vbench_long/collect.py --work vb_work --label sgf --out scores.csv
python eval/vbench_long/collect.py --work vb_work --label sgf+rule --out scores.csv --append
python eval/vbench_long/compare.py --scores scores.csv --seed 0 --pair sgf+rule:sgf
```

The [VBench-Long pipeline](eval/vbench_long/README.md) gives the setup (VBench @45e79ec) and the statistics; a new
6-frame rollf200 run is distinct from the archived 9-frame SGF supporting control. The
[full-VBench pipeline](eval/vbench_full/README.md) scores the 946-prompt suite.

### 4. Reproduce our tables

```bash
python eval/vbench_full/reproduce_common946.py
python eval/vbench_full/reproduce_common946.py --profile historical
python assets/source/make_commit_effects.py --check-only
```

The default command validates current point estimates, normalization, component sums and correspondence to the
frozen reported intervals; it does not recompute the updated arms' intervals. The historical profile replays the
preserved package's paired bootstrap from public per-prompt contributions. The last command checks the supporting
two-seed figure. Other comparisons and commands are listed in [RESULTS.md](RESULTS.md) and [results/](results/README.md).
