"""Rolling Sink (arXiv 2602.07775) with or without Commit Forcing.

    python integrations/rolling_sink/generate.py --code /path/to/Rolling-Sink --rule on \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/rolling_sink

--code: Rolling-Sink at e384dc7, commit_rule.patch applied, weights from its shell_scripts/download_ckpt.sh.
"""
import argparse
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from common import runner  # noqa: E402

BASE = "rolling_sink"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code", required=True, help="Rolling-Sink checkout with commit_rule.patch applied")
    runner.add_common_args(parser)
    args = parser.parse_args()
    # absolute paths, since load_pipeline chdirs
    args.code = os.path.abspath(args.code)
    args.prompts = os.path.abspath(args.prompts)
    args.out = os.path.abspath(args.out)
    args.ckpt = os.path.abspath(args.ckpt or os.path.join(args.code, "checkpoints", "self_forcing_dmd.pt"))
    return args


def load_pipeline(args):
    """Rolling Sink's pipeline with the Self-Forcing DMD generator (EMA weights)."""
    os.chdir(args.code)
    sys.path.insert(0, args.code)
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline

    config = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"),
                             OmegaConf.load("configs/self_forcing_dmd.yaml"))
    pipe = CausalInferencePipeline(config, device=torch.device("cuda"), commit_rule=args.rule == "on")
    pipe.generator.load_state_dict(torch.load(args.ckpt, map_location="cpu")["generator_ema"])
    pipe = pipe.to(dtype=torch.bfloat16)
    for module in (pipe.text_encoder, pipe.generator, pipe.vae):
        module.to("cuda")
    return pipe


def generate(pipe, prompt, latent_frames):
    """One video as a (T, H, W, 3) float tensor in [0, 255] on the CPU, and the counters."""
    layers = [block.self_attn for block in pipe.generator.model.blocks]
    for layer in layers:
        layer.num_real_commits = layer.num_replays = 0
    # upstream repeats one block of noise for every block
    noise = torch.randn([1, runner.CHUNK, 16, 60, 104], device="cuda", dtype=torch.bfloat16)
    noise = noise.repeat(1, latent_frames // runner.CHUNK, 1, 1, 1)
    video = pipe.inference(noise=noise, text_prompts=[prompt])
    pipe.vae.model.clear_cache()
    counters = {"blocks": latent_frames // runner.CHUNK,
                "real_commits": sum(layer.num_real_commits for layer in layers),
                "replays": sum(layer.num_replays for layer in layers)}
    expected = len(layers) * counters["blocks"] if pipe.commit_rule else 0
    if counters["real_commits"] != expected:
        raise RuntimeError(f"activation check failed: {counters}, want {expected} real commits")
    return 255.0 * video[0].permute(0, 2, 3, 1), counters


def main():
    args = parse_args()
    prompts = runner.load_prompts(args.prompts)
    frames = runner.latent_frames(args.seconds)
    todo = [i for i in runner.parse_ids(args.ids, len(prompts)) if not runner.done(args, i)]
    if not todo:
        return
    torch.set_grad_enabled(False)
    pipe = load_pipeline(args)
    for idx in todo:
        noise_seed = runner.seed_everything(args.seed, idx)
        with runner.Timer() as timer:
            video, counters = generate(pipe, prompts[idx], frames)
        runner.save(args, idx, video, dict(
            base=BASE, rule=args.rule, idx=idx, seed=args.seed, noise_seed=noise_seed, prompt=prompts[idx],
            seconds=args.seconds, latent_frames=frames, video_frames=video.shape[0], counters=counters,
            wall_s=round(timer.seconds, 1)))
        print(f"[{BASE}] rule {args.rule} seed {args.seed} idx {idx:03d}: {timer.seconds:.0f} s {counters}", flush=True)


if __name__ == "__main__":
    main()
