# Common 60 s VBench evaluation

The current main comparison contains six generators, 946 metadata entries, 944 distinct original prompts and all
16 dimensions. Each adapted arm uses **Commit Forcing**: the clean current block and stored KV of the
immediately preceding block, giving 6 latent frames after startup (3 + 3). Base denoising, cache storage and update
remain in place; other history is excluded from direct committing reads but can still influence the generated block
and preceding-block KV. Scores ×100; differences are computed before rounding.

<table>
<thead>
<tr><th rowspan="2" align="left">Model</th><th colspan="3">Quality</th><th colspan="3">Total</th></tr>
<tr><th>Base</th><th>Commit Forcing</th><th>Δ</th><th>Base</th><th>Commit Forcing</th><th>Δ</th></tr>
</thead>
<tbody>
<tr><td>Context Forcing</td><td align="right">84.79</td><td align="right">85.25</td><td align="right"><b>+0.46</b></td><td align="right">82.24</td><td align="right">82.68</td><td align="right"><b>+0.44</b></td></tr>
<tr><td>Rolling Sink</td><td align="right">84.84</td><td align="right">85.25</td><td align="right"><b>+0.41</b></td><td align="right">82.90</td><td align="right">83.26</td><td align="right"><b>+0.36</b></td></tr>
<tr><td>Recency Forcing, training-free †</td><td align="right">84.77</td><td align="right">85.42</td><td align="right"><b>+0.65</b></td><td align="right">82.24</td><td align="right">83.34</td><td align="right"><b>+1.10</b></td></tr>
<tr><td>LongLive</td><td align="right">84.70</td><td align="right">84.99</td><td align="right"><b>+0.29</b></td><td align="right">83.05</td><td align="right">83.36</td><td align="right"><b>+0.31</b></td></tr>
<tr><td>SGF+</td><td align="right">86.32</td><td align="right">86.63</td><td align="right">+0.32</td><td align="right">84.30</td><td align="right">84.64</td><td align="right">+0.34</td></tr>
<tr><td>SGF</td><td align="right">86.06</td><td align="right">87.33</td><td align="right"><b>+1.27</b></td><td align="right">83.85</td><td align="right">84.82</td><td align="right"><b>+0.98</b></td></tr>
</tbody>
</table>

Rows follow ascending adapted Total. Bold Δ marks a paired 95% interval excluding 0. Quality and Total improve
significantly on 5 of 6 generators, with positive point estimates on all six. RF-TF has the largest Total increase,
+1.10 points; SGF has the largest Quality increase, +1.27 points. RF-TF uses the public Recency Forcing Temporal
Response Bias on released Self-Forcing weights, without an RF-trained checkpoint.
[All current component scores and intervals](../../../RESULTS.md#full-vbench).

## Current six-generator source package

The [current6](current6/) directory separates the updated method from the frozen historical package in this folder.
CF and LongLive retain their existing 6-frame results; SGF, SGF+, RF-TF and Rolling Sink use the updated 6-frame arms.

| File | Content |
|:---|:---|
| [current6/full_scores.csv](current6/full_scores.csv) | 12 primary arms: Quality, Semantic, Total and all 16 unrounded component scores |
| [current6/aggregate_paired_ci.csv](current6/aggregate_paired_ci.csv) | 18 aggregate contrasts and paired 95% intervals |
| [current6/component_paired_ci.csv](current6/component_paired_ci.csv) | 96 component contrasts and paired 95% intervals |
| [current6/source_results.json](current6/source_results.json) | Unrounded report for the four updated 6-frame arms and their wider-context controls |
| [current6/protocol.json](current6/protocol.json) | Current method, source-arm mapping and aggregation provenance |
| [current6/data_manifest.json](current6/data_manifest.json) | Current package inventory and hashes |
| [current6/quality_decomposition.csv](current6/quality_decomposition.csv) | Weighted contributions to Quality for the current six-generator pairs |
| [current6/window_comparisons.csv](current6/window_comparisons.csv) | Current 6-frame minus earlier 9- or 21-frame aggregate contrasts |

Intervals use 4,000 paired bootstrap draws over 944 original-prompt clusters. Each arm retains its own official
surviving-record weights; filtering does not restrict a pair to common survivors. The published source intervals
are frozen as reported. The current package publishes aggregate scores and source summaries; it does not include
new per-prompt contributions. The default command validates point estimates, normalization, component sums and
correspondence to the saved intervals. It does not recompute the updated arms' bootstrap intervals.

```bash
python eval/vbench_full/reproduce_common946.py
```

## Separate ID-Forcing framework comparisons

The two 9-frame adaptations within ID-Forcing are [reported separately](../../../RESULTS.md#id-forcing-framework-comparisons).
They use 6 historical and 3 current frames. The Self-Forcing adaptation also changes cache handover and omits tail
recaching. Their Quality and Total intervals span zero; both Semantic intervals exclude zero, while Dynamic
Degree decreases significantly. Their original scores remain in the historical files below.

## Preserved historical eight-configuration package

The files at this directory's root remain the original 16-arm package. SGF and SGF+ use 9-frame recent-context
controls; RF-TF and Rolling Sink use 21 frames; CF and LongLive use 6 frames; the two ID-Forcing adaptations use
9 frames. These records are supporting context and framework controls, rather than the current six-generator main
comparison. Historical noise fingerprints and configuration details are retained exactly in `protocol.json`.

| File | Historical content |
|:---|:---|
| [full_scores.csv](full_scores.csv) | 16 arms, Quality / Semantic / Total and all 16 unrounded component scores |
| [aggregate_paired_ci.csv](aggregate_paired_ci.csv) | 24 aggregate contrasts and 95% intervals |
| [component_paired_ci.csv](component_paired_ci.csv) | 128 component contrasts and 95% intervals |
| [coverage.csv](coverage.csv) | All 256 arm × dimension coverage cells, clip counts, surviving denominators and omissions |
| [official_prompt_contributions.json](official_prompt_contributions.json) | Per-prompt numerators and denominators for the historical official aggregation and bootstrap |
| [prompt_clusters.csv](prompt_clusters.csv) | All 946 original-prompt identities and dimension assignments |
| [protocol.json](protocol.json) | Historical prompt hashes, evaluator revision, sampler/cache settings, weights and bootstrap configuration |
| [longlive6_source_results.json](longlive6_source_results.json) | Original LongLive Base, 12-frame control and 6-frame report |
| [longlive6_coverage_jobs.json](longlive6_coverage_jobs.json) | 128 completed LongLive 6-frame scoring jobs, prompt assignments, denominators and source hashes |

```bash
python eval/vbench_full/reproduce_common946.py --profile historical
python eval/vbench_full/reproduce_common946.py --profile historical --models LL
```

The historical command recomputes aggregate and component contrasts from the per-prompt contributions and checks
published CSVs, using 4,000 shared multinomial draws of 944 prompt clusters, seed 20261011.
The earlier three-model package under [results/vbench_full](../README.md) retains its own protocol and outputs.

### LongLive window and storage distinction

The current and preserved common946 six-frame LongLive pair stores 12 physical cache frames in both arms.
The public `LL_W` alias in the root CSVs refers to the six-frame source arm `W946_W6S`. The original three-arm
report instead calls the old 12-frame control `LL_W`; that control uses 15 physical cache frames. Relative to the
12-frame control, the six-frame arm changes Quality by +0.08 [−0.06,+0.21] and Total by +0.11 [−0.02,+0.25], with
both intervals spanning zero. The [control archive](ablation12/README.md) preserves the original nine-file package.
The custom-prompt LongLive studies retain 15-frame physical storage and report their configurations separately.
