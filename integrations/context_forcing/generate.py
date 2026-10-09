#!/usr/bin/env python3
"""Context Forcing (arXiv 2602.06028) with or without Commit Forcing.

    python integrations/context_forcing/generate.py --code /path/to/Context-Forcing --rule on \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/context_forcing

--code: upstream copy with commit_rule.patch applied and the weights in place.
Outputs: <out>/rule_<off|on|sink-only|memory-only>/seed<seed>/<idx:03d>.mp4 and .json.
"""
import argparse
import contextlib
import os
import sys

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import torch  # noqa: E402

from common.runner import (CHUNK, Timer, add_common_args, done, latent_frames, load_prompts, parse_ids,  # noqa: E402
                           save, seed_everything)

COMMIT_READ = {"off": "full", "on": "recent", "sink-only": "no_sink", "memory-only": "no_memory"}
CONFIG = "configs/context_dmd_inference.yaml"
EMA_PREFIX = "model._fsdp_wrapped_module."


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                conflict_handler="resolve")
    add_common_args(p)
    p.add_argument("--rule", choices=list(COMMIT_READ), required=True,
                   help="off: base model; on: fast window only; others: ablations")
    p.add_argument("--code", required=True, help="Context-Forcing copy with commit_rule.patch applied")
    p.add_argument("--attn", choices=["cudnn", "flash"], default="cudnn",
                   help="cudnn: PyTorch SDPA; flash: upstream flash-attn")
    args = p.parse_args()
    for key in ("prompts", "out", "code"):
        setattr(args, key, os.path.abspath(getattr(args, key)))
    args.ckpt = os.path.abspath(args.ckpt or os.path.join(args.code, "checkpoints", "model.pt"))
    return args


def build_pipeline(args, frames):
    """Upstream inference.py setup (EMA weights, bf16)."""
    os.chdir(args.code)  # upstream paths are relative
    sys.path.insert(0, args.code)
    from omegaconf import OmegaConf
    from pipeline import CausalLongInferencePipeline
    import wan.modules.attention as wan_attention

    wan_attention.USE_CUDNN_SDPA = args.attn == "cudnn"
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.set_grad_enabled(False)
    cfg = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"), OmegaConf.load(CONFIG))
    pipe = CausalLongInferencePipeline(cfg, num_max_frames=frames, device=torch.device("cuda"))
    ema = torch.load(args.ckpt, map_location="cpu", weights_only=True)["generator_ema"]
    pipe.generator.model.load_state_dict({k.removeprefix(EMA_PREFIX): v for k, v in ema.items()})
    pipe.commit_read = COMMIT_READ[args.rule]
    return pipe.to(device="cuda", dtype=torch.bfloat16)


def generate_latents(pipe, prompt, noise):
    """pipe.inference() without its whole-video decode."""
    for block in pipe.generator.model.blocks:
        block.self_attn.commit_log.clear()
    with open(os.devnull, "w") as null, contextlib.redirect_stdout(null):  # upstream prints every step
        cond = pipe.text_encoder(text_prompts=[prompt])
        latents, _ = pipe._predict_from_context(noise=noise, initial_latent=None, conditional_dict=cond)
    return latents


def commit_counters(pipe):
    """Sum the per-layer commit_log (cached, hi, lo); each commit pass drops frames [hi, lo)."""
    blocks = pipe.generator.model.blocks
    sink = blocks[0].self_attn.sink_size
    logs = [block.self_attn.commit_log for block in blocks]
    calls = [c for log in logs for c in log]
    return dict(
        commit_passes=len(logs[0]),
        commit_layer_calls=len(calls),
        restricted_layer_calls=sum(lo > hi for _, hi, lo in calls),
        frames_cached=sum(c for c, _, _ in calls),
        frames_read=sum(c - (lo - hi) for c, hi, lo in calls),
        sink_frames_dropped=sum(max(min(lo, sink) - hi, 0) for _, hi, lo in calls),
        memory_frames_dropped=sum(max(lo - max(hi, sink), 0) for _, hi, lo in calls),
        frames_read_last_commit=sorted({c - (lo - hi) for c, hi, lo in (log[-1] for log in logs)}),
        slow_memory_frames=[int(c["dynamic_context_tokens"]) // pipe.frame_seq_length for c in pipe.kv_cache1],
    )


@torch.no_grad()
def decode_uint8(vae, latents, chunk=30):
    """Chunked VAE decode; returns (T, H, W, 3) uint8 on the CPU."""
    scale = [vae.mean.to(latents.device, latents.dtype), 1.0 / vae.std.to(latents.device, latents.dtype)]
    z = latents.permute(0, 2, 1, 3, 4)[0]
    vae.model.clear_cache()
    frames = []
    for s in range(0, z.shape[1], chunk):
        x = vae.model.cached_decode(z[:, s:s + chunk].unsqueeze(0).contiguous(), scale).float().clamp_(-1, 1)[0]
        x = (x * 0.5 + 0.5).clamp(0, 1)
        frames.append((255.0 * x).clamp(0, 255).to(torch.uint8).permute(1, 2, 3, 0).cpu())
    vae.model.clear_cache()
    return torch.cat(frames)


def main():
    args = parse_args()
    frames = latent_frames(args.seconds)
    prompts = load_prompts(args.prompts)
    ids = [i for i in parse_ids(args.ids, len(prompts)) if not done(args, i)]
    if not ids:
        return
    pipe = build_pipeline(args, frames)
    for idx in ids:
        noise_seed = seed_everything(args.seed, idx)
        noise = torch.randn([1, frames, 16, 60, 104], generator=torch.Generator("cpu").manual_seed(noise_seed))
        with Timer() as gen:
            latents = generate_latents(pipe, prompts[idx], noise.to("cuda", torch.bfloat16))
            torch.cuda.synchronize()
        counters = commit_counters(pipe)
        assert counters["commit_passes"] == frames // CHUNK, counters
        pipe.kv_cache1 = pipe.crossattn_cache = None  # free memory before decoding
        with Timer() as dec:
            video = decode_uint8(pipe.vae, latents)
        save(args, idx, video, dict(
            base="context_forcing", rule=args.rule, commit_read=pipe.commit_read, prompt=prompts[idx], idx=idx,
            seed=args.seed, noise_seed=noise_seed, seconds=args.seconds, latent_frames=frames,
            pixel_frames=int(video.shape[0]), counters=counters, attn=args.attn, ckpt=args.ckpt,
            generate_seconds=round(gen.seconds, 1), decode_seconds=round(dec.seconds, 1)))
        print(f"[context_forcing] rule {args.rule} seed {args.seed} prompt {idx:03d}: {gen.seconds:.0f} s + decode "
              f"{dec.seconds:.0f} s, commit frames read {counters['frames_read']} / cached "
              f"{counters['frames_cached']}", flush=True)
        del latents, video
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
