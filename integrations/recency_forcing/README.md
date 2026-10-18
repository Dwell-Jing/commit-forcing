# Self-Forcing + sink, with and without the Recency Forcing reading

We pin [Self-Forcing](https://github.com/guandeh17/Self-Forcing) at `33593df` with its published `checkpoints/self_forcing_dmd.pt` (EMA weights) and Wan2.1-T2V-1.3B, and give it a KV cache of 24 latent frames whose first 3 frames stay at its head as an attention sink. The denoising passes read the sink and the newest 18 frames (12 history + 3 recent + 3 current): once the cache holds frames in between, they are skipped and the sink's temporal RoPE is shifted so that it sits right before the oldest frame read. This is the training-free setting of Recency Forcing (App. B, [arXiv 2609.19729](https://arxiv.org/abs/2609.19729)), which we re-implement here.

| `--trb` | compatible `--reading` | `--rule` | the 4 denoising passes read | the commit pass reads |
|---|---|---|---|---|
| `off` | `native` | `off` | sink + newest 18 | sink + newest 18 |
| `off` | `native` | `on` | sink + newest 18 | newest 21 real frames, no sink |
| `on` | `rf` | `off` | sink + newest 18, with TRB | sink + newest 18 |
| `on` | `rf` | `on` | sink + newest 18, with TRB | newest 21 real frames, no sink |

`--trb on/off` and `--reading rf/native` are two names for the same choice. With a full cache, denoising reads 21 frames in total: the 3-frame sink and the newest 18 real frames. `--rule on` gives the commit pass 21 real frames instead, including the current 3-frame block; its 18 history frames occupy the full budget without the sink. During warmup, each pass reads the available frames up to its budget.

`--trb on` adds Recency Forcing's temporal recency bias (TRB) to the history chunks in the denoising passes: bias = -4 dt^γ(t), dt = min(1, max(0, d - 1) / 4), γ(t) = 0.1 · 2^t at step t = 1..4, with d the distance in 3-frame chunks from the current chunk; the sink and the recent and current chunks get no bias. We compute the biased attention exactly, with one flash-attention call per group of equal bias, merged by log-sum-exp.

## RF implementations

The main RF-TF result uses released SF DMD EMA weights, without RF training. The SGF compatibility study and
alternative SF implementation use different cache geometry:

| Implementation | Weights | Physical cache | Denoising reads | Base committing | CF committing | Temporal positions |
|---|---|---:|---|---|---|---|
| Main RF-TF | SF DMD EMA | 24 | sink 3 + trajectory 18 | sink 3 + trajectory 18 | trajectory 21 | absolute trajectory RoPE; sink shifted before the recent window |
| RF denoising on SGF | SGF chunkwise EMA | 21 | sink 3 + trajectory 18 | sink 3 + trajectory 18 | trajectory 18 | `top_aligned`, positions 0–20; sink 0–2, steady-state trajectory 3–20 |
| Alternative RF on SF (`rf_v2`) | SF DMD EMA | 21 | sink 3 + trajectory 18 | sink 3 + trajectory 18 | trajectory 18 | SGF cache implementation, same `top_aligned` geometry |

Every context count includes the current 3-frame block. All three apply TRB in denoising steps 0–3 and layers 0–29,
and **disable TRB during clean committing** at timestep 0. In step-index notation, the exponent is
`0.1 * 2**(s+1)` for `s = 0, 1, 2, 3`: 0.2, 0.4, 0.8, 1.6. The raw schedule `[1000, 750, 500, 250]` is shifted by 5
to approximately `[1000, 937.5, 833.33, 625]`. Sink, preceding block and current block have zero bias.

The 60-second alternative-SF comparison is 81.89 → 82.38 Quality on 200 rollf200 prompts, seed 0. The 120/240-second
RF + CF runs instead use the main 24-frame implementation; those long-horizon runs have no matched RF-only arm.
The SGF [compatibility table](../../RESULTS.md#sgf-rf-compatibility) separates fixed-storage committing contrasts
from comparisons that also change denoising and storage.

```bash
bash setup/fetch.sh recency_forcing   # Self-Forcing at 33593df in third_party/recency_forcing, patch applied
cd third_party/recency_forcing        # weights as in the Self-Forcing README
huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir-use-symlinks False --local-dir wan_models/Wan2.1-T2V-1.3B
huggingface-cli download gdhe17/Self-Forcing checkpoints/self_forcing_dmd.pt --local-dir . && cd ../..
python integrations/recency_forcing/generate.py --code third_party/recency_forcing --trb on --rule on \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/recency_forcing
```

Videos go to `<out>/reading_<native|rf>/rule_<off|on>/seed<seed>/<idx:03d>.mp4`: `--trb off` maps to `reading_native` and `--trb on` to `reading_rf`. The JSON sidecar records `reading: native/rf`. The json counters count attention calls (30 layers × blocks) per pass (`step0`-`step3`, `commit`): `sink_shifted` (the sink read at its shifted position), `sink_in_place` (cache not full yet, the sink read where it is), `recency_bias` (TRB applied) and `commit_rule` (the commit pass left the sink out). We used Python 3.11, torch 2.9.1 and flash-attn 2.8.3 on H20 GPUs.
