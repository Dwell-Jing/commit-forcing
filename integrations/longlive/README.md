# LongLive

We apply Commit Forcing to [LongLive](https://github.com/NVlabs/LongLive) (LongLive-1.3B, upstream commit `e52d9ef`).
Each 3-frame latent block receives four denoising passes and one clean committing pass.

| Configuration | Denoising reads | Committing reads | Physical KV storage |
|:---|:---|:---|---:|
| Base, `--rule off` | sink 3 + newest 9 | sink 3 + newest 9 | 12 latent frames |
| Commit Forcing, `--rule on` | sink 3 + newest 9 | newest 6: current block + previous block | 12 latent frames |
| Legacy, `--rule on --commit-profile legacy12` | sink 3 + newest 9 | newest 12 | 15 latent frames |

The six-frame rule is the default. It preserves base storage and denoising access, excludes the separate sink read
from clean committing, and restores the native attention window after each commit. The initial block reads its
three available frames; later commits read the newest six. The legacy profile retains the previous 12-frame read
and 15-frame storage for historical results and assets.

## Setup

Apply the current patch to a clean checkout of the pinned upstream revision:

```bash
git clone https://github.com/NVlabs/LongLive && cd LongLive && git checkout e52d9ef
patch -p1 < /path/to/commit-forcing/integrations/longlive/commit_rule.patch
huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir wan_models/Wan2.1-T2V-1.3B
huggingface-cli download Efficient-Large-Model/LongLive-1.3B --local-dir longlive_models
```

`generate.py` checks patch version 2; the earlier patch uses a different default storage/read policy.

## Generate

Run from the root of this repository:

```bash
python integrations/longlive/generate.py --rule on --code /path/to/LongLive \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/longlive6
```

Use `--rule off` for Base. To reproduce the earlier 12-frame configuration, use a separate output directory:

```bash
python integrations/longlive/generate.py --rule on --commit-profile legacy12 --code /path/to/LongLive \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/longlive12
```

`--ckpt` and `--lora` default to the weights named in `configs/longlive_inference.yaml`. Each sidecar records the
profile and `counters`: physical `kv_cache_frames`, configured `commit_frames`, actual `commit_read_frames`, and
`sinkless_attention_calls`. The default rule requires physical cache 12 and read lengths 3/6; legacy requires
physical cache 15 and lengths 3/6/9/12. Both require 30 sink-free attention calls per block; Base requires zero.
Generation stops if these activation or read-length checks fail.

## Result provenance

The six-frame common946 results use the frozen standard-suite engine, arm `W946_W6S`: physical cache 12, unchanged
native denoising, and six-frame clean committing. This standalone entry point implements that read/storage policy
on the pinned upstream checkout. Its end-to-end output parity with the frozen engine has not been established.

Historical rollf200 and longer-video window ablations use their recorded generation engines and may retain
15-frame physical storage. They remain separate from `W946_W6S`; changing the standalone default does not relabel
their outputs. [`analysis/commit_window/generate.py`](../../analysis/commit_window/generate.py) explicitly preserves
the historical 15-frame ablation cache for its 3/6/9/12-frame comparisons.
