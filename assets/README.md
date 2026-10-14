# Figures

| Asset | Content |
|:---|:---|
| `teaser.png`, `teaser.svg`, `teaser.pdf` | Current Figure 1: fixed denoising access, different committing contexts, one real paired SGF case |
| `method.png` | Method overview: one generated block, its denoising passes and its commit pass |
| `sgf_committing_controls.png`, `.svg`, `.pdf` | SGF committing-source controls: equal read count and recent versus self-only |
| `commit_effects.png`, `.svg`, `.pdf` | Paired Quality and clip-to-clip Subject changes at 60 s, for generation seeds 0 and 1 |
| [`mechanisms/`](mechanisms/README.md) | independent distant-history denoising study |
| [`qualitative/`](qualitative/README.md) | paired long rollouts, base model vs + Commit Forcing |

## Current teaser

The PNG is 2200 × 825. Its SHA256 is
`3723861b6d32cf155e972b510fa09e1202c59921235f37d58ee7d8bb1d723e3e`.
The two result frames are SGF prompt 0, generation seed 0, at 238 s of a 240 s rollout.
The sink/recent cards are editable source-role schematics; the photographs are unchanged generated result frames.
The shared denoising box represents a fixed access policy, rather than equal recurrent KV or generated blocks.

[Source and inputs](source/) · [asset hashes and provenance](manifest.json).
Rebuild the SVG, PDF and PNG with Python and `rsvg-convert`:

```bash
python assets/source/make_teaser.py
```

The earlier multi-panel teaser is retained in [archive/](archive/README.md). It includes independent denoising
and supplementary switching panels, which are no longer the paper's opening example.

## SGF committing controls

![SGF committing-source controls](sgf_committing_controls.png)

Each card is one latent frame's K/V. Filled cards are attended during committing; hatched historical cards remain
stored but are not directly attended. Panel (a) compares 3 sink + 3 recent + 3 current frames with 6 recent + 3
current frames: both read 9 frames. Panel (b) repeats the recent context and compares it with the current 3-frame
block alone. The two panels use the same source order and duplicate the recent read set exactly.

All contexts use the same 12-frame physical cache, base denoising policy and original KV positions. Current K/V is
computed from the clean block. The read sets depict the full-cache state after warmup; numerical outcomes remain
in the linked result tables.

[Results and protocol](../analysis/sgf_committing_controls/README.md) · [SVG](sgf_committing_controls.svg) ·
[PDF](sgf_committing_controls.pdf) · [figure provenance](sgf_committing_controls.provenance.json).
Rebuild from the public readout and protocol records with Python, `rsvg-convert` and `pdftoppm`:

```bash
python assets/source/make_sgf_committing_controls.py
```

## Paired committing effects

[PNG](commit_effects.png) · [SVG](commit_effects.svg) · [PDF](commit_effects.pdf) ·
[numerical provenance](commit_effects.provenance.json).

The two panels show Quality and clip-to-clip Subject Consistency changes from base committing on 200 `rollf200`
prompts at 60 seconds. Points distinguish generation seeds 0 and 1; horizontal lines are paired prompt-bootstrap
95% intervals. Both axes use score points. LongLive uses the six-frame committing window; the other six rows retain
their reported settings. These are VBench-Long custom-input results, separate from the common946 standard suite.

The renderer checks all 28 estimates and intervals against the paper's numerical record, using the public score CSV
and the ordered evaluation specs. Rebuild with Python, NumPy and Matplotlib:

```bash
python assets/source/make_commit_effects.py --check-only
python assets/source/make_commit_effects.py
```
