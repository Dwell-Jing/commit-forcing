# Results

Per-video scores and the specs behind every table of [RESULTS.md](../RESULTS.md). The 60 s results below use
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
| `longlive`, `longlive+rule` | `integrations/longlive --rule off/on` |
| `context_forcing`, `context_forcing+rule`, `context_forcing+sink_only` | `integrations/context_forcing` |
| `rolling_sink`, `rolling_sink+rule` | `integrations/rolling_sink --rule off/on` |
| `idf_sf`, `idf_sf+rule`, `idf_longlive`, `idf_longlive+rule` | `integrations/id_forcing --generator self_forcing/longlive --rule off/on` |
| `sf` | Self-Forcing for long videos (no sink, so Commit Forcing changes nothing): `analysis/sf_router --route G3_R21` |

The tables also hold arms from our analyses: `sf+far_denoise` (Self-Forcing reads far history only in the last 2
denoising passes at layers 12-29; `analysis/sf_router --route G3_L12_29`), `sf_sink+commit_self` and
`longlive+commit_self` (the commit pass reads only its own chunk), `longlive+commit6` and `longlive+commit9` (the commit
pass reads the newest 6 / 9 real frames; [commit window](../analysis/commit_window/README.md)), and `rf_v2` (Recency
Forcing's reading implemented a second time in the SGF code base).

## Further evidence

- [Full VBench: 946 entries and 16 dimensions](vbench_full/README.md).
- [240-second videos](long_horizon/README.md), including TetherCache and its FIFO baseline.
- [Mechanism analyses](../README.md#mechanism-analyses).
