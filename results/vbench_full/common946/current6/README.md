# Current six-generator comparison

All six generators commit using the current block and the immediately preceding block (3 + 3 latent frames), with base denoising unchanged. The first block commits without historical context. Scores use the 60-second, 946-entry official suite.

- `full_scores.csv`: 12 Base / Commit Forcing arms, official aggregates and all 16 component means.
- `aggregate_paired_ci.csv`: 18 reported aggregate changes and intervals.
- `component_paired_ci.csv`: 96 reported component changes and intervals.
- `source_results.json`: frozen unrounded report for the four newly evaluated contexts, including comparisons to the earlier 9/21-frame contexts. CF and LongLive retain the six-frame results already published in the parent package.
- `quality_decomposition.csv`: six unrounded seven-component Quality decompositions.
- `window_comparisons.csv`: aggregate changes from the earlier committing contexts.
- `protocol.json` and `data_manifest.json`: settings, source aliases and checksums.

```bash
python eval/vbench_full/reproduce_common946.py
python eval/vbench_full/reproduce_common946.py --profile historical
```

The default command validates the current point estimates, official normalization, component sums, saved interval identities and source hashes. New per-prompt contributions are not included, so it does not independently recompute their confidence intervals. The historical profile retains full prompt-bootstrap replay of the previously public eight-configuration dataset. Those original data files are unchanged; their 9/21-frame and ID-framework contexts are not relabeled as current six-frame results.
