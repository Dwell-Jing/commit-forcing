# Quality decomposition and computation cost

## Current six-generator Quality effects

The current method commits the current block and the immediately preceding block (6 latent frames). Its standard-suite Quality changes decompose as follows.

| Generator | Δ Quality | Subject | Background | Flicker | MotionSm | Dynamic | Aesthetic | Imaging |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| Context Forcing | +0.46 | +0.04 | +0.06 | -0.04 | -0.06 | +0.26 | +0.06 | +0.13 |
| Rolling Sink | +0.41 | +0.03 | +0.06 | -0.02 | -0.06 | +0.27 | +0.08 | +0.06 |
| RF-TF | +0.65 | +0.11 | +0.16 | +0.04 | -0.03 | -0.22 | +0.37 | +0.23 |
| LongLive | +0.29 | +0.01 | +0.03 | -0.00 | -0.07 | +0.21 | +0.06 | +0.07 |
| SGF+ | +0.32 | +0.05 | +0.13 | +0.04 | -0.05 | +0.12 | +0.04 | -0.02 |
| SGF | +1.27 | +0.05 | +0.10 | +0.02 | -0.15 | +1.01 | +0.18 | +0.08 |

SGF's +1.27 Quality gain includes +1.01 from Dynamic Degree; Motion Smoothness changes by −0.29 raw score points. RF-TF has the largest Total gain (+1.10) and its Quality gain is driven mainly by Aesthetic and Imaging Quality.

[Current unrounded contributions](../../results/vbench_full/common946/current6/quality_decomposition.csv) · [Current scores and frozen intervals](../../results/vbench_full/common946/current6/README.md). The current validator checks official normalization and seven-term sums:

```bash
python eval/vbench_full/reproduce_common946.py
```

The measurements below retain their original contexts: SGF/SGF+9 frames, RF-TF/Rolling Sink21, CF/LongLive6, and ID-framework adaptations9. Their costs are not new six-frame timing runs for every generator.

## Historical context-control Quality decomposition

The historical eight-configuration VBench comparison uses seven normalized visual dimensions for Quality. The following table retains its original Base / context-control differences, in Quality points ×100.

| Model | Δ Quality | Subject | Background | Flicker | MotionSm | Dynamic | Aesthetic | Imaging |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| SGF | +1.16 | +0.03 | +0.08 | −0.07 | −0.14 | +1.10 | +0.07 | +0.08 |
| SGF+ | +0.29 | +0.04 | +0.12 | +0.03 | −0.05 | +0.13 | +0.03 | −0.02 |
| RF-TF | +0.47 | +0.05 | +0.06 | +0.06 | −0.07 | +0.02 | +0.22 | +0.14 |
| Context Forcing | +0.46 | +0.04 | +0.06 | −0.04 | −0.06 | +0.26 | +0.06 | +0.13 |
| LongLive | +0.29 | +0.01 | +0.03 | 0.00 | −0.07 | +0.21 | +0.06 | +0.07 |
| Rolling Sink | +0.32 | −0.03 | −0.01 | −0.02 | −0.07 | +0.32 | +0.07 | +0.05 |
| IDF-SF | −0.05 | +0.06 | +0.03 | +0.03 | +0.02 | −0.29 | +0.07 | +0.03 |
| IDF-LL | −0.27 | +0.02 | +0.03 | +0.04 | +0.06 | −0.47 | +0.03 | +0.02 |

SGF's +1.16 Quality gain includes +1.10 from Dynamic Degree. Its Subject and Background scores also increase, while
Flicker and Motion Smoothness decrease. RF-TF gains mainly through Aesthetic and Imaging Quality; Dynamic Degree is
the largest positive term for Context Forcing, LongLive and Rolling Sink. The ID-Forcing configurations have negative
Dynamic contributions. Thus the aggregate gains have different component profiles across models.

For scores already expressed as points ×100, each contribution is

```text
weight[d] × (score_CF[d] − score_Base[d]) / (high[d] − low[d]) / 6.5
```

The Dynamic Degree weight is 0.5; the other six weights are 1. The unrounded terms sum to ΔQuality; independently
rounded table entries can differ slightly from the displayed total. Normalization bounds follow VBench's
[`scripts/constant.py`](https://github.com/Vchitect/VBench/blob/45e79ec14e69a2187202c675d2dbce1a71843d53/scripts/constant.py).

[Unrounded contributions and Quality intervals](data/quality_decomposition.csv) ·
[Raw dimension changes and paired intervals](data/quality_components.csv) ·
[Original report, including the previous LongLive 12-frame control](data/QUALITY_DECOMP_report.md).
RF-TF uses released Self-Forcing weights with the published Temporal Response Bias, as in the
[main protocol](../../results/vbench_full/common946/README.md).

The current LongLive row uses **6-frame committing and 12-frame physical storage**, source arm `W946_W6S` under the
public `LL_W` alias. Its unrounded seven contributions sum to +0.29006434. The
[new source report](../../results/vbench_full/common946/longlive6_source_results.json) supplies its scores and
intervals. The original report remains unchanged and describes the previous 12-frame committing control; its
derived CSVs are preserved in [data/ablation12](data/ablation12/README.md). All other seven decomposition rows retain
their original values.

## Measured time and memory

The other seven configurations use one measured 60-second video after one warm-up video, on neighbouring dedicated
H20 GPUs (96 GB) of one node. The current LongLive committing-6 comparison uses **four repeats of the same prompt**:
four Base and four +CF jobs ran concurrently on eight dedicated H20 GPUs of one node. Each job warms up on entry 0
and measures entry 1 of the common 946-entry suite (240 latent frames). Its table entries are arithmetic means;
the wall-time ratio is the ratio of the two means. Each device peak is the maximum recorded `nvidia-smi
memory.used` over its run; the LongLive entries average four such peaks per arm.

| Model | Wall Base (s) | Wall +CF (s) | +CF / Base | Device peak Base (GiB) | Device peak +CF (GiB) |
|:---|---:|---:|---:|---:|---:|
| SGF | 218.7 | 216.2 | 0.988 | 34.2 | 34.2 |
| RF-TF | 288.3 | 287.1 | 0.996 | 37.3 | 37.3 |
| Context Forcing | 158.2 | 146.6 | 0.926 | 26.2 | 26.2 |
| LongLive, 6-frame committing | 231.1 | 223.8 | 0.968 | 35.9 | 35.9 |
| SGF+ | 221.3 | 217.7 | 0.984 | 37.1 | 36.8 |
| Rolling Sink | 271.6 | 271.7 | 1.000 | 41.9 | 48.1 |
| IDF-SF | 227.0 | 216.6 | 0.954 | 29.1 | 29.9 |
| IDF-LL | 222.7 | 230.6 | 1.035 | 31.8 | 31.8 |

The seven single-video observations retain their reported ratios. LongLive's means are 231.137706 and 223.767656
seconds, with ratio 0.968114: an observed 3.2% wall-time reduction over four repeats of one prompt. The repeats
measure this prompt's generation cost and do not estimate throughput across the suite.
Rolling Sink uses 6.2 GiB more device memory in its run. The IDF-SF adaptation changes the cache handover and removes
recurrent tail re-encoding, reducing clean DiT calls from 155 to 80.

| Model | Torch peak allocation Base (GiB) | +CF (GiB) | Clean calls Base | +CF | Denoising calls Base | +CF |
|:---|---:|---:|---:|---:|---:|---:|
| SGF | — | — | — | — | — | — |
| RF-TF | — | — | — | — | — | — |
| Context Forcing | — | — | — | — | — | — |
| LongLive, 6-frame committing | 30.7 | 30.7 | 80 | 80 | 320 | 320 |
| SGF+ | 32.8 | 32.8 | 80 | 80 | 320 | 320 |
| Rolling Sink | 38.1 | 43.7 | 80 | 80 | 320 | 320 |
| IDF-SF | 24.9 | 25.8 | 155 | 80 | 320 | 320 |
| IDF-LL | 25.2 | 25.2 | 80 | 80 | 320 | 320 |

Allocation peaks and forward counts were recorded by the engine; dashes denote unreported values.
All eight LongLive JSON observations record 12 physical cache frames, 80 clean forwards and 320 denoising forwards.
Their measured-video Torch allocated peaks are 30.669543 GiB in both arms. Each whole-device log records
36,747 MiB (35.885742 GiB). Torch allocated memory measures live tensor allocations; whole-device memory also
includes allocator cache and CUDA context.

[Cost CSV](data/cost_measurements.csv) · [LongLive four-repeat observations](data/longlive6_cost_per_repeat.csv) ·
[Numeric JSON snapshots and definitions](data/longlive6_cost/README.md).

### Previous LongLive 12-frame control

| Configuration | Wall Base (s) | Wall +CF (s) | Device peak Base (GiB) | Device peak +CF (GiB) |
|:---|---:|---:|---:|---:|
| LongLive, 12-frame committing | 231.5 | 231.4 | 35.9 | 37.0 |

This earlier single-video control uses 12 physical frames in Base and 15 in +CF. It remains in the unchanged
[original cost report](data/COST_report.md) and [archived CSV](data/ablation12/cost_measurements.csv); these memory
values are not assigned to the new committing-6 row.

## Reproduce the historical controls

```bash
python analysis/quality_cost/reproduce.py
```

The script uses Python's standard library. It checks source hashes, recalculates Quality contributions from the
public [full scores](../../results/vbench_full/common946/full_scores.csv), carries over the existing paired intervals,
and checks the seven-term sum and Total decomposition. It validates the original LongLive contribution report
against the archived 12-frame control, and the current row against the 6-frame source. It also verifies the derived
CSVs. `--write` regenerates these CSVs from the same sources.

[Provenance](provenance.json) records source hashes and measurement definitions. The other seven cost rows replay
their original reported summaries. LongLive's current wall-time, allocation and forward-count entries replay the
eight included numeric JSON snapshots. Its device peaks replay the eight memory logs retrieved with those
timers after the second run completed. The earlier timer-only cost observations remain in the
[archived first run](data/longlive6_cost/snapshots/first-completed-run/README.md).
