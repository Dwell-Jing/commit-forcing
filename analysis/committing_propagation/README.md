# Supplementary: propagation through recent committed KV

This supplementary study appears in Appendix A.6. A committing intervention can change KV written by later blocks
even when every clean latent block is fixed. Differences in later KV remain after the directly affected entries
leave the cache and decay across blocks. Late generation probes have small output differences without significant
signed saturation or brightness shifts.

The separate [KV construction control](../kv_construction/README.md) distinguishes the KV consumed by denoising
from the history read by later committing. In that SGF setting, the larger Quality and clip-to-clip consistency
losses follow construction of the denoising-facing KV. The recursive propagation observed here is a supplementary
dependency measurement, not an attribution of those losses or all drift to a single pathway.

![Fixed-content KV propagation](../../assets/committing_impulse.png)

## Single intervention with fixed clean content

We reconstruct two SGF caches from the same saved clean latents. The control commits with newest 9 frames throughout.
The intervention replaces 3 recent frames with 3 sink frames at block 20 or 40, then returns to newest-9 committing.
Both read sets include the current 3 frames. Denoising is fixed to sink 3 + prior recent 3 + current 3.
The released chunkwise EMA weights, 12-frame physical cache, and top-aligned positions within the 21-frame training
range are retained. There are 20 prompts with generation seed 0, each with both intervention positions, at 48 seconds.

| Cache lag after intervention | Later K relative L2 | Later V relative L2 |
|---|---:|---:|
| 1 | 0.1138 | 0.1932 |
| 2 | 0.1111 | 0.1857 |
| 3: directly affected block evicted | 0.0967 | 0.1626 |
| 5 | 0.0425 | 0.0746 |
| 8 | 0.0134 | 0.0255 |
| 11 | 0.0079 | 0.0155 |

The norm covers tokens from blocks strictly after the intervention that remain in the cache, normalized separately
for K and V in each of 30 layers and then averaged. Cache lag 3 is the first post-eviction cache measurement.
A generation probe after cache lag k generates block b*+k+1 and can evict the affected entries during that forward;
the first sampled post-eviction generation probe is therefore k=2.

With self-only committing, later K/V differences are exactly zero at measured lags 1–11, and isolated generation
probes match exactly at lags 2, 5 and 11. This intervention adds sink 3 to current 3 at the affected pass; unlike
recent-versus-sink committing, it changes that pass's read count. The initial self-only intervention is nonzero.
With recent-context committing, generation probes at lags 5 and 11 retain small pixel differences, but the signed
saturation and brightness intervals include zero.

## Exposure during free generation

A separate study uses 20 prompts × seeds 0/1, with initial noise and intermediate re-noising paired across arms.
We change either committing block 20 alone or commits 16–31 inclusive, then resume recent-context committing.
The single intervention leaves generated block 20 unchanged and first affects block 21.

| Burst window | Δ Saturation | Δ Brightness | Pixel MAE (0–255) | Latent relative L2 |
|---|---:|---:|---:|---:|
| 16–31: exposure | +0.00607 | −0.00848 | 28.52 | 0.548 |
| 32–35: just after exposure | +0.00663 | −0.00496 | 29.50 | 0.574 |
| 36–43 | −0.00001 | +0.00089 | 21.69 | 0.444 |
| 44–51 | −0.00029 | +0.00006 | 20.04 | 0.408 |
| 52–63 | −0.00127 | −0.00042 | 19.61 | 0.404 |

Later signed means have intervals spanning zero, while absolute trajectory differences remain. The fixed-content
burst counterpart yields probe pixel MAE 1.76 and 0.90 at blocks 37 and 43, versus 22.10 and 20.48 in free generation.
The two protocols use different probe noise and decoding context; these values describe feedback through generated
content without isolating a numerical amplification factor. The separate SF remote-history switching study uses
a different source, cache capacity, exposure duration and normalized color scale.

## Attention readout

The small `attention_*.json` records sample five prompts, seed 0, with 96 evenly spaced current-block queries per
full-context call. Stage-average sink attention mass is lower during committing (SGF 0.1843; LongLive 0.1137) than
during each denoising step. Individual layers have exceptions. These sampled softmax means measure allocation,
not causal utility. SGF uses 9-frame reads / 12-frame storage; LongLive uses 12-frame reads / 15-frame storage.
LongLive's recorded sink, previous-3 and current groups do not exhaust its 12-frame read set.

## Recent-context anchoring and boundary flow

We also compare self-only (`C`: current 3), recent (`R`: newest 9) and sink-context committing (`S`: sink 3 + newest 6)
on fixed SGF clean prefixes. For 20 prompts with generation seed 0, we reconstruct each cache and generate isolated
next-block probes after blocks 12, 20, 28, 36, 44 and 52, pairing initial noise, intermediate re-noising and denoising
context. Probe outputs do not enter later prefix reconstruction.

| Fixed-prefix SGF contrast | Δ Latent displacement ratio | Δ Latent direction cosine | Δ Luma boundary ratio | Δ Within-latent luma motion |
|---|---:|---:|---:|---:|
| Recent − self-only | −0.0387 | +0.0126 | −0.1210 | −0.1885 |
| Sink − recent | +0.0649 | +0.0390 | −0.2178 | −0.3403 |
| Sink − self-only | +0.0262 | +0.0516 | −0.3388 | −0.5288 |

The displacement ratio divides the generated next-block mean's distance from the preceding block mean by the
preceding fixed block-to-block displacement. The cosine compares these two latent displacement vectors. Recent
committing reduces the ratio relative to self-only, while the interval for its cosine change spans zero. Sink-context
committing suppresses within-latent luma motion further but increases displacement relative to recent committing.
Motion suppression is therefore different from proximity to the previous block mean. Luma motion uses adjacent-frame
differences on the 0–255 scale; ratios and cosines are dimensionless.

For existing 60-second videos, luma diagnostics use 200 prompts × seeds 0/1 from 4 seconds onward at 208×120 resolution.
Self-only-minus-recent within-latent luma changes are +0.1427 on SGF (interval spans zero) and +0.6897 on LongLive
(interval excludes zero). The full [anchoring readout](data/anchoring_readout.md) retains all means, comparisons
and paired intervals, including the other window and sink controls.

We separately use VBench RAFT at 240×416 (height×width), with 12 iterations, to inspect optical flow. At a new block
boundary, boundary flow is divided by the mean flow magnitudes of its adjacent within-latent frame pairs. Direction
cosine compares those two neighboring flows. A within-block latent boundary supplies a control. Existing-video
analysis uses prompts 0–99 × seeds 0/1, sampling every second generation boundary after 4 seconds; SGF fixed-prefix
probes use the same 20 prompts and six positions above.

| Flow contrast: recent − self-only | Δ Boundary flow ratio | Δ Control flow ratio | Δ Direction cosine | Δ Within-latent flow |
|---|---:|---:|---:|---:|
| Existing SGF | −0.3887 | −0.1849 | +0.0349 | +0.0359 |
| Existing LongLive | −0.0686 | +0.0463 | −0.0045 | −0.1649 |
| Fixed-prefix SGF probe | −0.7027 | −0.1130 | +0.0174 | +0.0455 |

On SGF, the boundary and control flow-ratio intervals are negative in both studies. Within-latent flow-magnitude
intervals span zero. On LongLive, recent committing reduces within-latent flow, while the boundary-ratio interval
spans zero. For the SGF probe, the directional-cosine interval also spans zero. These diagnostics support anchoring
and model-dependent motion suppression; they do not establish transfer of motion direction through committing.
Flow magnitudes use pixels per adjacent frame pair at the evaluation resolution, not perceptual quality scores or
human preferences. All original intervals use 4,000 prompt-cluster draws, retaining the two seeds or six positions.

The [complete flow readout](data/boundary_flow_readout.md) includes sink-minus-recent effects, after/before speed,
and all intervals. These two files are frozen statistical summaries: their complete per-prompt metric inputs are
not in this release, so the CPU replay below applies to the single/burst propagation studies rather than these
anchoring and flow summaries. [Source hashes](data/reported_diagnostics.json) identify the archived readouts.

## CPU replay

```bash
python analysis/committing_propagation/replay_fixed_latent.py
python analysis/committing_propagation/replay_free_generation.py
```

Requires NumPy. The scripts recompute the archived statistics and 4,000-draw prompt-cluster intervals from scalar
per-prompt records, preserving both intervention positions or generation seeds within each prompt. They print to
stdout; `--output PATH` saves a readout. Original complete numerical readouts are in
[data/fixed_latent_readout.md](data/fixed_latent_readout.md) and
[data/free_generation_readout.md](data/free_generation_readout.md). Public cells contain measured scalars and per-layer
scalar norms, not KV tensors, latent arrays or videos. Source video hashes are retained, but source-video equality
checks are not replayed without those videos. [Provenance](data/provenance.json) records source and released-file hashes.
