# How many frames the commit pass reads

On LongLive, the commit pass can read the newest 3, 6, 9 or 12 real frames instead of the sink and the newest 9.
Every window raises Quality over the base model, by +0.42 to +0.64 over both generation seeds. The window trades
motion against long-range consistency: 3 frames (the block itself) move the most, and
6 frames give the highest clip-to-clip subject consistency of the windows run on both seeds (9 frames, run on seed 0
only, ties with 6). Quality differences between windows stay within ±0.17 and change sign between seeds.

VBench-Long, rollf200 × 60 s, ×100, generation seed 0 / seed 1 (`*`: the paired 95% bootstrap interval excludes 0).
Consistency: clip-to-clip subject consistency.

| Commit pass reads | Quality | Dynamic | Consistency | Background, clip to clip | Δ Quality to base |
|---|---|---|---|---|---|
| sink 3 + newest 9 (base) | 82.23 / 82.19 | 42.98 / 42.03 | 86.01 / 86.02 | 88.40 / 88.20 | |
| newest 3 (the block itself) | 82.73 / 82.83 | 53.03 / 54.18 | 86.21 / 85.91 | 88.79 / 88.49 | +0.49\* / +0.64\* |
| newest 6 | 82.73 / 82.66 | 49.40 / 48.65 | 87.21 / 87.09 | 89.53 / 89.36 | +0.49\* / +0.46\* |
| newest 9 | 82.72 / – | 49.47 / – | 87.23 / – | 89.55 / – | +0.48\* / – |
| newest 12 (Commit Forcing) | 82.65 / 82.67 | 49.38 / 50.20 | 86.93 / 86.70 | 89.17 / 88.84 | +0.42\* / +0.48\* |

Between windows, Consistency: 6 − 3 +1.00\* / +1.18\*, 6 − 12 +0.28\* / +0.38\*, 9 − 6 +0.02 (seed 0); Dynamic: 6 − 3
−3.63\* / −5.53\*; Quality: 6 − 3 +0.00 / −0.17\*, 6 − 12 +0.08 / −0.02.

Self-Forcing with a 3-frame sink (`integrations/recency_forcing --trb off`), where every denoising pass reads
the sink and the newest 18 frames; seed 0:

| Commit pass reads | Quality | Consistency |
|---|---|---|
| sink 3 + newest 18, as the denoising passes | 81.33 | 75.18 |
| newest 3 (the block itself) | 81.28 | 74.69 |
| newest 21 (Commit Forcing) | **81.63** | **78.56** |

Commit Forcing − sink: Quality +0.31 [−0.30, +0.83], Consistency +3.38\*; Commit Forcing − block itself: Quality +0.36
[−0.16, +0.81], Consistency +3.87\*. Reading only the block itself drops the recent frames together with the sink; Commit
Forcing drops only the sink.

```bash
# LongLive: the commit pass reads the newest 3 / 6 / 9 / 12 frames (12 = integrations/longlive --rule on)
python analysis/commit_window/generate.py --commit-frames 6 --code /path/to/LongLive \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window
# Self-Forcing + sink: the block itself (21 = integrations/recency_forcing --trb off --rule on)
python analysis/commit_window/generate_sf_sink.py --commit-frames 3 --code /path/to/Self-Forcing \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window
# score <out>/commit6 etc. with eval/vbench_long (prep.py --videos outputs/commit_window/commit6, score.sh, collect.py)
python analysis/commit_window/tables.py      # the tables above, from results/vbench_long_60s.csv
python eval/vbench_long/compare.py --spec results/specs/vbl60_longlive_commit_window.json
```

`tables.py` replays the specs `vbl60_seed0`, `vbl60_longlive_commit_window`, `vbl60_longlive_commit6_vs_12`,
`vbl60_seed1_a` and `vbl60_seed1_b` with `compare.py`, so every interval is the one in `results/tables/`. Labels in
`results/`: `longlive`, `longlive+commit_self` (3), `longlive+commit6`, `longlive+commit9`, `longlive+rule` (12),
`sf_sink`, `sf_sink+commit_self`, `sf_sink+rule`. `generate.py` uses the per-pass control of
[`analysis/longlive_sink/generate.py`](../longlive_sink/generate.py).
