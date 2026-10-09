# Commit switch: drift enters through the commit pass

Self-Forcing has no sink. We give it a KV cache of 160 latent frames (40 s), let its denoising passes s1-s3
read all of it (far history: everything beyond the newest 12 frames), and switch far reading on or off in the commit
pass only. Routes of [`analysis/sf_router`](../sf_router/README.md): `S123R` (the commit pass reads the newest 12 real
frames), `S123C` (it also reads far history), `SWCR` / `SWRC` (it reads far history in blocks 0-31, i.e. 0-24 s, only
/ from block 32 on), `R12` (nothing reads far history), `R160` (every pass reads it), `S0`-`S23` (one or two denoising
passes read it), `C` (only the commit pass reads it). 20 prompts x seeds 0-2 = 60 videos per route, 48 s.

**Table 1.** Identity at 38-47.5 s (DINOv2), its retention from 4-8 s, median late / early motion, share of videos with reduced
motion (motion ratio < 0.85) and DiT time.

| Route | Far history read in | Identity | Retention | Motion ratio | Reduced motion | DiT ms / block |
|---|---|---|---|---|---|---|
| `R12` | none | 0.0182 | 0.141 | 1.03 | 0.20 | 1656 |
| `S123R` | s1-s3 | 0.1315 | 0.861 | 0.72 | 0.65 | 5566 |
| `S123C` | s1-s3 + commit | 0.1077 | 0.729 | 0.64 | 0.87 | 6870 |
| `R160` | s0-s3 + commit | 0.1155 | 0.762 | 0.60 | 0.97 | 8330 |

`S123C` - `S123R`: identity -0.0237* [-0.0392, -0.0102] (better in 17% of the videos), log motion ratio -0.154*
[-0.220, -0.093] (motion x0.86). Adding far reads to s0 as well (`R160` - `S123C`) changes identity by +0.0078 [-0.0068,
+0.0216].

**Table 2.** Saturation drift (saturation relative to the same video at 4-8 s), difference between routes.

| Contrast | Slope per 10 s, 8-48 s | 8-16 s | 38-48 s |
|---|---|---|---|
| `S123C` - `S123R` | +0.0541* [+0.0403, +0.0690] | +0.0359* [+0.0219, +0.0510] | +0.2032* [+0.1604, +0.2474] |
| `SWCR` - `S123C`, after the switch (26-48 s) | -0.0585* [-0.0724, -0.0461] | | |
| `SWRC` - `S123C`, after the switch (24-34 s) | +0.0285* [+0.0171, +0.0407] | | |
| `SWCR` - `S123R` | | | +0.0832* [+0.0596, +0.1091] |

The four properties of the commit pass, all at equal far reading in the denoising passes:
1. Drift grows with how much the commit pass reads: identity falls by -0.0105 [-0.0246, +0.0023] (`SWCR`) and -0.0102*
   [-0.0146, -0.0058] (`SWRC`) for half of the blocks, -0.0237* for all of them.
2. It stops growing when the reading stops: after the switch the saturation slope of `SWCR` drops by 0.0585* per 10 s
   below that of `S123C`, which removes the +0.054* per 10 s that `S123C` adds over `S123R`.
3. Drift already written stays: at 38-48 s, 14-24 s after the switch, `SWCR` is still +0.083* more saturated than
   `S123R`.
4. No self-amplification: from the switch on, `SWRC` (clean history) drifts faster than `S123C` (drifted history).

The same far history read only by the denoising passes steadies color and identity. Saturation drift at 38-48 s
relative to `R12`: `S0` -0.073*, `S1` -0.138*, `S2` -0.186*, `S3` -0.252*, `S23` -0.202*, `S123R` -0.182*; reading it
in the commit pass as well brings it back (`S123C` +0.021 [-0.092, +0.120]); the commit pass alone gives `C` +0.439*.
`*`: the 95% bootstrap interval over prompts excludes 0. `tables.py` prints every number, with contrast, detail and
brightness drift and the CLIP identity, from `data/commit_switch_48s.csv` (one row per video: identity, motion, DiT
time, commit-pass window, per-second drift).

```bash
for r in R12 S123R S123C R160 SWCR SWRC C S0 S1 S2 S3 S23; do for s in 0 1 2; do
  python analysis/sf_router/generate.py --code third_party/sf_router --route $r \
      --prompts analysis/sf_router/prompts20.txt --seconds 48 --seed $s --out outputs/sf_router
done; done
python analysis/metrics/compute.py outputs/sf_router --clip openai/clip-vit-large-patch14 --out metrics.csv
python analysis/commit_switch/tables.py
```

`analysis/metrics/compute.py` gives the identity, motion and drift columns of `data/*.csv` from new videos;
`dit_ms_per_block` and the commit-pass windows (`counters.commit_windows`) are in each video's json.
