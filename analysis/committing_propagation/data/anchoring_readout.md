# Recent-context committing: anchor to the past, motion trend, and the seam motion of self-only committing

## SEAM: frame differences on existing rollf200 videos (luma, 0-255; from 4 s; 200 prompts x 2 seeds)

| model | arm | seam | in-block latent step | inside latent | seam ratio |
|---|---|---|---|---|---|
| LongLive | self-only (3) | 7.52 | 5.46 | 5.85 | 1.399 |
| LongLive | recent 6 | 6.69 | 4.92 | 5.16 | 1.375 |
| LongLive | recent 12 | 6.85 | 4.98 | 5.22 | 1.408 |
| LongLive | released (sink + 9) | 6.16 | 4.43 | 4.67 | 1.423 |
| SGF | self-only (3) | 10.33 | 6.08 | 6.16 | 1.822 |
| SGF | recent 9 | 8.73 | 5.49 | 6.01 | 1.683 |
| SGF | sink 3 + recent 6 | 5.97 | 4.34 | 4.69 | 1.372 |
| SGF | released (sink + 9) | 6.42 | 4.61 | 4.99 | 1.404 |

| model | contrast | d seam ratio | d seam | d in-block latent step | d inside latent |
|---|---|---|---|---|---|
| LongLive | self-only (3) - recent 6 | +0.0243* [+0.0077, +0.0451] | +0.8345* [+0.6579, +1.0312] | +0.5349* [+0.4174, +0.6584] | +0.6897* [+0.5575, +0.8251] |
| LongLive | self-only (3) - recent 12 | -0.0088 [-0.0265, +0.0139] | +0.6711* [+0.4659, +0.9034] | +0.4823* [+0.3470, +0.6220] | +0.6232* [+0.4730, +0.7819] |
| LongLive | recent 6 - released (sink + 9) | -0.0486* [-0.0658, -0.0323] | +0.5254* [+0.3359, +0.7225] | +0.4982* [+0.3610, +0.6447] | +0.4884* [+0.3438, +0.6387] |
| SGF | self-only (3) - recent 9 | +0.1387* [+0.0916, +0.1873] | +1.5993* [+1.2795, +1.9117] | +0.5961* [+0.3896, +0.8062] | +0.1427 [-0.0748, +0.3514] |
| SGF | recent 9 - released (sink + 9) | +0.2793* [+0.2260, +0.3334] | +2.3053* [+1.8717, +2.7414] | +0.8769* [+0.5864, +1.1812] | +1.0232* [+0.7186, +1.3523] |
| SGF | recent 9 - sink 3 + recent 6 | +0.3106* [+0.2575, +0.3667] | +2.7583* [+2.2845, +3.2284] | +1.1420* [+0.8287, +1.4550] | +1.3208* [+0.9789, +1.6733] |

## ANC: fixed-latent probe on SGF (20 cells x 6 positions; sources identical to SGFX_SR: 20/20)

| commit read | step_rel (move vs previous step) | trend (cosine with previous step) | to_prev | seam ratio | in-block motion |
|---|---|---|---|---|---|
| self-only | 1.046 | -0.311 | 0.461 | 1.849 | 7.18 |
| recent 9 | 1.007 | -0.299 | 0.449 | 1.728 | 6.99 |
| sink 3 + recent 6 | 1.072 | -0.260 | 0.466 | 1.510 | 6.65 |

| contrast | d step_rel | d trend | d seam ratio | d in-block motion |
|---|---|---|---|---|
| R - C | -0.0387* [-0.0640, -0.0179] | +0.0126 [-0.0077, +0.0306] | -0.1210* [-0.2221, -0.0346] | -0.1885* [-0.3866, -0.0271] |
| S - R | +0.0649* [+0.0340, +0.0966] | +0.0390* [+0.0236, +0.0535] | -0.2178* [-0.4032, -0.0627] | -0.3403* [-0.6347, -0.0962] |
| S - C | +0.0262 [-0.0090, +0.0635] | +0.0516* [+0.0281, +0.0731] | -0.3388* [-0.5823, -0.1284] | -0.5288* [-0.9413, -0.1813] |
