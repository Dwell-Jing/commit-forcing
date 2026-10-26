# Transfer across cache constructions

The benefits of restricting historical context depend on the generator and its cache construction. Released
Rolling Forcing favors its recent 21-frame update over six-frame committing on clip-to-clip consistency.
WorldPlay's joint context re-encoding gives a separate boundary, with no persistent committing chain.

## Released Rolling Forcing

This experiment uses the [released Rolling Forcing model](https://arxiv.org/abs/2509.25161), not the Recency Forcing
training-free bias on Self-Forcing weights (RF-TF). Its native clean-cache update reads the latest 21 latent frames,
including the current three-frame block, and excludes the initial global block.

On rollf200 prompts 0–99 at 60 seconds with generation seed 0, we either replace three recent frames with the three
global frames at the same context size or shorten committing to the latest six frames. The changes begin after the
cache is full. Denoising, sampler, cache geometry, positional encoding and generation noise are retained.

| Committing context, relative to recent 21 | Δ Quality [95% CI] | Δ Dynamic Degree | Δ Subject c2c | Δ Background c2c |
|:---|---:|---:|---:|---:|
| Global 3 + recent 18 | −0.18* [−0.31, −0.03] | −0.20 | −0.61* | −0.57* |
| Recent 6 | −0.09 [−0.25, +0.07] | −0.67 | −0.65* | −0.31* |

Scores use 0–100 points. Quality brackets retain the available 95% intervals from 4,000 paired prompt-bootstrap
draws; asterisks report intervals excluding zero. Both alternatives reduce clip-to-clip Subject and Background
Consistency. Global insertion also reduces Quality significantly; the six-frame Quality interval includes zero.
Thus this released model supplies a boundary to applying the six-frame rule across generators.

## WorldPlay joint context re-encoding

We evaluate [WorldPlay](https://arxiv.org/abs/2512.14614) with its HunyuanVideo-1.5 action model, four denoising steps and 480p outputs.
Before each four-latent-frame block, a noncausal context pass jointly re-encodes the latest 12 frames and up to eight
older frames: the initial four-frame block and a four-frame clip retrieved by camera-view overlap. The resulting
memory KV is read by denoising; there is no persistent committing chain.

The intervention restricts **recent-frame queries during context construction** to text and recent-frame keys.
Older-frame queries keep access to all keys. Denoising continues to read the constructed memory KV, including the
older context. It does not bypass that memory.

### Protocol and readouts

- Ten released test scenes; generation seeds 1 and 2; paired by scene, trajectory and seed.
- Default 20-frame context: a 40-second rotation with two full yaw turns, a 20-second forward-and-back walk and a
  40-second forward walk. Final-return similarity uses only the two returning trajectories.
- Separate 40-frame context test: the same ten scenes on the 40-second rotation trajectory with generation seed 1.
  Restricted and unrestricted construction are compared within the same budget.
- Final-return similarity is DINOv2 similarity to the opening at the last return pose.
- Color drift is the sum of absolute departures from one of late-to-early saturation and brightness ratios, using
  the final and first five seconds. Seam ratio measures frame changes at block boundaries. The one-second score
  compares DINOv2 embeddings of frames one second apart.
- Intervals use 4,000 bootstrap draws over scenes. These diagnostics retain their original scales and are not
  VBench score points.

| Restricted − unrestricted construction | Δ at 20 frames [95% CI] | Δ at 40 frames [95% CI] |
|:---|---:|---:|
| Final-return similarity ↑ | −0.0317 [−0.1141, +0.0545] | −0.1769* [−0.2926, −0.0636] |
| Color drift ↓ | −0.0142 [−0.0676, +0.0353] | −0.0885 [−0.2350, +0.0796] |
| Seam ratio ↓ | +0.2067* [+0.0338, +0.3842] | +0.1542 [−0.0019, +0.3111] |
| One-second similarity ↑ | −0.0089* [−0.0167, −0.0025] | −0.0114 [−0.0242, +0.0024] |

At 20 frames, restriction significantly worsens the seam ratio and one-second similarity, with no significant
return-similarity or color-drift change. At 40 frames, it significantly reduces final-return similarity. Other
intervals cross zero. Restricting older context during recent-KV construction therefore does not reproduce the
persistent-cache generators' gains in this joint re-encoding configuration.

## Aggregate record

[`summary.json`](summary.json) preserves all reported contrasts, original scales, protocol differences and source
hashes from the supplied manuscript snapshot. No per-scene or per-prompt values are added. Read it with:

```bash
python analysis/kv_construction/readout.py --summary analysis/transfer_boundaries/summary.json
```

The reader checks and prints existing aggregate values; it does not rerun the experiments or estimate new intervals.
