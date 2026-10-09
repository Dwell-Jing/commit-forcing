# ID-Forcing

[ID-Forcing](https://github.com/In-Distribution-Forcing/ID-Forcing) (arXiv 2610.03120) runs on the published LongLive and Self-Forcing checkpoints. It keeps chunk 0 as a sink and re-rotates the entries of the two most recent chunks onto trained RoPE frames. Its commit pass *self-caches*: the clean forward that writes a chunk's KV attends to the chunk itself only. On Self-Forcing it takes over at chunk 7, and before denoising chunk *n* it also re-encodes chunk *n*−1 attending to the self-cached entry of chunk *n*−2.

With `--rule on` we keep ID-Forcing's window, noise, sampler and decoding, and change the caching procedure: chunk *n* is committed attending to the stored entries of chunks *n*−2 and *n*−1 (chunk 0 only while it is one of them), never to the sink as such. On Self-Forcing the first two entries are Self-Forcing's own commits of chunks 5 and 6, and we drop the re-encoding, because every stored entry already attended to the chunks before it. With `--rule off` we call ID-Forcing's `rollout()` unchanged.

**Setup.** We do not ship ID-Forcing's code; `generate.py` imports it from the checkout given by `--idf-code`. Clone it at commit `4cd6a4c` and download Wan2.1 and the Self-Forcing / LongLive checkpoints into it as its README describes; the environment of [`setup`](../../setup/README.md) runs it. `--ckpt` defaults to the paths in that README; for LongLive it is `lora.pt`, and `longlive_base.pt` is read from the same folder.

```bash
git clone https://github.com/In-Distribution-Forcing/ID-Forcing && git -C ID-Forcing checkout 4cd6a4c
python integrations/id_forcing/generate.py --generator self_forcing --rule on --idf-code ID-Forcing \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/id_forcing
python integrations/id_forcing/generate.py --generator longlive --rule off --idf-code ID-Forcing \
    --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/id_forcing
```

**Outputs.** `<out>/<generator>/rule_<on|off>/seed<s>/<idx:03d>.mp4` (16 fps) and a `.json` with the prompt, length, timings and two counters: `rule_commits`, the number of commit passes made by Commit Forcing (every chunk after chunk 0 on LongLive, every chunk from chunk 7 on for Self-Forcing; 0 with `--rule off`), and `prefix_frames`, these commits counted by how many latent frames of earlier chunks they attended to (3 for LongLive's chunk 1, otherwise 6). The script stops if the counters do not match this pattern.

**Noise.** ID-Forcing's rollouts seed themselves; we pass them `seed * 100003 + idx`, the per-prompt seed of this repository. On Self-Forcing the whole noise tape is drawn right after seeding, and the sampler's re-noising is seeded with that value + 1. On LongLive the noise of the first 80 chunks (60 s) is drawn right after seeding and the rest when chunk 80 is reached.

## ID-Forcing's fixed noise

`--noise-seed 1356145` gives every prompt the fixed rollout noise seed of ID-Forcing's scripts instead of
`seed * 100003 + idx`. Files still live under `seed<--seed>`, and the value is recorded as `noise_seed` in each sidecar;
use a separate output root.

```bash
python integrations/id_forcing/generate.py --generator self_forcing --rule off --noise-seed 1356145 \
    --idf-code third_party/id_forcing --prompts third_party/id_forcing/prompts/moviegenbench_128.txt \
    --ids 0-127 --seconds 120 --seed 0 --out outputs/idf_authors_seed
```
