# Longer videos

VBench-Long on 120 s and 240 s videos, scored as in [`results`](../README.md), generation seed 0. The tables are in
[RESULTS.md](../../RESULTS.md#longer-videos); this page describes the prompts, the drift measure, the files and the
commands. CF and LongLive use the current and immediately preceding blocks (6 latent frames). SGF remains
a 9-frame source-control reference; its +5.07 consistency gain is supporting evidence for that wider context.
ID-Forcing retains its separate 9-frame framework adaptation.

## 240 s, 32 MovieGen prompts

The first 32 extended MovieGen prompts of Self-Forcing (`prompts/MovieGenVideoBench_extended.txt`, `--ids 0-31`),
960 latent frames per video. Quality drift is the imaging quality of the first
2 s clip minus that of the last one (positive: the video loses quality over time).

## 120 s and 240 s, ID-Forcing's 128 MovieGen prompts

The MovieGen prompts of ID-Forcing (`prompts/moviegenbench_128.txt` of its repository). ID-Forcing on Self-Forcing
with the 9-frame adaptation uses recent-context KV construction with the documented handover and re-encoding changes
([`analysis/not_ood`](../../analysis/not_ood/README.md)).

The original 120/240-second files retain LongLive's base-policy and 12-frame committing control, both with 15-frame
physical storage. Their `longlive+rule` label remains the 12-frame control.
The six-frame results at [120 seconds](longlive6_120/README.md) and [240 seconds](longlive6_240/README.md) are complete
and reported separately. The current common946 main configuration
uses six-frame committing and 12-frame storage in both arms, so these historical longer-video rows have a distinct
cache configuration.

## Files and commands

| File | Content |
|---|---|
| `vbench_long_240s_moviegen32.csv`, `quality_drift_240s_moviegen32.csv` | per video: VBench-Long (columns of `eval/vbench_long/collect.py`) and dDrift1 / dDrift5 (first / last 1 or 5 clips), 6 arms × 32 prompts |
| `vbench_long_{120,240}s_idf128.csv` | per video: VBench-Long, 6 / 5 arms × 128 prompts |
| `longlive6_240/` | complete four-arm scores, 33 six-frame paired effects, drift scores and CPU replay |
| `specs/*.json`, `tables/*.txt` | the arms and contrasts of each table and their output; every table reproduces exactly |

```bash
python results/long_horizon/quality_drift.py table --spec results/long_horizon/specs/moviegen32_240s_sgf.json
python results/long_horizon/quality_drift.py table --spec results/long_horizon/specs/moviegen32_240s_context_forcing.json
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_120s.json
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_240s.json
python results/long_horizon/longlive6_240/replay.py
```

To regenerate an arm, retain its recorded committing context (including the wider-context profile for SGF) and
run its integration with `--seconds 120` or `240`. Score it with
[`eval/vbench_long`](../../eval/vbench_long/README.md) (`prep.py --num-prompts 32` or `128`); for the MovieGen32 table, add
the quality drift:

```bash
python results/long_horizon/quality_drift.py collect --work vb_work --label sgf+rule --out quality_drift.csv
# Historical 12-frame committing control (15-frame physical storage):
python integrations/longlive/generate.py --code third_party/longlive --rule on --commit-profile legacy12 \
    --seconds 120 --seed 0 --prompts third_party/id_forcing/prompts/moviegenbench_128.txt --ids 0-127 \
    --out outputs/idf128_120s/longlive12
```

| Historical arm | Integration and recorded committing context |
|---|---|
| `sgf`, `sgf+rule` | SGF native denoising; Base / 9-frame source-control reference |
| `context_forcing`, `+rule`, `+sink_only` | Context Forcing; Base / 6-frame full rule / sink-exclusion control |
| `context_forcing+memory_only` | `integrations/context_forcing --rule memory-only` (exclude slow memory and older frames while retaining sink + recent) |
| `longlive` | historical Base access with 15-frame physical storage (`analysis/longlive_sink/generate.py --arm LLS_33`) |
| `longlive+rule` | historical 12-frame committing control, 15-frame physical storage (`integrations/longlive --rule on --commit-profile legacy12`) |
| `idf_sf`, `idf_sf+rule` | ID-Forcing on Self-Forcing; Base / 9-frame framework adaptation |
| `rf+rule` | RF-TF denoising; 21-frame recent-context control |
| `sf` | Self-Forcing (no sink): `analysis/sf_router --route G3_R21` |

The RF-TF 21-frame recent-context long-horizon control stores 24 physical frames and disables TRB during clean committing.
It has no matched RF-only arm at either duration. See [RF implementations](../../integrations/recency_forcing/README.md#rf-implementations).
