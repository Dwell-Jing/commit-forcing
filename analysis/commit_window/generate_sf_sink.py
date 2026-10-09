"""Self-Forcing + 3-frame sink: the commit pass reads the newest N real frames and no sink (N = 3, 6, ..., 21).

    python analysis/commit_window/generate_sf_sink.py --commit-frames 3 --code /path/to/Self-Forcing \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window

Needs Self-Forcing at 33593df with integrations/recency_forcing/commit_rule.patch applied; N = 21 is the commit rule.
Outputs: <out>/sf_sink_commit<N>/seed<seed>/<i:03d>.mp4 and a JSON sidecar with the attention counters."""
import argparse
import importlib.util
import os
import sys

import torch

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
from common.runner import (Timer, latent_frames, load_prompts, parse_ids, reuse, seed_everything,  # noqa: E402
                           settings, write)

_spec = importlib.util.spec_from_file_location("recency_forcing_integration",
                                               os.path.join(REPO, "integrations", "recency_forcing", "generate.py"))
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)
LAYERS = 30


def check(counts, frames, n):
    """Commit pass: never the sink, n frames in every block whose cache holds more than n."""
    blocks = frames // 3
    want = LAYERS * sum(1 for k in range(1, blocks + 1) if min(3 * k, rf.CACHE_FRAMES) > n)
    got = counts.get("commit_rule", {}).get("commit", 0)
    sink_at_commit = sum(counts.get(e, {}).get("commit", 0) for e in ("sink_shifted", "sink_in_place"))
    shifted = all(counts.get("sink_shifted", {}).get(f"step{i}", 0) > 0 for i in range(4))
    if got != want or sink_at_commit or (frames > rf.CACHE_FRAMES and not shifted):
        raise RuntimeError(f"activation check failed: {counts}, want commit_rule {want} at commit")


def main():
    parser = argparse.ArgumentParser(description="Self-Forcing + sink: commit window of N frames")
    parser.add_argument("--commit-frames", type=int, required=True, choices=range(3, 22, 3), metavar="{3,6,...,21}")
    parser.add_argument("--code", required=True, help="Self-Forcing checkout (33593df), patched")
    parser.add_argument("--prompts", required=True, help="text file, one prompt per line")
    parser.add_argument("--ids", default="all", help="prompt indices: 'all', '0-199', or '0,5,7'")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seconds", type=float, default=60.0, help="video length; a whole number of blocks")
    parser.add_argument("--out", required=True, help="output root")
    parser.add_argument("--ckpt", help="default: <code>/checkpoints/self_forcing_dmd.pt")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    n = args.commit_frames
    code, prompts_path = os.path.abspath(args.code), os.path.abspath(args.prompts)
    ckpt = os.path.abspath(args.ckpt or os.path.join(code, "checkpoints", "self_forcing_dmd.pt"))
    folder = os.path.join(os.path.abspath(args.out), f"sf_sink_commit{n}", f"seed{args.seed}")
    os.makedirs(folder, exist_ok=True)
    path = lambda idx, ext: os.path.join(folder, f"{idx:03d}.{ext}")
    prompts = load_prompts(prompts_path)
    frames = latent_frames(args.seconds)
    ids = [i for i in parse_ids(args.ids, len(prompts))
           if not reuse(path(i, "json"), settings(args, i), args.overwrite)]
    if not ids:
        return
    pipe = rf.build_pipeline(code, ckpt)
    counts = pipe.generator.model.set_cache_reading(recent_frames=rf.RECENT_FRAMES, recency_bias=False, commit_frames=n)
    for idx in ids:
        counts.clear()
        noise_seed = seed_everything(args.seed, idx)
        with Timer() as timer:
            video = rf.generate(pipe, prompts[idx], frames)
        check(counts, frames, n)
        meta = dict(base="self_forcing_sink", reading="native", commit_frames=n, idx=idx, seed=args.seed,
                    noise_seed=noise_seed, prompt=prompts[idx], seconds=args.seconds, latent_frames=frames,
                    video_frames=video.shape[0], counters=counts, wall_seconds=round(timer.seconds, 1))
        write(path(idx, "mp4"), path(idx, "json"), video, dict(meta, settings=settings(args, idx)))
        pipe.vae.model.clear_cache()
        torch.cuda.empty_cache()
        print(f"[sf_sink_commit{n}] seed {args.seed} prompt {idx:03d}: {counts}, {timer.seconds:.0f} s", flush=True)


if __name__ == "__main__":
    main()
