# Figures

The six figures updated on November 9, 2026 are listed below. The PDF and SVG files preserve the figure exports, and each PNG is rendered from its PDF at 2200 pixels wide.

| Asset | Content | Downloads |
|:---|:---|:---|
| [`teaser.png`](teaser.png) | Shared denoising policy, two committing contexts, and the fixed SGF example at 238 s | [PDF](teaser.pdf) · [SVG](teaser.svg) |
| [`method.png`](method.png) | Denoising and committing dependencies for Base, Self-only, and Commit Forcing | [PDF](method.pdf) · [SVG](method.svg) |
| [`qualitative_grid.png`](qualitative_grid.png) | SGF and Context Forcing cases at 0, 120, and 238 s | [PDF](qualitative_grid.pdf) · [SVG](qualitative_grid.svg) |
| [`committing_content_age.png`](committing_content_age.png) | Ten finite-lag Subject c2c means for SGF and LongLive | [PDF](committing_content_age.pdf) · [SVG](committing_content_age.svg) |
| [`committing_window_mechanisms.png`](committing_window_mechanisms.png) | LongLive Subject c2c by the number of preceding committing blocks | [PDF](committing_window_mechanisms.pdf) · [SVG](committing_window_mechanisms.svg) |
| [`gain_over_time.png`](gain_over_time.png) | Paired DINOv2 similarity gains to the opening window | [PDF](gain_over_time.pdf) · [SVG](gain_over_time.svg) |

Commit Forcing uses three current latent frames and the stored KV from the immediately preceding three frames during committing. The first block uses only its current latents. In the method diagram, crosses mark entries excluded from direct committing access. Green marks the KV produced at block *b* and read when committing block *b* + 1.

The teaser compares native 12-frame SGF committing with six-frame Commit Forcing. The paired frames come from SGF prompt 0 with seed 0, at 238 s. Each uses the same `[90,0,326,240]` crop from its 416×240 frame. [Input hashes](source/teaser_inputs/source.json)

The qualitative grid uses SGF prompt 19 and Context Forcing prompt 10, seed 0, at 0, 120, and 238 s. Yellow circles mark visual differences. The Context Forcing case has a negative per-video Quality result. [Frame list](source/qualitative_grid_inputs/source.json) · [Earlier nine-frame SGF cases](archive/README.md)

LongLive Subject c2c is 86.21, 87.21, 87.23, and 86.93 with zero to three preceding blocks, respectively, on 200 rollf200 prompts at 60 s with seed 0. Each context also includes the current block. The dashed line shows Base at 86.01. Base reads three sink frames and the latest nine trajectory frames, including the current three, in a 15-frame physical cache. [Paired comparisons](../analysis/window_effects/README.md)

The separate appendix controls show twelve bars: retained correction magnitude, consistency gain, and motion suppression for frame averaging, a 4×4 grid, and 16/64 content regions. The correction is measured before the attention output projection. Outcomes use 100 prompts; normalization uses the reported 200-prompt self-only/current-plus-previous endpoints. All fractions, including SG16's 0.42 consistency and 0.61 motion-suppression retention, are preserved. These controls change spatial structure as well as magnitude.

The gain-over-time plot shows the paired difference in DINOv2 similarity between each five-second window and the opening window, scaled by 100. The shaded bands show 95% prompt-bootstrap intervals and the dashed lines mark training horizons. [Protocol and results](../RESULTS.md#gain-over-time)

## Reproduction

The portable scripts and provenance for the teaser, method, qualitative grid, content age, and window figures describe the October 30 layouts. The November 9 layouts and gain-over-time plot are provided as frozen exports. Python dependencies are NumPy, Matplotlib, and Pillow. Vector export also uses `rsvg-convert` and `pdftoppm` (Poppler). Set `FIGURE_OUTPUT_DIR` to render into a separate directory.

```bash
FIGURE_OUTPUT_DIR=figure-build python assets/source/make_method.py
```

The manifest records current export hashes and previous renderer checks. The scripts render the archived figures' data and photographs from `assets/source/` and `analysis/`. [Manifest](manifest.json) · [Portable sources](source/)

## Historical and additional assets

These retain their original protocols and source records:

- [`committing_tradeoff_variants.png`](committing_tradeoff_variants.png): all 27 LongLive discovery variants at their reported coordinates. [Source](source/make_committing_tradeoff_variants.py).
- [`committing_correction_controls.png`](committing_correction_controls.png): four spatial-averaging controls with three retained fractions per arm. [Source](source/make_committing_correction_controls.py).
- [`committing_recurrence.png`](committing_recurrence.png): fixed-latent layer/lag maps, sink responses, and one-pass sink-read responses. [Protocol](../analysis/committing_recurrence/README.md) · [Source](source/make_committing_recurrence.py).
- [`committing_impulse.png`](committing_impulse.png), [`SVG`](committing_impulse.svg), and [`PDF`](committing_impulse.pdf): the earlier SGF nine-frame fixed-content committing intervention, including its self-only zero control. [Source](source/make_committing_impulse.py) and [study](../analysis/committing_propagation/README.md).
- [`committing_correction_dose.png`](committing_correction_dose.png), [`SVG`](committing_correction_dose.svg), and [`PDF`](committing_correction_dose.pdf): the original standalone plot of four averaging arms and eight effect points. Its `y=x` line is an equal-fraction reference. [Source](source/make_committing_correction_dose.py).
- [`sgf_committing_controls.png`](sgf_committing_controls.png): committing-source read sets at equal frame count, and recent versus self-only. [Protocol](../analysis/sgf_committing_controls/README.md).
- [`commit_effects.png`](commit_effects.png): paired 60 s Quality and Subject c2c changes for two generation seeds. [Source](source/make_commit_effects.py).
- [`qualitative/`](qualitative/README.md): additional paired videos and frames, with historical configurations identified.
- [`mechanisms/`](mechanisms/README.md): the independent distant-history denoising study, retaining positive and negative results.
- [`archive/`](archive/README.md): earlier teaser assets.
