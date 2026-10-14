# Common 60 s VBench evaluation

946 metadata entries, 944 distinct original prompts, 8 paired configurations and all 16 dimensions.
Generate from VBench's Wan2.1 extension and score under the original metadata; keep released weights and
native model configurations. Scores ×100. Compare each Base / + Commit Forcing pair.

These 8 configurations across 7 methods are the common-protocol comparisons used in the current paper and release.
Quality gains are significant in 5 configurations and Total gains in 5; the largest Total gain is SGF's +1.09 points.
RF-TF is the public Recency Forcing Temporal Response Bias applied to released Self-Forcing weights, without an
RF-trained checkpoint. MovieGen and longer-video comparisons are reported under their separate protocols.

<table>
<thead>
<tr><th rowspan="2" align="left">Model</th><th colspan="3">Quality</th><th colspan="3">Total</th></tr>
<tr><th>Base</th><th>+ CF</th><th>Δ</th><th>Base</th><th>+ CF</th><th>Δ</th></tr>
</thead>
<tbody>
<tr><td>SGF</td><td align="right">86.06</td><td align="right">87.22</td><td align="right"><b>+1.16</b></td><td align="right">83.85</td><td align="right">84.94</td><td align="right"><b>+1.09</b></td></tr>
<tr><td>Recency Forcing, training-free †</td><td align="right">84.77</td><td align="right">85.24</td><td align="right"><b>+0.47</b></td><td align="right">82.24</td><td align="right">83.08</td><td align="right"><b>+0.85</b></td></tr>
<tr><td>Context Forcing</td><td align="right">84.79</td><td align="right">85.25</td><td align="right"><b>+0.46</b></td><td align="right">82.24</td><td align="right">82.68</td><td align="right"><b>+0.44</b></td></tr>
<tr><td>SGF+</td><td align="right">86.32</td><td align="right">86.61</td><td align="right">+0.29</td><td align="right">84.30</td><td align="right">84.60</td><td align="right">+0.30</td></tr>
<tr><td>LongLive</td><td align="right">84.70</td><td align="right">84.99</td><td align="right"><b>+0.29</b></td><td align="right">83.05</td><td align="right">83.36</td><td align="right"><b>+0.31</b></td></tr>
<tr><td>Rolling Sink</td><td align="right">84.84</td><td align="right">85.15</td><td align="right"><b>+0.32</b></td><td align="right">82.90</td><td align="right">83.18</td><td align="right"><b>+0.28</b></td></tr>
<tr><td>ID-Forcing on Self-Forcing</td><td align="right">85.26</td><td align="right">85.21</td><td align="right">−0.05</td><td align="right">82.96</td><td align="right">83.15</td><td align="right">+0.19</td></tr>
<tr><td>ID-Forcing on LongLive</td><td align="right">84.91</td><td align="right">84.64</td><td align="right">−0.27</td><td align="right">82.92</td><td align="right">82.91</td><td align="right">−0.01</td></tr>
</tbody>
</table>

**+ CF**: + Commit Forcing. Bold Δ marks statistically significant changes; full statistics are in the CSV files.
See [RESULTS.md](../../../RESULTS.md#full-vbench) for all 16 component contrasts.

## Data and reproduction

| File | Content |
|:---|:---|
| [full_scores.csv](full_scores.csv) | 16 arms, Quality / Semantic / Total and all 16 unrounded component scores |
| [aggregate_paired_ci.csv](aggregate_paired_ci.csv) | 24 aggregate contrasts and 95% intervals |
| [component_paired_ci.csv](component_paired_ci.csv) | 128 component contrasts and 95% intervals |
| [coverage.csv](coverage.csv) | All 256 arm × dimension coverage cells, clip counts, surviving denominators and omissions |
| [official_prompt_contributions.json](official_prompt_contributions.json) | Per-prompt numerators and denominators used by official aggregation and bootstrap |
| [prompt_clusters.csv](prompt_clusters.csv) | All 946 original-prompt identities and dimension assignments |
| [protocol.json](protocol.json) | Prompt hashes, evaluator revision, sampler/cache settings, weights and bootstrap configuration |
| [longlive6_source_results.json](longlive6_source_results.json) | Original 3-arm report for LongLive Base, 12-frame control and the 6-frame main configuration |
| [longlive6_coverage_jobs.json](longlive6_coverage_jobs.json) | 128 completed LongLive 6-frame scoring jobs, prompt assignments, denominators and source hashes |

### LongLive committing window

The LongLive main variant commits from the newest **6 latent frames**: 3 recent trajectory frames plus the current
3-frame block. It retains the base denoising policy and **12-frame physical cache**. Its public `LL_W` alias refers
to the source arm `W946_W6S`. The 6-frame window was selected using the separate rollf200 and quick59 studies, then
evaluated on this 946-entry suite with the same prompts, released weights, evaluator and aggregation.

Relative to Base, Quality changes by +0.29 [+0.05,+0.52] and Total by +0.31 [+0.10,+0.52]. Relative to the previous
12-frame committing context, Quality changes by +0.08 [−0.06,+0.21] and Total by +0.11 [−0.02,+0.25]; these latter
intervals span zero. The [original 3-arm report](longlive6_source_results.json) retains the comparisons. In that
source report, `LL_W` denotes the old 12-frame control and `W946_W6S` denotes the new 6-frame variant; the current
main CSVs use `LL_W` for the new variant.

The old 12-frame configuration and original nine-file data package are preserved byte for byte in the
[control archive](ablation12/README.md). All other seven configurations, including their baselines, scores,
intervals and per-prompt contributions, retain their original values.

```bash
python eval/vbench_full/reproduce_common946.py
# Check the updated LongLive intervals while retaining all data/coverage checks.
python eval/vbench_full/reproduce_common946.py --models LL
```

This CPU command recomputes all aggregate and component contrasts from the per-prompt contributions and verifies
them against the published CSVs. It uses 4,000 shared multinomial draws of 944 original-prompt clusters, seed 20261011.
Each arm retains its own official surviving-record weights; filtering does not restrict a pair to common survivors.

The 5 added configurations use their native CUDA bf16 noise draws, and each pair records matching initial-noise and RNG
fingerprints. SGF, training-free RF and Context Forcing reuse completed common946 videos and raw scores; those historical
outputs do not retain complete noise fingerprints. The same generation seed convention is retained.

The older integration commands and three-model CSV/spec package reproduce the earlier experiments. Their SGF+ positional
configuration differs from this common-protocol run; the settings used here are in `protocol.json`.
