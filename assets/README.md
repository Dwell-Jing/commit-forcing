# Figures

Current manuscript figures are supplied as editable SVG, vector PDF, and PNG previews. Released PDFs and SVGs are byte-for-byte copies of the accepted manuscript exports; PNGs are rendered from those PDFs at 2200 pixels wide.

| Asset | Content | Portable source |
|:---|:---|:---|
| [`teaser.png`](teaser.png) | Historical-source overview and actual SGF native-12 versus current-plus-previous-6 example at 238 s | [`make_teaser.py`](source/make_teaser.py) |
| [`method.png`](method.png) | Committing from the current block and immediately preceding block, six latent frames in total | [`make_method.py`](source/make_method.py) |
| [`committing_tradeoff_variants.png`](committing_tradeoff_variants.png) | All 27 LongLive discovery variants relative to six-frame committing | [`make_committing_tradeoff_variants.py`](source/make_committing_tradeoff_variants.py) |
| [`qualitative_grid.png`](qualitative_grid.png) | Actual six-frame SGF and Context Forcing examples at 0, 120 and 238 s | [`make_qualitative_grid.py`](source/make_qualitative_grid.py) |

The adopted rule uses three current and three immediately preceding latent frames; the first block commits from current only. Base denoising and the cache update remain unchanged. The teaser's lower branch selects only the latest Recent block and Current, masking both older source cards. Its actual SGF_W6 image uses fixed prompt 0, seed 0 and 238 s; both arms share the recorded `[90,0,326,240]` display crop. [`teaser_inputs/source.json`](source/teaser_inputs/source.json) contains portable image hashes, layout and configuration details.

The qualitative grid uses fixed SGF prompt 19 and Context Forcing prompt 10, seed 0, at 0/120/238 s. SGF method images are actual SGF_W6 frames; baseline and Context Forcing cells retain their original bytes. Both method rows say “Recent-context”. Transparent yellow vector circles are visual guides. The cases were selected for readable differences and do not estimate average behavior; the Context Forcing case retains its negative per-video Quality result. The [portable frame list](source/qualitative_grid_inputs/source.json) contains no new per-case scores or private video paths. Previously released nine-frame SGF metadata and images remain separately [archived](archive/README.md).

The scatter shows 27 discovery variants on 100 prompts. Its dashed reference joins the six-frame origin and self-only endpoint `(+3.63, −1.00)`, measured on 200 prompts; it is not fitted to the discovery means. Open markers have a reported 95% G interval containing zero (22 variants); filled markers have an interval below zero (5). The graph does not establish a universal one-dimensional law. [Complete aggregate results, separate confirmation findings and costs](../analysis/committing_variants/README.md).

## Reproduction

Python dependencies are NumPy, Matplotlib, and Pillow. SVG/PDF export also uses `rsvg-convert` and `pdftoppm` (Poppler). Run from the repository root:

```bash
python assets/source/make_teaser.py
python assets/source/make_method.py
python assets/source/make_committing_content_age.py
python assets/source/make_committing_impulse.py
python assets/source/make_qualitative_grid.py
python assets/source/make_committing_tradeoff_variants.py
```

All runtime inputs are released relative paths under `assets/source/` or `analysis/committing_variants/`; no private manuscript files, videos or sidecars are required. Set `FIGURE_OUTPUT_DIR` to render into another directory. The teaser's PowerPoint hash is a historical layout reference only. Current SVG/PDF assets carry the actual six-frame example. Fonts and renderer versions can alter export metadata, PDF rasterization and SVG IDs. The teaser regenerates byte-for-byte in SVG and pixel-for-pixel in the PDF preview. The current Matplotlib 3.10.0 reproduction of plots exported with 3.10.8 preserves all reported coordinates, labels and vector geometry; minor raster differences are recorded in the manifest. Released files retain the original manuscript exports.

The recency renderer validates all 1,200 released per-video Subject c2c scores, including both sink controls, before drawing the ten finite-lag means. Sink remains a separate source control in the released data; it is not a numerical lag on the recency plot. The propagation renderer reads recorded means and prompt-bootstrap intervals from [`kv_propagation.csv`](source/kv_propagation.csv). The qualitative renderer verifies all twelve source-frame hashes and dimensions. The scatter renderer verifies all 27 points and the reported interval categories from the released aggregate record. No inference, rescoring, image generation, or retouching is performed by these scripts.

Hashes, dimensions, source mappings, and regeneration checks are recorded in [`manifest.json`](manifest.json) and the current `*.provenance.json` files. Colors are defined in [`paper_palette.py`](source/paper_palette.py), with plot/export settings in [`paper_style.py`](source/paper_style.py).

## Supplementary and historical assets

These assets retain their recorded protocols and configurations:

- [`committing_content_age.png`](committing_content_age.png): finite-lag SGF and LongLive Subject c2c results, with both sink controls retained in the released data. [Source](source/make_committing_content_age.py).
- [`committing_impulse.png`](committing_impulse.png), [`SVG`](committing_impulse.svg), and [`PDF`](committing_impulse.pdf): Appendix A.6's decaying K/V differences after a fixed-content committing intervention, with the self-only zero control. [Source](source/make_committing_impulse.py) and [complete supplementary study](../analysis/committing_propagation/README.md). The separate [KV construction control](../analysis/kv_construction/README.md) addresses the larger Quality and consistency losses.
- [`sgf_committing_controls.png`](sgf_committing_controls.png): committing-source read sets at equal frame count, and recent versus self-only. [Protocol and results](../analysis/sgf_committing_controls/README.md).
- [`commit_effects.png`](commit_effects.png): paired 60 s Quality and Subject c2c changes for two generation seeds. [Source](source/make_commit_effects.py).
- [`qualitative/`](qualitative/README.md): additional paired videos and frames, with historical configurations identified.
- [`mechanisms/`](mechanisms/README.md): independent distant-history denoising study, retaining positive and negative results.
- [`archive/`](archive/README.md): earlier multi-panel teaser.
