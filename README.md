<div align="center">

<h1>What Helps Denoising Can Hurt Memory:<br>Rethinking History in Long Video Generation</h1>

**Commit Forcing: construct new KV from the current and immediately preceding blocks.**

[![Paper](https://img.shields.io/badge/Paper-coming%20soon-b31b1b.svg)](#news)&nbsp;
[![Models](https://img.shields.io/badge/models-6-orange.svg)](integrations/)&nbsp;
[![Videos](https://img.shields.io/badge/videos-60%E2%80%93240%20s-orange.svg)](RESULTS.md)&nbsp;
[![Code](https://img.shields.io/badge/code-Apache--2.0-blue.svg)](LICENSE)

</div>

## News

- **2026-10-09**: Initial release: code and evaluation results.
- arXiv preprint coming soon.

Commit Forcing constructs KV from the clean current block and the preceding block's stored KV, while preserving
base denoising. It requires no training or additional DiT forward passes.

## Results

60-second VBench, 946 entries. Each row compares the same model with and without Commit Forcing.

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

Scores ×100. Bold Δ indicates a significant paired gain. † RF-TF uses released Self-Forcing weights with
Recency Forcing's Temporal Response Bias. [Full results and evaluation protocols](RESULTS.md).

## Method

<p align="center">
  <img src="assets/method.png" width="100%" alt="Commit Forcing constructs KV from the current and preceding blocks while retaining base denoising.">
</p>

## Examples

<p align="center">
  <img src="assets/qualitative_grid.png" width="100%" alt="Base and Commit Forcing on SGF and Context Forcing at 0, 120 and 238 seconds.">
</p>

Paired 240-second videos, using the same prompt and initial-noise seed.
[Cases and source frames](assets/README.md).

## Quickstart

### Setup

```bash
git clone https://github.com/Dwell-Jing/commit-forcing.git
cd commit-forcing
bash setup/fetch.sh sgf
```

Install the [environment](setup/README.md) and download the weights following the
[SGF integration guide](integrations/sgf/README.md). Other models are in [integrations/](integrations/).

### Generate

```bash
python integrations/sgf/generate.py --code third_party/sgf --reading native --rule on \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf
```

Use `--rule off` for the base model.

### Evaluate

Reproduce the reported VBench table:

```bash
python eval/vbench_full/reproduce_common946.py
```

To score generated videos, follow the [VBench-Long](eval/vbench_long/README.md) or
[full VBench](eval/vbench_full/README.md) instructions.

## Citation

```bibtex
@misc{jing2026commitforcing,
  title  = {What Helps Denoising Can Hurt Memory: Rethinking History in Long Video Generation},
  author = {Jing, Yubin and Zhang, Ziyang and Chen, Meng and
            Li, Yuyao and Wang, Haofan and Gong, Yichen},
  year   = {2026},
  url    = {https://github.com/Dwell-Jing/commit-forcing}
}
```
