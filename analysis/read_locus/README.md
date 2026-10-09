# Read locus: where far history helps the denoising passes

[![Measured denoising-pass and layer effects](../../assets/mechanisms/read_locus.png)](../../assets/mechanisms/read_locus.pdf)

[Code-rendered figures, content controls and vector exports](../../assets/mechanisms/README.md).

Self-Forcing has no sink. With a KV cache of 160 latent frames (40 s) and a near window of 12, we read far
history (every 4th frame beyond the near window, +ln 4 mass) in exactly one (denoising pass, layer band) cell; every
other pass and layer, and the commit pass, read the newest 12 frames (routes `MM_*` of
[`analysis/sf_router`](../sf_router/README.md)). 20 prompts x seeds 0-2, 48 s; identity at 38-47.5 s (DINOv2) minus
that of `MM_R12` (no far read), share of videos with reduced motion in brackets (`MM_R12`: 0.17).

| Pass \ layers | 0-9 | 10-19 | 20-29 |
|---|---|---|---|
| s0 | +0.0125* (0.48) | +0.0051 (0.18) | +0.0023 (0.10) |
| s1 | +0.0127* (0.50) | +0.0123 (0.27) | +0.0031 (0.18) |
| s2 | +0.0208* (0.78) | +0.0037 (0.15) | +0.0261* (0.17) |
| s3 | +0.0121* (0.68) | +0.0225* (0.23) | **+0.0481*** (0.00) |

- s3 x layers 20-29 gets 41% of the gain of reading far history everywhere (`MM_ALL`: +0.1182*, reduced motion 0.52),
  without reducing motion: motion-adjusted +0.0526*, late / early saturation 0.233 below `MM_R12`, DiT time +7%.
- Layers 0-9 reduce motion in every pass (log motion ratio -0.22* to -0.40*); adjusted for motion, their gain is no longer
  significant (+0.0010 to +0.0146).
- Attention share does not explain the location: with far reads everywhere, the far anchors take about the same share
  of attention in every pass and layer band (0.54-0.61), with no peak in late passes or deep layers.
- The gain needs the old frames (Table 1). In `M4_*` the anchors keep their slots and +ln 4 mass, but hold other content.

**Table 1.** Identity vs `MM_R12`; region A = s3 x layers 20-29, region B = s2 and s3 x layers 20-29.

| Far anchors hold | A | B |
|---|---|---|
| old frames of this video | +0.0481* | +0.0581* |
| recent frames (near window) | -0.0012 | +0.0061 |
| statistics-matched random | -0.0154* | -0.0192* |
| temporal mean of the old frames | +0.0134 | +0.0164* |

**Table 2.** VBench-Long, rollf200 x 48 s, `MM_S3_L20_29` - `MM_R12` (x100), generation seeds 0 / 1: Quality -0.04
[-0.52, +0.34] / +0.04 [-0.46, +0.42], clip-to-clip subject +6.00* / +5.31*, clip-to-clip background +6.16* / +5.99*,
dynamic degree +7.58* / +10.04*, imaging quality -1.71* / -1.97*.

`*`: the 95% bootstrap interval over prompts excludes 0. `tables.py` prints all tables (with intervals, motion, reduced-motion
and saturation columns, DiT time and attention shares) from `data/`; `--vbench` adds Table 2 via
`eval/vbench_long/compare.py` and `specs/vbl48_seed{0,1}.json`.

```bash
for r in MM_R12 MM_ALL MM_S23 MM_S{0,1,2,3}_L{0_9,10_19,20_29} M4_A_{RECENT,RAND,MEAN} M4_B_{NORMAL,RECENT,RAND,MEAN}; do
  for s in 0 1 2; do python analysis/sf_router/generate.py --code third_party/sf_router --route $r \
      --prompts analysis/sf_router/prompts20.txt --seconds 48 --seed $s --out outputs/sf_router; done; done
# VBench-Long: MM_R12, MM_S3_L20_29 on eval/prompts/rollf200.txt, seeds 0, 1, then eval/vbench_long (prep, score, collect)
python analysis/read_locus/tables.py --vbench
```
