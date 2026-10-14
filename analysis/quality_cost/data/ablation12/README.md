# Previous LongLive 12-frame control summaries

These three derived CSVs retain the original Quality decomposition, component changes, and single-video costs
before the LongLive main committing window changed to 6 frames. Their original source reports remain unchanged at
[QUALITY_DECOMP_report.md](../QUALITY_DECOMP_report.md) and [COST_report.md](../COST_report.md).

The previous LongLive Commit Forcing arm committed from 12 frames and stored 15 physical frames. Its single-video
device peaks were 35.9 GiB for Base and 37.0 GiB for that 12-frame control. These measurements do not describe the
new committing-6 implementation. The other seven configurations retain their original values in the current
[Quality and cost page](../../README.md).

The complete original standard-suite package is retained once in
[common946/ablation12](../../../../results/vbench_full/common946/ablation12/README.md).
