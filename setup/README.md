# Setup

## Code

```bash
bash setup/fetch.sh all        # or a subset: sgf sgf_plus recency_forcing longlive context_forcing rolling_sink id_forcing tethercache
```

`fetch.sh` clones each upstream repository into `third_party/<method>`, checks out the commit we tested and applies
`integrations/<method>/commit_rule.patch`. Each `generate.py` takes the patched checkout with `--code` (ID-Forcing:
`--idf-code`).

## Environment

We ran every integration and every VBench score in one environment on NVIDIA H20 GPUs (96 GB): Python 3.11, CUDA 12.8,
torch 2.9.1, diffusers at commit 0f1abc4, transformers 4.57.1, numpy 2.4. `requirements.txt` pins all of its packages.
Install it instead of the upstream `requirements.txt` files, which pin older versions (diffusers 0.31.0, numpy 1.24.4,
av 13.1.0) that conflict with it:

```bash
pip install -r setup/requirements.txt
pip install flash-attn==2.8.3 --no-build-isolation
pip install --no-deps -r setup/requirements_vbench.txt     # pyiqa, openai-clip, dreamsim, scenedetect
```

The last four are VBench's extras. We install them without dependencies because pyiqa 0.1.16 declares
transformers >= 5; `requirements.txt` holds what they use. Scoring also needs VBench at 45e79ec with its checkpoints
([`eval/vbench_long`](../eval/vbench_long/README.md)) and ffmpeg on `PATH` (we used 7.0.2). The `score.sh` scripts put
`vbench_compat/` on `PYTHONPATH`: its `sitecustomize.py` makes three imports of VBench work with these versions. The 9 semantic dimensions of full VBench run with VBench's older pins from a separate folder
([`eval/vbench_full`](../eval/vbench_full/README.md)):

```bash
pip install --no-deps --target semantic_pkgs -r setup/requirements_semantic.txt
git clone https://github.com/facebookresearch/detectron2 && git -C detectron2 checkout b4a4a3bd
pip install --no-deps --no-build-isolation --target semantic_pkgs ./detectron2
```

## Weights

Each integration README names the checkpoint it expects and where the upstream project publishes it. All methods
build on the Wan2.1-T2V-1.3B text encoder and VAE in `wan_models/Wan2.1-T2V-1.3B`, as in the upstream instructions.
