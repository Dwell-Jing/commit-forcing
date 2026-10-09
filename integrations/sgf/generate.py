#!/usr/bin/env python3
"""Self Gradient Forcing (chunkwise checkpoint) with or without Commit Forcing.

    python integrations/sgf/generate.py --code /path/to/Self_Gradient_Forcing --rule on --reading native \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/sgf

--code: github.com/zhuang2002/Self_Gradient_Forcing @ ba16e1b, commit_rule.patch applied, weights downloaded.
Outputs: <out>/<reading>/rule_<on|off>/seed<s>/<idx:03d>.mp4 and .json.
"""
import argparse
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common import runner  # noqa: E402

CONFIG = "configs/self_gradient_forcing_chunkwise.yaml"
CKPT = "checkpoints/chunkwise/ar/model.pt"
STREAMING = dict(long_video=True, kv_cache_sink=3, kv_cache_train_frames=21, kv_cache_position_mode="top_aligned")
READINGS = {  # cache_frames includes the sink; window: commit read with the rule on
    "native": dict(cache_frames=12, window=9, trb=False),
    "rf": dict(cache_frames=21, window=18, trb=True),
}
COUNTERS = ("commit_calls", "rule_reads", "trb_calls")


def load_pipeline(code, ckpt):
    """Upstream chunkwise pipeline (EMA weights, bf16); returns (pipeline, COMMIT_RULE)."""
    os.chdir(code)  # upstream paths are relative
    sys.path.insert(0, code)
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline
    from wan.modules import causal_model
    assert hasattr(causal_model, "COMMIT_RULE"), f"{code} is not patched; apply commit_rule.patch"

    torch.set_grad_enabled(False)
    config = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"), OmegaConf.load(CONFIG))
    pipe = CausalInferencePipeline(config, device=torch.device("cuda"))
    state = torch.load(ckpt, map_location="cpu")["generator_ema"]
    pipe.generator.load_state_dict({k.replace("model._fsdp_wrapped_module.", "model.", 1): v for k, v in state.items()})
    del state
    pipe = pipe.to(dtype=torch.bfloat16)
    for module in (pipe.text_encoder, pipe.generator, pipe.vae):
        module.to(device="cuda")
    return pipe, causal_model.COMMIT_RULE


def generate(pipe, rule, cache_frames, prompt, frames, noise_seed):
    """One video: (T, H, W, 3) frames in [0, 255] on the CPU, counter increments, wall seconds."""
    noise = torch.randn([1, frames, 16, 60, 104], generator=torch.Generator().manual_seed(noise_seed))
    noise = noise.to("cuda", torch.bfloat16)
    before = {k: rule[k] for k in COUNTERS}
    with runner.Timer() as timer:
        video, _ = pipe.inference(noise=noise, text_prompts=[prompt], return_latents=True,
                                  kv_cache_max_frames=cache_frames, **STREAMING)
        torch.cuda.synchronize()
    pipe.vae.model.clear_cache()
    counts = {k: rule[k] - before[k] for k in COUNTERS}
    return 255.0 * video[0].permute(0, 2, 3, 1).cpu(), counts, timer.seconds


def check_counters(counts, blocks, layers, steps, rule_on, trb):
    """One commit per block; TRB acts in every layer and step from the fourth block on (first history chunk)."""
    want = dict(commit_calls=blocks, rule_reads=layers * blocks if rule_on else 0,
                trb_calls=layers * steps * max(0, blocks - 3) if trb else 0)
    if counts != want:
        raise RuntimeError(f"activation counters {counts}, expected {want}")


def main():
    parser = argparse.ArgumentParser(description="Self Gradient Forcing with or without Commit Forcing")
    runner.add_common_args(parser)
    parser.add_argument("--reading", choices=sorted(READINGS), default="native",
                        help="native: SGF's own cache; rf: Recency Forcing reading")
    parser.add_argument("--code", required=True, help="upstream checkout with commit_rule.patch applied")
    args = parser.parse_args()

    code = os.path.abspath(args.code)  # before chdir
    ckpt = os.path.abspath(args.ckpt) if args.ckpt else os.path.join(code, CKPT)
    args.out = os.path.join(os.path.abspath(args.out), args.reading)
    prompts = runner.load_prompts(args.prompts)
    frames = runner.latent_frames(args.seconds)
    ids = [i for i in runner.parse_ids(args.ids, len(prompts)) if not runner.done(args, i)]
    if not ids:
        print("[sgf] nothing to do")
        return

    reading = READINGS[args.reading]
    pipe, rule = load_pipeline(code, ckpt)
    rule.update(window=reading["window"] if args.rule == "on" else None, trb=reading["trb"])
    blocks = frames // pipe.num_frame_per_block
    for idx in ids:
        noise_seed = runner.seed_everything(args.seed, idx)
        video, counts, wall = generate(pipe, rule, reading["cache_frames"], prompts[idx], frames, noise_seed)
        check_counters(counts, blocks, len(pipe.generator.model.blocks), len(pipe.denoising_step_list),
                       args.rule == "on", reading["trb"])
        meta = dict(base="sgf", rule=args.rule, reading=args.reading, commit_window=rule["window"],
                    cache_frames=reading["cache_frames"], sink_frames=STREAMING["kv_cache_sink"], seed=args.seed,
                    idx=idx, prompt=prompts[idx], seconds=args.seconds, latent_frames=frames, ckpt=ckpt,
                    counters=counts, wall_s=round(wall, 1))
        runner.save(args, idx, video, meta)
        print(f"[sgf] {args.reading} rule {args.rule} seed {args.seed} prompt {idx}: {wall:.0f} s {counts}", flush=True)


if __name__ == "__main__":
    main()
