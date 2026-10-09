#!/usr/bin/env python3
r"""SGF+ (Self Gradient Forcing Plus, chunkwise, arXiv 2610.10429) with or without Commit Forcing.

    python integrations/sgf_plus/generate.py --rule on --code ../Self_Gradient_Forcing_Plus \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf_plus

--code: Self_Gradient_Forcing_Plus at 14cda9b, commit_rule.patch applied, Wan2.1-T2V-1.3B in <code>/wan_models.
--ckpt defaults to <code>/hf_weights/chunkwise/model.pt.
"""
import argparse
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common import runner  # noqa: E402

WINDOW = 9  # latent frames the commit pass reads with --rule on
# KV cache: sink 3 + FIFO 6 + current 3 latent frames
GEOMETRY = dict(kv_cache_max_frames=12, kv_cache_sink=3, kv_cache_train_frames=21, kv_cache_position_mode="top_aligned")
COUNTERS = ("commit_calls", "rule_reads", "sink_dropped")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    runner.add_common_args(parser)
    parser.add_argument("--code", required=True, help="Self_Gradient_Forcing_Plus checkout with commit_rule.patch")
    args = parser.parse_args()
    # absolute paths before chdir
    args.code = os.path.abspath(args.code)
    args.ckpt = os.path.abspath(args.ckpt or os.path.join(args.code, "hf_weights", "chunkwise", "model.pt"))
    args.prompts = os.path.abspath(args.prompts)
    args.out = os.path.abspath(args.out)
    return args


def load_pipeline(args, device):
    """SGF+ chunkwise pipeline with the EMA generator in bf16."""
    os.chdir(args.code)
    sys.path.insert(0, args.code)
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline
    import wan.modules.causal_model as causal_model
    if not hasattr(causal_model, "COMMIT_RULE"):
        raise SystemExit(f"{args.code}: apply integrations/sgf_plus/commit_rule.patch first")

    config = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"),
                             OmegaConf.load("configs/sgf_plus_chunkwise.yaml"))
    pipe = CausalInferencePipeline(config, device=device)
    state = torch.load(args.ckpt, map_location="cpu")
    weights = "generator_ema" if "generator_ema" in state else "generator"
    pipe.generator.load_state_dict(
        {k.replace("model._fsdp_wrapped_module.", "model.", 1): v for k, v in state[weights].items()})
    del state
    pipe = pipe.to(dtype=torch.bfloat16)
    for module in (pipe.text_encoder, pipe.generator, pipe.vae):
        module.to(device=device)
    return pipe, causal_model.COMMIT_RULE, weights


def generate(pipe, prompt, frames, device):
    """One video from the current RNG state; returns (T, H, W, 3) float frames in [0, 255] on the CPU."""
    noise = torch.randn([1, frames, 16, 60, 104]).to(device, torch.bfloat16)  # drawn on the CPU
    video = pipe.inference(noise=noise, text_prompts=[prompt], long_video=True, **GEOMETRY)
    pipe.vae.model.clear_cache()
    return 255.0 * video[0].permute(0, 2, 3, 1).cpu()


def check_activation(counts, blocks, layers, rule_on):
    """One commit pass per block; with the rule on, every layer of it applies the rule."""
    want = dict(commit_calls=blocks, rule_reads=layers * blocks if rule_on else 0)
    got = {k: counts[k] for k in want}
    if got != want:
        raise RuntimeError(f"activation check failed: {got}, expected {want}")


def main():
    args = parse_args()
    prompts = runner.load_prompts(args.prompts)
    ids = [i for i in runner.parse_ids(args.ids, len(prompts)) if not runner.done(args, i)]
    frames = runner.latent_frames(args.seconds)
    if not ids:
        print("[sgf_plus] all requested videos exist")
        return

    torch.set_grad_enabled(False)
    device = torch.device("cuda")
    pipe, rule, weights = load_pipeline(args, device)
    rule.update(on=args.rule == "on", window=WINDOW)
    assert pipe.num_frame_per_block == runner.CHUNK, pipe.num_frame_per_block
    blocks, layers = frames // runner.CHUNK, len(pipe.generator.model.blocks)

    for idx in ids:
        before = {k: rule[k] for k in COUNTERS}
        noise_seed = runner.seed_everything(args.seed, idx)
        with runner.Timer() as timer:
            video = generate(pipe, prompts[idx], frames, device)
        counts = {k: rule[k] - before[k] for k in COUNTERS}
        check_activation(counts, blocks, layers, rule["on"])
        meta = dict(base="sgf_plus", rule=args.rule, window=WINDOW if rule["on"] else None, prompt=prompts[idx],
                    idx=idx, seed=args.seed, noise_seed=noise_seed, seconds=args.seconds, latent_frames=frames,
                    geometry=GEOMETRY, ckpt=args.ckpt, weights=weights, wall_s=round(timer.seconds, 1), **counts)
        runner.save(args, idx, video, meta)
        print(f"[sgf_plus] rule {args.rule} seed {args.seed} prompt {idx:03d}: {timer.seconds:.0f} s, "
              + ", ".join(f"{k} {v}" for k, v in counts.items()), flush=True)
        del video
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
