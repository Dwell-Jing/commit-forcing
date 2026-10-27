# Recent-context KV construction within ID-Forcing

ID-Forcing (arXiv 2610.03120) caches each chunk from its own clean pass (self-only caching), motivated by a mismatch
between the KV states of training and those of long videos. We compare its full procedure with recent-context KV
construction inside its framework on Self-Forcing, which trains on 5 s clips. With `--rule on`, the
[integration](../../integrations/id_forcing/README.md) keeps ID-Forcing's sink, short window, RoPE realignment, sampler
and decoding, and commits each chunk from the previous two chunks and the chunk itself.

On Self-Forcing, the adaptation also retains Self-Forcing's original commits of chunks 5 and 6 at handover and omits
ID-Forcing's recurrent re-encoding of chunk n−1 on top of chunk n−2. These results compare the combined KV construction
and handover procedures. They do not isolate the committing read set alone. The native-framework
[recent versus self-only comparison](../commit_window/README.md) and the
[LongLive stage intervention](../longlive_sink/README.md) provide the controlled core comparisons.

The [SGF four-group control](../sgf_committing_controls/README.md) also compares recent context with self-only
committing within SGF. It finds no significant Quality or clip-to-clip Subject difference, with a smoothness–motion
tradeoff. This native-framework control does not compare the complete ID-Forcing procedure.

| Length (× training) | Prompts | Seed | ID-Forcing | 9-frame adaptation | Δ Quality | Δ Consistency | Δ Background, clip to clip | Δ Dynamic |
|:---|:---|--:|--:|--:|:---|--:|--:|--:|
| 60 s (12×) | rollf200 | 0 | 82.20 | 82.44 | +0.23* [+0.07, +0.40] | +2.53* | +1.79* | −1.17 |
| 60 s (12×) | rollf200 | 1 | 82.47 | 82.67 | +0.20* [+0.04, +0.37] | +2.27* | +1.51* | −2.25* |
| 120 s (24×) | ID-Forcing's 128 | 0 | 81.62 | 81.68 | +0.06 [−0.15, +0.26] | +3.05* | +2.05* | −3.78* |
| 240 s (48×) | ID-Forcing's 128 | 0 | 81.32 | 81.65 | +0.34* [+0.05, +0.70] | +3.58* | +2.68* | −2.62* |

ID-Forcing and its 9-frame adaptation: VBench-Long Quality, x100. Consistency: clip-to-clip subject consistency. Δ: paired by
prompt (`idf_sf+rule − idf_sf`), `*` = the 95% bootstrap interval excludes 0. rollf200 is our custom-prompt set,
ID-Forcing's 128 its own MovieGen prompts. This SF adaptation raises clip-to-clip subject and background consistency
at every tested length, up to 48 times the training length, and Quality at 60 s (both seeds) and 240 s. The 120 s
Quality interval spans zero. Dynamic Degree decreases significantly at 60 s seed 1, 120 s and 240 s, so the consistency
gains also have a motion tradeoff. These results do not establish a general cause of train/inference mismatch.

## Commands

```bash
# generation: ID-Forcing checkout at 4cd6a4c (bash setup/fetch.sh id_forcing)
python integrations/id_forcing/generate.py --generator self_forcing --rule off --idf-code third_party/id_forcing \
    --prompts eval/prompts/rollf200.txt --seconds 60 --seed 0 --out outputs/id_forcing       # then --rule on, --seed 1
python integrations/id_forcing/generate.py --generator self_forcing --rule on --idf-code third_party/id_forcing \
    --prompts third_party/id_forcing/prompts/moviegenbench_128.txt --seconds 120 --seed 0 --out outputs/idf128_120s
# Historical output label: rows "ID-Forcing + Commit Forcing - ID-Forcing" of
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed0.json                  # 60 s, seed 0
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed1_a.json                # 60 s, seed 1
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_120s.json
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_240s.json
```

The videos are scored with [`eval/vbench_long`](../../eval/vbench_long/README.md); the 120 s and 240 s scores are in
[`results/long_horizon`](../../results/long_horizon/README.md).
