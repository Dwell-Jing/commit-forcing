# Recent-context committing within ID-Forcing

ID-Forcing (arXiv 2610.03120) caches each chunk from its own clean pass (self-only caching), motivated by a mismatch
between the KV states of training and those of long videos. We test recent-context committing inside its framework, on
Self-Forcing, which trains on 5 s clips. With `--rule on`, the [integration](../../integrations/id_forcing/README.md)
keeps ID-Forcing's sink, short window, RoPE realignment, sampler and decoding, and commits each chunk from the previous
two chunks and the chunk itself.

| Length (× training) | Prompts | Seed | ID-Forcing | + Commit Forcing | Δ Quality | Δ Consistency | Δ Background, clip to clip | Δ Dynamic |
|:---|:---|--:|--:|--:|:---|--:|--:|--:|
| 60 s (12×) | rollf200 | 0 | 82.20 | 82.44 | +0.23* [+0.07, +0.40] | +2.53* | +1.79* | −1.17 |
| 60 s (12×) | rollf200 | 1 | 82.47 | 82.67 | +0.20* [+0.04, +0.37] | +2.27* | +1.51* | −2.25* |
| 120 s (24×) | ID-Forcing's 128 | 0 | 81.62 | 81.68 | +0.06 [−0.15, +0.26] | +3.05* | +2.05* | −3.78* |
| 240 s (48×) | ID-Forcing's 128 | 0 | 81.32 | 81.65 | +0.34* [+0.05, +0.70] | +3.58* | +2.68* | −2.62* |

ID-Forcing and + Commit Forcing: VBench-Long Quality, x100. Consistency: clip-to-clip subject consistency. Δ: paired by
prompt (`idf_sf+rule − idf_sf`), `*` = the 95% bootstrap interval excludes 0. rollf200 is our main prompt set,
ID-Forcing's 128 its own MovieGen prompts. Replacing self-only caching with recent-context committing raises
clip-to-clip subject and background consistency at every length, up to 48 times the training length, and Quality at
60 s (both seeds) and 240 s.

One implementation detail differs besides the commit context. ID-Forcing re-encodes chunk n−1 on top of the self-cached
entry of chunk n−2 before denoising chunk n. The + Commit Forcing arm drops this re-encoding: every stored entry was
committed attending to the chunks before it, so it already carries that context.

## Commands

```bash
# generation: ID-Forcing checkout at 4cd6a4c (bash setup/fetch.sh id_forcing)
python integrations/id_forcing/generate.py --generator self_forcing --rule off --idf-code third_party/id_forcing \
    --prompts eval/prompts/rollf200.txt --seconds 60 --seed 0 --out outputs/id_forcing       # then --rule on, --seed 1
python integrations/id_forcing/generate.py --generator self_forcing --rule on --idf-code third_party/id_forcing \
    --prompts third_party/id_forcing/prompts/moviegenbench_128.txt --seconds 120 --seed 0 --out outputs/idf128_120s
# tables: rows "ID-Forcing + Commit Forcing - ID-Forcing" of
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed0.json                  # 60 s, seed 0
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed1_a.json                # 60 s, seed 1
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_120s.json
python eval/vbench_long/compare.py --spec results/long_horizon/specs/idf128_240s.json
```

The videos are scored with [`eval/vbench_long`](../../eval/vbench_long/README.md); the 120 s and 240 s scores are in
[`results/long_horizon`](../../results/long_horizon/README.md).
