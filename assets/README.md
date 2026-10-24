# Figures

The five current paper figures are supplied as editable SVG, vector PDF, and PNG previews. Released PDFs and SVGs are byte-for-byte copies of the current accepted manuscript figure exports. Every PNG is rendered from its released PDF at 2200 pixels wide.

| Asset | Content | Portable source |
|:---|:---|:---|
| [`teaser.png`](teaser.png) | Historical-source dependency overview and the original SGF base-12 versus recent-9 example at 238 s | [`make_teaser.py`](source/make_teaser.py) |
| [`method.png`](method.png) | Recent-Context Committing from the current block and immediately previous block, six latent frames in total | [`make_method.py`](source/make_method.py) |
| [`committing_content_age.png`](committing_content_age.png) | SGF and LongLive Subject c2c at tested history lags 1–16 blocks | [`make_committing_content_age.py`](source/make_committing_content_age.py) |
| [`committing_impulse.png`](committing_impulse.png) | Recorded K/V propagation after one fixed-content intervention, with the self-only zero control | [`make_committing_impulse.py`](source/make_committing_impulse.py) |
| [`qualitative_grid.png`](qualitative_grid.png) | Original SGF 9-frame source control and Context Forcing 6-frame method at 0, 120, and 238 s | [`make_qualitative_grid.py`](source/make_qualitative_grid.py) |

The adopted method includes three current and three immediately preceding latent frames; the first block commits from current only. Base denoising and cache update remain unchanged. Figure 4 is the compact computation diagram, with no alternative-window panel. Figure 1 remains the original base-12 versus recent-9 source-control example; it does not depict a new six-frame case. Its two original PNGs, common `[90, 0, 326, 240]` display crop, and accepted PowerPoint bracket/arrow coordinates are retained in [`teaser_inputs/source.json`](source/teaser_inputs/source.json).

The qualitative grid labels SGF “Recent (9 frames)” and Context Forcing “Recent-context”; the latter is the six-frame current-plus-previous method. Four transparent yellow vector circles with dark outlines highlight paired comparison regions. The twelve 416 × 240 source PNGs remain byte-for-byte unchanged. Selection and per-case scores are in [`qualitative_grid_inputs/source.json`](source/qualitative_grid_inputs/source.json), including the Context Forcing case’s negative Quality change.

## Reproduction

Python dependencies are NumPy, Matplotlib, and Pillow. SVG/PDF export also uses `rsvg-convert` and `pdftoppm` (Poppler). Run from the repository root:

```bash
python assets/source/make_teaser.py
python assets/source/make_method.py
python assets/source/make_committing_content_age.py
python assets/source/make_committing_impulse.py
python assets/source/make_qualitative_grid.py
```

All inputs are public relative paths under `assets/source/`; no manuscript sources or private filesystem paths are required. Set `FIGURE_OUTPUT_DIR` to render into another directory. The editable PowerPoint is a preserved layout reference, not a runtime dependency: its approved hash and accepted native-shape anchors are recorded with the teaser inputs. Fonts and renderer versions can change export metadata, PDF text metrics, and SVG object IDs. With the recorded figure environment, all five portable renderers produce PDF rasterizations pixel-identical to the released figures at 2200 pixels wide; teaser and method SVGs also regenerate byte-for-byte.

The recency renderer validates all 1,200 released per-video Subject c2c scores, including both sink controls, before drawing the ten finite-lag means. Sink remains a separate source control in the released data; it is not a numerical lag on the recency plot. The propagation renderer reads recorded means and prompt-bootstrap intervals from [`kv_propagation.csv`](source/kv_propagation.csv). The qualitative renderer verifies all twelve source-frame hashes and dimensions. No inference, rescoring, image generation, or retouching is performed by these scripts.

Hashes, dimensions, source mappings, and regeneration checks are recorded in [`manifest.json`](manifest.json) and the current `*.provenance.json` files. Colors are defined in [`paper_palette.py`](source/paper_palette.py), with plot/export settings in [`paper_style.py`](source/paper_style.py).

## Supplementary and historical assets

These assets retain their recorded protocols and configurations:

- [`sgf_committing_controls.png`](sgf_committing_controls.png): committing-source read sets at equal frame count, and recent versus self-only. [Protocol and results](../analysis/sgf_committing_controls/README.md).
- [`commit_effects.png`](commit_effects.png): paired 60 s Quality and Subject c2c changes for two generation seeds. [Source](source/make_commit_effects.py).
- [`qualitative/`](qualitative/README.md): additional paired videos and frames, with historical configurations identified.
- [`mechanisms/`](mechanisms/README.md): independent distant-history denoising study, retaining positive and negative results.
- [`archive/`](archive/README.md): earlier multi-panel teaser.
