"""RF-TF: Self-Forcing with a sink/TRB, with or without Recent-Context Committing.

    python integrations/recency_forcing/generate.py --code /path/to/Self-Forcing --trb on --rule on \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/recency_forcing

--code: Self-Forcing at 33593df with commit_rule.patch applied, checkpoints/ and wan_models/ in place.
Outputs: <out>/reading_<native|rf>/rule_<on|off>/seed<seed>/<idx:03d>.mp4 and .json.
"""
import argparse
import os
import sys

import torch
from einops import rearrange

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from common.runner import (Timer, add_common_args, done, latent_frames, load_prompts, parse_ids,  # noqa: E402
                           save, seed_everything)
from integrations.commit_contract import check_read_counts  # noqa: E402

CACHE_FRAMES = 24  # KV cache length in latent frames
SINK_FRAMES = 3
RECENT_FRAMES = 18  # read after the sink: 12 history + 3 recent + 3 current
COMMIT_FRAMES = 6  # current clean block + immediately preceding block


def build_pipeline(code, ckpt):
    """Self-Forcing's CausalInferencePipeline with a 24-frame KV cache and a 3-frame sink."""
    os.chdir(code)  # upstream paths are relative
    sys.path.insert(0, code)
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline
    from utils.wan_wrapper import WanDiffusionWrapper, WanTextEncoder, WanVAEWrapper

    config = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"),
                             OmegaConf.load("configs/self_forcing_dmd.yaml"))
    generator = WanDiffusionWrapper(**config.model_kwargs, is_causal=True,
                                    local_attn_size=CACHE_FRAMES, sink_size=SINK_FRAMES)
    generator.load_state_dict(torch.load(ckpt, map_location="cpu", weights_only=False)["generator_ema"])
    pipe = CausalInferencePipeline(config, device="cuda", generator=generator,
                                   text_encoder=WanTextEncoder(), vae=WanVAEWrapper())
    return pipe.to(device="cuda", dtype=torch.bfloat16).eval()


def generate(pipe, prompt, frames):
    """One video as a (T, H, W, 3) float tensor in [0, 255]."""
    noise = torch.randn([1, frames, 16, 60, 104], device="cuda", dtype=torch.bfloat16)
    with torch.no_grad():
        video = pipe.inference(noise=noise, text_prompts=[prompt])
    return 255.0 * rearrange(video, "b t c h w -> b t h w c").cpu()[0]


def check(counts, args, frames):
    """Once the cache is full the sink must shift; commit rule and TRB fire only when selected."""
    reads = {int(event.removeprefix("commit_read_")): per_pass.get("commit", 0)
             for event, per_pass in counts.items() if event.startswith("commit_read_")}
    window = commit_window(args)
    check_read_counts(reads, frames // 3, 30, window)
    if frames < CACHE_FRAMES:
        return
    fired = {event: sum(per_pass.values()) for event, per_pass in counts.items()}
    assert fired.get("sink_shifted", 0) > 0, counts
    assert (fired.get("commit_rule", 0) > 0) == (args.rule == "on"), counts
    assert (fired.get("recency_bias", 0) > 0) == (args.reading == "rf"), counts


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common_args(parser)
    reading = parser.add_mutually_exclusive_group(required=True)
    reading.add_argument("--trb", choices=["on", "off"],
                         help="on: temporal recency bias; off: no attention bias")
    reading.add_argument("--reading", choices=["native", "rf"],
                         help="alias for --trb: native = off; rf = on")
    parser.add_argument("--code", required=True, help="Self-Forcing checkout with commit_rule.patch applied")
    parser.add_argument("--commit-profile", choices=["recent6", "legacy21"], default="recent6",
                        help="on: recent6 reads 6 latent frames; legacy21 retains the previous 21-frame control")
    args = parser.parse_args(argv)
    if args.trb is not None:
        args.reading = "rf" if args.trb == "on" else "native"
    return args


def commit_window(args):
    return (COMMIT_FRAMES if args.commit_profile == "recent6" else 21) if args.rule == "on" else None


def main():
    args = parse_args()
    args.code, args.prompts = os.path.abspath(args.code), os.path.abspath(args.prompts)
    args.ckpt = os.path.abspath(args.ckpt or os.path.join(args.code, "checkpoints", "self_forcing_dmd.pt"))
    args.out = os.path.join(os.path.abspath(args.out), f"reading_{args.reading}")

    prompts = load_prompts(args.prompts)
    frames = latent_frames(args.seconds)
    ids = [i for i in parse_ids(args.ids, len(prompts)) if not done(args, i)]
    if not ids:
        return
    pipe = build_pipeline(args.code, args.ckpt)
    counts = pipe.generator.model.set_cache_reading(
        recent_frames=RECENT_FRAMES, recency_bias=args.reading == "rf",
        commit_frames=commit_window(args))
    for idx in ids:
        counts.clear()
        noise_seed = seed_everything(args.seed, idx)
        with Timer() as timer:
            video = generate(pipe, prompts[idx], frames)
        check(counts, args, frames)
        save(args, idx, video, dict(
            base="recency_forcing", method="RF-TF", reading=args.reading, rule=args.rule,
            commit_profile=args.commit_profile, commit_frames=commit_window(args),
            cache_frames=CACHE_FRAMES, idx=idx, seed=args.seed,
            noise_seed=noise_seed, prompt=prompts[idx], seconds=args.seconds, latent_frames=frames,
            video_frames=video.shape[0], counters=counts, wall_s=round(timer.seconds, 1)))
        pipe.vae.model.clear_cache()
        torch.cuda.empty_cache()
        print(f"[recency_forcing] reading {args.reading} rule {args.rule} seed {args.seed} idx {idx:03d}: "
              f"{timer.seconds:.0f} s", flush=True)


if __name__ == "__main__":
    main()
