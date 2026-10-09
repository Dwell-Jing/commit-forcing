# SGF: a base with a sink does not use history outside its window

Self Gradient Forcing (SGF) keeps a 3-frame sink in its cache. We run SGF with the Recency Forcing reading (cache: 3
sink frames + newest 18 latent frames; TRB bias in the denoising passes) and Commit Forcing; this is arm `SGF_RFW`. In
a far read, layers 20-29 also read, in the last two of the four denoising passes, up to 40 frames that have left the
cache (far anchors: every frame, or every 2nd or 4th), at their relative RoPE positions and with the TRB bias of their
distance (-4). This is where far reads raise identity on Self-Forcing. The commit pass never reads far anchors.

1. Far reads leave subject consistency unchanged at every density, with or without Commit Forcing (Table 1), and also
   with a weaker bias on the far anchors (Table 2, top).
2. Moving the far anchors to RoPE positions inside the trained range 0-20 does not help either (Table 2, bottom;
   a position effect would need an identity interval above 0 without more videos with reduced motion). All upper bounds
   are at most +0.01, well below the +0.048 that far reads give Self-Forcing.
3. Without the sink, the denoising passes lose almost all identity, and far history does not bring it back (Table 3).

**Table 1.** VBench-Long, 48 s, 200 prompts x 2 seeds; difference to `SGF_RFW` (x100; reduced motion: share of videos).

| Arm | Far anchors | Subject | Consistency (clip to clip) | Dynamic | Reduced motion |
|---|---|---|---|---|---|
| `SGF_RFW_ST1L20_NM` | every frame | -0.016 [-0.072, +0.037] | -0.117 [-0.672, +0.397] | -0.615 [-3.062, +1.781] | +0.0075 [-0.0325, +0.0475] |
| `SGF_RFW_ST2L20_NM` | every 2nd frame | -0.040 [-0.088, +0.004] | -0.071 [-0.513, +0.358] | -0.438 [-3.052, +2.094] | +0.0050 [-0.0325, +0.0450] |
| `SGF_RFW_ST4L20_NM` | every 4th frame | -0.013 [-0.064, +0.038] | +0.170 [-0.302, +0.616] | -0.844 [-3.062, +1.469] | +0.0125 [-0.0250, +0.0501] |
| `SGF_RFW_ST4L12_NM` | every 4th, layers 12-29 | -0.038 [-0.092, +0.015] | +0.027 [-0.473, +0.514] | +0.156 [-2.552, +2.917] | +0.0275 [-0.0100, +0.0650] |
| `SGF_RF_ST1L20_NM` - `SGF_RF` (without Commit Forcing) | every frame | +0.042 [-0.011, +0.094] | +0.422 [-0.125, +0.974] | -2.198 [-4.365, +0.042] | +0.0025 [-0.0251, +0.0325] |

**Table 2.** Identity at 38-47.5 s (DINOv2), 48 s, 20 prompts x 3 (top) / 4 (bottom) seeds; difference to `SGF_RFW`.

| Arm | Far read | Identity | Reduced motion | Brightness late/early |
|---|---|---|---|---|
| `SGF_RFW` | none | | 0.15 | 1.010 |
| `SGF_RFW_ST1L20_NM` | every frame, TRB bias -4 | -0.0048 [-0.0388, +0.0305] | 0.08 | 1.021 |
| `SGF_RFW_ST1L20_NM_B2` | every frame, bias -2 | -0.0226 [-0.0555, +0.0107] | 0.08 | 1.015 |
| `SGF_RFW_ST1L20_NM_B0` | every frame, bias 0 | -0.0208 [-0.0518, +0.0058] | 0.22 | 1.038 |
| `SGF_RFW_ST4L20` | every 4th frame + ln 4, positions -37..2 | -0.0129 [-0.0290, +0.0049] | 0.15 (none: 0.10) | |
| `SGF_RFW_ST4L20_PA` | same, (a) on the sink positions 0-2 | -0.0101 [-0.0286, +0.0086] | 0.14 | |
| `SGF_RFW_ST4L20_PB` | same, (b) on positions 3-5, replacing the oldest block | -0.0108 [-0.0316, +0.0094] | 0.12 | |

**Table 3.** Identity at 38-47.5 s (DINOv2), 48 s, 20 prompts x 3 seeds (SGF's own cache: 2 seeds).

| Contrast | Identity | Reduced motion |
|---|---|---|
| sink left out of the denoising passes: `SGF_RFW_NS` - `SGF_RFW` | -0.1672* [-0.2039, -0.1330] | 0.15 -> 0.02 |
| far read (bias 0) with the sink: `SGF_RFW_ST1L20_NM_B0` - `SGF_RFW` | -0.0208 [-0.0518, +0.0058] | 0.15 -> 0.22 |
| far read (bias 0) without the sink: `SGF_RFW_NS_ST1L20_NM_B0` - `SGF_RFW_NS` | +0.0064 [-0.0029, +0.0160] | 0.02 -> 0.02 |
| interaction: without - with the sink | +0.0272 [-0.0027, +0.0625] | |
| SGF's own cache (sink 3 + newest 9), sink also left out of denoising steps 0-1: `SGF_WL` - `SGF_W` | -0.0963* [-0.1392, -0.0586] | 0.07 -> 0.17 |

Without the sink, late identity keeps 0.018 of its early value (1.000 with it); far anchors restore 3.8% of the loss
(+0.0007 with the TRB bias). Without Commit Forcing, the contrast on SGF's own cache is -0.0400*. Brackets: 95% bootstrap
intervals over prompts; `*`: the interval excludes 0. `tables.py` prints the tables from `data/*.csv` (one row per
video). `generate.py` makes every arm (see `ARMS`) with the SGF integration and `sgf_boundary.patch`:

```bash
bash setup/fetch.sh sgf && patch -d third_party/sgf -p1 < analysis/boundaries/sgf/sgf_boundary.patch
python analysis/boundaries/sgf/generate.py --code third_party/sgf --arm SGF_RFW_ST1L20_NM \
    --prompts eval/prompts/rollf200.txt --seconds 48 --seed 0 --out outputs/sgf_boundary   # Table 1: seeds 0, 1
python analysis/boundaries/sgf/generate.py --code third_party/sgf --arm SGF_RFW_NS \
    --prompts analysis/boundaries/sgf/prompts20.txt --seconds 48 --seed 0 --out outputs/sgf_boundary   # seeds 0-2 (0-3)
python analysis/boundaries/sgf/tables.py
```
