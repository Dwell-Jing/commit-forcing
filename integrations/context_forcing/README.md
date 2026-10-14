# Context Forcing

We pin [Context Forcing](https://arxiv.org/abs/2602.06028) at `github.com/chenshuo20/Context-Forcing` commit `9ba918d`, with the published student `ShuoChen20/context_forcing/model.pt` (Hugging Face revision `d44ae93b`) and Wan2.1-T2V-1.3B. Context Forcing is licensed CC BY-NC-SA 4.0, so we ship only `commit_rule.patch` (same license), no upstream files.

Its KV cache holds 21 latent frames: a 3-frame sink, a slow memory of up to 12 promoted keyframe copies, and a 6-frame fast window (the previous block and the block being written). After each 3-frame block is denoised, the commit pass re-encodes the clean block at timestep 0 and writes its K/V. We change only the cache rows the commit pass reads; the 4 denoising passes, the cache writes and the keyframe promotion run unchanged. The arms first differ at the commit of block 2, where the sink leaves the fast window and the first slow-memory copies can sit in it.

| `--rule` | the commit pass reads | frames in steady state |
|---|---|---|
| `off` | sink + slow memory + fast window (base) | 21 |
| `on` | the fast window only, without slow-memory copies that still sit in it | 6 |
| `sink-only` | everything but the sink (ablation) | 18 |
| `memory-only` | everything but the slow memory and the older frames: sink + fast window (ablation) | 9 |

```bash
cp -r Context-Forcing cf && patch -d cf -p1 < integrations/context_forcing/commit_rule.patch
# add cf/wan_models/Wan2.1-T2V-1.3B and cf/checkpoints/model.pt as in their README
python integrations/context_forcing/generate.py --code cf --rule on --prompts eval/prompts/rollf200.txt \
    --ids 0-199 --seconds 60 --seed 0 --out outputs/context_forcing
```

Videos go to `<out>/rule_<off|on|sink-only|memory-only>/seed<seed>/<idx:03d>.mp4`. The json counters are summed over the 30 layers: `commit_passes` (one per block), `frames_cached` (what the base commit pass reads), `frames_read`, `sink_frames_dropped`, `memory_frames_dropped` (slow memory and older frames), `frames_read_last_commit` (per layer: 21 / 6 / 18 / 9), and `slow_memory_frames` per layer at the end. `--attn cudnn` (default, all our results) runs attention through PyTorch SDPA with the cuDNN backend; `--attn flash` keeps their flash-attn path. We used Python 3.11, torch 2.9.1 and flash-attn 2.8.3 on H20 GPUs.
