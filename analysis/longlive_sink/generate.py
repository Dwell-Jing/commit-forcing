"""LongLive with the context of each pass set separately: sink 2x2 here, commit window in analysis/commit_window.

    python analysis/longlive_sink/generate.py --arm LLS_d0 --code /path/to/LongLive \
        --prompts analysis/longlive_sink/prompts20.txt --seconds 48 --seed 0 --out outputs/longlive_sink

Needs LongLive at e52d9ef with integrations/longlive/commit_rule.patch applied; --arm is a key of ARMS.
Outputs: <out>/<arm>/seed<seed>/<i:03d>.mp4 and a JSON sidecar with counters, motion and dit_ms_per_block."""
import argparse
import importlib.util
import os
import sys
from types import SimpleNamespace

import torch

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
from common.runner import (FPS, Timer, latent_frames, load_prompts, parse_ids, reuse,  # noqa: E402
                           seed_everything, settings, write)

_spec = importlib.util.spec_from_file_location("longlive_integration",
                                               os.path.join(REPO, "integrations", "longlive", "generate.py"))
integration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(integration)
FRAME_TOKENS = integration.FRAME_TOKENS

WINDOW = 12  # frames per pass: sink 3 + newest 9, or newest 12
ARMS = {  # arm: (denoise reads sink, commit reads sink, commit frames)
    "LLS_33": (True, True, WINDOW),
    "LLS_c0": (True, False, WINDOW),
    "LLS_d0": (False, True, WINDOW),
    "LLS_00": (False, False, WINDOW),
}


class PassContext:
    """Wraps generator.forward: sets read_sink / max_attention_size per pass class; counts and times the calls."""

    def __init__(self, pipe, denoise_sink, commit_sink, commit_frames):
        self.layers = [m for m in pipe.generator.model.modules() if hasattr(m, "read_sink")]
        self.context_noise = float(pipe.args.context_noise)
        self.window = WINDOW * FRAME_TOKENS
        self.setting = {"denoise": (denoise_sink, self.window), "commit": (commit_sink, commit_frames * FRAME_TOKENS)}
        self.forward = pipe.generator.forward
        pipe.generator.forward = self
        self.reset()

    def reset(self):
        self.calls = {"denoise": 0, "commit": 0}
        self.sinkless = {"denoise": 0, "commit": 0}
        self.events = []

    def __call__(self, *args, **kw):
        cls = "commit" if float(kw["timestep"].flatten()[-1]) == self.context_noise else "denoise"
        read_sink, size = self.setting[cls]
        for m in self.layers:
            m.read_sink, m.max_attention_size = read_sink, size
        before = sum(m.sinkless_reads for m in self.layers)
        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        start.record()
        try:
            return self.forward(*args, **kw)
        finally:
            end.record()
            self.events.append((start, end))
            self.calls[cls] += 1
            self.sinkless[cls] += sum(m.sinkless_reads for m in self.layers) - before
            for m in self.layers:
                m.read_sink, m.max_attention_size = True, self.window

    def counters(self, pipe, blocks):
        """Counters of the last video; raises if a pass ignored its setting."""
        layers = len(self.layers)
        out = dict(blocks=blocks, kv_cache_frames=pipe.kv_cache1[0]["k"].shape[1] // FRAME_TOKENS,
                   calls=dict(self.calls), sinkless_attention_calls=dict(self.sinkless),
                   commit_frames=self.setting["commit"][1] // FRAME_TOKENS)
        want = dict(calls={"denoise": 4 * blocks, "commit": blocks},
                    sinkless={c: 0 if self.setting[c][0] else n * layers for c, n in out["calls"].items()})
        if out["calls"] != want["calls"] or out["sinkless_attention_calls"] != want["sinkless"]:
            raise RuntimeError(f"activation check failed: {out}, want {want}")
        return out

    def dit_ms(self):
        torch.cuda.synchronize()
        return sum(a.elapsed_time(b) for a, b in self.events)


def motion(v01, lo, hi):
    """Mean absolute frame-to-frame change (0-255) over seconds lo-hi; None beyond the video."""
    a, b = int(lo * FPS) + 1, min(int(hi * FPS), v01.shape[0])
    return float(255.0 * (v01[a:b] - v01[a - 1:b - 1]).abs().mean()) if b > a else None


def build(args, denoise_sink, commit_sink, commit_frames):
    os.chdir(args.code)  # LongLive loads configs by relative path
    sys.path.insert(0, args.code)
    torch.set_grad_enabled(False)
    # rule "on" keeps sink + newest 12 in the cache
    pipe = integration.build_pipeline(SimpleNamespace(rule="on", ckpt=args.ckpt, lora=args.lora))
    return pipe, PassContext(pipe, denoise_sink, commit_sink, commit_frames)


def generate(pipe, ctx, prompt, noise):
    """One video as a (T, H, W, 3) tensor in [0, 255] on the CPU, plus its JSON fields."""
    from einops import rearrange

    ctx.reset()
    video = pipe.inference(noise=noise, text_prompts=[prompt])
    blocks = noise.shape[1] // pipe.num_frame_per_block
    v01 = video[0].float()
    fields = dict(counters=ctx.counters(pipe, blocks), dit_ms_per_block=ctx.dit_ms() / blocks,
                  motion_early_4_8=motion(v01, 4.0, 8.0), motion_late_38_47=motion(v01, 38.0, 47.5))
    return (255.0 * rearrange(video, "b t c h w -> b t h w c").cpu())[0], fields


def run(args, arm, denoise_sink, commit_sink, commit_frames):
    """Generate every selected prompt into <out>/<arm>/seed<seed>/, skipping finished videos."""

    for name in ("code", "prompts", "out", "ckpt", "lora"):
        if getattr(args, name, None):
            setattr(args, name, os.path.abspath(getattr(args, name)))
    prompts = load_prompts(args.prompts)
    frames = latent_frames(args.seconds)
    folder = os.path.join(args.out, arm, f"seed{args.seed}")
    os.makedirs(folder, exist_ok=True)
    path = lambda idx, ext: os.path.join(folder, f"{idx:03d}.{ext}")
    ids = [i for i in parse_ids(args.ids, len(prompts))
           if not reuse(path(i, "json"), settings(args, i), args.overwrite)]
    if not ids:
        return
    pipe, ctx = build(args, denoise_sink, commit_sink, commit_frames)
    for idx in ids:
        noise_seed = seed_everything(args.seed, idx)
        noise = torch.randn([1, frames, *integration.LATENT], device="cuda", dtype=torch.bfloat16)
        with Timer() as timer:
            video, fields = generate(pipe, ctx, prompts[idx], noise)
        meta = dict(base="longlive", arm=arm, idx=idx, seed=args.seed, noise_seed=noise_seed, prompt=prompts[idx],
                    seconds=args.seconds, latent_frames=frames, video_frames=video.shape[0],
                    denoise_reads_sink=denoise_sink, commit_reads_sink=commit_sink, **fields,
                    wall_seconds=round(timer.seconds, 1))
        write(path(idx, "mp4"), path(idx, "json"), video, dict(meta, settings=settings(args, idx)))
        print(f"[{arm}] seed {args.seed} prompt {idx:03d}: {fields['counters']}, {timer.seconds:.0f} s", flush=True)
        del video, noise
        torch.cuda.empty_cache()


def add_args(parser):
    parser.add_argument("--code", required=True, help="LongLive e52d9ef checkout + commit_rule.patch")
    parser.add_argument("--prompts", required=True, help="text file, one prompt per line")
    parser.add_argument("--ids", default="all", help="prompt indices: 'all', '0-19', or '0,5,7'")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seconds", type=float, default=48.0, help="video length; a whole number of blocks")
    parser.add_argument("--out", required=True, help="output root")
    parser.add_argument("--ckpt", help="generator checkpoint (default: LongLive config)")
    parser.add_argument("--lora", help="LoRA checkpoint (default: LongLive config)")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main():
    parser = argparse.ArgumentParser(description="LongLive sink 2x2: which passes read the sink")
    parser.add_argument("--arm", required=True, choices=list(ARMS))
    args = add_args(parser).parse_args()
    run(args, args.arm, *ARMS[args.arm])


if __name__ == "__main__":
    main()
