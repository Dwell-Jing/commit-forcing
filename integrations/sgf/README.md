# Self Gradient Forcing

We pin [Self Gradient Forcing](https://arxiv.org/abs/2607.20368) at `github.com/zhuang2002/Self_Gradient_Forcing` commit `ba16e1b` (Apache-2.0) with its chunkwise checkpoint `checkpoints/chunkwise/ar/model.pt` (EMA weights) and Wan2.1-T2V-1.3B, in its streaming long-video mode. We ship only `commit_rule.patch`:

- `pipeline/causal_inference.py`: we mark the commit pass, the timestep-0 pass that writes each finished 3-frame block into the KV cache, and pass the denoising step index to the attention.
- `wan/modules/causal_model.py`: with Commit Forcing on, the commit pass reads only the cache slots of the newest W latent frames, at their usual RoPE positions. The sink and older frames stay in the cache for the 4 denoising passes, which we do not change.
- The same file adds an optional Recency Forcing reading (arXiv 2609.19729, App. B, training-free): a 21-frame cache and its TRB bias on history chunks, in the denoising passes only.

| `--reading` | cache the denoising passes read | commit pass, `--rule off` | commit pass, `--rule on` |
|---|---|---|---|
| `native` | sink 3 + FIFO 6 + current 3 latent frames, as in SGF | whole cache | newest 9 frames |
| `rf` | sink 3 + newest 18 frames, TRB | whole cache | newest 18 frames |

```bash
git clone https://github.com/zhuang2002/Self_Gradient_Forcing sgf && git -C sgf checkout ba16e1b
patch -d sgf -p1 < integrations/sgf/commit_rule.patch
(cd sgf && bash scripts/download_weights.sh)   # we use wan_models/Wan2.1-T2V-1.3B and checkpoints/chunkwise/ar/model.pt
A="--code sgf --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf"
python integrations/sgf/generate.py $A --reading native --rule off   # base SGF
python integrations/sgf/generate.py $A --reading native --rule on    # SGF + Commit Forcing
python integrations/sgf/generate.py $A --reading rf --rule off       # SGF + Recency Forcing reading
python integrations/sgf/generate.py $A --reading rf --rule on        # SGF + Recency Forcing reading + Commit Forcing
```

Videos go to `<out>/<reading>/rule_<off|on>/seed<seed>/<idx:03d>.mp4`. `generate.py` checks the activation counters it writes to each json; for a video of B blocks (B = 80 at 60 s) they are `commit_calls` = B; `rule_reads` = 30 B with the rule on (one per layer and commit pass, 2400 at 60 s), else 0; `trb_calls` = 120 (B - 3) with `--reading rf` (one per layer and denoising step from the fourth block on, 9240 at 60 s), else 0. The TRB needs flash-attn, which upstream installs. We used Python 3.11, torch 2.9.1 and flash-attn 2.8.3 on H20 GPUs.
