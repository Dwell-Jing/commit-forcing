# SGF committing-context protocol

The source protocol was written on 2026-10-13 at approximately 18:40, before generating the self-only and equal-count
controls. This public transcription retains the experimental choices and interpretation rules; file paths refer
to this repository and its scored inputs.

| Group | Committing context | Latent frames read | Source |
|---|---|---:|---|
| A | 3 sink + 6 recent + 3 current | 12 | Existing SGF base outputs, seeds 0 and 1 |
| B | 6 recent + 3 current | 9 | Existing SGF Commit Forcing outputs, seeds 0 and 1 |
| C | 3 current | 3 | New self-only outputs |
| D | 3 sink + 3 recent + 3 current | 9 | New equal-count outputs retaining the sink |

## Fixed settings

Released SGF EMA weights, 12-frame cache geometry with a 3-frame sink, top-aligned positions, the same sampler,
denoising steps, attention kernels, and number of forwards. The evaluation uses 200
[rollf200 prompts](../../../eval/prompts/rollf200.txt), 60 seconds (240 latent frames), and generation seeds 0 and 1.
The committing context is selected by index after RoPE; retained entries are not renumbered.

C and D use the same generator and RNG protocol as the reused A and B: initial noise is seeded by
`seed * 100003 + prompt_index`, while the sampler's intermediate device re-noising draws are not fixed.
Each new video checks the read count at every committing call: C reads 3 frames; D reads 9 once the cache is full
and retains the sink. Scoring uses the same custom-input seven visual dimensions of VBench-Long as A and B,
including unfiltered Temporal Flickering and fused Subject/Background scores.

## Registered contrasts and statistics

Only B−A, B−C, and B−D. Pair by prompt and generation seed. Report each seed separately with 4,000 prompt-bootstrap
draws; for the pooled result, average the two seeds within each prompt and bootstrap the 200 prompts 4,000 times.
Report Quality, clip-to-clip Subject, Dynamic Degree, Motion Smoothness, Temporal Flickering, clip-to-clip Background,
fused Subject, Aesthetic Quality, and Imaging Quality together. Supplementary motion adjustment reports the
intercept of the clip-to-clip Subject change regressed on the Dynamic Degree change, using 2,000 prompt-bootstrap
draws retaining each prompt's seeds. The readout uses NumPy `default_rng(0)` sequentially in its specified contrast
and metric order.

## Interpretation rules fixed before the controls

- B−C: greater continuity with less motion is a tradeoff. No clear difference provides no additional SGF evidence
  for retaining recent frames, without establishing equivalence. If C is stably better without a clear cost, revisit
  the recommendation of retaining recent frames on SGF.
- B−D: improvement at the same read count excludes reading fewer frames as the sole explanation; it does not
  separately identify content, age, and position inside the model.
- B−A: reread the existing result under the same statistical protocol.

No further window, route, or layer group is added to these registered contrasts after seeing the results.

The SHA-256 of the original protocol is `c4b7e8f0e11705b280a5eaaa76ae5beb455fd282871137235631aed20f70327f`.
The original source hash is retained in [provenance.json](provenance.json); this public transcription has
different bytes because infrastructure paths and private coordination notes have been removed.
