# Historical source and assigned position during committing

## Rolling Sink: replayed history versus trajectory history

We compare Rolling Sink's base committing context, which contains replayed old content, with recent trajectory
context. Both have a 21-latent-frame total committing capacity, including the current clean block. The denoising
and replay policies are retained. Recent context improves motion retention and gives a small positive
appearance-consistency change in this 48-second comparison.

| Recent context − base context (`RS_real − RS_off`) | Estimate [reported paired 95% CI] | Interpretation |
|---|---|---|
| Appearance consistency | +0.0106\* [+0.00002, +0.0234] | Interval excludes zero; baseline mean 0.1434 |
| Log late/early motion | +0.168 [+0.132, +0.208] | More motion retained |
| Late/early brightness ratio | +0.0265 [+0.0142, +0.0413] | Brightness level increases |
| Late/early saturation ratio | −0.013 [−0.031, +0.002] | Interval spans zero |

These values retain the original diagnostic scales. Appearance consistency is the contrastive DINOv2 diagnostic
used in the [LongLive stage study](../longlive_sink/README.md), not VBench Subject Consistency. Motion is
`log(motion_late_38_47 / motion_early_4_8)`. Its change corresponds to an 18.3% increase in the geometric-mean
late/early ratio, with a reported interval equivalent to 14.1–23.1%. Reported median motion ratios are 0.96 for base
context and 1.13 for recent context. The fraction with late motion below 0.85 × early motion changes from 15% to 0%;
this diagnostic does not identify literal frozen frames.

The unrounded consistency lower endpoint is `+0.000017281547188758977`. Earlier four-decimal displays rounded it
to zero; the interval excludes zero. Decomposing this diagnostic, Own increases by +0.0236 and Sibling by +0.0130;
only Own has an interval excluding zero. Both are full-frame appearance similarities. The
[Own/Sibling decomposition](../similarity_components/README.md) includes the saved embeddings and a CPU replay.

Brightness and saturation are the mean over seconds 38–47 divided by the mean over seconds 4–7. The reported
brightness ratios are 0.985 and 1.011. Both absolute brightness- and saturation-drift magnitude intervals span zero.
The signed brightness level increase therefore does not establish a reduction in absolute drift.

## What the comparison holds fixed

The experiment uses the same 20 prompts as [longlive_sink/prompts20.txt](../longlive_sink/prompts20.txt), seeds 0
and 1, and nominal 48-second rollouts (192 latent frames): 40 paired videos per arm. The reported bootstrap resamples
20 prompt clusters, retaining both seeds, for 4000 draws with NumPy `default_rng(0)` and percentile endpoints
2.5 and 97.5. Consistency and its two terms can be recomputed from the released opening and tail embeddings.

Recency refers to a frame's original position in the generated trajectory. Replaying an old frame into a nearby
cache slot does not make its content recent. `RS_off` reads the native cache containing replayed history during
committing. `RS_real` reads a parallel FIFO cache of actual committed trajectory K/V during committing, while new
K/V is also stored in the native cache and its replay replacements continue. See the public
[Rolling Sink integration](../../integrations/rolling_sink/README.md) for code and the additional physical cache.
Equal committing capacity does not imply equal physical storage or memory cost.

Prompt, seed, initial-noise construction, denoising policy, replay policy and committing capacity are paired.
Later latents and actual KV states can diverge. Repeat-run variation was observed in the native pipeline, so we
interpret this as a rollout-policy comparison. The equal-capacity intervention does not fully separate historical
content, trajectory age and cache position, nor does it imply identical latents or complete RNG-stream alignment.
The recovered report does not specify exact old/recent source counts, so none are inferred here.

## Available evidence and replay

- [data/readout_rs.out](data/readout_rs.out) is the recovered original readout: 40 pairs, arm-level summaries,
  appearance-consistency and motion contrasts. Historical verdict wording in that file is retained as source
  material; the interpretation above limits the current claims.
- [data/reported_contrasts.csv](data/reported_contrasts.csv) contains the paired estimates and intervals.
  Consistency and its two terms use the feature-backed numerical summary. Motion retains the recovered readout;
  brightness and saturation retain the original experiment report and are identified separately in the CSV.
- [source/rs_verdict.py](source/rs_verdict.py) preserves the original evaluator and bootstrap implementation. Its
  historical printed hypothesis labels are not the conclusion of this page.
- [data/provenance.json](data/provenance.json) records evidence types, source hashes and limits.

The DINOv2 feature arrays reproduce consistency and Own/Sibling intervals. The complete videos, per-video sidecars
and original motion/color inputs are not included; their reported intervals remain transcribed summaries.

```bash
# Print the reported contrasts without re-estimating any interval.
python analysis/committing_source/tables.py
# New generation uses the public integration; this does not reproduce the missing original metric inputs.
python integrations/rolling_sink/generate.py --rule off --code /path/to/Rolling-Sink \
    --prompts analysis/longlive_sink/prompts20.txt --seconds 48 --seed 0 --out outputs/rolling_sink_source
# Repeat for both rules and both seeds, then score with the diagnostic pipeline if running a new experiment.
```

The [recent-context versus self-only comparison](../commit_window/README.md) uses a separate 60-second
VBench-Long protocol and exposes the continuity–motion tradeoff of retaining recent dependencies.
The [SGF equal-count control](../sgf_committing_controls/README.md) separately compares two 9-frame committing read sets.

## LongLive: source × assigned temporal position

We cross the provenance of three historical KV frames with their assigned temporal positions. The common committing
context contains the newest 9 trajectory frames, including the current 3-frame block. We add either the 3 sink
frames (`S`) or the oldest 3 of the newest 12 trajectory frames (`R`), assigned to initial (`S`) or recent (`R`)
positions. The first letter of `CP_*` denotes source and the second denotes position.

| Source | Assigned position | Consistency ↑ | Drift ↓ | Δ Drift from recent@recent |
|---|---|---:|---:|---:|
| Recent | Recent (`CP_RR`) | 0.0887 | 0.033 | — |
| Sink | Initial (`CP_SS`) | 0.0971 | 0.051 | +0.0188 |
| Recent | Initial (`CP_RS`) | 0.0928 | 0.040 | +0.0072 |
| Sink | Recent (`CP_SR`) | 0.0723 | 0.102 | +0.0692 |

Sink KV still increases Drift when moved to recent positions. Position also matters: moving sink KV from initial to
recent positions increases Drift by 0.0504, with its paired interval excluding zero. Moving recent KV to initial
positions gives a smaller increase whose interval spans zero. Source and position therefore both affect the
committing outcome. Provenance here includes content, trajectory age and encoding history.

The experiment uses 20 prompts × seeds 0/1 at 48 seconds, with all four arms generated fresh. Every condition stores
15 frames, denoises with sink 3 + newest 9, and commits with 12 frames. The first four blocks use the base context.
Position changes re-rotate only the temporal RoPE component of K on the read copy; stored entries and V stay unchanged.
Per-video seeds and the sampler call sequence are retained. This is the 12-frame diagnostic committing context,
separate from the six-frame Commit Forcing default on LongLive.

The [original readout](data/longlive_content_position_readout.txt) and
[full contrasts](data/longlive_content_position_contrasts.txt) retain all paired intervals and motion/color readouts.
[data/longlive_content_position.json](data/longlive_content_position.json) provides the compact reported statistics.
Arm means use the original rounding. These are archived summary statistics; the full metric inputs are not included.
The [recency experiment](../committing_content_age/README.md) separately varies source-block lag at a fixed
six-frame committing size and fixed assigned positions.
