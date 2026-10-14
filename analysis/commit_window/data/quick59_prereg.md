# LongLive quick59 window protocol

The initial protocol was written on 2026-10-13 at approximately 17:30, before generating its quick60 window videos.
The fixed-6 addendum was written at approximately 19:55, after the first adaptive verdicts and before generating
any fixed-6 video. This public transcription retains the experimental choices and decision rules.

## Prior observations used for the refinement

The rollf200, 60-second, seed-0 adaptive-3 development comparison against 12-frame committing gave Quality +0.18*,
Dynamic +2.98*, Subject c2c −0.38*, and Background c2c −0.26*. The consistency decrease was concentrated in videos
whose committing context narrowed to 3 frames for at least 90% of calls. A development analysis of the most static
third favored a 6-frame context over 3 frames. These observations motivate the new prompt and seed check.

## Protocol

Released LongLive base weights and LoRA. Denoising retains the released sink-3 plus newest-9 policy. The committing
pass never directly reads sink KV. Start from a quick60 list disjoint from rollf200, extended-MovieGen200, the older
quick20 set, and training prompts. Exclude the one prompt also present in the calibration list from every readout,
leaving 59 prompts. Generate 48-second videos (192 latent frames) with seeds 0, 1, and 2.

The static test uses the running mean latent motion of committed blocks, with threshold 0.26105 determined on a
separate 40-prompt calibration set. Its 180 selected local heads are retained from that calibration. Sampler,
attention kernels, and RNG protocol are shared across contexts.

| Label | Committing context when static | Otherwise |
|---|---|---|
| `LLS_c0` | 12 recent/current frames | 12 |
| `LLW_ad` | 3 current frames | 12 |
| `LLW_ad6` | 6 recent/current frames | 12 |
| `LLW_adh6` | local heads read 3 frames, other heads read 6 | 12 |

All counts include the current 3-frame block. A separate local-head-only adaptive variant was implemented but was
not generated in this check. VBench-Long uses the same custom-input seven visual dimensions as the development
comparison, including unfiltered Temporal Flickering. Scores are displayed ×100.

## Registered analysis

Each context minus `LLS_c0`, paired by prompt and seed. Report each seed with 4,000 prompt-bootstrap draws; pool the
per-prompt mean across three seeds and bootstrap the 59 prompts 4,000 times. Report Quality, Dynamic Degree,
Subject c2c, Background c2c, Subject within clips, and the motion-adjusted Subject c2c intercept. Prompt-cluster
resampling retains all seeds for that descriptive regression adjustment.

- Q1: the adaptive-3 consistency decrease replicates if its pooled Subject c2c interval is below zero and at least
  two of the three seed means are negative.
- Q2: among adaptive contexts with a positive Quality interval and a Subject c2c interval not wholly below zero,
  select the largest pooled Quality gain. Within 0.05 Quality points, prefer larger Subject c2c. If no context
  qualifies, report the tradeoff and retain adaptive 3 as the candidate.
- For adaptive contexts, also report changes by the fraction of static committing calls: never, partly, and at
  least 90%.

The completed readout groups these calls using the fraction of recorded `commit_windows` values equal to 3.
The public per-video CSV preserves that historical marker statistic. It does not impose the same actual 3-frame
read count on adaptive 6 or the mixed-head context; their configured read sets are listed above.

## Fixed-6 addendum

`LLW_w6` always reads the newest 6 trajectory frames, without a static test. Use the same generator code path,
kernels, RNG protocol, quick60 list, 48-second duration, and seeds 0–2.

Q3 compares adaptive 6 minus fixed 6, pairing prompts and seeds and pooling over three seeds. The static test adds
value if the pooled Quality or Subject c2c interval is above zero and neither is below zero. If either interval is
below zero, favor the fixed context; otherwise there is no evidence of added value from the static test. The fixed
control is not retroactively added as a Q2 candidate; Q1 and Q2 retain their original readouts.

Any 946-entry claim requires a separate standard-suite comparison. The quick59 result does not replace the
12-frame LongLive committing configuration in the published main table.

The original protocol SHA-256 is `2fa674edd26c857bfe054011c19d806d20020518a89ff56eaa98aacaca2c1f81`.
This transcription removes internal infrastructure and coordination notes; [quick59_provenance.json](quick59_provenance.json)
retains the source hash and reported-data scope.
