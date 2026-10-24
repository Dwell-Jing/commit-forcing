# Rolling Sink

We apply Recent-Context Committing to [Rolling Sink](https://github.com/Rolling-Sink/Rolling-Sink) (arXiv 2602.07775, commit
`e384dc7`) with the Self-Forcing DMD weights (EMA), as in its `inference.py`. Once the 21-frame KV cache is full,
Rolling Sink writes replayed early frames into its history slots at every commit pass. We add a per-layer cache of the
real committed K/V (same size and first-in-first-out eviction, about 6 GB more in bf16) and let the commit pass attend
to its newest 6 frames: the current clean 3-frame block and the immediately preceding block. The first block reads
its 3 available frames. Denoising and replays are unchanged. The real archive remains 21 frames; changing the read
window does not resize it or the base cache. Keys retain their already encoded RoPE positions. `commit_rule.patch` adds
`commit_rule` and `commit_frames` arguments to `CausalInferencePipeline` (`pipeline/causal_inference.py`) and the commit-pass branch and
counters to `wan/modules/causal_model.py`; off, Rolling Sink runs unchanged. Rolling Sink is licensed under the Adobe
Research License (noncommercial research only), and the patch modifies its files.

`--commit-profile recent6` is the default. Use `--commit-profile legacy21` for the historical full-real-archive
21-frame control and a separate `--out` directory. `--rule off` preserves the base path and allocates no real archive.

Setup, then generation from the root of this repository (`--rule off` is the base Rolling Sink):

    git clone https://github.com/Rolling-Sink/Rolling-Sink && cd Rolling-Sink && git checkout e384dc7
    patch -p1 < /path/to/commit-forcing/integrations/rolling_sink/commit_rule.patch
    sh shell_scripts/download_ckpt.sh    # wan_models/ and checkpoints/self_forcing_dmd.pt (the default --ckpt)
    cd /path/to/commit-forcing
    python integrations/rolling_sink/generate.py --rule on --code /path/to/Rolling-Sink \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/rolling_sink

Each `<idx>.json` reports `counters`: `blocks`; `real_commits`, the commit passes that read the real history (30 layers
× `blocks` on, 0 off); and `replays`, Rolling Sink's replay insertions (30 layers per block from the 8th block on,
the same for both rules). `commit_read_frame_counts` must show a 3-frame first commit and 6-frame later commits by
default; `legacy21` warms up through 3/6/9/12/15/18 to 21. Sidecars record the profile, configured window, and archive
capacity. Generation stops on activation or read-length mismatches. The six-frame read can differ from Base before
the first replay once a third block is available. Reapply the current patch to a clean pinned checkout.
