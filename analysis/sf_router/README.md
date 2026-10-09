# KV router for Self-Forcing

Self-Forcing generates a video in blocks of 3 latent frames. Each block runs 4 denoising passes (`s0`-`s3`, timesteps
1000 / 937.5 / 833.3 / 625) and one commit pass (`c`), which re-encodes the clean block at timestep 0 and writes its keys
and values into the KV cache. `router.patch` (against [Self-Forcing](https://github.com/guandeh17/Self-Forcing) @33593df)
passes the name of the pass to every self-attention layer and adds `wan/modules/kv_router.py`. A route sets, for each
pass and layer, the window (how many of the newest cached frames the layer reads, the block itself included) and how
the frames older than the near window are read:

- `dense`: every frame of the window (the upstream reading, with a different window);
- `anchors`: the near window in full and, beyond it, the newest of every 4 older frames (far anchors), merged with the
  near part by log-sum-exp after raising the far log-mass by ln 4. A window of at most near + 4 frames is read densely.

Every route keeps a KV cache of 160 latent frames (40 s) and no sink.

| Routes | Model | Far history (beyond the near window) is read | Commit pass reads | Used in |
|---|---|---|---|---|
| `R12` | Self-Forcing | nowhere | newest 12 | commit switch |
| `R160` | Self-Forcing | dense, newest 160, in every pass | newest 160 | commit switch |
| `S0`, `S1`, `S2`, `S3`, `S23` | Self-Forcing | dense, newest 160, in that pass (`S23`: s2 and s3) | newest 12 | commit switch |
| `S123R` (`S123`) | Self-Forcing | dense, newest 160, in s1-s3 | newest 12 | commit switch |
| `S123C` | Self-Forcing | dense, newest 160, in s1-s3 | newest 160 | commit switch |
| `C` | Self-Forcing | nowhere in the denoising passes | newest 160 | commit switch |
| `SWCR`, `SWRC` | Self-Forcing | dense, newest 160, in s1-s3 | 160 in blocks 0-31 (0-24 s), then 12 / the reverse | commit switch |
| `G3_R21` | Self-Forcing | nowhere; every pass reads the newest 21 frames (the base model for long videos) | newest 21 | `sf` in [`results`](../../results/README.md) |
| `G3_L12_29` | Self-Forcing | anchors in s2 and s3, layers 12-29 | newest 12 | `sf+far_denoise` in `results` |
| `MM_R12` | Self-Forcing | nowhere | newest 12 | read locus |
| `MM_S{s}_L0_9`, `_L10_19`, `_L20_29` | Self-Forcing | anchors in pass s{s}, one layer band (12 routes) | newest 12 | read locus |
| `MM_S23`, `MM_ALL` | Self-Forcing | anchors in s2 and s3 / in s0-s3, all layers | newest 12 | read locus |
| `M4_A_*`, `M4_B_*` | Self-Forcing | anchors in s3 (A) or s2 and s3 (B), layers 20-29, with content `NORMAL` / `RECENT` / `RAND` / `MEAN` | newest 12 | read locus |

Anchor content: `RECENT` fills the anchor slots with the near-window frames (no old content), `RAND` with Gaussian keys
and values that match the anchors' per-channel mean and standard deviation (no content), `MEAN` with the mean anchor
(old content without temporal detail). `python analysis/sf_router/generate.py --list-routes` prints every route with
its windows.

```bash
git clone https://github.com/guandeh17/Self-Forcing.git third_party/sf_router
git -C third_party/sf_router checkout 33593df
git -C third_party/sf_router apply "$PWD/analysis/sf_router/router.patch"
# checkpoints/self_forcing_dmd.pt and wan_models/Wan2.1-T2V-1.3B as in the Self-Forcing README
python analysis/sf_router/generate.py --code third_party/sf_router --route S123C \
    --prompts analysis/sf_router/prompts20.txt --ids 0-19 --seconds 48 --seed 0 --out outputs/sf_router
```

Videos go to `<out>/<route>/seed<seed>/<idx:03d>.mp4` with a `.json` holding the route, the router counters (generator
calls and layer windows per pass, far reads per pass, the kept share of far tokens, the attention share of the anchors
per pass and layer, the commit-pass window of every block, anchor replacements), the DiT time per block and the
`motion_early_4_8` / `motion_late_38_47` of the decoded video. `prompts20.txt` holds the 20 prompts of both studies
(48 s, seeds 0-2). The noise of prompt i under seed s comes from `torch.manual_seed(s * 100003 + i)`. On one H20 a
48 s video takes 2 (`R12`) to 9 (`R160`) minutes. We used Python 3.11, torch 2.9.1 and flash-attn 2.8.3.
