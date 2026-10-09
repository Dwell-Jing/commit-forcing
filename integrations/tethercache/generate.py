"""TetherCache (arXiv 2606.13035) with or without Commit Forcing.

    python integrations/tethercache/generate.py --code /path/to/TetherCache --memory tether --rule on \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/tethercache

--code: TetherCache at 37c581a, commit_rule.patch applied, wan_models/ and checkpoints/ in place.
Outputs: <out>/<memory>/rule_<on|off>/seed<s>/<idx:03d>.mp4 and .json.
"""
import argparse
import contextlib
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from common import runner  # noqa: E402

BASE = "tethercache"
LATENT = (16, 60, 104)  # latent of one 480x832 frame


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    runner.add_common_args(parser)
    parser.add_argument("--memory", choices=["tether", "fifo"], required=True,
                        help="tether: TetherCache; fifo: its FIFO baseline")
    parser.add_argument("--code", required=True, help="TetherCache checkout with commit_rule.patch applied")
    parser.add_argument("--attn", choices=["cudnn", "flash"], default="cudnn",
                        help="cudnn: PyTorch SDPA; flash: upstream flash-attn")
    args = parser.parse_args()
    # absolute paths before chdir
    args.code, args.prompts = os.path.abspath(args.code), os.path.abspath(args.prompts)
    args.ckpt = os.path.abspath(args.ckpt or os.path.join(args.code, "checkpoints", "self_forcing_dmd.pt"))
    args.out = os.path.join(os.path.abspath(args.out), args.memory)
    return args


def use_cudnn_attention():
    """Route unpadded attention through SDPA, cuDNN first; rebinds flash_attention in both modules."""
    import wan.modules.attention as attention_module
    import wan.modules.model as model_module
    from torch.nn.attention import SDPBackend, sdpa_kernel

    flash_attention = attention_module.flash_attention

    def routed(q, k, v, q_lens=None, k_lens=None, dropout_p=0., softmax_scale=None, q_scale=None, causal=False,
               window_size=(-1, -1), deterministic=False, dtype=torch.bfloat16, version=None):
        if q_lens is None and k_lens is None and q_scale is None and dropout_p == 0 and tuple(window_size) == (-1, -1):
            with sdpa_kernel([SDPBackend.CUDNN_ATTENTION, SDPBackend.FLASH_ATTENTION], set_priority=True):
                out = torch.nn.functional.scaled_dot_product_attention(
                    q.transpose(1, 2).to(dtype), k.transpose(1, 2).to(dtype), v.transpose(1, 2).to(dtype),
                    is_causal=causal, scale=softmax_scale)
            return out.transpose(1, 2).contiguous().type(q.dtype)
        return flash_attention(q, k, v, q_lens, k_lens, dropout_p, softmax_scale, q_scale, causal, window_size,
                               deterministic, dtype, version)

    attention_module.flash_attention = model_module.flash_attention = routed


def build_pipeline(args):
    """Upstream inference_long.py without its data loader, with the EMA generator weights."""
    os.chdir(args.code)
    sys.path.insert(0, args.code)
    from omegaconf import OmegaConf
    from pipeline import CausalInferencePipeline
    from tethercache import TetherCacheConfig, force_local_attn, install_tethercache
    from wan.modules import causal_model

    if not hasattr(causal_model, "COMMIT_RULE"):
        sys.exit(f"{args.code} is not patched; apply integrations/tethercache/commit_rule.patch")
    if args.attn == "cudnn":
        use_cudnn_attention()
    config = OmegaConf.merge(OmegaConf.load("configs/default_config.yaml"),
                             OmegaConf.load("configs/self_forcing_dmd.yaml"))
    pipe = CausalInferencePipeline(config, device=torch.device("cuda"))
    pipe.generator.load_state_dict(torch.load(args.ckpt, map_location="cpu", weights_only=False)["generator_ema"])
    cache = TetherCacheConfig()  # upstream defaults: K 21 = sink 3 + memory 14 + recent 4
    force_local_attn(pipe, cache.budget_size, cache.sink_size)
    if args.memory == "tether":
        install_tethercache(pipe, cache)
    pipe = pipe.to(dtype=torch.bfloat16)
    for module in (pipe.text_encoder, pipe.generator, pipe.vae):
        module.to("cuda")
    causal_model.COMMIT_RULE["rule"] = args.rule == "on"
    return pipe, cache


@contextlib.contextmanager
def decode_separately(vae):
    """Stub pipe.inference's whole-video decode; the latents are decoded in chunks afterwards."""
    vae.decode_to_pixel = lambda latent, use_cache=False: latent.new_zeros(1, 1, 3, 1, 1)
    try:
        yield
    finally:
        del vae.decode_to_pixel


@torch.no_grad()
def decode_uint8(vae, latents, chunk=30):
    """Chunked VAE decode (cache cleared once per video); returns (T, H, W, 3) uint8 on the CPU."""
    scale = [vae.mean.to(latents.device, latents.dtype), 1.0 / vae.std.to(latents.device, latents.dtype)]
    z = latents.permute(0, 2, 1, 3, 4)[0]
    vae.model.clear_cache()
    frames = []
    for start in range(0, z.shape[1], chunk):
        x = vae.model.cached_decode(z[:, start:start + chunk].unsqueeze(0).contiguous(), scale).float().clamp_(-1, 1)[0]
        x = (x * 0.5 + 0.5).clamp(0, 1)
        frames.append((255.0 * x).clamp(0, 255).to(torch.uint8).permute(1, 2, 3, 0).cpu())
    vae.model.clear_cache()
    return torch.cat(frames)


def check_counters(counters, args, cache, layers):
    """Closed-form counts: cache full from the commit of block 6; first eviction (GRAB) at block 7."""
    blocks, on = counters["blocks"], args.rule == "on"
    full = max(0, blocks - cache.budget_size // runner.CHUNK + 1)
    frames = cache.recent_size if args.memory == "tether" else cache.budget_size - cache.sink_size
    want = dict(blocks=blocks, commit_calls=blocks, rule_reads=layers * full if on else 0,
                frames_read=layers * full * frames if on else 0)
    if args.memory == "tether":
        grab_calls = layers * max(0, blocks - cache.budget_size // runner.CHUNK)
        want.update(rejections=runner.CHUNK * grab_calls - counters["admissions"], edits=counters["admissions"])
        if grab_calls and not counters["admissions"]:
            raise RuntimeError(f"GRAB admitted no frame: {counters}")
    got = {key: counters[key] for key in want}
    if got != want:
        raise RuntimeError(f"activation check failed: {got}, want {want}")


def generate(pipe, args, cache, prompt, frames, noise_seed):
    """One video as (T, H, W, 3) uint8 frames on the CPU, and the activation counters."""
    from tethercache import reset_tethercache_state
    from wan.modules.causal_model import COMMIT_RULE

    noise = torch.randn([1, frames, *LATENT], generator=torch.Generator().manual_seed(noise_seed))
    noise = noise.to("cuda", torch.bfloat16)
    COMMIT_RULE.update(commit_calls=0, rule_reads=0, frames_read=0)
    if args.memory == "tether":
        reset_tethercache_state(pipe)
    # silence upstream's step prints; decode in chunks
    with open(os.devnull, "w") as null, contextlib.redirect_stdout(null), decode_separately(pipe.vae):
        _, latents = pipe.inference(noise=noise, text_prompts=[prompt], return_latents=True)
    counters = dict(blocks=frames // runner.CHUNK, commit_calls=COMMIT_RULE["commit_calls"],
                    rule_reads=COMMIT_RULE["rule_reads"], frames_read=COMMIT_RULE["frames_read"])
    layers = [block.self_attn for block in pipe.generator.model.blocks]
    if args.memory == "tether":
        states = [layer.tether_state for layer in layers]
        counters.update(admissions=sum(s.n_admissions for s in states), rejections=sum(s.n_rejections for s in states),
                        edits=sum(s.n_edits for s in states))
    check_counters(counters, args, cache, len(layers))
    return decode_uint8(pipe.vae, latents), counters


def main():
    args = parse_args()
    prompts = runner.load_prompts(args.prompts)
    frames = runner.latent_frames(args.seconds)
    todo = [i for i in runner.parse_ids(args.ids, len(prompts)) if not runner.done(args, i)]
    if not todo:
        return
    torch.set_grad_enabled(False)
    pipe, cache = build_pipeline(args)
    for idx in todo:
        noise_seed = runner.seed_everything(args.seed, idx)
        with runner.Timer() as timer:
            video, counters = generate(pipe, args, cache, prompts[idx], frames, noise_seed)
        runner.save(args, idx, video, dict(
            base=BASE, memory=args.memory, rule=args.rule, idx=idx, seed=args.seed, noise_seed=noise_seed,
            prompt=prompts[idx], seconds=args.seconds, latent_frames=frames, video_frames=video.shape[0],
            counters=counters, attn=args.attn, ckpt=args.ckpt, wall_s=round(timer.seconds, 1)))
        print(f"[{BASE}] memory {args.memory} rule {args.rule} seed {args.seed} idx {idx:03d}: {timer.seconds:.0f} s "
              f"{counters}", flush=True)
        del video
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
