#!/usr/bin/env python3
r"""ID-Forcing (arXiv 2610.03120) on LongLive or Self-Forcing, with or without Commit Forcing.

    python integrations/id_forcing/generate.py --generator longlive --rule on --idf-code /path/to/ID-Forcing \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/id_forcing

Imports ID-Forcing from --idf-code (commit 4cd6a4c). Outputs: <out>/<generator>/rule_<on|off>/seed<s>/."""
import argparse
import importlib.util
import os
import sys
from collections import Counter
from functools import partial

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common import runner  # noqa: E402
import torch  # noqa: E402

DEFAULT_CKPT = {"self_forcing": "checkpoints/self_forcing_dmd.pt",  # relative to --idf-code
                "longlive": "checkpoints/longlive/models/lora.pt"}
CONFIG = {"self_forcing": "self_forcing_dmd.yaml", "longlive": "longlive_inference.yaml"}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--generator", choices=["longlive", "self_forcing"], required=True)
    parser.add_argument("--idf-code", required=True, help="checkout of ID-Forcing at commit 4cd6a4c")
    runner.add_common_args(parser)
    parser.add_argument("--noise-seed", type=int, default=None,
                        help="noise seed for all prompts instead of seed * 100003 + idx")
    args = parser.parse_args()
    args.idf_code = os.path.abspath(args.idf_code)  # before chdir
    args.ckpt = os.path.abspath(args.ckpt or os.path.join(args.idf_code, DEFAULT_CKPT[args.generator]))
    args.prompts = os.path.abspath(args.prompts)
    args.out = os.path.join(os.path.abspath(args.out), args.generator)
    return args


def load_idforcing(code, generator):
    """Import <generator>/idforcing.py; it needs the checkout as cwd (wan_models/ is relative)."""
    if not os.path.isdir(os.path.join(code, "wan_models")):
        sys.exit(f"{code}/wan_models not found; set up the ID-Forcing checkout first")
    folder = os.path.join(code, generator)
    os.chdir(code)
    sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location("idforcing", os.path.join(folder, "idforcing.py"))
    idf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(idf)
    return idf


def plain_lora_without_torchao():
    """peft refuses to build LoRA layers with an older torchao; report torchao as unavailable."""
    try:
        import peft.import_utils
        import peft.tuners.lora.torchao
    except ImportError:
        return
    peft.import_utils.is_torchao_available = lambda: False
    peft.tuners.lora.torchao.is_torchao_available = lambda: False


def build_pipeline(idf, args, device):
    config = os.path.join(args.idf_code, args.generator, "configs", CONFIG[args.generator])
    if args.generator == "self_forcing":
        return idf.build_pipeline(config, args.ckpt, device)
    plain_lora_without_torchao()
    base = os.path.join(os.path.dirname(args.ckpt), "longlive_base.pt")
    return idf.build_pipeline(config, base, args.ckpt, device)


def commit(idf, clean_pass, latents, start, scratch, context, commits):
    """Commit under the rule: the chunk attends to `context`, a list of (kv, rope_frame); returns its new kv."""
    F = idf.F
    frames = [frame for _, frame in context]
    assert frames == list(range(start - F * len(context), start, F)), (frames, start)
    for j, (kv, _) in enumerate(context):
        idf.place(scratch, kv, F * j)
    idf.set_indices(scratch, F * len(context), start)  # the chunk goes after the context
    clean_pass(latents, start, scratch)
    commits.append(F * len(context))
    return idf.read(scratch, F * len(context), F)


def realign(entries, rotate, F):
    """Keep the two latest entries, moved onto RoPE frames 3-5 and 6-8."""
    entries = entries[-2:]
    for j, e in enumerate(entries):
        if e["frame"] != F * (j + 1):
            e["kv"] = rotate(e["kv"], F * (j + 1) - e["frame"])
            e["frame"] = F * (j + 1)
    return entries


@torch.no_grad()
def rollout_longlive_rule(idf, pipe, cond, n_chunks, seed, device, commits):
    """ID-Forcing's LongLive rollout with the rule's commit in place of self-caching."""
    from utils.misc import set_seed  # LongLive's, from the checkout
    F, FSL, LATENT, NATIVE = idf.F, idf.FSL, idf.LATENT, idf.NATIVE_CHUNKS
    window = pipe.local_attn_size  # 12 frames: sink, two entries, the chunk
    assert window == 4 * F, window
    scratch = idf.new_kv_cache(3 * F, device)  # two context entries and the chunk
    half = 128 // 2  # complex channels per head
    freqs_t = pipe.generator.model.freqs.to(device).split([half - 2 * (half // 3), half // 3, half // 3], dim=1)[0]
    rotate = partial(idf.rotate, freqs_t=freqs_t)
    clean_pass = partial(idf.cache_clean, pipe, cond, device=device)

    set_seed(seed)  # noise of chunks 0..NATIVE-1; the rest later
    tape = torch.randn([1, NATIVE * F, *LATENT], device=device, dtype=torch.bfloat16)
    # chunk 0: base LongLive; its entry becomes the sink
    pipe._initialize_kv_cache(batch_size=1, dtype=torch.bfloat16, device=device, kv_cache_size_override=window * FSL)
    pipe._initialize_crossattn_cache(batch_size=1, dtype=torch.bfloat16, device=device)
    pipe.generator.model.local_attn_size = window
    pipe._set_all_modules_max_attention_size(window)
    den = idf.denoise(pipe, cond, tape[:, :F], 0, pipe.kv_cache1, device)
    clean_pass(den, 0, pipe.kv_cache1)
    sink = idf.read(pipe.kv_cache1, 0, F)
    pipe.kv_cache1 = None
    chunks = [den]

    cache, entries = idf.new_kv_cache(window, device), []  # entries: {"kv", "frame"}, oldest first
    for n in range(1, n_chunks):
        if n == NATIVE:
            tape = torch.randn([1, (n_chunks - NATIVE) * F, *LATENT], device=device, dtype=torch.bfloat16)
        i = n if n < NATIVE else n - NATIVE
        entries = realign(entries, rotate, F)
        idf.place(cache, sink, 0)
        for e in entries:
            idf.place(cache, e["kv"], e["frame"])
        frame = F * (len(entries) + 1)  # 3, 6, then 9 from chunk 3 on
        idf.set_indices(cache, frame, frame)
        den = idf.denoise(pipe, cond, tape[:, i * F:(i + 1) * F], frame, cache, device)
        context = ([(sink, 0)] if n <= 2 else []) + [(e["kv"], e["frame"]) for e in entries]
        entries.append(dict(kv=commit(idf, clean_pass, den, frame, scratch, context[-2:], commits), frame=frame))
        chunks.append(den)
    return torch.cat(chunks, dim=1)


@torch.no_grad()
def rollout_self_forcing_rule(idf, pipe, cond, n_chunks, seed, device, commits):
    """ID-Forcing's Self-Forcing rollout with the rule's commit in place of self-caching and re-encoding."""
    F, LATENT, NATIVE = idf.F, idf.LATENT, idf.NATIVE_CHUNKS
    torch.manual_seed(seed)  # noise tape, drawn as ID-Forcing does
    noise = torch.randn([1, n_chunks * F, *LATENT], device=device, dtype=torch.bfloat16)
    torch.manual_seed(seed + 1)  # then the sampler's re-noising
    torch.cuda.manual_seed_all(seed + 1)
    pipe._initialize_crossattn_cache(batch_size=1, dtype=torch.bfloat16, device=device)
    cache = idf.new_kv_cache(pipe, idf.CACHE_FRAMES, device)
    scratch = idf.new_kv_cache(pipe, 3 * F, device)
    rotate = partial(idf.rotate, pipe)
    clean_pass = partial(idf.cache_clean, pipe, cond)
    out = torch.zeros([1, n_chunks * F, *LATENT], device=device, dtype=torch.bfloat16)

    sink, entries = None, []
    for n in range(n_chunks):
        noisy = noise[:, n * F:(n + 1) * F]
        if n < NATIVE:  # chunks 0-6: base Self-Forcing
            den = idf.denoise(pipe, cond, noisy, n * F, cache)
            out[:, n * F:(n + 1) * F] = den
            clean_pass(den, n * F, cache)
            if n == 0:
                sink = idf.read(cache, 0, F)
            if n >= NATIVE - 2:  # base commits of chunks 5 and 6
                entries.append(dict(kv=idf.read(cache, n * F, F), frame=n * F))
            continue
        entries = realign(entries, rotate, F)
        idf.place(cache, sink, 0)
        for e in entries:
            idf.place(cache, e["kv"], e["frame"])
        idf.set_indices(cache, 3 * F, 3 * F)
        den = idf.denoise(pipe, cond, noisy, 3 * F, cache)
        out[:, n * F:(n + 1) * F] = den
        context = [(e["kv"], e["frame"]) for e in entries]
        entries.append(dict(kv=commit(idf, clean_pass, den, 3 * F, scratch, context, commits), frame=3 * F))
    return out


def expected_commits(generator, n_chunks, native_chunks):
    """Frames of history each rule commit reads: LongLive 3, then 6; Self-Forcing 6 from chunk 7 on."""
    if generator == "longlive":
        return [3] + [6] * (n_chunks - 2) if n_chunks > 1 else []
    return [6] * max(0, n_chunks - native_chunks)


def decode(pipe, latents):
    """Latents to (T, H, W, 3) uint8 on the CPU, decoded chunk by chunk like ID-Forcing's save_video()."""
    vae = pipe.vae
    vae.model.clear_cache()
    frames = []
    for start in range(0, latents.shape[1], runner.CHUNK):
        pixels = vae.decode_to_pixel(latents[:, start:start + runner.CHUNK], use_cache=True)[0]  # (t, 3, H, W)
        pixels = (pixels.to("cpu", torch.float32) * 0.5 + 0.5).clamp(0, 1)
        frames.append((pixels.permute(0, 2, 3, 1) * 255).to(torch.uint8))
    vae.model.clear_cache()
    torch.cuda.empty_cache()
    return torch.cat(frames)


def main():
    args = parse_args()
    prompts = runner.load_prompts(args.prompts)
    ids = [i for i in runner.parse_ids(args.ids, len(prompts)) if not runner.done(args, i)]
    n_chunks = runner.latent_frames(args.seconds) // runner.CHUNK
    print(f"[id_forcing] {args.generator} rule {args.rule}: {len(ids)} prompt(s) to generate, {n_chunks} chunks",
          flush=True)
    if not ids:
        return
    idf = load_idforcing(args.idf_code, args.generator)
    torch.set_grad_enabled(False)
    device = torch.device("cuda")
    pipe = build_pipeline(idf, args, device)
    rule_rollout = rollout_longlive_rule if args.generator == "longlive" else rollout_self_forcing_rule

    for idx in ids:
        noise_seed = args.seed * 100003 + idx if args.noise_seed is None else args.noise_seed
        commits = []
        with runner.Timer() as gen:
            cond = pipe.text_encoder(text_prompts=[prompts[idx]])
            if args.rule == "off":
                latents = idf.rollout(pipe, cond, n_chunks, noise_seed, device)
            else:
                latents = rule_rollout(idf, pipe, cond, n_chunks, noise_seed, device, commits)
            torch.cuda.synchronize()
        if args.rule == "on" and commits != expected_commits(args.generator, n_chunks, idf.NATIVE_CHUNKS):
            raise RuntimeError(f"rule commits {commits} do not match the window for {n_chunks} chunks")
        torch.cuda.empty_cache()
        with runner.Timer() as dec:
            frames = decode(pipe, latents)
        meta = dict(base="id_forcing", generator=args.generator, rule=args.rule, idx=idx, prompt=prompts[idx],
                    seed=args.seed, noise_seed=noise_seed, seconds=args.seconds, latent_frames=n_chunks * runner.CHUNK,
                    video_frames=int(frames.shape[0]), rule_commits=len(commits),
                    prefix_frames=dict(sorted(Counter(commits).items())),
                    gen_seconds=round(gen.seconds, 1), decode_seconds=round(dec.seconds, 1))
        runner.save(args, idx, frames, meta)
        print(f"[id_forcing] {idx:03d}: {frames.shape[0]} frames, {len(commits)} rule commits, "
              f"{gen.seconds:.0f} s generation", flush=True)
        del cond, latents, frames
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
