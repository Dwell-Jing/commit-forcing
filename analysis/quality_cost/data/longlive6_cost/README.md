# LongLive committing-6 cost observations

Eight numeric JSON snapshots and their memory logs preserve four Base and four committing-6 runs from the
second completed cost run. Each job generates entry 0 as warm-up and entry 1 as the measured 60-second video.
All jobs ran concurrently on eight dedicated H20 GPUs of one node, alternating Base and committing-6.
The `repeat` field identifies the four technical repeats of the same measured prompt.

Each JSON retains wall timers, Torch allocated and reserved peaks, activation/cache counters and its original
SHA-256. Statistics use `videos[1]`, after warm-up. Each `.mem` file contains recorded whole-device memory in
MiB; the per-run peak is `max(samples) / 1024`. Table values average the four observations in each arm.

| Observation | Base | Committing-6 |
|---|---:|---:|
| Mean wall time (s), four repeats | 231.137706 | 223.767656 |
| Minimum wall time (s) | 230.425555 | 222.811820 |
| Maximum wall time (s) | 232.340612 | 224.584199 |
| Device peak (GiB), every recorded run | 35.885742 | 35.885742 |
| Torch peak allocated (GiB), every measured run | 30.669543 | 30.669543 |
| Torch peak reserved (GiB), every measured run | 35.437500 | 35.437500 |
| Physical cache (latent frames) | 12 | 12 |
| Clean forwards per video | 80 | 80 |
| Denoising forwards per video | 320 | 320 |

The ratio of mean wall times is 0.968114, an observed 3.2% reduction on this prompt. Device memory and Torch
allocation are separate measures. The recorded device peaks include allocator cache, weights, activations and
CUDA context. Each included log has one retained device-memory sample; it supports the reported logged peak.

[retrieval.json](retrieval.json) records original file hashes, output timestamps, a stable retrieval check and a
completion marker later than every output. [summary.json](summary.json) stores the resulting means. These files
identify a fixed observation set matching the paper; paths and host details are omitted. The earlier
[first completed run](snapshots/first-completed-run/README.md) remains archived and is not used by the main table.

```bash
python analysis/quality_cost/reproduce.py
```

This command checks source hashes and counters, recalculates timers and memory peaks, and validates
[the per-repeat CSV](../longlive6_cost_per_repeat.csv) and current cost table. Source hashes and accepted fields
are recorded in [provenance.json](../../provenance.json).
