# Not a train/inference mismatch: the LongLive sink 2x2

LongLive is trained with its 3-frame attention sink read in every pass, the commit pass included, on rollouts of up to
60 s. At 48 s, inside that length, we switch the sink read separately in the 4 denoising passes and in the commit pass.
Taking the sink out of the commit pass alone (Commit Forcing, `LLS_c0`) still helps: brightness +0.023\*, saturation
drift −0.019\*, motion +0.118\*, videos with reduced motion 28% → 5%, and identity does not change significantly (−0.008). Reading
the sink only in the commit pass (`LLS_d0`) loses identity (−0.085\*) and the colors blow up (saturation drift +0.205\*).
The denoising passes need the sink; the commit pass is better without it, although LongLive was trained with it there.

| Arm | Denoising passes read | Commit pass reads | Identity retention | Reduced motion | Saturation late/early | Brightness late/early |
|---|---|---|---|---|---|---|
| `LLS_33`, base | sink 3 + newest 9 | sink 3 + newest 9 | 0.817 | 0.28 | 0.972 | 0.979 |
| `LLS_c0`, Commit Forcing | sink 3 + newest 9 | newest 12 | 0.775 | 0.05 | 0.981 | 1.002 |
| `LLS_d0` | newest 12 | sink 3 + newest 9 | 0.105 | 0.33 | 1.233 | 0.992 |
| `LLS_00` | newest 12 | newest 12 | 0.270 | 0.15 | 0.964 | 0.987 |

| Difference to `LLS_33` | Identity [95% CI] | Brightness | Saturation drift | Brightness drift | Log motion [95% CI] |
|---|---|---|---|---|---|
| `LLS_c0` | −0.0081 [−0.0180, +0.0006] | +0.0231\* | −0.0187\* | −0.0034 | +0.118\* [+0.061, +0.177] |
| `LLS_d0` | −0.0853\* [−0.1215, −0.0528] | +0.0128 | +0.2052\* | +0.1636\* | +0.068 [−0.084, +0.231] |
| `LLS_00` | −0.0676\* [−0.0910, −0.0459] | +0.0083 | +0.0822\* | +0.0720\* | +0.165\* [+0.084, +0.257] |

Protocol: 48 s (192 latent frames), the 20 prompts of `prompts20.txt` (lines 0–4 and 6–20 of Self-Forcing's
`prompts/MovieGenVideoBench_extended.txt`) × seeds 0 and 1 = 40 videos per arm, paired by (prompt, seed); 95% bootstrap
over prompts, `*`: the interval excludes 0. Every arm keeps the sink and the newest 12 frames in its KV cache, and every
pass reads 12 frames. Per video, with the column names of `data/longlive_sink_48s.csv`:

- identity `dino_late_38_47`: DINOv2 similarity of seconds 38–47.5 to the video's own opening (0.5–2 s) minus the
  similarity to the opening of the other seed of the same prompt; retention = mean late / mean early (4–8 s) identity;
- colors: late (seconds 38–47) over early (seconds 4–7) mean of the per-second saturation `sat_k` and brightness
  `bri_k`; drift = |ratio − 1|;
- motion: log(`motion_late_38_47` / `motion_early_4_8`), the mean frame-to-frame change late over early; a video has
  reduced motion when its late motion is below 0.85 × its early motion.

`tables.py` also prints detail (`det_k`), the identity difference at equal motion (ANCOVA) and the DiT time per block.

```bash
for arm in LLS_33 LLS_c0 LLS_d0 LLS_00; do for seed in 0 1; do
  python analysis/longlive_sink/generate.py --arm $arm --code /path/to/LongLive \
      --prompts analysis/longlive_sink/prompts20.txt --seconds 48 --seed $seed --out outputs/longlive_sink
done; done
python analysis/metrics/compute.py outputs/longlive_sink --out longlive_sink.csv     # the columns of data/*.csv
python analysis/longlive_sink/tables.py                    # our data; --csv longlive_sink.csv for new videos
```

`generate.py` builds LongLive with `integrations/longlive` (LongLive at `e52d9ef` + `commit_rule.patch`, see its README
for the weights) and sets the sink read and the window of every pass; `LLS_33` and `LLS_c0` give the videos of
`integrations/longlive --rule off` and `--rule on`.
