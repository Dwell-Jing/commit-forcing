# SGF+ (Self Gradient Forcing Plus)

After denoising each 3-frame block, SGF+ runs a commit pass: its memory expert re-encodes the clean block at timestep 0
and writes its keys and values into the KV cache. We mark this pass in `pipeline/causal_inference.py`; with `--rule on`
its self-attention (`wan/modules/causal_model.py`) reads only the newest 6 latent frames: the current clean block and
the immediately preceding block. The first block reads its 3 available frames. The denoising passes, cache storage, and RoPE
positions are unchanged, and `--rule off` is the base SGF+. Cache: sink 3 + FIFO 6 + current 3 latent frames,
top-aligned RoPE, `kv_cache_train_frames=21` (upstream's launcher uses 12).

This standalone geometry preserves the supporting rollf200 configuration. The standard-suite SGF+ results instead
use a 12-frame training-position range and contiguous temporal positions, while keeping the same 12-frame physical
cache and separate committing parameters. This entry point implements the six-frame read policy; its preserved
21-frame/top-aligned geometry does not reproduce that complete standard-suite configuration.

Commit Forcing uses `--commit-profile recent6` by default. The historical 9-frame control remains
available through `--commit-profile legacy9`; choose a separate `--out` for each profile. `--rule off` keeps base
reads, storage, and denoising regardless of the profile.

Setup (the environment of [`setup`](../../setup/README.md); inference needs only Wan2.1-T2V-1.3B and the chunkwise checkpoint):

    git clone https://github.com/Zihan-Su/Self_Gradient_Forcing_Plus.git && cd Self_Gradient_Forcing_Plus
    git checkout 14cda9b && patch -p1 < /path/to/commit-forcing/integrations/sgf_plus/commit_rule.patch
    hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir wan_models/Wan2.1-T2V-1.3B
    hf download ZihanSu/Self_Gradient_Forcing_Plus chunkwise/model.pt --local-dir hf_weights

Generate from the repository root, once per rule (`--ckpt` defaults to `<code>/hf_weights/chunkwise/model.pt`):

    python integrations/sgf_plus/generate.py --rule on --code ../Self_Gradient_Forcing_Plus \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf_plus

Each `<idx>.json` holds the activation counters. With n blocks (n = 4 × seconds / 3; 80 for 60 s): `commit_calls` = n;
`rule_reads` = 30 n with `--rule on`, 0 with `--rule off`; `sink_dropped` = 30 max(0, n − 2) with the default
six-frame rule, or 30 max(0, n − 3) with `legacy9`, and 0 off. `commit_read_frame_counts` must report 3 frames on
the first commit and 6 thereafter by default. `generate.py` checks all these counters. Sidecars record the profile,
window, and full geometry. Apply the updated patch to a clean pinned checkout; `COMMIT_RULE` remains the code name.
