# Figures

The current figures below match the local manuscript snapshot of 2026-10-30. Their PDF and SVG files are exact copies of those manuscript exports; each PNG is rendered from the released PDF at 2200 pixels wide. This snapshot is separate from the earlier Overleaf revision.

| Asset | Content | Portable source |
|:---|:---|:---|
| [`teaser.png`](teaser.png) | Shared denoising, two committing contexts, and the fixed SGF example at 238 s | [`make_teaser.py`](source/make_teaser.py) |
| [`method.png`](method.png) | Common denoising and recurrent committing dependencies for Base, Self-only, and Commit Forcing | [`make_method.py`](source/make_method.py) |
| [`qualitative_grid.png`](qualitative_grid.png) | SGF and Context Forcing cases at 0, 120, and 238 s | [`make_qualitative_grid.py`](source/make_qualitative_grid.py) |
| [`committing_content_age.png`](committing_content_age.png) | Ten finite-lag Subject c2c means for SGF and LongLive | [`make_committing_content_age.py`](source/make_committing_content_age.py) |
| [`committing_window_mechanisms.png`](committing_window_mechanisms.png) | LongLive Subject c2c against the number of preceding committing blocks | [`make_committing_window_mechanisms.py`](source/make_committing_window_mechanisms.py) |
| [`committing_tradeoff_variants.png`](committing_tradeoff_variants.png) | All 27 LongLive discovery variants at their reported coordinates | [`make_committing_tradeoff_variants.py`](source/make_committing_tradeoff_variants.py) |
| [`committing_correction_controls.png`](committing_correction_controls.png) | Four spatial-averaging controls, with three retained fractions per arm | [`make_committing_correction_controls.py`](source/make_committing_correction_controls.py) |
| [`committing_recurrence.png`](committing_recurrence.png) | Fixed-latent layer/lag maps, sink responses, and one-pass sink-read responses | [`make_committing_recurrence.py`](source/make_committing_recurrence.py) |

Commit Forcing reads three current and three immediately preceding latent frames during committing; the first block uses current only. Base denoising and cache updates are retained. The method diagram keeps the stored sink visible while crossing out its direct committing access for Self-only and Commit Forcing. Its arrows depict dependencies across separate committing calls, rather than identical generated latents across methods.

The teaser labels the selected inputs **Previous KV** and **Clean block**. Its photographs use SGF prompt 0, seed 0, at 238 s: the native-12 example shows a white jacket and the actual six-frame method example shows a black jacket. Both use the same `[90,0,326,240]` crop of the archived 416×240 frame. The [input record](source/teaser_inputs/source.json) contains image hashes and layout details.

The qualitative grid uses SGF prompt 19 and Context Forcing prompt 10, seed 0, at 0/120/238 s. All twelve embedded photographs retain their archived bytes. Yellow circles are vector annotations; the Context Forcing case retains its negative per-video Quality result. The [frame list](source/qualitative_grid_inputs/source.json) records the fixed cases. Earlier nine-frame SGF images and metadata remain [archived](archive/README.md).

The main committing-window figure now shows one absolute Subject c2c curve: h=0/1/2/3 gives 86.21/87.21/87.23/86.93 on 200 rollf200 prompts, 60 s, seed 0. Here h counts preceding blocks, excluding the current block. The dashed Base reference is 86.01 and reads sink 3 plus latest 9 trajectory frames including current 3, with 15-frame physical storage. It is a separate configuration, rather than an h=4 point. The [window record](../analysis/window_effects/README.md) retains the paired comparisons.

The separate appendix controls show twelve bars: retained correction magnitude, consistency gain, and motion suppression for frame averaging, a 4×4 grid, and 16/64 content regions. The correction is measured before the attention output projection. Outcomes use 100 prompts; normalization uses the reported 200-prompt self-only/current-plus-previous endpoints. All fractions, including SG16's 0.42 consistency and 0.61 motion-suppression retention, are preserved. These controls change spatial structure as well as magnitude.

The new recurrence study uses fixed clean latents and reported aggregate layer/lag matrices and curves. Its inputs contain no latent tensors, KV tensors, videos, or per-prompt records. It is separate from the earlier SGF nine-frame [impulse study](../analysis/committing_propagation/README.md), whose original figure remains available below. See the [recurrence protocol](../analysis/committing_recurrence/README.md).

## Reproduction

Python dependencies are NumPy, Matplotlib, and Pillow. Vector export also uses `rsvg-convert` and `pdftoppm` (Poppler). Run from the repository root:

```bash
python assets/source/make_teaser.py
python assets/source/make_method.py
python assets/source/make_qualitative_grid.py
python assets/source/make_committing_content_age.py
python assets/source/make_committing_window_mechanisms.py
python assets/source/make_committing_tradeoff_variants.py
python assets/source/make_committing_correction_controls.py
python assets/source/make_committing_recurrence.py
```

Runtime inputs use released relative paths under `assets/source/` and aggregate records under `analysis/`. Set `FIGURE_OUTPUT_DIR` to render elsewhere. The teaser's PowerPoint hash identifies a historical layout reference and is not a runtime dependency. The renderers retain the reported values and archived photographs without generation or rescoring.

The method and teaser reproduce the canonical SVG bytes. For the Matplotlib figures, the complete SVG geometry, text, styles, and embedded images match after normalizing generated IDs and metadata. This was checked with Matplotlib 3.10.8 for the updated plots and 3.10.0 for recurrence. Renderer and font versions can affect metadata, text metrics, and rasterization. The released PDF/SVG files retain the manuscript exports.

Hashes, dimensions, source mappings, and checks are recorded in [`manifest.json`](manifest.json) and each figure's provenance file. Colors are defined in [`paper_palette.py`](source/paper_palette.py); measured plots use [`paper_style.py`](source/paper_style.py).

## Historical and additional assets

These retain their original protocols and source records:

- [`committing_impulse.png`](committing_impulse.png), [`SVG`](committing_impulse.svg), and [`PDF`](committing_impulse.pdf): the earlier SGF nine-frame fixed-content committing intervention, including its self-only zero control. [Source](source/make_committing_impulse.py) and [study](../analysis/committing_propagation/README.md).
- [`committing_correction_dose.png`](committing_correction_dose.png), [`SVG`](committing_correction_dose.svg), and [`PDF`](committing_correction_dose.pdf): the original standalone plot of four averaging arms and eight effect points. Its `y=x` line is an equal-fraction reference. [Source](source/make_committing_correction_dose.py).
- [`sgf_committing_controls.png`](sgf_committing_controls.png): committing-source read sets at equal frame count, and recent versus self-only. [Protocol](../analysis/sgf_committing_controls/README.md).
- [`commit_effects.png`](commit_effects.png): paired 60 s Quality and Subject c2c changes for two generation seeds. [Source](source/make_commit_effects.py).
- [`qualitative/`](qualitative/README.md): additional paired videos and frames, with historical configurations identified.
- [`mechanisms/`](mechanisms/README.md): the independent distant-history denoising study, retaining positive and negative results.
- [`archive/`](archive/README.md): earlier teaser assets.
