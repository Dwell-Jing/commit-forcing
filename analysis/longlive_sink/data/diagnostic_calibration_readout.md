# Calibration of the DINOv2 consistency diagnostic

## A. Tail edits of the SGF-X rule videos (40 cells): change vs re-encode-only (E0)

| edit | DINOv2 late consistency change | as % of the instance-swap drop | CLIP late consistency change | DINOv2 early (unedited window) change |
|---|---|---|---|---|
| E0 (re-encode) | level 0.1612 | | level 0.0667 | level 0.1772 |
| colour small (sat x1.04, bri x1.045) | -0.0003 [-0.0014, +0.0010] | 0% | -0.0002 [-0.0011, +0.0006] | -0.00025 |
| colour large (sat x1.20, bri x1.25) | -0.0008 [-0.0048, +0.0047] | 0% | -0.0044* [-0.0071, -0.0016] | +0.00049 |
| freeze tail | -0.0039 [-0.0155, +0.0080] | 1% | -0.0039* [-0.0075, -0.0005] | -0.00038 |
| view: 80% centre crop | -0.0241* [-0.0350, -0.0135] | 7% | -0.0125* [-0.0177, -0.0075] | +0.00028 |
| instance swap (other seed, same prompt) | -0.3225* [-0.3825, -0.2653] | 100% | -0.1339* [-0.1591, -0.1117] | +0.00003 |
| prompt swap | -0.1623* [-0.1944, -0.1340] | 50% | -0.0646* [-0.0766, -0.0536] | +0.00070 |

Reported DINOv2 consistency contrasts for scale: SGF-X SR - SS +0.019, RS - SS -0.137; LongLive c0 - 33 -0.008, d0 - 33 -0.085.

## B / C. Mechanism contrasts: DINOv2 vs CLIP, and DINOv2 at equal colour drift and motion

| contrast | DINOv2 | CLIP | DINOv2 adjusted for d|sat-1|, d|bri-1|, d log motion | colour / motion differences (d|sat-1|, d|bri-1|, d log m) |
|---|---|---|---|---|
| SGF two-stage cross: SGFX_SR - SGFX_SS | +0.0194* [+0.0073, +0.0310] | +0.0156* [+0.0090, +0.0223] | +0.0132 [-0.0058, +0.0346] | -0.024, -0.026, +0.062 |
| SGF two-stage cross: SGFX_RS - SGFX_SS | -0.1373* [-0.1686, -0.1070] | -0.0505* [-0.0615, -0.0398] | -0.1318* [-0.2004, -0.0632] | +0.219, +0.266, +0.431 |
| SGF two-stage cross: SGFX_RR - SGFX_SS | -0.1327* [-0.1620, -0.1043] | -0.0521* [-0.0636, -0.0409] | -0.1280* [-0.1856, -0.0838] | +0.126, +0.174, +0.000 |
| SGF two-stage cross: SGFX_RS - SGFX_RR | -0.0046 [-0.0226, +0.0118] | +0.0016 [-0.0028, +0.0065] | -0.0045 [-0.0428, +0.0268] | +0.093, +0.092, +0.431 |
| LongLive stage cross: LLS_c0 - LLS_33 | -0.0081 [-0.0185, +0.0009] | -0.0029 [-0.0083, +0.0022] | -0.0140 [-0.0342, +0.0022] | -0.019, -0.003, +0.118 |
| LongLive stage cross: LLS_d0 - LLS_33 | -0.0853* [-0.1212, -0.0536] | -0.0272* [-0.0382, -0.0172] | -0.0427 [-0.0922, +0.0136] | +0.205, +0.164, +0.068 |
| LongLive stage cross: LLS_00 - LLS_33 | -0.0676* [-0.0898, -0.0458] | -0.0234* [-0.0324, -0.0150] | -0.0691* [-0.1032, -0.0380] | +0.082, +0.072, +0.165 |
| LongLive stage cross: LLS_d0 - LLS_00 | -0.0177* [-0.0358, -0.0010] | -0.0038 [-0.0109, +0.0027] | +0.0013 [-0.0160, +0.0285] | +0.123, +0.092, -0.097 |
| Rolling Sink source: RS_off - RS_real | -0.0106 [-0.0236, +0.0001] | -0.0034* [-0.0073, -0.0001] | -0.0237* [-0.0460, -0.0042] | -0.009, +0.008, -0.168 |
