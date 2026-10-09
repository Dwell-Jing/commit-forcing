#!/usr/bin/env python3
"""Self-Forcing with a per-pass, per-layer KV router: the arms of the commit-switch and read-locus analyses.

    python analysis/sf_router/generate.py --code third_party/sf_router --route S123C \
        --prompts analysis/sf_router/prompts20.txt --seconds 48 --seed 0 --out outputs/sf_router

--code is Self-Forcing at 33593df with router.patch applied; --route is a key of ROUTES (--list-routes prints them).
Outputs: <out>/<route>/seed<seed>/<idx:03d>.mp4 and .json (route, router counters, DiT time per block, motion)."""
import argparse
import math
import os
import sys

import torch
from einops import rearrange

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.runner import (Timer, latent_frames, load_prompts, parse_ids, reuse, seed_everything,  # noqa: E402
                           settings, write)

CACHE_FRAMES = 160  # 40 s of latent frames
PASSES = ("s0", "s1", "s2", "s3", "c")
BANDS = {"L0_9": "0-9", "L10_19": "10-19", "L20_29": "20-29"}


def route(base, near, far="dense", content=None, far_log_mass=None, commit_switch=None, **windows):
    """windows: pass name to per-layer window spec ('12' or '12,20-29=160'); other passes read the near window"""
    return dict(base=base, near=near, far=far, content=content, far_log_mass=far_log_mass, commit_switch=commit_switch,
                windows={p: windows.get(p, str(near)) for p in PASSES})


SF = "self_forcing"
ROUTES = {
    # commit switch: near 12, dense far reads over 160 frames
    "R12": route(SF, 12),
    "R160": route(SF, 12, s0="160", s1="160", s2="160", s3="160", c="160"),
    "S0": route(SF, 12, s0="160"),
    "S1": route(SF, 12, s1="160"),
    "S2": route(SF, 12, s2="160"),
    "S3": route(SF, 12, s3="160"),
    "S23": route(SF, 12, s2="160", s3="160"),
    "S123": route(SF, 12, s1="160", s2="160", s3="160"),
    "S123R": route(SF, 12, s1="160", s2="160", s3="160"),
    "S123C": route(SF, 12, s1="160", s2="160", s3="160", c="160"),
    "C": route(SF, 12, c="160"),
    "SWCR": route(SF, 12, s1="160", s2="160", s3="160", commit_switch=(32, "before")),
    "SWRC": route(SF, 12, s1="160", s2="160", s3="160", commit_switch=(32, "from")),
    # main tables: base (newest 21), far anchors in steps 2-3
    "G3_R21": route(SF, 21),
    "G3_L12_29": route(SF, 12, "anchors", s2="12,12-29=160", s3="12,12-29=160"),
    # read locus: near 12, far anchors (stride 4, +ln4)
    "MM_R12": route(SF, 12, "anchors"),
    "MM_ALL": route(SF, 12, "anchors", s0="160", s1="160", s2="160", s3="160"),
    "MM_S23": route(SF, 12, "anchors", s2="160", s3="160"),
    **{f"MM_S{s}_{b}": route(SF, 12, "anchors", **{f"s{s}": f"12,{lay}=160"}) for s in range(4) for b, lay in BANDS.items()},
    **{f"M4_A_{c.upper()}": route(SF, 12, "anchors", c, s3="12,20-29=160") for c in ("recent", "rand", "mean")},
    "M4_B_NORMAL": route(SF, 12, "anchors", s2="12,20-29=160", s3="12,20-29=160"),
    **{f"M4_B_{c.upper()}": route(SF, 12, "anchors", c, s2="12,20-29=160", s3="12,20-29=160") for c in ("recent", "rand", "mean")},
}


def make_router(KVRouter, spec):
    """Far log-mass: +ln(stride), plus ln(C) - ln(stride) on the dose routes (C0 = no compensation)."""
    c = spec["far_log_mass"]
    offset = 0.0 if c in (None, 4) else (math.log(c) if c else 0.0) - math.log(4)
    return KVRouter(spec["windows"], spec["near"], far=spec["far"], stride=4, far_log_mass_offset=offset,
                    content=spec["content"], commit_switch=spec["commit_switch"],
                    commit_far_window=CACHE_FRAMES if spec["commit_switch"] else None)


def build_pipeline(code, ckpt):
    """Self-Forcing's CausalInferencePipeline, KV cache of 160 latent frames, no sink, bf16 on the GPU"""
    os.chdir(code)  # upstream loads configs/ and wan_models/ by relative path
    sys.path.insert(0, code)
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline
    from utils.wan_wrapper import WanDiffusionWrapper, WanTextEncoder, WanVAEWrapper
    from wan.modules.kv_router import KVRouter

    config = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"),
                             OmegaConf.load("configs/self_forcing_dmd.yaml"))
    generator = WanDiffusionWrapper(**config.model_kwargs, is_causal=True, local_attn_size=CACHE_FRAMES, sink_size=0)
    state = torch.load(ckpt, map_location="cpu", weights_only=False)
    key = "generator_ema" if "generator_ema" in state else "generator"
    generator.load_state_dict(state[key])
    del state
    pipe = CausalInferencePipeline(config, device="cuda", generator=generator,
                                   text_encoder=WanTextEncoder(), vae=WanVAEWrapper())
    return pipe.to(device="cuda", dtype=torch.bfloat16).eval(), KVRouter, key


def motion(v01, lo, hi):
    """mean |frame_t - frame_t-1| x 255 of the decoded [0, 1] video (T, C, H, W) over [lo, hi) seconds"""
    a, b = int(lo * 16) + 1, min(int(hi * 16), v01.shape[0])
    return float(255.0 * (v01[a:b] - v01[a - 1:b - 1]).abs().mean()) if b > a else None


def check(spec, counters, frames):
    blocks = frames // 3
    assert all(n == blocks for n in counters["calls"].values()), counters["calls"]
    far_passes = {p for p in PASSES[:4] if max(int(x.split("=")[-1]) for x in spec["windows"][p].split(",")) > spec["near"]}
    if spec["far"] == "anchors" and frames > spec["near"] + 4 + 3:
        assert set(counters["far_reads"]) == far_passes, (counters["far_reads"], far_passes)
    if spec["content"]:
        assert counters["content_calls"] == sum(counters["far_reads"].values()) > 0, counters


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--route", help="a preset of ROUTES")
    parser.add_argument("--code", help="Self-Forcing 33593df checkout + router.patch")
    parser.add_argument("--prompts", help="text file, one prompt per line")
    parser.add_argument("--ids", default="all", help="prompt indices: 'all', '0-199', or '0,5,7'")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seconds", type=float, default=48.0, help="video length; a whole number of blocks (0.75 s)")
    parser.add_argument("--out", help="output root")
    parser.add_argument("--ckpt", help="default: <code>/checkpoints/self_forcing_dmd.pt")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--list-routes", action="store_true", help="print the route table and exit")
    args = parser.parse_args()
    if args.list_routes:
        for name, spec in ROUTES.items():
            extra = [f"{k} {spec[k]}" for k in ("content", "far_log_mass", "commit_switch") if spec[k] is not None]
            print(f"{name:22s} {spec['base']:15s} near {spec['near']:3d} {spec['far']:8s} " +
                  " ".join(f"{p}={spec['windows'][p]}" for p in PASSES) + ("  " + ", ".join(extra) if extra else ""))
        return
    for need in ("route", "code", "prompts", "out"):
        if getattr(args, need) is None:
            parser.error(f"--{need} is required")
    spec = ROUTES[args.route]
    args.code, args.prompts, args.out = map(os.path.abspath, (args.code, args.prompts, args.out))
    if args.ckpt is None:
        args.ckpt = os.path.join(args.code, "checkpoints", "self_forcing_dmd.pt")
    args.ckpt = os.path.abspath(args.ckpt)
    prompts = load_prompts(args.prompts)
    frames = latent_frames(args.seconds)
    out_dir = os.path.join(args.out, args.route, f"seed{args.seed}")
    os.makedirs(out_dir, exist_ok=True)
    paths = lambda i: (os.path.join(out_dir, f"{i:03d}.mp4"), os.path.join(out_dir, f"{i:03d}.json"))
    ids = [i for i in parse_ids(args.ids, len(prompts)) if not reuse(paths(i)[1], settings(args, i), args.overwrite)]
    if not ids:
        return
    pipe, KVRouter, payload = build_pipeline(args.code, args.ckpt)
    router = make_router(KVRouter, spec)
    pipe.generator.model.set_router(router)
    for idx in ids:
        noise_seed = seed_everything(args.seed, idx)
        router.reset(noise_seed)
        with Timer() as timer:
            noise = torch.randn([1, frames, 16, 60, 104], device="cuda", dtype=torch.bfloat16)
            with torch.no_grad():
                video = pipe.inference(noise=noise, text_prompts=[prompts[idx]])
        counters = router.summary()
        check(spec, counters, frames)
        v01 = video[0].float()
        meta = dict(base=spec["base"], route=args.route, spec=spec, ckpt=args.ckpt, ckpt_payload=payload, idx=idx,
                    seed=args.seed, noise_seed=noise_seed, prompt=prompts[idx], seconds=args.seconds,
                    latent_frames=frames, video_frames=video.shape[1], counters=counters,
                    dit_ms_per_block=sum(counters["dit_ms"].values()) / (frames // 3),
                    motion_early_4_8=motion(v01, 4.0, 8.0), motion_late_38_47=motion(v01, 38.0, 47.5),
                    wall_s=round(timer.seconds, 1))
        write(*paths(idx), 255.0 * rearrange(video, "b t c h w -> b t h w c").cpu()[0],
              dict(meta, settings=settings(args, idx)))
        del video, v01
        pipe.vae.model.clear_cache()
        torch.cuda.empty_cache()
        print(f"[sf_router] {args.route} seed {args.seed} idx {idx:03d}: {timer.seconds:.0f} s, "
              f"DiT {meta['dit_ms_per_block']:.0f} ms/block, far kept {counters['far_kept']:.3f}", flush=True)


if __name__ == "__main__":
    main()
