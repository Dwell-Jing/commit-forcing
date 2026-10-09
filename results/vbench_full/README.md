## Full VBench

VBench's standard suite on 60 s videos: 946 entries, one video each (generation seed 0), all 16 dimensions scored with
VBench-Long ([pipeline](../../eval/vbench_full/README.md)). Total, Quality and Semantic are VBench's
`cal_final_score.py`; Δ is the paired difference with its 95% bootstrap interval over the 944 distinct prompts, `*` when
the interval excludes 0.

The tables are in [RESULTS.md](../../RESULTS.md#full-vbench).

| File | Content |
|---|---|
| `vbench_full_60s.csv` | one row per video, 6 arms × 946 entries: the 16 dimension scores (mean over the video's clips; empty where the video is not scored) and the in-clip / clip-to-clip parts of subject and background consistency |
| `vbench_full_60s_shards.csv` | VBench-Long's overall score and video count per arm, dimension and scoring shard |
| `specs/*.json`, `tables/*.txt` | one spec per method and the output of `compare.py --spec`; every table reproduces exactly |

```bash
python eval/vbench_full/compare.py --spec results/vbench_full/specs/sgf.json
```

| Arm | Integration and flags |
|---|---|
| `sgf`, `sgf+rule` | `integrations/sgf --reading native --rule off/on` |
| `rf`, `rf+rule` | `integrations/recency_forcing --reading rf --rule off/on` |
| `context_forcing`, `context_forcing+rule` | `integrations/context_forcing --rule off/on` |
