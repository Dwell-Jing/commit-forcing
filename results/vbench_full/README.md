# Full VBench

**Current main results:** [common946: six paired generators](common946/README.md), each using Commit Forcing
with the current and immediately preceding blocks (6 latent frames after startup). Updated summaries
live under [common946/current6](common946/current6/). The original eight-pair package remains a separate historical
record, including the two 9-frame ID-Forcing framework adaptations.

## Earlier three-model analysis

VBench's standard suite on 60 s videos: 946 entries, one video each (generation seed 0), all 16 dimensions scored with
VBench-Long ([pipeline](../../eval/vbench_full/README.md)). Total, Quality and Semantic are VBench's
`cal_final_score.py`; Δ is the paired difference with its 95% bootstrap interval over the 944 distinct prompts, `*` when
the interval excludes 0.

This earlier package retains 9-frame SGF, 21-frame RF-TF and 6-frame CF controls. It differs from the current
six-generator method and the later historical eight-pair aggregation. Current and preserved results appear in
[RESULTS.md](../../RESULTS.md#full-vbench).

| File | Content |
|---|---|
| `vbench_full_60s.csv` | one row per video, 6 arms × 946 entries: the 16 dimension scores (mean over the video's clips; empty where the video is not scored) and the in-clip / clip-to-clip parts of subject and background consistency |
| `vbench_full_60s_shards.csv` | VBench-Long's overall score and video count per arm, dimension and scoring shard |
| `specs/*.json`, `tables/*.txt` | one spec per method and the output of `compare.py --spec`; every table reproduces exactly |

```bash
python eval/vbench_full/compare.py --spec results/vbench_full/specs/sgf.json
```

| Historical arm | Integration and recorded committing context |
|---|---|
| `sgf`, `sgf+rule` | SGF native denoising; Base / 9-frame recent-context control |
| `rf`, `rf+rule` | RF-TF denoising; Base / 21-frame recent-context control |
| `context_forcing`, `context_forcing+rule` | Context Forcing; Base / 6-frame Commit Forcing |
