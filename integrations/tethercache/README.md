# TetherCache

This integration applies Commit Forcing to [TetherCache](https://github.com/my4f175/TetherCache) at upstream commit
`37c581ace23ff5df201f45e8282065d19b4ace8c`. A block contains 3 latent frames and runs 4 denoising passes, followed by a
timestep-0 commit pass that re-encodes the clean block and writes its K/V into the cache. Commit Forcing changes the
attention read of that commit pass once the 21-frame cache is full, starting with block 6 (zero based).

| `--memory` | `--rule` | Label in `results/` | Attention read of a full-cache commit |
|---|---|---|---|
| `tether` | `off` | `tethercache` | sink 3 + GRAB memory 14 + recent 4 |
| `tether` | `on` | `tethercache+rule` | recent 4, including the new 3-frame block |
| `fifo` | `off` | `tethercache_fifo` | sink 3 + newest 18 |
| `fifo` | `on` | `tethercache_fifo+rule` | newest 18 |

Both settings keep a 21-frame cache. Denoising passes use the upstream attention read, and TetherCache's GRAB selection,
TAME editing and RoPE positioning retain their upstream implementations. Changing the commit read changes subsequent
generation and can therefore change which frames GRAB admits. The patch marks the commit pass in
`pipeline/causal_inference.py` and restricts reads in `tethercache/patched_attention.py` and `wan/modules/causal_model.py`.

`generate.py` uses `TetherCacheConfig()` with its code defaults: budget 21, sink 3, memory 14, recent 4, GRAB
`alpha=0.35`, TAME `tau=0.35`, and `score_temperature=1.0`. The FIFO setting uses the same budget and sink without
installing GRAB or TAME. We load `generator_ema` from the Self-Forcing DMD checkpoint.

Setup from this repository's root, using the environment described in [setup/README.md](../../setup/README.md):

```bash
bash setup/fetch.sh tethercache
hf download Wan-AI/Wan2.1-T2V-1.3B \
    --local-dir third_party/tethercache/wan_models/Wan2.1-T2V-1.3B
hf download gdhe17/Self-Forcing checkpoints/self_forcing_dmd.pt \
    --local-dir third_party/tethercache
```

`fetch.sh` checks out the pinned upstream commit and applies `commit_rule.patch`. To prepare an existing checkout, check
out the full commit above and run `patch -d /path/to/TetherCache -p1 < integrations/tethercache/commit_rule.patch`.
The upstream package requires flash-attn for attention calls that use its original path; the tested environment uses
flash-attn 2.8.3. The default `--attn cudnn` routes eligible attention calls through PyTorch SDPA with cuDNN first and
PyTorch flash attention second (`sdpa_kernel(..., set_priority=True)`). Use the tested torch 2.9.1 environment for this
API. `--attn flash` selects the upstream flash-attn path; our results use `cudnn`.

Generate TetherCache with Commit Forcing:

```bash
python integrations/tethercache/generate.py \
    --code third_party/tethercache --memory tether --rule on --attn cudnn \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 \
    --out outputs/tethercache
```

`--ckpt` defaults to `<code>/checkpoints/self_forcing_dmd.pt`. Videos and JSON sidecars go to
`<out>/<memory>/rule_<on|off>/seed<seed>/<idx:03d>.{mp4,json}`. The sidecar records the prompt, RNG seed, attention
option, checkpoint, lengths, wall time, raw-frame MD5, motion measurements and activation counters. Finished videos
with the same settings are skipped; `--overwrite` regenerates them. Video length must be a multiple of 0.75 s (one 3-latent-frame block).

For `B` blocks and 30 attention layers, the runner checks `commit_calls = B`. With Commit Forcing on,
`rule_reads = 30 * max(0, B - 6)` and `frames_read` is that count times 4 (`tether`) or 18 (`fifo`); both counters are
zero without it. For TetherCache, admissions plus rejections equal `3 * 30 * max(0, B - 7)`, edits equal
admissions, and a video that reaches GRAB must admit at least one frame. A mismatch stops generation.
