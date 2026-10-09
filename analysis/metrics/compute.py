#!/usr/bin/env python3
"""Per-video metrics: DINOv2 / CLIP identity, per-second color and detail drift, and motion. One CSV row per video.

    python analysis/metrics/compute.py VIDEO_OR_DIR [...] --out metrics.csv \
        [--dino facebook/dinov2-base] [--clip openai/clip-vit-large-patch14] [--fast-processor] [--workers 8]

Directories are searched recursively for <root>/<arm>/seed<s>/<i:03d>.mp4 or <root>/<arm>_seed<s>.vid/<i>-0_ema.mp4.
Identity compares a video with the other seeds of the same prompt in the same (root, arm): pass all seeds together."""
import argparse
import csv
import glob
import json
import math
import os
import re
import warnings
from collections import defaultdict
from multiprocessing import Pool

import imageio.v2 as imageio
import numpy as np
import torch

FPS = 16.0
OPENING = (0.5, 2.0)  # identity reference window, seconds
WINDOWS = "early_4_8:4-8,mid_20_26:20-26,late_38_47:38-47.5"
MOTION = {"motion_early_4_8": (4.0, 8.0), "motion_late_38_47": (38.0, 47.5)}
DRIFT = ("sat", "con", "det", "bri")
LAYOUTS = (re.compile(r"(?P<root>.*)/(?P<arm>[^/]+)_seed(?P<seed>\d+)\.vid/(?P<prompt>\d+)-0_ema\.mp4$"),
           re.compile(r"(?P<root>.*)/(?P<arm>[^/]+)/seed(?P<seed>\d+)/(?P<prompt>\d+)\.mp4$"))


def find_videos(args):
    """[(path, (root, arm, prompt, seed))], symlinks resolved, each file once, sorted by the key."""
    found, other = {}, set()
    for arg in args:
        paths = [arg] if os.path.isfile(arg) else glob.glob(os.path.join(arg, "**", "*.mp4"), recursive=True)
        for path in paths:
            real = os.path.realpath(path)
            m = LAYOUTS[0].match(real) or LAYOUTS[1].match(real)
            if m:
                found[real] = (m["root"], m["arm"], int(m["prompt"]), int(m["seed"]))
            else:
                other.add(real)
    if other:
        print(f"skipped {len(other)} mp4 files outside the two layouts, e.g. {sorted(other)[0]}")
    return sorted(found.items(), key=lambda kv: kv[1])


def parse_windows(spec):
    """'early_4_8:4-8,...' to {name: (lo, hi)} in seconds"""
    return {name: tuple(float(x) for x in rng.split("-")) for name, rng in (s.split(":") for s in spec.split(","))}


def sample_frames(n, windows):
    """Frame indices: opening every 0.25 s in [0.5, 2) s, 6 per window (window end capped 0.4 s before the end)."""
    dur = n / FPS
    times = list(np.arange(OPENING[0], OPENING[1], 0.25))
    times += [t for lo, hi in windows.values() for t in np.linspace(lo, min(hi, dur - 0.4), 6)]
    return [i for i in sorted({int(round(t * FPS)) for t in times}) if 0 <= i < n]


def load_encoders(dino, clip, device, fast=False):
    """{tag: (image processor, embedding function)} in float32; fast=True selects torchvision processors."""
    from transformers import AutoImageProcessor, AutoModel, CLIPModel
    enc = {}
    if clip:
        m = CLIPModel.from_pretrained(clip).to(device, torch.float32).eval()
        enc["clip"] = (AutoImageProcessor.from_pretrained(clip, use_fast=fast),
                       lambda pv, m=m: m.visual_projection(m.vision_model(pixel_values=pv).pooler_output))
    m = AutoModel.from_pretrained(dino).to(device, torch.float32).eval()
    enc["dino"] = (AutoImageProcessor.from_pretrained(dino, use_fast=fast),
                   lambda pv, m=m: m(pixel_values=pv).last_hidden_state[:, 0])  # CLS token
    return enc


def embed(enc, frames, device, batch=16):
    """L2-normalised embeddings of RGB uint8 frames, {tag: (N, D) tensor on the device}."""
    from PIL import Image
    out = defaultdict(list)
    for i in range(0, len(frames), batch):
        ims = [Image.fromarray(x) for x in frames[i:i + batch]]
        with torch.no_grad():
            for tag, (proc, forward) in enc.items():
                e = forward(proc(images=ims, return_tensors="pt")["pixel_values"].to(device))
                out[tag].append(e / e.norm(dim=-1, keepdim=True))
    return {tag: torch.cat(v) for tag, v in out.items()}


def mean_direction(emb, mask):
    a = emb[torch.tensor(mask)].mean(0, keepdim=True)
    return (a / a.norm(dim=-1, keepdim=True)).cpu()


def window_embeddings(path, windows, enc, device):
    """{(tag, 'opening' or window name): mean embedding direction, None if the window has no frame}"""
    rd = imageio.get_reader(path)
    idx = sample_frames(rd.count_frames(), windows)
    frames = []
    for i in idx:
        rd.set_image_index(i)
        frames.append(np.asarray(rd.get_next_data()))
    rd.close()
    ts = np.array(idx) / FPS
    out = {}
    for tag, emb in embed(enc, frames, device).items():
        out[tag, "opening"] = mean_direction(emb, (ts >= OPENING[0]) & (ts <= OPENING[1]))
        for name, (lo, hi) in windows.items():
            m = (ts >= lo) & (ts <= hi)
            out[tag, name] = mean_direction(emb, m) if m.any() else None
    return out


def identity(emb):
    """<tag>_<window> = cos to the own opening minus mean cos to the openings of the other seeds of the prompt."""
    seeds = defaultdict(list)  # keys per (root, arm, prompt)
    for key in sorted(emb):
        seeds[key[:3]].append(key)
    res = defaultdict(dict)
    for key in sorted(emb):
        sibs = [emb[k] for k in seeds[key[:3]] if k != key]
        for (tag, name), cur in emb[key].items():
            if name == "opening" or cur is None or not sibs:
                continue
            own = float(cur @ emb[key][tag, "opening"].T)
            oth = float(np.mean([float(cur @ s[tag, "opening"].T) for s in sibs]))
            res[key][f"{tag}_{name}"] = own - oth
    return res


def frame_stats(fr):
    """Saturation, contrast (luma std), detail (mean |Laplacian| of luma) and brightness of a frame at half size."""
    x = fr[::2, ::2].astype(np.float32) / 255.0
    mx, mn = x.max(2), x.min(2)
    sat = float(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0).mean())
    y = 0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2]
    det = float(np.abs(4 * y[1:-1, 1:-1] - y[:-2, 1:-1] - y[2:, 1:-1] - y[1:-1, :-2] - y[1:-1, 2:]).mean())
    return {"sat": sat, "con": float(y.std()), "det": det, "bri": float(y.mean())}


def motion_range(n, lo, hi):
    """(a, b): frames t whose difference to frame t - 1 falls in [lo, hi) s, or None if empty."""
    a, b = int(lo * FPS) + 1, min(int(hi * FPS), n)
    return (a, b) if b > a else None


def mean_abs_diff(x, scale=1.0):
    return float(scale * (x[1:].float() - x[:-1].float()).abs().mean())


def motion(frames, lo, hi, scale=1.0):
    """Mean |frame_t - frame_{t-1}| over frames in [lo, hi) s, 0-255 units; pass scale=255 for float frames in 0-1."""
    r = motion_range(frames.shape[0], lo, hi)
    return None if r is None else mean_abs_diff(frames[r[0] - 1:r[1]], scale)


def late_over_early(x):
    """sat_le / bri_le / det_le: mean of seconds 38-47 over mean of seconds 4-7."""
    x = np.array(x, dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.nanmean(x[38:48]) / np.nanmean(x[4:8]))


def scan(job):
    """Decode every frame once: per-second drift series (every 2nd frame) and motion."""
    path, seconds = job
    acc = {k: defaultdict(list) for k in DRIFT}
    spans = [(int(lo * FPS), int(hi * FPS)) for lo, hi in MOTION.values()]
    kept, n = {}, 0
    rd = imageio.get_reader(path)
    for i, fr in enumerate(rd):
        fr, n = np.asarray(fr), i + 1
        if any(a <= i < b for a, b in spans):
            kept[i] = fr
        if i % 2 == 0:
            for k, v in frame_stats(fr).items():
                acc[k][i // 16].append(v)
    rd.close()
    sec = seconds or math.ceil(n / FPS)  # last bin takes all later frames
    out = {"frames": n}
    for k, per in acc.items():
        bins = [per.get(t, []) for t in range(sec - 1)] + [[v for t in sorted(per) if t >= sec - 1 for v in per[t]]]
        out[k] = [float(np.mean(v)) if v else float("nan") for v in bins]
    for key, (lo, hi) in MOTION.items():
        r = motion_range(n, lo, hi)
        out[key + "_mp4"] = None if r is None else mean_abs_diff(torch.from_numpy(np.stack(
            [kept[i] for i in range(r[0] - 1, r[1])])))
    return out


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path) as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("videos", nargs="+", help="mp4 files or directories")
    ap.add_argument("--out", required=True, help="output CSV")
    ap.add_argument("--dino", default="facebook/dinov2-base", help="DINOv2 (Hugging Face id or local path)")
    ap.add_argument("--clip", help="also compute CLIP identity (clip_* columns)")
    ap.add_argument("--fast-processor", action="store_true", help="use torchvision image processors")
    ap.add_argument("--windows", default=WINDOWS, help="identity windows, name:lo-hi in seconds")
    ap.add_argument("--drift-seconds", type=int, help="number of 1 s drift bins (default: video length)")
    ap.add_argument("--workers", type=int, default=8, help="processes for decoding, drift and motion")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    videos = find_videos(a.videos)
    if not videos:
        raise SystemExit("no videos found")
    windows = parse_windows(a.windows)
    print(f"{len(videos)} videos", flush=True)
    with Pool(a.workers, initializer=torch.set_num_threads, initargs=(1,)) as pool:  # before CUDA starts
        scans = pool.map_async(scan, [(path, a.drift_seconds) for path, _ in videos])
        enc = load_encoders(a.dino, a.clip, a.device, a.fast_processor)
        emb = {}
        for n, (path, key) in enumerate(videos, 1):
            emb[key] = window_embeddings(path, windows, enc, a.device)
            if n % 20 == 0:
                print(f"identity {n}/{len(videos)}", flush=True)
        scans = scans.get()
    ident = identity(emb)
    if len(ident) < len(videos):
        print(f"no identity for {len(videos) - len(ident)} videos (no other seed of the prompt, or too short)")
    tags = ["clip", "dino"] if a.clip else ["dino"]
    sec = max(len(s["sat"]) for s in scans)
    cols = (["root", "arm", "seed", "prompt", "video", "frames"] + [f"{t}_{w}" for t in tags for w in windows]
            + list(MOTION) + [k + "_mp4" for k in MOTION] + [k + "_le" for k in DRIFT]
            + [f"{k}_{t}" for k in DRIFT for t in range(sec)])
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for (path, key), s in zip(videos, scans):
            meta = read_json(path[:-4] + ".json")
            row = dict(root=key[0], arm=key[1], prompt=key[2], seed=key[3], video=path, frames=s["frames"])
            row.update(ident.get(key, {}))
            row.update({k: meta.get(k) for k in MOTION})
            row.update({k + "_mp4": s[k + "_mp4"] for k in MOTION})
            row.update({k + "_le": late_over_early(s[k]) for k in DRIFT})
            row.update({f"{k}_{t}": v for k in DRIFT for t, v in enumerate(s[k])})
            w.writerow(["" if row.get(c) is None else row[c] for c in cols])
    print(f"{len(videos)} rows -> {a.out}")


if __name__ == "__main__":
    main()
