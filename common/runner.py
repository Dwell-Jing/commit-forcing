r"""Shared command line and output layout for integrations/<method>/generate.py.

    python integrations/<method>/generate.py --rule on --prompts eval/prompts/rollf200.txt --ids 0-199 \
        --seconds 60 --seed 0 --out outputs/<method>

Outputs: <out>/rule_<on|off>/seed<seed>/<i:03d>.mp4 (16 fps) and .json. A rerun skips finished videos.
"""
import argparse
import hashlib
import json
import os
import time

import torch

FPS = 16
LATENT_FRAMES_PER_SECOND = 4  # Wan2.1 VAE: 4 video frames per latent frame
CHUNK = 3  # latent frames per block
# mean abs frame difference (0-255) over [lo, hi) s, before mp4 encoding
MOTION = {"motion_early_4_8": (4.0, 8.0), "motion_late_38_47": (38.0, 47.5)}


def add_common_args(parser, default_ckpt=None):
    parser.add_argument("--rule", choices=["on", "off"], required=True,
                        help="on: commit pass reads recent frames only; off: base")
    parser.add_argument("--prompts", required=True, help="text file, one prompt per line")
    parser.add_argument("--ids", default="all", help="prompt indices: 'all', '0-199', or '0,5,7'")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seconds", type=float, default=60.0, help="video length; must be a whole number of blocks")
    parser.add_argument("--out", required=True, help="output root")
    parser.add_argument("--ckpt", default=default_ckpt, help="generator checkpoint")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def parse_ids(spec, n):
    if spec == "all":
        return list(range(n))
    ids = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            ids.extend(range(int(a), int(b) + 1))
        else:
            ids.append(int(part))
    bad = [i for i in ids if not 0 <= i < n]
    assert not bad, f"prompt indices out of range 0..{n - 1}: {bad[:5]}"
    return ids


def load_prompts(path):
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip()]


def latent_frames(seconds):
    f = round(seconds * LATENT_FRAMES_PER_SECOND)
    assert abs(f - seconds * LATENT_FRAMES_PER_SECOND) < 1e-6 and f % CHUNK == 0, \
        f"--seconds {seconds} must be a multiple of {CHUNK / LATENT_FRAMES_PER_SECOND} s (one block)"
    return f


def seed_everything(seed, idx):
    s = seed * 100003 + idx
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)
    return s


def out_paths(args, idx):
    d = os.path.join(args.out, f"rule_{args.rule}", f"seed{args.seed}")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{idx:03d}.mp4"), os.path.join(d, f"{idx:03d}.json")


NOT_SETTINGS = ("ids", "out", "overwrite", "prompts")
PATH_SETTINGS = ("code", "idf_code", "ckpt", "lora")


def settings(args, idx):
    """Prompt and options of video idx, resolved on the first call (before any chdir)."""
    if not hasattr(args, "_settings"):
        s = {k: (os.path.abspath(v) if k in PATH_SETTINGS and v else v) for k, v in vars(args).items()
             if k not in NOT_SETTINGS}
        args._settings = (json.loads(json.dumps(s, sort_keys=True)), load_prompts(args.prompts))
    s, prompts = args._settings
    return dict(s, prompt=prompts[idx])


def reuse(js, want, overwrite=False):
    """True if js is the sidecar of a finished video with settings `want`; exits if they differ."""
    if overwrite or not (os.path.exists(js) and os.path.exists(js[:-len(".json")] + ".mp4")):
        return False
    try:
        with open(js) as fh:
            meta = json.load(fh)
    except ValueError:
        return False
    if "frames_md5" not in meta:
        return False
    have = meta.get("settings") or {}
    if have != want:
        diff = sorted(k for k in set(have) | set(want) if have.get(k) != want.get(k))
        raise SystemExit(f"{js} has other settings ({', '.join(diff)}); use another --out or pass --overwrite")
    return True


def done(args, idx):
    return reuse(out_paths(args, idx)[1], settings(args, idx), args.overwrite)


def motion(video, lo, hi):
    a, b = int(lo * FPS) + 1, min(int(hi * FPS), video.shape[0])
    return float((video[a:b].float() - video[a - 1:b - 1].float()).abs().mean()) if b > a else None


def write(mp4, js, video_thwc, meta):
    """Write the mp4, then the json sidecar; its frames_md5 marks the video as finished."""
    from torchvision.io import write_video
    if os.path.exists(js):
        os.remove(js)
    frames = torch.as_tensor(video_thwc, dtype=torch.uint8).cpu()
    write_video(mp4 + ".tmp.mp4", frames, fps=FPS)
    os.replace(mp4 + ".tmp.mp4", mp4)
    meta = dict(meta, frames_md5=hashlib.md5(frames.numpy().tobytes()).hexdigest())
    with open(js + ".tmp", "w") as fh:
        json.dump(meta, fh, indent=1)
    os.replace(js + ".tmp", js)


def save(args, idx, video_thwc, meta):
    meta = dict(meta, **{k: motion(video_thwc, lo, hi) for k, (lo, hi) in MOTION.items()}, settings=settings(args, idx))
    write(*out_paths(args, idx), video_thwc, meta)


class Timer:
    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, *exc):
        self.seconds = time.time() - self.t0
