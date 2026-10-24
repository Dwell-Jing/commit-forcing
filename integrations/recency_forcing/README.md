# RF-TF: Self-Forcing + sink and Temporal Response Bias

We pin [Self-Forcing](https://github.com/guandeh17/Self-Forcing) at `33593df` with its published `checkpoints/self_forcing_dmd.pt` (EMA weights) and Wan2.1-T2V-1.3B, and give it a KV cache of 24 latent frames whose first 3 frames stay at its head as an attention sink. The denoising passes read the sink and the newest 18 frames (12 history + 3 recent + 3 current): once the cache holds frames in between, they are skipped and the sink's temporal RoPE is shifted so that it sits right before the oldest frame read. This is the training-free setting of Recency Forcing (App. B, [arXiv 2609.19729](https://arxiv.org/abs/2609.19729)), which we re-implement here.

| `--trb` | compatible `--reading` | `--rule` | the 4 denoising passes read | the commit pass reads |
|---|---|---|---|---|
| `off` | `native` | `off` | sink + newest 18 | sink + newest 18 |
| `off` | `native` | `on` | sink + newest 18 | newest 6 real frames |
| `on` | `rf` | `off` | sink + newest 18, with TRB | sink + newest 18 |
| `on` | `rf` | `on` | sink + newest 18, with TRB | newest 6 real frames |

`--trb on/off` and `--reading rf/native` are two names for the same choice. With a full cache, denoising reads 21
frames in total: the 3-frame sink and the newest 18 real frames. Recent-Context Committing (`--rule on`, default
`--commit-profile recent6`) reads the current clean 3-frame block and its immediately preceding block. The first
commit reads only its 3 available frames. We select post-RoPE keys and corresponding values without changing their
positions, the 24-frame physical cache, or denoising. The historical 21-frame control remains available with
`--commit-profile legacy21`; use a separate `--out` for it. `--rule off` preserves base behavior for either profile.

`--trb on` adds Recency Forcing's Temporal Response Bias (TRB) to the history chunks in the denoising passes: bias = -4 dt^γ(t), dt = min(1, max(0, d - 1) / 4), γ(t) = 0.1 · 2^t at step t = 1..4, with d the distance in 3-frame chunks from the current chunk; the sink and the recent and current chunks get no bias. We compute the biased attention exactly, with one flash-attention call per group of equal bias, merged by log-sum-exp.

## RF implementations

The main RF-TF result uses released SF DMD EMA weights and the training-free TRB reimplementation, without RF
training. RF-TF here is distinct from Rolling Forcing and its trained checkpoints. The SGF compatibility study and
alternative SF implementation use different cache geometry. The table preserves the historical wider controls
alongside the new main six-frame setting:

| Implementation | Weights | Physical cache | Denoising reads | Base committing | Recent-context committing | Temporal positions |
|---|---|---:|---|---|---|---|
| Main RF-TF | SF DMD EMA | 24 | sink 3 + trajectory 18 | sink 3 + trajectory 18 | trajectory 6; historical control 21 | absolute trajectory RoPE; sink shifted before the recent window |
| RF denoising on SGF | SGF chunkwise EMA | 21 | sink 3 + trajectory 18 | sink 3 + trajectory 18 | trajectory 6 by default; historical control 18 | `top_aligned`, positions 0–20; sink 0–2, steady-state trajectory 3–20 |
| Alternative RF on SF (`rf_v2`, historical) | SF DMD EMA | 21 | sink 3 + trajectory 18 | sink 3 + trajectory 18 | trajectory 18 | SGF cache implementation, same `top_aligned` geometry |

Every context count includes the current 3-frame block. All three apply TRB in denoising steps 0–3 and layers 0–29,
and **disable TRB during clean committing** at timestep 0. In step-index notation, the exponent is
`0.1 * 2**(s+1)` for `s = 0, 1, 2, 3`: 0.2, 0.4, 0.8, 1.6. The raw schedule `[1000, 750, 500, 250]` is shifted by 5
to approximately `[1000, 937.5, 833.33, 625]`. Sink, preceding block and current block have zero bias.

The 60-second alternative-SF comparison is 81.89 → 82.38 Quality on 200 rollf200 prompts, seed 0. The 120/240-second
RF + recent-context runs instead use the 24-frame implementation with the historical 21-frame committing context;
those long-horizon runs have no matched RF-only arm. They are separate from the new six-frame standard-suite result.
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

The sidecar also records `method: RF-TF`, `commit_profile`, and `commit_frames`. Events named `commit_read_3`,
`commit_read_6`, etc. count the actual post-RoPE committing reads. Generation checks every expected read count:
30 layer calls at 3 frames followed by 30 calls per block at 6 by default. Apply the current patch to a clean pinned
checkout before using this wrapper.
