# Full VBench on long videos

We score VBench's standard prompt suite on 60 s videos: the 946 entries of `prompts/all_dimension.txt`, one video each,
all 16 dimensions with VBench-Long in mode `long_vbench_standard`, and Quality / Semantic / Total as VBench's
`scripts/cal_final_score.py` computes them. Results: [`results/vbench_full`](../../results/vbench_full/README.md).

## Prompts

Video i is generated from line i of VBench's Wan2.1 prompt extension,
`prompts/augmented_prompts/Wan2.1-T2V-1.3B/all_dimension_aug_wanx_seed42.txt` (Wan2.1's prompt-extension script with
Qwen2.5-3B-Instruct at seed 42, see `aug.md` next to it), and scored under the original prompt of line i. Both lists
ship with VBench; we keep no copy. Two prompts occur twice in the list (lines 495 / 748 and 503 / 746), so the suite
has 944 distinct prompts; each of the 946 videos is scored on the dimensions of its own line.

## Setup

VBench at `45e79ec` with its checkpoints, as for [VBench-Long](../vbench_long/README.md). The 9 semantic dimensions also
need detectron2 (for GRiT) and VBench's pinned transformers 4.33.2 and timm 1.0.12, which [`setup`](../../setup/README.md)
installs into the folder `semantic_pkgs`. Pass it as `SEMANTIC_PYTHONPATH`: `score.sh` prepends it to `PYTHONPATH` for
the semantic dimensions only, so the 7 quality dimensions run with the same packages as all our VBench-Long results. GRiT
loads the `bert-base-uncased` tokenizer by name; without internet access, put a copy into the VBench folder, where
`score.sh` runs.

## Steps

```bash
VB=VBench; AUG=$VB/prompts/augmented_prompts/Wan2.1-T2V-1.3B/all_dimension_aug_wanx_seed42.txt
# 1. 946 videos per arm, 60 s each, generation seed 0
python integrations/sgf/generate.py --code third_party/sgf --rule off --prompts $AUG --seconds 60 --seed 0 --out outputs/vbench_full/sgf
python integrations/sgf/generate.py --code third_party/sgf --rule on  --prompts $AUG --seconds 60 --seed 0 --out outputs/vbench_full/sgf
# 2. name the videos by VBench's prompts, split them once, cut 135 shards per arm
python eval/vbench_full/prep.py --vbench $VB --videos outputs/vbench_full/sgf/native/rule_off --label sgf --work vbs_work
python eval/vbench_full/prep.py --vbench $VB --videos outputs/vbench_full/sgf/native/rule_on --label sgf+rule --work vbs_work
# 3. score: one copy per GPU
for g in 0 1 2 3 4 5 6 7; do SEMANTIC_PYTHONPATH=semantic_pkgs bash eval/vbench_full/score.sh $VB vbs_work $g & done; wait
# 4. CSV files, then the contrast
python eval/vbench_full/collect.py --vbench $VB --work vbs_work --label sgf --scores scores.csv --shards shards.csv
python eval/vbench_full/collect.py --vbench $VB --work vbs_work --label sgf+rule --scores scores.csv --shards shards.csv --append
python eval/vbench_full/compare.py --scores scores.csv --shards shards.csv --pair sgf+rule:sgf
```

`prep.py` splits each video with VBench-Long's preprocess: 10 s clips for prompts of human_action, temporal_style or
overall_consistency, 2 s clips otherwise, no semantic splitting. It cuts each dimension into shards of about 10 prompts,
and refuses unfinished videos, videos not generated from their line, and a label staged before from other videos.
`score.sh` runs a shard through `run_eval_long.py`, VBench-Long's `eval_long.py` with one fix (see the file), with
`--dev_flag` as in all our VBench-Long results, one sample per prompt and VBench's static filter for temporal flickering.

## Statistics

A dimension score is VBench's: the overall score of each shard, weighted by the number of videos it scored. Quality is
the weighted mean of the 7 normalised quality dimensions (dynamic degree weight 0.5), Semantic the mean of the 9 normalised
semantic dimensions, Total = (4 Quality + Semantic) / 5, with the bounds of VBench's `scripts/constant.py`. A contrast
pairs the per-video scores by prompt. We draw 4000 multinomial resamples of the 944 distinct prompts once; every
dimension and the composite scores use these same resamples. Each spec in `results/vbench_full/specs` reproduces our
table exactly:

```bash
python eval/vbench_full/compare.py --spec results/vbench_full/specs/sgf.json
```
