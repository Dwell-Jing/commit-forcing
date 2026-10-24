"""LongLive (NVlabs/LongLive @ e52d9ef) with or without Recent-Context Committing.

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


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="LongLive with or without Recent-Context Committing")
    add_common_args(parser)
    parser.add_argument("--code", required=True, help="LongLive checkout with commit_rule.patch applied")
    parser.add_argument("--lora", help="LoRA checkpoint (default: lora_ckpt of the config)")
    parser.add_argument("--commit-profile", choices=["recent6", "legacy12"], default="recent6",
                        help="on: recent6 reads 6 frames with base 12-frame storage; legacy12 reads 12 with 15-frame storage")
    args = parser.parse_args(argv)
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

    if getattr(CausalInferencePipeline, "COMMIT_RULE_VERSION", 0) < 2:
        sys.exit(f"{getattr(args, 'code', os.getcwd())} needs version 2 of integrations/longlive/commit_rule.patch")
    config = OmegaConf.load(CONFIG)
    config.commit_rule = args.rule == "on"
    # Existing analysis callers omit this option and retain their historical 15-frame cache.
    profile = getattr(args, "commit_profile", "legacy12")
    config.commit_frames = 6 if profile == "recent6" else 12
    config.commit_cache_extra_frames = 0 if profile == "recent6" else config.model_kwargs.sink_size
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
    if len(layers) != 30:
        raise RuntimeError(f"expected 30 LongLive self-attention layers, found {len(layers)}")
    for m in layers:
        m.sinkless_reads = 0
        m.sinkless_read_tokens = []
    video = pipe.inference(noise=noise, text_prompts=[prompt])
    blocks = noise.shape[1] // pipe.num_frame_per_block
    counters = dict(blocks=blocks,
                    kv_cache_frames=pipe.kv_cache1[0]["k"].shape[1] // FRAME_TOKENS,
                    sinkless_attention_calls=sum(m.sinkless_reads for m in layers),
                    commit_frames=pipe.commit_frames if rule == "on" else pipe.local_attn_size,
                    commit_read_frames=sorted({n // FRAME_TOKENS for m in layers for n in m.sinkless_read_tokens}))
    want = blocks * len(layers) if rule == "on" else 0  # one per layer per commit pass
    if counters["sinkless_attention_calls"] != want:
        raise RuntimeError(f"activation check failed: {counters}, want {want} sink-free reads")
    physical = pipe.local_attn_size + (pipe.commit_cache_extra_frames if rule == "on" else 0)
    if counters["kv_cache_frames"] != physical:
        raise RuntimeError(f"cache check failed: {counters}, want {physical} physical frames")
    if rule == "on":
        lengths = [min((b + 1) * pipe.num_frame_per_block, pipe.commit_frames) * FRAME_TOKENS
                   for b in range(blocks)]
        if any(m.sinkless_read_tokens != lengths for m in layers):
            raise RuntimeError(f"commit read-length check failed: {counters}")
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
        meta = dict(base="longlive", rule=args.rule, commit_profile=args.commit_profile,
                    idx=idx, seed=args.seed, noise_seed=noise_seed,
                    prompt=prompts[idx], seconds=args.seconds, latent_frames=frames, video_frames=video.shape[0],
                    counters=counters, wall_seconds=round(timer.seconds, 1))
        save(args, idx, video, meta)
        print(f"[longlive] rule {args.rule} seed {args.seed} prompt {idx:03d}: {counters}, "
              f"{timer.seconds:.0f} s", flush=True)
        del video, noise
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
