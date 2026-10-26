# Why One Preceding Block

The committing-window scans show rising consistency, a plateau, and a decline as more history is read.
The controls below support a temporal-smoothing interpretation of the initial gain and an outdated-content
interpretation of the decline. Plateau locations depend on the generator: SF with a sink favors 9–12 frames,
and framewise SGF has a different block size. [Complete window scans](../../results/current6_custom/README.md).

## Rising: correction magnitude and retained effects

On LongLive, adding the preceding block improves clip-to-clip Subject Consistency while reducing Dynamic Degree.
Spatial pooling retains part of this history-induced attention correction and part of both effects.

[Figure](../../assets/committing_correction_dose.svg) · [PDF](../../assets/committing_correction_dose.pdf)

| Spatial averaging | Retained correction | Retained consistency gain | Retained motion suppression |
|:---|---:|---:|---:|
| CG: spatial mean within each frame | 0.36 | 0.29 | 0.37 |
| CM16: 16 content regions | 0.47 | 0.47 | 0.48 |
| SG16: 4×4 spatial grid | 0.48 | 0.42 | 0.61 |
| CM64: 64 content regions | 0.56 | 0.55 | 0.48 |

These are four reported arms and eight observed effect points. The plotted horizontal coordinate is measured
independently from the outcome scores. Let `D = O_(C+H) − O_C`, where C is the current clean block, H is the
preceding block, and O is the committing self-attention output **before its output projection**. The retained
correction is `||pool(D)||_F / max(||D||_F, 1e-12)`, computed in float32 over current tokens, heads and channels.
It is an attention-output correction norm, rather than a norm of stored K or V.

The ratio is measured for each attention call, averaged over 30 layers and 79 post-startup committing passes
within each video, then averaged over 100 rollf200 prompts. Videos last 60 seconds with generation seed 0.
The figure uses the reported two-decimal ratios; it does not derive the horizontal coordinates from retained effects.

For each metric, the retained effect is `1 − Δ_variant / Δ_self`, using paired changes from recent-context
committing. Effect normalization uses the reported **200-prompt** self-only comparison: Δ Subject c2c = −1.00
and Δ Dynamic Degree = +3.63. Variant outcomes use 100 prompts. The released fractions preserve this reported
normalization; they do not remix absolute means from the two prompt sets.

The dashed `y=x` line marks equal retained fractions. Endpoints `(0,0)` and `(1,1)` define normalization and are
not extra observations. Error bars are not supplied for these rounded fractions. The controls support a relation
between correction magnitude and both effects, while pooling also changes correction structure. They do not
establish a strict linear law or a unique smoothing mechanism. P and U have no reported horizontal norm ratios
in this comparison and are not plotted.

SG16 departs from equal retention: its consistency-gain fraction is 0.42 and its motion-suppression fraction is 0.61.

### Confirmation by selecting KV versions during denoising

A separate LongLive diagnostic constructs recent-context and self-only KV versions for each block. At all four
denoising steps, zero-indexed layers 15–29 read the recent-context version and layers 0–14 read the self-only
version. The confirmation uses 200 rollf200 prompts, new generation seeds 2 and 3, and 400 paired 60-second outputs.
The reference is full recent-context committing (MOT_w6), using recent-context KV throughout denoising.

| Metric | Layer-selective minus reference | Reported significance |
|:---|---:|:---|
| Clip-to-clip Subject Consistency | +0.257 [+0.045, +0.477] | Significant |
| Dynamic Degree | −0.47 | Not significant |
| Quality | −0.03 | Not significant |
| Temporal Flickering | −0.06 | Significant decrease |
| G | +0.14 [−0.20, +0.48] | Not significant |

The +0.257 change is an additional gain over full recent-context committing. In this same confirmation set,
self-only committing scores 1.10 points below the full scheme. That seed-2/3 contrast is separate from the
seed-0 self-only comparison used for effect normalization; their values are not combined.

Scores use 0–100 points. The manuscript supplies Subject c2c and G intervals; other interval endpoints remain
unreported. The selection diagnostic localizes an effect of recent-context KV during denoising, with a
flicker cost and no significant G gain. It does not identify a unique encoded attribute. Constructing two KV
versions belongs to this diagnostic, rather than the one-pass main committing rule.

The [extra-old-KV controls](../kv_construction/README.md#extra-old-kv-during-denoising) supply additional history
during denoising without a significant Subject c2c gain. Their complete quality gains, losses and intervals remain
in that separate record.

## Plateau: small marginal benefit from additional direct history

On LongLive, adding a second preceding block changes Subject c2c by +0.02 points without a significant gain.
The preceding block's KV can already carry earlier dependencies, which may reduce the benefit of reading those
blocks directly again. As cross-model corroboration, the [SGF fixed-latent probe](../committing_propagation/README.md)
demonstrates an indirect path: differences persist in later KV after directly affected entries leave the cache,
with decreasing magnitude. This supports a possible explanation of LongLive's plateau, rather than a direct
causal test of that plateau in LongLive.

## Decline: outdated-content interference

The [fixed-size recency controls](../committing_content_age/README.md) show lower consistency with older trajectory
content at fixed assigned temporal positions. The [source-position controls](../committing_source/README.md)
also retain sink-related losses when its KV is placed at recent positions.

Spatial pooling reduces the sink correction's loss but does not remove it. FP16 averages that correction within
16 content regions before adding it. On 100 LongLive rollf200 prompts at 60 seconds, seed 0:

| FP16 comparison | Metric | Change |
|:---|:---|---:|
| FP16 − recent-context | Subject c2c | −1.76, significant |
| FP16 − recent-context | G | −2.97 [−3.92, −2.07], significant |
| FP16 − unaveraged sink correction (FR) | G | +0.72 [+0.05, +1.37], significant |

The −2.97 value is departure from the consistency–motion reference, not the original Subject c2c change.
Regional averaging retains regional information, so these controls do not fully exclude geometric effects.

The [complete 27-variant table and separate attention-sharpening confirmations](../committing_variants/README.md)
remain available, including negative results, nonsignificant results, positive confirmation gains and their costs.

## Aggregate record

[`summary.json`](summary.json) transcribes reported aggregates from Overleaf commit
`6a1fe891587440c56f78e7eb728a4a21a02b2114` and records the relevant source SHA-256 hashes.
It contains no per-prompt numerical records, videos, personal answers or participant identifiers.

```bash
python analysis/window_effects/readout.py
```

The standard-library reader checks four distinct pooling arms, eight observed effect points, the measurement
schema and reported comparison intervals. It prints the frozen fractions rather than deriving them anew from
rounded performance values. Missing interval endpoints are `null`; no bootstrap or new evaluation is run.
