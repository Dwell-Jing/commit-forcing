# VBench-Long evaluation

We follow the protocol of Recency Forcing Tab. 3: 200 MovieGen prompts ([`rollf200`](../prompts/README.md)),
one 60 s video per prompt, VBench-Long, and Quality = the min-max normalised mean of 7 dimensions with dynamic degree
weighted 0.5. We add the clip-to-clip part of subject consistency, which VBench-Long computes from the first frame of
every 2 s clip, as our long-range measure.

## Setup

```bash
git clone https://github.com/Vchitect/VBench.git && git -C VBench checkout 45e79ec
```

Install the environment of [`setup`](../../setup/README.md), not VBench's `requirements.txt` (its pins conflict with
it), and let VBench download its checkpoints (or point `VBENCH_CACHE_DIR` at a copy).

## Steps

```bash
# 1. generate 200 videos per arm (any integration; 60 s = 240 latent frames)
python integrations/sgf/generate.py --code third_party/sgf --reading native --rule off --prompts eval/prompts/rollf200.txt --seconds 60 --seed 0 --out outputs/sgf
python integrations/sgf/generate.py --code third_party/sgf --reading native --rule on --prompts eval/prompts/rollf200.txt --seconds 60 --seed 0 --out outputs/sgf

# 2. link, split into clips once, and shard (8 shards per arm)
python eval/vbench_long/prep.py --vbench VBench --videos outputs/sgf/native/rule_off --label sgf --seeds 0 --work vb_work
python eval/vbench_long/prep.py --vbench VBench --videos outputs/sgf/native/rule_on --label sgf+rule --seeds 0 --work vb_work

# 3. score: one copy per GPU, each takes the next unscored shard
for g in 0 1 2 3 4 5 6 7; do bash eval/vbench_long/score.sh VBench vb_work $g & done; wait

# 4. one CSV row per video, then paired contrasts
python eval/vbench_long/collect.py --work vb_work --label sgf --out scores.csv
python eval/vbench_long/collect.py --work vb_work --label sgf+rule --out scores.csv --append
python eval/vbench_long/compare.py --scores scores.csv --seed 0 --pair sgf+rule:sgf
```

`score.sh` runs VBench-Long with `--mode long_custom_input --dev_flag`; `--dev_flag` fuses the in-clip and
clip-to-clip parts of subject and background consistency (0.5 / 0.5, `configs/slow_fast_params.yaml`).
On our GPUs one arm of 200 videos takes about 10 GPU-hours.

`prep.py` refuses unfinished videos (a json sidecar without `frames_md5`), videos of different lengths, and a label
staged before from other videos. `collect.py` refuses a label with an unscored shard or a video without all 7
dimensions. VBench-Long computes the clip-to-clip parts on an mp4 of the clips' first frames, so rescoring a video can
change them slightly.

## Statistics

We pair each contrast by prompt: `compare.py` averages the per-prompt differences (x100) and bootstraps prompts
(4000 resamples, 95% percentile interval). One random stream with seed 0 runs through the contrasts in order, so a spec
in [`results/specs`](../../results/specs) reproduces our intervals exactly:

```bash
python eval/vbench_long/compare.py --spec results/specs/vbl60_seed0.json
```
