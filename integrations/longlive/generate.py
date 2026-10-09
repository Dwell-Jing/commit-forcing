"""LongLive (NVlabs/LongLive @ e52d9ef) with or without Commit Forcing.

    python integrations/longlive/generate.py --rule on --code /path/to/LongLive \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/longlive

--code: LongLive at e52d9ef, commit_rule.patch applied, weights in wan_models/ and longlive_models/.
"""
import argparse
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from common.runner import (Timer, add_common_args, done, latent_frames, load_prompts, parse_ids,  # noqa: E402
                           save, seed_everything)

CONFIG = "configs/longlive_inference.yaml"
LATENT = (16, 60, 104)  # latent of one 480x832 frame
FRAME_TOKENS = 1560  # tokens per latent frame


def parse_args():
    parser = argparse.ArgumentParser(description="LongLive with or without Commit Forcing")
    add_common_args(parser)
    parser.add_argument("--code", required=True, help="LongLive checkout with commit_rule.patch applied")
    parser.add_argument("--lora", help="LoRA checkpoint (default: lora_ckpt of the config)")
    args = parser.parse_args()
    for name in ("code", "prompts", "out", "ckpt", "lora"):  # before chdir
        if getattr(args, name):
            setattr(args, name, os.path.abspath(getattr(args, name)))
    return args


def allow_peft_without_torchao():
    """peft refuses to build LoRA layers with an older torchao; report torchao as unavailable."""
    import peft.import_utils
    import peft.tuners.lora.torchao
    try:
        peft.import_utils.is_torchao_available()
    except ImportError:
        peft.import_utils.is_torchao_available = lambda: False
        peft.tuners.lora.torchao.is_torchao_available = lambda: False


def build_pipeline(args):
    """LongLive's inference.py setup on one GPU: base weights, then the LoRA, in bf16."""
    import peft
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline
    from utils.lora_utils import configure_lora_for_model

    if not hasattr(CausalInferencePipeline, "_set_all_modules_read_sink"):
        sys.exit(f"{args.code} is not patched; apply integrations/longlive/commit_rule.patch")
    config = OmegaConf.load(CONFIG)
    config.commit_rule = args.rule == "on"
    pipe = CausalInferencePipeline(config, device=torch.device("cuda"))
    state = torch.load(args.ckpt or config.generator_ckpt, map_location="cpu")
    pipe.generator.load_state_dict(state["generator"] if "generator" in state else state["model"])
    allow_peft_without_torchao()
    pipe.generator.model = configure_lora_for_model(pipe.generator.model, model_name="generator",
                                                    lora_config=config.adapter, is_main_process=True)
    lora = torch.load(args.lora or config.lora_ckpt, map_location="cpu")
    peft.set_peft_model_state_dict(pipe.generator.model, lora.get("generator_lora", lora))
    pipe = pipe.to(dtype=torch.bfloat16)
    pipe.generator.to("cuda")
    pipe.vae.to("cuda")
    pipe.text_encoder.to("cuda")
    return pipe


def generate(pipe, prompt, noise, rule):
    """One video as a (T, H, W, 3) float tensor in [0, 255] on the CPU, and the counters."""
    from einops import rearrange

    layers = [m for m in pipe.generator.model.modules() if hasattr(m, "sinkless_reads")]
    for m in layers:
        m.sinkless_reads = 0
    video = pipe.inference(noise=noise, text_prompts=[prompt])
    blocks = noise.shape[1] // pipe.num_frame_per_block
    counters = dict(blocks=blocks,
                    kv_cache_frames=pipe.kv_cache1[0]["k"].shape[1] // FRAME_TOKENS,
                    sinkless_attention_calls=sum(m.sinkless_reads for m in layers))
    want = blocks * len(layers) if rule == "on" else 0  # one per layer per commit pass
    if counters["sinkless_attention_calls"] != want:
        raise RuntimeError(f"activation check failed: {counters}, want {want} sink-free reads")
    return (255.0 * rearrange(video, "b t c h w -> b t h w c").cpu())[0], counters


def main():
    args = parse_args()
    prompts = load_prompts(args.prompts)
    frames = latent_frames(args.seconds)
    ids = [i for i in parse_ids(args.ids, len(prompts)) if not done(args, i)]
    if not ids:
        return
    os.chdir(args.code)
    sys.path.insert(0, args.code)
    torch.set_grad_enabled(False)
    pipe = build_pipeline(args)
    for idx in ids:
        noise_seed = seed_everything(args.seed, idx)
        noise = torch.randn([1, frames, *LATENT], device="cuda", dtype=torch.bfloat16)
        with Timer() as timer:
            video, counters = generate(pipe, prompts[idx], noise, args.rule)
        meta = dict(base="longlive", rule=args.rule, idx=idx, seed=args.seed, noise_seed=noise_seed,
                    prompt=prompts[idx], seconds=args.seconds, latent_frames=frames, video_frames=video.shape[0],
                    counters=counters, wall_seconds=round(timer.seconds, 1))
        save(args, idx, video, meta)
        print(f"[longlive] rule {args.rule} seed {args.seed} prompt {idx:03d}: {counters}, "
              f"{timer.seconds:.0f} s", flush=True)
        del video, noise
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
