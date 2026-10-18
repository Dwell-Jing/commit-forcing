# Sink access across denoising and committing

We vary access to LongLive's 3-frame sink separately in the 4 denoising passes and the clean committing pass, on
paired 48-second videos. Excluded sink reads are replaced with recent trajectory frames to retain a 12-frame read
capacity, including the current block. Excluding the sink only during committing (`LLS_c0`, the legacy 12-frame control) reduces
absolute saturation drift and improves motion retention. Its appearance-consistency change is small and the paired
interval spans zero. Excluding the sink during denoising (`LLS_d0`) instead reduces consistency and increases drift.

The following changes are relative to sink access in both stages (`LLS_33`). Consistency is the contrastive DINOv2
diagnostic below, drift is the absolute deviation of the late/early saturation ratio from 1, and motion is the log
late/early motion ratio. These are the original diagnostic scales, not VBench scores or normalized effects.

| Arm | Denoising reads sink | Committing reads sink | Δ Consistency [95% CI] | Δ Saturation drift [95% CI] | Δ Log motion [95% CI] |
|---|---|---|---|---|---|
| `LLS_33`, base access | yes | yes | — | — | — |
| `LLS_c0`, legacy 12-frame control | yes | no | −0.0081 [−0.0180, +0.0006] | −0.0187\* [−0.0287, −0.0091] | +0.1179\* [+0.0611, +0.1766] |
| `LLS_d0` | no | yes | −0.0853\* [−0.1215, −0.0528] | +0.2052\* [+0.1264, +0.2985] | +0.0681 [−0.0841, +0.2313] |
| `LLS_00` | no | no | −0.0676\* [−0.0910, −0.0459] | +0.0822\* [+0.0460, +0.1198] | +0.1649\* [+0.0838, +0.2569] |

The baseline means are 0.0969514 for consistency and 0.0513247 for saturation drift. `*` means the paired 95%
interval excludes zero. `LLS_c0` also reduces the fraction of videos with late motion below 0.85 × early motion from
28% to 5%; this flag does not measure literal frozen frames.

The [Own/Sibling decomposition](../similarity_components/README.md) separates the full-frame similarity terms.
Excluding the sink during committing increases Own by +0.0112 and Sibling by +0.0193, both significant, while their
difference is not significant. Saved opening/tail embeddings and a CPU script reproduce these intervals.

LongLive's training uses sink access during committing and rollouts of up to 60 seconds. These 48-second results
therefore show that matching the training-time access configuration alone does not explain the sink's committing
effect in the tested configuration.


## SGF stage intervention

The same stage crossing on chunkwise SGF gives the same direction of Drift effects. Each condition uses 20 prompts,
seeds 0 and 1, and 48-second videos. `S` reads 3 sink + 3 prior recent + 3 current frames; `R` reads 6 prior recent +
3 current frames. Every stage therefore reads 9 frames, while all conditions retain a 12-frame physical cache,
including the sink. These are latent-frame counts; warm-up can read fewer available frames.

| Denoising | Committing | Consistency ↑ | Drift ↓ |
|---|---|---:|---:|
| S | S | 0.1399 | 0.034 |
| S | R | 0.1592 | 0.010 |
| R | S | 0.0026 | 0.253 |
| R | R | 0.0072 | 0.160 |

Removing sink access during committing changes Consistency by +0.0194 and Drift by −0.0241. Removing it during
denoising changes Consistency by −0.1373 and Drift by +0.2190. The complete original paired intervals and motion,
brightness, saturation and detail readouts are in [sgf_stage_readout.txt](data/sgf_stage_readout.txt); the
[additional contrasts](data/sgf_stage_contrasts.txt) compare the two stages. The [calibration readout](data/diagnostic_calibration_readout.md) also reports how these appearance diagnostics
respond to edited tails and alternate embeddings. The small Consistency gain from
committing changes to +0.0132 with an interval spanning zero after descriptive adjustment for measured drift and
motion. Consistency uses full-frame DINOv2 features rather than an identity classifier.

The intervention preserves the positions of selected KV entries, with top-aligned positions within the 21-frame
training range. Per-video RNG resets pair initial noise and intermediate re-noising across all four conditions.
The 9-frame `S/S` reference is not the native 12-frame-read SGF benchmark. This stage study is also distinct from the
[formal SGF committing-context comparison](../sgf_committing_controls/README.md), whose original four-arm runs
were paired by prompt and generation seed without locking the intermediate step RNG across arms.

`data/sgf_stage.json` transcribes the reported arm means and paired differences; its arm means retain the original
rounding. The complete original metric inputs were not recovered, so these files preserve the reported statistics
rather than claiming a new bootstrap replay. The existing LongLive CSV and `tables.py` below remain replayable.

## Arm levels and additional diagnostics

| Arm | Denoising passes read | Commit pass reads | Identity retention | Reduced motion | Saturation late/early | Brightness late/early |
|---|---|---|---|---|---|---|
| `LLS_33`, base | sink 3 + newest 9 | sink 3 + newest 9 | 0.817 | 0.28 | 0.972 | 0.979 |
| `LLS_c0`, legacy 12-frame control | sink 3 + newest 9 | newest 12 | 0.775 | 0.05 | 0.981 | 1.002 |
| `LLS_d0` | newest 12 | sink 3 + newest 9 | 0.105 | 0.33 | 1.233 | 0.992 |
| `LLS_00` | newest 12 | newest 12 | 0.270 | 0.15 | 0.964 | 0.987 |

| Difference to `LLS_33` | Brightness ratio [95% CI] | Saturation ratio [95% CI] | Absolute brightness drift [95% CI] |
|---|---|---|---|
| `LLS_c0` | +0.0231\* [+0.0095, +0.0396] | +0.0093 [−0.0046, +0.0228] | −0.0034 [−0.0133, +0.0052] |
| `LLS_d0` | +0.0128 [−0.0827, +0.1155] | +0.2611\* [+0.1686, +0.3653] | +0.1636\* [+0.1023, +0.2350] |
| `LLS_00` | +0.0083 [−0.0371, +0.0546] | −0.0071 [−0.0640, +0.0522] | +0.0720\* [+0.0414, +0.1047] |

Brightness and saturation ratio changes retain their sign; absolute drift measures their distance from 1. A ratio
increase and a reduction in absolute drift are different readouts.

## Protocol and replay

Protocol: 48 s (192 latent frames), the 20 prompts of `prompts20.txt` (lines 0–4 and 6–20 of Self-Forcing's
`prompts/MovieGenVideoBench_extended.txt`) × seeds 0 and 1 = 40 videos per arm, paired by (prompt, seed); 95% bootstrap
over prompts (4000 draws, NumPy `default_rng(0)`). Every arm stores 15 latent frames (sink 3 + newest 12), and every
pass has a 12-frame read capacity. This historical factorial study is distinct from the current main LongLive
Base / six-frame pair, where both arms store 12 physical frames. At a full read window, sink access uses 3 sink,
6 prior recent and 3 current frames; sink exclusion uses 9 prior recent and 3 current frames. Warm-up can use fewer
available frames. The current block is noisy during denoising and clean during committing. Per video, with the
column names of [data/longlive_sink_48s.csv](data/longlive_sink_48s.csv):

- identity `dino_late_38_47`: DINOv2 similarity of seconds 38–47.5 to the video's own opening (0.5–2 s) minus the
  similarity to the opening of the other seed of the same prompt and arm. Similarity uses cosine similarity between
  normalized temporal means of normalized full-frame DINOv2 CLS embeddings; retention = mean late / mean early
  (4–8 s) identity. Retention is a derived ratio, distinct from the consistency differences in the first table;
- colors: late (seconds 38–47) over early (seconds 4–7) mean of the per-second saturation `sat_k` and brightness
  `bri_k`; drift = |ratio − 1|;
- motion: log(`motion_late_38_47` / `motion_early_4_8`), the mean frame-to-frame change late over early; a video has
  reduced motion when its late motion is below 0.85 × its early motion.

`tables.py` also prints detail (`det_k`), the identity difference at equal motion (ANCOVA) and the DiT time per block.

```bash
for arm in LLS_33 LLS_c0 LLS_d0 LLS_00; do for seed in 0 1; do
  python analysis/longlive_sink/generate.py --arm $arm --code /path/to/LongLive \
      --prompts analysis/longlive_sink/prompts20.txt --seconds 48 --seed $seed --out outputs/longlive_sink
done; done
python analysis/metrics/compute.py outputs/longlive_sink --out longlive_sink.csv     # the columns of data/*.csv
python analysis/longlive_sink/tables.py                    # our data; --csv longlive_sink.csv for new videos
```

`generate.py` builds LongLive with [integrations/longlive](../../integrations/longlive/README.md) (LongLive at
`e52d9ef` + `commit_rule.patch`, see its README for the weights) and sets sink access and the window of every pass.
The read policies of `LLS_33` and `LLS_c0` correspond to the integration's `--rule off` and
`--rule on --commit-profile legacy12`; the factorial harness retains the same 15-frame storage for all four arms,
including the base-policy arm. The default integration `--rule on` now reads six frames with 12-frame storage.

The other core comparisons examine [committing sources on Rolling Sink](../committing_source/README.md) and
[recent-context versus self-only committing](../commit_window/README.md).

Related probes separate [historical source and assigned position](../committing_source/README.md),
[fixed-content KV propagation](../committing_propagation/README.md), and
[historical recency at fixed positions](../committing_content_age/README.md).
