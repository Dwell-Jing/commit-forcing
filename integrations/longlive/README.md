# LongLive

We apply Commit Forcing to [LongLive](https://github.com/NVlabs/LongLive) (LongLive-1.3B, upstream commit `e52d9ef`).
Each block of 3 latent frames gets 4 denoising passes and a commit pass that writes the clean block into the KV cache;
in the base model, every pass reads a 3-frame attention sink plus the newest 9 frames (a 12-frame window). With Commit Forcing
(`--rule on`), the commit pass reads the newest 12 frames and no sink, the denoising passes are unchanged, and the KV cache holds 15
frames (sink 3 + 12 recent) instead of 12. `commit_rule.patch` adds a `commit_rule` config flag to
`pipeline/causal_inference.py` and a `read_sink` switch to `wan/modules/causal_model.py`; off, LongLive runs unchanged.

Setup:

    git clone https://github.com/NVlabs/LongLive && cd LongLive && git checkout e52d9ef
    patch -p1 < /path/to/commit-forcing/integrations/longlive/commit_rule.patch
    huggingface-cli download Wan-AI/Wan2.1-T2V-1.3B --local-dir wan_models/Wan2.1-T2V-1.3B
    huggingface-cli download Efficient-Large-Model/LongLive-1.3B --local-dir longlive_models

Generate from the root of this repository (`--rule off` is the base LongLive):

    python integrations/longlive/generate.py --rule on --code /path/to/LongLive \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/longlive

`--ckpt` and `--lora` default to the weights named in LongLive's `configs/longlive_inference.yaml`. Each `<idx>.json`
reports `counters`: `blocks`, `kv_cache_frames` (12 off, 15 on) and `sinkless_attention_calls`, the attention calls
that skipped the sink (30 layers × `blocks` on, 0 off; generate.py stops on a mismatch).
