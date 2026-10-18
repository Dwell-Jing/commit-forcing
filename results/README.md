# Results

Scores and reproduction data behind [RESULTS.md](../RESULTS.md). The [common946 main evaluation](vbench_full/common946/README.md) contains all 8 paired configurations and complete 16-dimensional scores. The 60 s results below use
VBench-Long on 200 fixed [`rollf200`](../eval/prompts/README.md) MovieGen prompts, 60 s per video, with the official
seven-dimensional Quality formula ([evaluation](../eval/vbench_long/README.md)). The
[standard-suite results](vbench_full/README.md) use different prompts, dimension-specific subsets and Flickering
filtering; both sets retain their own paired Base / + Commit Forcing comparisons.

| File | Content |
|---|---|
| `vbench_long_60s.csv` | one row per video and generation seed: 29 arms, 200 prompts, seed 0 for all and seed 1 for 20 |
| `specs/*.json` | the arms and contrasts of each table |
| `tables/*.txt` | the output of `compare.py --spec`; every table reproduces exactly from the CSV |

```bash
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed0.json
```

## Arm names

| Arm | Integration and flags |
|---|---|
| `sgf`, `sgf+rule` | `integrations/sgf --reading native --rule off/on` |
| `sgf_rf`, `sgf_rf+rule` | `integrations/sgf --reading rf --rule off/on` |
| `sgf_plus`, `sgf_plus+rule` | `integrations/sgf_plus --rule off/on` |
| `sf_sink`, `sf_sink+rule` | RF geometry without TRB: `integrations/recency_forcing --trb off --rule off/on` |
| `rf`, `rf+rule` | `integrations/recency_forcing --reading rf --rule off/on` |
| `longlive` | historical Base access, sink 3 + newest 9; 15-frame physical cache |
| `longlive+rule` | historical 12-frame committing control; 15-frame physical cache (`--rule on --commit-profile legacy12`) |
| `longlive+commit6` | historical 6-frame committing arm; 15-frame physical cache (`analysis/commit_window/generate.py --commit-frames 6`) |
| `context_forcing`, `context_forcing+rule`, `context_forcing+sink_only` | `integrations/context_forcing` |
| `rolling_sink`, `rolling_sink+rule` | `integrations/rolling_sink --rule off/on` |
| `idf_sf`, `idf_sf+rule`, `idf_longlive`, `idf_longlive+rule` | `integrations/id_forcing --generator self_forcing/longlive --rule off/on` |
| `sf` | Self-Forcing for long videos (no sink, so Commit Forcing changes nothing): `analysis/sf_router --route G3_R21` |

The tables also hold arms from our analyses: `sf+far_denoise` (Self-Forcing reads far history only in the last 2
denoising passes at layers 12-29; `analysis/sf_router --route G3_L12_29`), `sf_sink+commit_self` and
`longlive+commit_self` (the commit pass reads only its own chunk), `longlive+commit6` and `longlive+commit9` (the commit
pass reads the newest 6 / 9 real frames; [commit window](../analysis/commit_window/README.md)), and `rf_v2` (Recency
Forcing's reading implemented a second time in the SGF code base).

RF arm names refer to distinct implementations. Main `rf` / `rf+rule` store 24 physical latent frames and read
3 sink + 18 trajectory frames during denoising; CF committing reads 21 trajectory frames. `sgf_rf` and `rf_v2`
store 21 physical frames and read 18 trajectory frames during CF committing. Clean committing disables TRB in
all three. The alternative `rf_v2` Quality comparison, 81.89 → 82.38, uses 60-second rollf200 videos with seed 0.
[Exact configurations](../integrations/recency_forcing/README.md#rf-implementations).

LongLive labels in `vbench_long_60s.csv` describe the historical window study: Base-policy and window arms retain
15-frame physical storage. In particular, `longlive+rule` remains the 12-frame control and `longlive+commit6` the
six-frame arm. The current common946 main pair uses six-frame committing with 12-frame physical storage in both
Base and +Commit Forcing. The public integration now defaults to that read/storage policy; its explicit
`--commit-profile legacy12` preserves the previous configuration. These labels and their recorded scores are unchanged.
See the [window controls](../analysis/commit_window/README.md) and
[LongLive integration](../integrations/longlive/README.md) for the generation settings.

## Further evidence

- [Full VBench: 946 entries and 16 dimensions](vbench_full/README.md).
- [120- and 240-second videos](long_horizon/README.md), including [six-frame LongLive at 240 seconds](long_horizon/longlive6_240/README.md).
- [Human evaluation](human_evaluation/README.md).
- [Mechanism analyses](../README.md#mechanism-analyses).
