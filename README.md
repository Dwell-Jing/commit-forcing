<div align="center">

<h1>What Helps Denoising Can Hurt Memory:<br>Rethinking History in Long Video Generation</h1>

**Recent-Context Committing: construct new KV from the current and immediately preceding blocks.**

[![Paper](https://img.shields.io/badge/Paper-coming%20soon-b31b1b.svg)](#news)&nbsp;
[![Models](https://img.shields.io/badge/models-6-orange.svg)](#supported-models)&nbsp;
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

Autoregressive video diffusion uses historical KV to denoise the current block and to construct clean KV for
future blocks. On LongLive and SGF, sink access helps denoising but can increase drift during committing.
At fixed context size and temporal positions, older trajectory content produces lower mean long-range Subject
Consistency on both generators.

**Recent-Context Committing** preserves the base denoising policy and constructs new clean KV using the current
block and the immediately preceding block from the original generated trajectory. The current block supplies clean
latents; the preceding block is accessed through its stored KV. With 3 latent frames per block, the committing
context contains 6 frames after startup (3 at the first block). Direct access to other history, including sink KV, is
excluded during committing. Base cache storage and update remain in place; earlier history can still affect new KV
indirectly through the generated current block and the preceding block's KV. The scheme requires no training or
additional DiT forwards. Repository names and CLI flags retain their existing spelling for compatibility.

## Contributions

- **Stage and source effects.** Controlled interventions on LongLive and SGF show that historical context can have
  different effects during denoising and committing, even at fixed read counts.
  ([stage interventions](analysis/longlive_sink/README.md), [historical sources](analysis/committing_source/README.md))
- **Committing dependencies.** We vary historical source and age at fixed context size and positions, distinguish
  the KV read by denoising from the history read by later committing, and characterize generator-dependent
  consistency and motion tradeoffs.
  ([historical recency](analysis/committing_content_age/README.md), [KV construction](analysis/kv_construction/README.md))
- **Training-free committing.** On 60-second VBench, current-plus-previous-block committing improves Quality and
  Total significantly on 5 of 6 generators; all six paired point estimates are positive. LongLive gains in long-range
  Subject Consistency extend to 120 and 240 seconds. Separate wider-context controls retain their two-seed results.
  ([results](#results))

<p align="center">
  <img src="assets/method.png" width="92%" alt="Recent-Context Committing: construct new KV from the current and immediately preceding blocks while preserving base denoising and storage.">
</p>

<sub>The clean committing pass reads the current block and stored KV of the immediately preceding block: 3 + 3
latent frames. Base denoising and cache storage remain in place.</sub>

## Results

**Main evaluation: full VBench, 60 s**, the common 946-entry suite, one video per entry (generation seed 0), all 16 dimensions.
Each row compares the same released weights with and without Recent-Context Committing. Every adapted generator
uses the current and immediately preceding blocks (6 latent frames after startup). Native denoising, sampler and
physical-storage settings remain model-specific; prompts and scoring protocol are shared.

<table>
<thead>
<tr><th rowspan="2" align="left">Model</th><th colspan="3">Quality</th><th colspan="3">Total</th></tr>
<tr><th>Base</th><th>Recent-context</th><th>Δ</th><th>Base</th><th>Recent-context</th><th>Δ</th></tr>
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

Rows follow ascending Total with recent-context committing. Scores ×100; differences are computed before rounding.
Bold Δ marks a paired 95% prompt-cluster interval excluding 0. Quality combines seven visual dimensions; Total
also includes nine semantic dimensions. † RF-TF applies Recency Forcing's Temporal Response Bias to released
Self-Forcing weights; it uses no RF-trained checkpoint.
Quality and Total improve significantly on 5 of 6 generators. RF-TF has the largest Total gain, +1.10 points.
SGF's Quality gain is +1.27, of which Dynamic Degree contributes +1.01; Motion Smoothness decreases by 0.29 points.
[All dimensions, intervals and protocol records](results/vbench_full/common946/README.md).
The two 9-frame ID-Forcing adaptations are [separate framework comparisons](RESULTS.md#id-forcing-framework-comparisons).

**Supporting context controls: MovieGen, 60 s videos**, 200 fixed [MovieGen prompts](eval/prompts/README.md), generation seed 0.
Quality combines VBench's seven visual dimensions using its official normalization and weights.

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

The standard suite scores dimension-specific subsets and applies VBench's static filter for Flickering.
The MovieGen evaluation scores all seven visual dimensions on each prompt and leaves Flickering unfiltered.
Each Base / adapted pair shares its inputs and scoring settings.
LongLive uses 6-frame committing: 3 recent frames and the current 3-frame block.

**Longer videos, 120–240 s**, VBench-Long Quality. Compare within each prompt set:

| Model | Length | Prompts | Base | Recent-context | Δ Quality | Δ Consistency |
|:---|:---|:---|--:|--:|--:|--:|
| SGF, 9-frame control | 240 s | 32 MovieGen | 83.97 | 84.69 | **+0.72** | **+5.07** |
| Context Forcing | 240 s | 32 MovieGen | 83.60 | 84.04 | +0.44 | **+2.23** |
| LongLive, 6 frames | 120 s | 128 of ID-Forcing | 81.72 | 82.05 | **+0.33** | **+1.87** |
| LongLive, 6 frames | 240 s | 128 of ID-Forcing | 81.56 | 81.84 | **+0.28** | **+2.55** |
| ID-Forcing on Self-Forcing, 9-frame adaptation | 240 s | 128 of ID-Forcing | 81.32 | 81.65 | **+0.34** | **+3.58** |

CF and LongLive use the current and preceding blocks. SGF remains a wider-context supporting reference; the
ID-Forcing adaptation uses 9 frames within its own framework. Intervals, the second seed, 120 s videos and every component score: **[RESULTS.md](RESULTS.md)**.
The 240-second LongLive six-frame results are complete; the [12-frame control](results/long_horizon/README.md) remains available.

## Human evaluation

Blinded 60-second comparisons, with 18 prompt-matched pairs per comparison. Five people contributed 3 response
units, including one joint response from 3 people. Win rates exclude ties.

| Comparison | Subject and scene consistency | Overall preference |
|:---|--:|--:|
| SGF, 9-frame recent-context control vs. SGF | **75%** | **74%** |
| LongLive + Recent-Context Committing vs. LongLive | 43% | 45% |
| LongLive + Recent-Context Committing vs. ID-Forcing | **90%** | **88%** |

The SGF rates describe the 9-frame supporting control. LongLive uses the current and preceding blocks.
[Counts, recorded intervals and evaluation protocol](results/human_evaluation/README.md).

## Qualitative comparisons

<p align="center">
  <img src="assets/qualitative_grid.png" width="100%" alt="Paired SGF and Context Forcing frames at 0, 120 and 238 seconds, with base and recent-context rows.">
</p>

Paired 240-second examples use the same prompt and initial-noise seed. SGF is the 9-frame source-control reference;
Context Forcing uses the current and preceding blocks. SGF retains church and coastline details; Context Forcing
retains the requested figure inside a glass sphere. The CF example has a lower
Quality score (−0.40 points). [Selection and source frames](assets/README.md) · [More examples and videos](assets/qualitative/README.md).

## Quickstart

### 1. Fetch the code

```bash
git clone https://github.com/Dwell-Jing/commit-forcing.git && cd commit-forcing
bash setup/fetch.sh sgf     # upstream code at the tested commit, with our patch, in third_party/sgf
```

Install the [tested environment](setup/README.md) and download the weights as described in each
[integration README](#supported-models).

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

## Supported models

The current main method uses the same 6-frame committing context on each of these generators. The released
integration interfaces and historical controls are documented per model; a command reproducing a supporting
control should retain that control's original context.

| Model | Upstream code | Current main committing context |
|:---|:---|:---|
| [SGF](integrations/sgf/README.md) | [Self_Gradient_Forcing](https://github.com/zhuang2002/Self_Gradient_Forcing) | current block + immediately preceding block |
| [SGF+](integrations/sgf_plus/README.md) | [Self_Gradient_Forcing_Plus](https://github.com/Zihan-Su/Self_Gradient_Forcing_Plus) | current block + immediately preceding block |
| [Recency Forcing, training-free](integrations/recency_forcing/README.md) | [Self-Forcing](https://github.com/guandeh17/Self-Forcing) | current block + immediately preceding block |
| [LongLive](integrations/longlive/README.md) | [LongLive](https://github.com/NVlabs/LongLive) | current block + immediately preceding block |
| [Context Forcing](integrations/context_forcing/README.md) | [Context-Forcing](https://github.com/chenshuo20/Context-Forcing) | current block + immediately preceding block |
| [Rolling Sink](integrations/rolling_sink/README.md) | [Rolling-Sink](https://github.com/Rolling-Sink/Rolling-Sink) | current block + immediately preceding block |

[ID-Forcing](integrations/id_forcing/README.md) is retained as a separate framework comparison with 9-frame
adaptations (6 historical + 3 current frames). On its Self-Forcing backbone, the adaptation also retains original
handover KV and omits recurrent tail re-encoding.
LongLive's standard-suite comparison uses 12 physical cache frames in both arms. Its custom-prompt runs retain
15 physical frames in both arms; 12-frame committing remains a control. Recent history is defined by its original
time in the generated trajectory; replaying an old frame into a nearby cache slot does not make it recent.

## Mechanism analyses

| Committing question | Analysis |
|:---|:---|
| How does sink access differ across stages? | [LongLive and SGF stage interventions](analysis/longlive_sink/README.md) |
| Does the source or position of history matter? | [Source and position controls](analysis/committing_source/README.md) · [SGF equal-count control](analysis/sgf_committing_controls/README.md) |
| Does historical age matter at a fixed context size? | [Fixed-position recency intervention](analysis/committing_content_age/README.md) |
| Which constructed KV carries the larger generation losses? | [Separate denoising and committing caches](analysis/kv_construction/README.md) |
| Does extra old KV during denoising reproduce the gain? | [LongLive extra-history controls](analysis/kv_construction/README.md#extra-old-kv-during-denoising) |
| What does recent context retain over self-only? | [Continuity and motion tradeoffs](analysis/commit_window/README.md) |
| How does recent context work within ID-Forcing? | [Cache-construction comparisons](analysis/not_ood/README.md) |
| How many frames should the commit pass read? | [Commit window](analysis/commit_window/README.md) |
| What contributes to the score and computational cost? | [Quality decomposition and inference measurements](analysis/quality_cost/README.md) |

<p align="center">
  <img src="assets/committing_content_age.png" width="100%" alt="At fixed committing-context size and temporal positions, mean clip-to-clip Subject Consistency decreases with historical age on SGF and LongLive.">
</p>

**Historical recency.** Both models commit with 3 historical and 3 current frames at fixed positions. Mean clip-to-clip
Subject Consistency decreases across the tested lags of 1, 2, 4, 8 and 16 blocks. The oldest tested context loses
0.69 points on SGF and 2.46 on LongLive relative to the newest; Dynamic Degree increases.
[Scores, controls and protocol](analysis/committing_content_age/README.md).

**KV construction.** A two-cache SGF control separates KV read by denoising (D) from history read by later committing
(C); both KV versions are constructed using history from C. Native construction of D alone reduces Quality by
1.12 and clip-to-clip Subject Consistency by 5.67 points relative to recent-only construction of both caches.
Native construction of C alone changes these scores by −0.07 and −0.09, neither significant, while affecting other
components. This control retains base denoising access and uses the earlier 9-frame recent context.
[All four contrasts and LongLive extra-history controls](analysis/kv_construction/README.md).

The supporting 9-frame [SGF equal-count control](analysis/sgf_committing_controls/README.md) compares 2 nine-frame contexts within the
same physical cache. Recent context improves Quality by 1.25 and clip-to-clip Subject by 4.54 points over sink plus recent.
Relative to self-only, it improves smoothness and flicker while reducing Dynamic Degree, with no significant Quality
or long-range Subject advantage. [Window comparisons](analysis/commit_window/README.md).

Supplementary observations: [fixed-latent KV propagation](analysis/committing_propagation/README.md),
[switching the committing context](analysis/commit_switch/README.md) and
[SGF + RF-TF compatibility](RESULTS.md#sgf-rf-compatibility).
[DINOv2 Own/Sibling components](analysis/similarity_components/README.md) separate the appearance-similarity terms.

### Transfer boundaries

Released **Rolling Forcing** retains better clip-to-clip consistency with its native 21-frame recent context than
with 6 frames. This is separate from the training-free Recency Forcing reproduction (RF-TF) in the main table.
On **WorldPlay**, restricting older-context access during joint context re-encoding worsens some temporal measures
at the default budget and lowers return similarity at the larger tested budget. Denoising still reads the constructed
memory KV. [Protocols, aggregate results and intervals](analysis/transfer_boundaries/README.md).

### Independent denoising studies

[Step, layer and content interventions](analysis/read_locus/README.md),
[SGF boundary controls](analysis/boundaries/sgf/README.md) and the [historical mechanism figure](assets/mechanisms/README.md)
belong to the separate distant-history reading study. Their data, code, negative results and visual costs remain
available. [Diagnostic metrics](analysis/metrics/README.md) defines the associated identity, color and motion readouts.

## Scope

We evaluate released Wan-based generators with persistent KV and a clean committing pass. Window comparisons
show generator-dependent continuity and motion tradeoffs; they do not establish a universally optimal context
length. The main method fixes the context to the current and immediately preceding blocks. Training the committing
rule and learned context selection are future work. The separate Rolling Forcing and WorldPlay tests characterize
limits of shorter contexts and transfer to joint context re-encoding.

## Read more

| | |
|---|---|
| **[RESULTS.md](RESULTS.md)** | every result table: 60 s (2 seeds), full VBench, 120 s and 240 s |
| [results/](results/README.md) | per-video score CSVs, table specs and exact outputs |
| [eval/vbench_long](eval/vbench_long/README.md) · [eval/vbench_full](eval/vbench_full/README.md) | the two evaluation pipelines |
| [analysis/](#mechanism-analyses) | the mechanism studies, their data and generators |
| [assets/qualitative](assets/qualitative/README.md) | paired early / late frames and comparison videos |
| [setup/](setup/README.md) | fetching upstream code and the tested environment |
| [NOTICE](NOTICE) | upstream projects and their licenses |

## License

Code is Apache-2.0 ([LICENSE](LICENSE)), except `integrations/rolling_sink` (Adobe Research License) and
`integrations/context_forcing` (CC BY-NC-SA 4.0), which are for non-commercial research ([NOTICE](NOTICE)).
Questions: open an [issue](https://github.com/Dwell-Jing/commit-forcing/issues).
