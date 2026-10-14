#!/usr/bin/env python3
"""SGF boundary arms: far reads, far-anchor positions and the sink in the denoising passes.

    python analysis/boundaries/sgf/generate.py --code third_party/sgf --arm SGF_RFW_ST1L20_NM \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 48 --seed 0 --out outputs/sgf_boundary

--code: upstream SGF checkout (integrations/sgf) with commit_rule.patch, then sgf_boundary.patch applied.
Outputs: <out>/<arm>/rule_<on|off>/seed<s>/<idx:03d>.mp4 with a JSON sidecar; --arm is a key of ARMS."""
import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, REPO)
from common import runner  # noqa: E402

_spec = importlib.util.spec_from_file_location("sgf_integration",
                                               os.path.join(REPO, "integrations", "sgf", "generate.py"))
sgf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sgf)


def far(stride, lo=20, hi=29, mass=False):
    """Far anchors: evicted frames with f % stride == stride - 1; mass adds ln(stride) to their logits."""
    return dict(stride=stride, layers=(lo, hi), steps=(2, 3), cap=40, mass=mass)


ARMS = {
    # rf: sink 3 + newest 18 frames, TRB in denoising passes
    "SGF_RF": dict(reading="rf", rule="off"),
    "SGF_RFW": dict(reading="rf", rule="on"),
    "SGF_RF_ST1L20_NM": dict(reading="rf", rule="off", far=far(1)),
    "SGF_RFW_ST1L20_NM": dict(reading="rf", rule="on", far=far(1)),
    "SGF_RFW_ST2L20_NM": dict(reading="rf", rule="on", far=far(2)),
    "SGF_RFW_ST4L20_NM": dict(reading="rf", rule="on", far=far(4)),
    "SGF_RFW_ST4L12_NM": dict(reading="rf", rule="on", far=far(4, lo=12)),
    "SGF_RFW_ST1L20_NM_B2": dict(reading="rf", rule="on", far=far(1), far_bias=-2.0),
    "SGF_RFW_ST1L20_NM_B0": dict(reading="rf", rule="on", far=far(1), far_bias=0.0),
    "SGF_RFW_ST4L20": dict(reading="rf", rule="on", far=far(4, mass=True)),
    "SGF_RFW_ST4L20_PA": dict(reading="rf", rule="on", far=far(4, mass=True), far_pos="sink"),
    "SGF_RFW_ST4L20_PB": dict(reading="rf", rule="on", far=far(4, mass=True), far_pos="oldest"),
    "SGF_RFW_NS": dict(reading="rf", rule="on", sink=False),
    "SGF_RFW_NS_ST1L20_NM": dict(reading="rf", rule="on", sink=False, far=far(1)),
    "SGF_RFW_NS_ST1L20_NM_B0": dict(reading="rf", rule="on", sink=False, far=far(1), far_bias=0.0),
    # native: SGF's cache, sink 3 + FIFO 6 + current 3 frames
    "SGF_N": dict(reading="native", rule="off"),
    "SGF_W": dict(reading="native", rule="on"),
    "SGF_NL": dict(reading="native", rule="off", early_window=9),
    "SGF_WL": dict(reading="native", rule="on", early_window=9),
}
KEYS = ("far_reads", "far_anchors", "sink_dropped", "pos_mapped", "pos_dropped", "early_reads")


def expected(cfg, blocks, layers, steps):
    """Closed-form boundary counters of one video; frames start leaving the 21-frame cache at block 7."""
    want = dict.fromkeys(KEYS, 0)
    f = cfg.get("far")
    if f:
        calls = (f["layers"][1] - f["layers"][0] + 1) * len(f["steps"])
        for b in range(7, blocks):
            kept = sum(1 for a in range(3, 3 * (b - 6) + 3) if a % f["stride"] == f["stride"] - 1)
            want["far_reads"] += calls
            want["far_anchors"] += calls * min(kept, f["cap"])
        want["pos_mapped"] = want["far_reads"] if cfg.get("far_pos") else 0
        want["pos_dropped"] = 3 * want["far_reads"] if cfg.get("far_pos") == "oldest" else 0
    if cfg.get("sink") is False:
        want["sink_dropped"] = layers * steps * max(0, blocks - 7)
    if cfg.get("early_window"):
        want["early_reads"] = layers * 2 * blocks
    return want


def main():
    parser = argparse.ArgumentParser(description="SGF boundary arms (far reads, positions, sink)")
    parser.add_argument("--arm", required=True, choices=list(ARMS))
    parser.add_argument("--code", required=True, help="SGF checkout, both patches applied")
    parser.add_argument("--prompts", required=True, help="text file, one prompt per line")
    parser.add_argument("--ids", default="all", help="prompt indices: 'all', '0-199', or '0,5,7'")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seconds", type=float, default=48.0, help="video length; a whole number of blocks")
    parser.add_argument("--out", required=True, help="output root")
    parser.add_argument("--ckpt", default=None, help="checkpoint (default: chunkwise release in --code)")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    cfg = ARMS[args.arm]
    assert cfg["reading"] == "rf" or not (cfg.get("far") or cfg.get("sink") is False), "far reads / sink removal: rf"
    assert cfg["reading"] == "native" or not cfg.get("early_window"), "early sink hiding: native reading"
    args.rule = cfg["rule"]
    code = os.path.abspath(args.code)
    ckpt = os.path.abspath(args.ckpt) if args.ckpt else os.path.join(code, sgf.CKPT)
    args.out = os.path.join(os.path.abspath(args.out), args.arm)
    prompts = runner.load_prompts(args.prompts)
    frames = runner.latent_frames(args.seconds)
    ids = [i for i in runner.parse_ids(args.ids, len(prompts)) if not runner.done(args, i)]
    if not ids:
        print("[sgf boundary] nothing to do")
        return

    reading = sgf.READINGS[cfg["reading"]]
    pipe, rule = sgf.load_pipeline(code, ckpt)
    from wan.modules import causal_model  # importable after load_pipeline
    assert hasattr(causal_model, "BOUNDARY"), f"{code} lacks sgf_boundary.patch"
    bound = causal_model.BOUNDARY
    rule.update(window=reading["window"] if args.rule == "on" else None, trb=reading["trb"])
    bound.update(far=cfg.get("far"), far_bias=cfg.get("far_bias"), far_pos=cfg.get("far_pos"),
                 sink=cfg.get("sink", True), early_window=cfg.get("early_window"))
    attn = [m for m in pipe.generator.modules() if isinstance(m, causal_model.CausalWanSelfAttention)]
    for i, m in enumerate(attn):
        m.boundary_layer = i
    blocks, steps = frames // pipe.num_frame_per_block, len(pipe.denoising_step_list)
    want = expected(cfg, blocks, len(attn), steps)
    for idx in ids:
        noise_seed = runner.seed_everything(args.seed, idx)
        for cache in pipe.kv_cache1 or []:
            cache.pop("far", None)  # anchors are per video
        before = {k: bound[k] for k in KEYS}
        video, counts, wall = sgf.generate(pipe, rule, reading["cache_frames"], prompts[idx], frames, noise_seed)
        sgf.check_counters(counts, blocks, len(attn), steps, args.rule == "on", reading["trb"])
        extra = {k: bound[k] - before[k] for k in KEYS}
        if extra != want:
            raise RuntimeError(f"boundary counters {extra}, expected {want}")
        meta = dict(base="sgf", arm=args.arm, reading=cfg["reading"], rule=args.rule, commit_window=rule["window"],
                    cache_frames=reading["cache_frames"], sink_frames=sgf.STREAMING["kv_cache_sink"],
                    far=cfg.get("far"), far_bias=cfg.get("far_bias"), far_pos=cfg.get("far_pos"),
                    sink_in_denoising=cfg.get("sink", True), early_window=cfg.get("early_window"), seed=args.seed,
                    idx=idx, prompt=prompts[idx], seconds=args.seconds, latent_frames=frames, ckpt=ckpt,
                    counters={**counts, **extra}, wall_s=round(wall, 1))
        runner.save(args, idx, video, meta)
        print(f"[sgf boundary] {args.arm} seed {args.seed} prompt {idx}: {wall:.0f} s {meta['counters']}", flush=True)


if __name__ == "__main__":
    main()
