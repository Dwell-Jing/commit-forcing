# SGF+ (Self Gradient Forcing Plus)

After denoising each 3-frame block, SGF+ runs a commit pass: its memory expert re-encodes the clean block at timestep 0
and writes its keys and values into the KV cache. We mark this pass in `pipeline/causal_inference.py`; with `--rule on`
its self-attention (`wan/modules/causal_model.py`) reads only the newest 9 latent frames, i.e. the current block and the
6 frames before it, and no longer the 3 sink frames. The denoising passes, the frames kept in the cache and the RoPE
positions are unchanged, and `--rule off` is the base SGF+. Cache: sink 3 + FIFO 6 + current 3 latent frames,
top-aligned RoPE, `kv_cache_train_frames=21` (upstream's launcher uses 12).

Setup (the environment of [`setup`](../../setup/README.md); inference needs only Wan2.1-T2V-1.3B and the chunkwise checkpoint):

    git clone https://github.com/Zihan-Su/Self_Gradient_Forcing_Plus.git && cd Self_Gradient_Forcing_Plus
    git checkout 14cda9b && patch -p1 < /path/to/commit-forcing/integrations/sgf_plus/commit_rule.patch
    hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir wan_models/Wan2.1-T2V-1.3B
    hf download ZihanSu/Self_Gradient_Forcing_Plus chunkwise/model.pt --local-dir hf_weights

Generate from the repository root, once per rule (`--ckpt` defaults to `<code>/hf_weights/chunkwise/model.pt`):

    python integrations/sgf_plus/generate.py --rule on --code ../Self_Gradient_Forcing_Plus \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf_plus

Each `<idx>.json` holds the activation counters. With n blocks (n = 4 × seconds / 3; 80 for 60 s): `commit_calls` = n;
`rule_reads` = 30 n with `--rule on`, 0 with `--rule off`; `sink_dropped` = 30 (n − 3) with `--rule on` (from
block 3 on the window no longer reaches the sink), 0 with `--rule off`. `generate.py` stops if `commit_calls` or
`rule_reads` differ.
