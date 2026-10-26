# Results

Scores and reproduction data behind [RESULTS.md](../RESULTS.md). The [current common946 main evaluation](vbench_full/common946/README.md)
contains six paired generators, each using **Recent-Context Committing** with the current and immediately preceding
blocks (6 latent frames after startup). Its [current6 summaries](vbench_full/common946/current6/) are separate from
the preserved eight-pair historical package and its two 9-frame ID-Forcing framework adaptations.

The 60-second files below use VBench-Long on 200 fixed [`rollf200`](../eval/prompts/README.md) MovieGen prompts,
with the official seven-dimensional Quality formula ([evaluation](../eval/vbench_long/README.md)). They retain
supporting context controls: 9 frames on SGF and SGF+, 21 on RF-TF, Rolling Sink and Self-Forcing with sink,
6 on CF's full rule and LongLive, and 9 within ID-Forcing. CF sink exclusion is a separate control.
The [standard-suite results](vbench_full/README.md) use different prompts, dimension-specific subsets and Flickering
filtering. Each recorded Base / adapted pair retains its own protocol and scores.

| File | Content |
|---|---|
| `vbench_long_60s.csv` | one row per video and generation seed: 29 arms, 200 prompts, seed 0 for all and seed 1 for 20 |
| `specs/*.json` | the arms and contrasts of each table |
| `tables/*.txt` | the output of `compare.py --spec`; every table reproduces exactly from the CSV |

```bash
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed0.json
```

## Arm names

| Historical arm | Integration and recorded committing context |
|---|---|
| `sgf`, `sgf+rule` | SGF native denoising; Base / 9-frame control |
| `sgf_rf`, `sgf_rf+rule` | SGF RF denoising; Base / 18-frame control |
| `sgf_plus`, `sgf_plus+rule` | SGF+; Base / 9-frame control |
| `sf_sink`, `sf_sink+rule` | RF geometry without TRB; Base / 21-frame control |
| `rf`, `rf+rule` | RF-TF denoising; Base / 21-frame control |
| `longlive` | historical Base access, sink 3 + newest 9; 15-frame physical cache |
| `longlive+rule` | historical 12-frame committing control; 15-frame physical cache (`--rule on --commit-profile legacy12`) |
| `longlive+commit6` | historical 6-frame committing arm; 15-frame physical cache (`analysis/commit_window/generate.py --commit-frames 6`) |
| `context_forcing`, `context_forcing+rule`, `context_forcing+sink_only` | Context Forcing; Base / 6-frame full rule / sink-exclusion control |
| `rolling_sink`, `rolling_sink+rule` | Rolling Sink; Base / 21-frame control |
| `idf_sf`, `idf_sf+rule`, `idf_longlive`, `idf_longlive+rule` | ID-Forcing on the named backbone; Base / 9-frame framework adaptation |
| `sf` | Self-Forcing for long videos, the original no-sink reference: `analysis/sf_router --route G3_R21` |

The tables also hold arms from our analyses: `sf+far_denoise` (Self-Forcing reads far history only in the last 2
denoising passes at layers 12-29; `analysis/sf_router --route G3_L12_29`), `sf_sink+commit_self` and
`longlive+commit_self` (the commit pass reads only its own chunk), `longlive+commit6` and `longlive+commit9` (the commit
pass reads the newest 6 / 9 real frames; [commit window](../analysis/commit_window/README.md)), and `rf_v2` (Recency
Forcing's reading implemented a second time in the SGF code base).

RF arm names refer to distinct implementations. Historical `rf` / `rf+rule` store 24 physical latent frames and read
3 sink + 18 trajectory frames during denoising; the adapted control reads 21 trajectory frames. `sgf_rf` and `rf_v2`
store 21 physical frames and read 18 trajectory frames during adapted committing. Clean committing disables TRB in
all three. The alternative `rf_v2` Quality comparison, 81.89 → 82.38, uses 60-second rollf200 videos with seed 0.
[Exact configurations](../integrations/recency_forcing/README.md#rf-implementations).

LongLive labels in `vbench_long_60s.csv` describe the historical window study: Base-policy and window arms retain
15-frame physical storage. In particular, `longlive+rule` remains the 12-frame control and `longlive+commit6` the
six-frame arm. The current common946 main pair uses six-frame committing with 12-frame physical storage in both
Base and Recent-Context Committing. The public integration defaults to that read/storage policy; its explicit
`--commit-profile legacy12` preserves the previous configuration. These labels and their recorded scores are unchanged.
Current integration defaults use the 6-frame method. To regenerate historical SGF/SGF+, RF-TF or Rolling Sink
controls, retain the corresponding wider context documented in each integration.
See the [window controls](../analysis/commit_window/README.md) and
[LongLive integration](../integrations/longlive/README.md) for the generation settings.

## Further evidence

- [Current six-frame custom-prompt results and window scans](current6_custom/README.md): aggregate records for both generation seeds and the six-frame SGF 240-second comparison.
- [Committing variants](../analysis/committing_variants/README.md): all 27 discovery variants, separate confirmations and component costs.
- [Full VBench: 946 entries and 16 dimensions](vbench_full/README.md).
- [120- and 240-second videos](long_horizon/README.md), including [six-frame LongLive at 240 seconds](long_horizon/longlive6_240/README.md).
- [Human evaluation](human_evaluation/README.md).
- [Separate denoising/committing KV construction and extra old history](../analysis/kv_construction/README.md): recorded aggregate contrasts and configurations.
- [Released Rolling Forcing and WorldPlay transfer boundaries](../analysis/transfer_boundaries/README.md): aggregate results on their respective protocols and scales.
- [Mechanism analyses](../README.md#mechanism-analyses).
