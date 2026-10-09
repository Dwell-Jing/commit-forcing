# Per-video metrics

`compute.py` computes the per-video metrics of the mechanism analyses from the videos: identity, color and detail drift,
and motion. It writes one CSV row per video. The columns carry the key names of our per-video data, and the
`data/*.csv` files of the analysis folders use the same names.

```bash
python analysis/metrics/compute.py outputs/longlive/rule_on outputs/longlive/rule_off --out metrics.csv \
    --dino facebook/dinov2-base --clip openai/clip-vit-large-patch14 --workers 8
```

It reads `<root>/<arm>/seed<s>/<i:03d>.mp4` (the layout of `common/runner.py`) and `<root>/<arm>_seed<s>.vid/<i>-0_ema.mp4`;
a row starts with `root`, `arm`, `seed`, `prompt`, `video` and `frames`. Identity compares the seeds of a prompt within
an arm, so we pass every seed of an arm in one call. The windows set the sampled frames and their batches; to reproduce
a readout that used only early and late, we pass `--windows early_4_8:4-8,late_38_47:38-47.5`.

| Columns | Definition |
|---|---|
| `dino_early_4_8`, `dino_mid_20_26`, `dino_late_38_47` | Identity at 4-8 s, 20-26 s and 38-47.5 s. We embed frames with DINOv2 ViT-B/14 (`facebook/dinov2-base`, float32, CLS token, L2-normalized; image processor: shorter side 256 bicubic, center crop 224). The opening is the mean embedding of the frames at 0.5, 0.75, ..., 1.75 s; a window is the mean of 6 frames evenly spaced from its start to min(end, video end - 0.4 s); both means are renormalized. Identity = cos(window, own opening) - mean over the other seeds of the same prompt and arm of cos(window, their opening): the prompt cancels, what is left is specific to the run. |
| `clip_early_4_8`, ... | The same with CLIP ViT-L/14 projected image embeddings (`--clip`; shorter side 224 bicubic, center crop 224). The findings use DINOv2. |
| `sat_t`, `con_t`, `det_t`, `bri_t` | Drift series, t = 0, 1, ... s. On every 2nd frame at half resolution (every 2nd row and column), RGB in [0, 1]: saturation = mean HSV S, contrast = std of the luma Y = 0.299R + 0.587G + 0.114B, detail = mean absolute 4-neighbour Laplacian of Y, brightness = mean Y. Second t averages frames 16t to 16t + 15; the last second also takes every later frame. |
| `sat_le`, `con_le`, `det_le`, `bri_le` | Mean of seconds 38-47 over mean of seconds 4-7. |
| `motion_early_4_8`, `motion_late_38_47` | Mean absolute difference between consecutive frames over all pixels and channels, in 0-255 units, for frames t = 65-127 (4-8 s) and t = 609-759 (38-47.5 s). Computed on the decoded frames before the mp4 is written, as the json sidecars of the research generators carry it; `compute.py` copies it from the sidecar when present. `motion()` in `compute.py` is the generators' function. |
| `motion_early_4_8_mp4`, `motion_late_38_47_mp4` | The same on the frames decoded from the mp4. H.264 lowers it by 2-7% on average. |

Quantities derived from these columns:
- Retention (`ret`): mean late identity over mean early identity of an arm.
- Relative drift: a video's series divided by its own 4-8 s mean, r(t) = x(t) / mean(x_4, ..., x_7). Arms compare by
  Δ(t) = r_A(t) - r_B(t) per cell; early = seconds 8-15, late = seconds 38-47, slope per 10 s by least squares per cell.
- Reduced motion: `motion_late_38_47 / motion_early_4_8 < 0.85`. Motion change: the log of this ratio; a change of x% is
  exp(mean Δ log ratio) - 1; `m_med` = exp(median log ratio).

## Comparing arms

- A cell is a (prompt, seed) pair. Arms are compared on the cells they share, by per-cell differences A - B. Identity
  needs at least 2 seeds of the prompt. The reduced-motion share, retention and `m_med` are per arm over these cells.
- 95% CI: prompt-level bootstrap with 4000 resamples from `np.random.default_rng(0)`. A resample draws as many prompts
  as there are, with replacement, and takes every cell (all seeds) of each drawn prompt:
  `boot = [np.concatenate([np.where(prom == p)[0] for p in rng.choice(up, len(up))]) for _ in range(4000)]`, with `prom`
  the prompt of each cell and `up = np.unique(prom)`. The CI is the 2.5 and 97.5 percentiles of the resampled mean; `*`
  marks a CI that excludes 0. All contrasts on one cell set share these resamples. The drift readouts draw the sets of
  successive cell sets from one generator, in order of first use.
- Motion adjustment (ANCOVA): across cells, least squares Δidentity = a + b Δlog(motion ratio). We report a, the identity
  difference at equal motion change; its CI refits a on each resample.

The generators also record quantities that do not come from the videos: `dit_ms_per_block` and `wall_s` (cost),
activation counters, and in `*.mm.json` the attention share of far history per denoising step and layer (`far_mass`).
`compute.py` does not compute them.

`--fast-processor` switches to the torchvision image processors, which change identity by up to 1.5e-3.
