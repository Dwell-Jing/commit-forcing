# Longer videos

VBench-Long on 120 s and 240 s videos, scored as in [`results`](../README.md), generation seed 0. The tables are in
[RESULTS.md](../../RESULTS.md#longer-videos); this page describes the prompts, the drift measure, the files and the
commands.

## 240 s, 32 MovieGen prompts

The first 32 extended MovieGen prompts of Self-Forcing (`prompts/MovieGenVideoBench_extended.txt`, `--ids 0-31`),
960 latent frames per video. Quality drift is the imaging quality of the first
2 s clip minus that of the last one (positive: the video loses quality over time).

## 120 s and 240 s, ID-Forcing's 128 MovieGen prompts

The MovieGen prompts of ID-Forcing (`prompts/moviegenbench_128.txt` of its repository). ID-Forcing on Self-Forcing
+ Commit Forcing uses recent-context KV construction with the documented handover and re-encoding changes
([`analysis/not_ood`](../../analysis/not_ood/README.md)).

The original 120/240-second files retain LongLive's base-policy and 12-frame committing control, both with 15-frame
physical storage. Their `longlive+rule` label remains the 12-frame control.
The [120-second six-frame result](longlive6_120/README.md) is reported separately; the 240-second six-frame evaluation
is pending. The current common946 main configuration
uses six-frame committing and 12-frame storage in both arms, so these historical longer-video rows have a distinct
cache configuration.

## Files and commands

| File | Content |
|---|---|
| `vbench_long_240s_moviegen32.csv`, `quality_drift_240s_moviegen32.csv` | per video: VBench-Long (columns of `eval/vbench_long/collect.py`) and dDrift1 / dDrift5 (first / last 1 or 5 clips), 6 arms × 32 prompts |
| `vbench_long_{120,240}s_idf128.csv` | per video: VBench-Long, 6 / 5 arms × 128 prompts |
| `specs/*.json`, `tables/*.txt` | the arms and contrasts of each table and their output; every table reproduces exactly |

```bash
python results/long_horizon/quality_drift.py table --spec results/long_horizon/specs/moviegen32_240s_sgf.json
python results/long_horizon/quality_drift.py table --spec results/long_horizon/specs/moviegen32_240s_context_forcing.json
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_120s.json
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_240s.json
```

To regenerate an arm, run its integration with `--seconds 120` or `240` and score it with
[`eval/vbench_long`](../../eval/vbench_long/README.md) (`prep.py --num-prompts 32` or `128`); for the MovieGen32 table, add
the quality drift:

```bash
python integrations/sgf/generate.py --code third_party/sgf --reading native --rule on --seconds 240 --seed 0 \
    --prompts third_party/recency_forcing/prompts/MovieGenVideoBench_extended.txt --ids 0-31 --out outputs/moviegen32_240s/sgf
python results/long_horizon/quality_drift.py collect --work vb_work --label sgf+rule --out quality_drift.csv
# Historical 12-frame committing control (15-frame physical storage):
python integrations/longlive/generate.py --code third_party/longlive --rule on --commit-profile legacy12 \
    --seconds 120 --seed 0 --prompts third_party/id_forcing/prompts/moviegenbench_128.txt --ids 0-127 \
    --out outputs/idf128_120s/longlive12
```

| Arm | Integration and flags |
|---|---|
| `sgf`, `sgf+rule` | `integrations/sgf --reading native --rule off/on` |
| `context_forcing`, `+rule`, `+sink_only` | `integrations/context_forcing --rule off/on/sink-only` |
| `context_forcing+memory_only` | `integrations/context_forcing --rule memory-only` (exclude slow memory and older frames while retaining sink + recent) |
| `longlive` | historical Base access with 15-frame physical storage (`analysis/longlive_sink/generate.py --arm LLS_33`) |
| `longlive+rule` | historical 12-frame committing control, 15-frame physical storage (`integrations/longlive --rule on --commit-profile legacy12`) |
| `idf_sf`, `idf_sf+rule` | `integrations/id_forcing --generator self_forcing --rule off/on` |
| `rf+rule` | `integrations/recency_forcing --reading rf --rule on` |
| `sf` | Self-Forcing (no sink): `analysis/sf_router --route G3_R21` |
