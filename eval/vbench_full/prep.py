#!/usr/bin/env python3
"""Stage one arm for full VBench: name the videos by VBench's prompts, split them into clips, cut into shards.

    python eval/vbench_full/prep.py --vbench VBench --videos outputs/sgf/rule_on --label sgf+rule --work vbs_work

Input: <videos>/seed<s>/<index:03d>.mp4 per line of all_dimension.txt, generated from VBench's Wan2.1 extension.
Output in --work: <label>/ (all/ with clips, <dimension>__s<j>/ shards, videos.json) and jobs.txt for score.sh."""
import argparse
import json
import math
import multiprocessing as mp
import os
import shutil
import sys

AUGMENTED = "prompts/augmented_prompts/Wan2.1-T2V-1.3B/all_dimension_aug_wanx_seed42.txt"
FULL_INFO = "vbench2_beta_long/VBench_full_info.json"
PER_SHARD = 10
FPS = 16


def link(src, dst):
    if not os.path.lexists(dst):
        os.symlink(os.path.abspath(src), dst)
    assert os.path.realpath(dst) == os.path.realpath(src), f"{dst} links elsewhere"


def split(args):
    vbench, folder = args
    sys.path.insert(0, vbench)
    import torch
    from vbench2_beta_long import VBenchLong
    vb = VBenchLong(torch.device("cpu"), os.path.join(vbench, FULL_INFO), folder.rstrip("/") + "_out")
    vb.preprocess(folder, "long_vbench_standard", use_semantic_splitting=False, clip_length_config="clip_length_mix.yaml",
                  static_filter_flag=False, preprocess_dimension_flag=None)
    return folder


def video_frames(path):
    from decord import VideoReader, cpu
    return len(VideoReader(path, ctx=cpu(0), num_threads=1))


def clip_count(folder):
    return len([x for x in os.listdir(folder) if x.endswith(".mp4")]) if os.path.isdir(folder) else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vbench", required=True, help="VBench checkout (commit 45e79ec)")
    p.add_argument("--videos", required=True, help="<out>/rule_<on|off> folder of a generate.py run")
    p.add_argument("--label", required=True, help="arm name in the CSV and tables (no spaces)")
    p.add_argument("--seed", type=int, default=0, help="generation seed (folder <videos>/seed<seed>)")
    p.add_argument("--work", required=True, help="full-VBench work folder, shared by all arms")
    p.add_argument("--workers", type=int, default=8, help="parallel splitting processes")
    args = p.parse_args()
    vbench = os.path.abspath(args.vbench)
    info = json.load(open(os.path.join(vbench, FULL_INFO)))
    augmented = open(os.path.join(vbench, AUGMENTED)).read().split("\n")[:946]
    assert len(info) == 946 and " " not in args.label
    row_of = {}
    lines_of = {}
    for i, entry in enumerate(info):
        lines_of.setdefault(entry["prompt_en"], []).append(i)
        for dim in entry["dimension"]:
            assert (entry["prompt_en"], dim) not in row_of
            row_of[(entry["prompt_en"], dim)] = i
    names = list(lines_of)
    assert not any("_" in n or "/" in n for n in names), "VBench-Long parses clip names on '_' and '/'"
    src, md5 = {}, {}
    for i in range(946):
        f = os.path.join(args.videos, f"seed{args.seed}", f"{i:03d}.mp4")
        assert os.path.exists(f) and os.path.exists(f[:-4] + ".json"), f"missing video {f}"
        meta = json.load(open(f[:-4] + ".json"))
        assert "frames_md5" in meta, f"unfinished video {f}"
        prompt = meta.get("settings", {}).get("prompt", meta.get("prompt"))
        assert prompt == augmented[i].strip(), f"{f} was not generated from line {i}"
        src[i], md5[f"{i:03d}"] = f, meta["frames_md5"]
    frames = video_frames(src[0])
    clips_per_name = {n: math.ceil(frames / (FPS * max(_clip_lengths(vbench)[d] for i in lines_of[n]
                                                         for d in info[i]["dimension"]))) for n in names}

    arm = os.path.join(args.work, args.label)
    every = os.path.join(arm, "all")
    os.makedirs(os.path.join(every, "split_clip"), exist_ok=True)
    manifest = os.path.join(arm, "videos.json")
    if os.path.exists(manifest):
        assert json.load(open(manifest)) == md5, \
            f"{arm} was staged from other videos: use another --label, or delete it with its results"
    with open(manifest + ".tmp", "w") as fh:
        json.dump(md5, fh, indent=1)
    os.replace(manifest + ".tmp", manifest)
    folders = {}  # line: (video link, clip folder)
    for n in names:
        link(src[lines_of[n][0]], os.path.join(every, f"{n}-0.mp4"))
        folders[lines_of[n][0]] = (os.path.join(every, f"{n}-0.mp4"), os.path.join(every, "split_clip", f"{n}-0"))
    for n in names:
        for i in lines_of[n][1:]:  # repeated prompts
            d = os.path.join(arm, "_line", str(i))
            os.makedirs(d, exist_ok=True)
            link(src[i], os.path.join(d, f"{n}-0.mp4"))
            folders[i] = (os.path.join(d, f"{n}-0.mp4"), os.path.join(d, "split_clip", f"{n}-0"))

    want = {i: clips_per_name[info[i]["prompt_en"]] for i in folders}
    todo = [lines_of[n][0] for n in names if clip_count(folders[lines_of[n][0]][1]) != want[lines_of[n][0]]]
    if todo:  # first lines, split in parallel
        tmp = os.path.join(arm, "_split")
        shutil.rmtree(tmp, ignore_errors=True)
        subsets = [os.path.join(tmp, str(k)) for k in range(args.workers)]
        for k, i in enumerate(todo):
            os.makedirs(subsets[k % args.workers], exist_ok=True)
            link(src[i], os.path.join(subsets[k % args.workers], os.path.basename(folders[i][0])))
        with mp.Pool(args.workers) as pool:
            for folder in pool.imap_unordered(split, [(vbench, d) for d in subsets if os.path.isdir(d)]):
                for x in os.listdir(os.path.join(folder, "split_clip")):
                    shutil.rmtree(os.path.join(every, "split_clip", x), ignore_errors=True)
                    os.rename(os.path.join(folder, "split_clip", x), os.path.join(every, "split_clip", x))
        shutil.rmtree(tmp)
    for n in names:  # later lines, one folder each
        for i in lines_of[n][1:]:
            if clip_count(folders[i][1]) != want[i]:
                shutil.rmtree(os.path.dirname(folders[i][1]), ignore_errors=True)
                split((vbench, os.path.dirname(folders[i][0])))
    bad = {i: (clip_count(c), want[i]) for i, (_, c) in folders.items() if clip_count(c) != want[i]}
    assert not bad, f"clip counts (got, want) off for {len(bad)} videos: {list(bad.items())[:3]}"

    jobs = []
    for dim in sorted({d for entry in info for d in entry["dimension"]}):
        prompts = [n for n in names if (n, dim) in row_of]
        k = max(1, round(len(prompts) / PER_SHARD))
        for j in range(k):
            shard = os.path.join(arm, f"{dim}__s{j}")
            shutil.rmtree(shard, ignore_errors=True)
            os.makedirs(os.path.join(shard, "split_clip"))
            for n in prompts[j::k]:
                video, clips = folders[row_of[(n, dim)]]
                link(os.path.realpath(video), os.path.join(shard, f"{n}-0.mp4"))
                os.symlink(os.path.abspath(clips), os.path.join(shard, "split_clip", f"{n}-0"))
            json.dump([info[row_of[(n, dim)]] for n in prompts[j::k]], open(shard + ".full_info.json", "w"))
            jobs.append(f"{args.label} {dim} {j}")
    path = os.path.join(args.work, "jobs.txt")
    old = open(path).read().splitlines() if os.path.exists(path) else []
    with open(path + ".tmp", "w") as f:
        f.write("\n".join(old + [j for j in jobs if j not in old]) + "\n")
    os.replace(path + ".tmp", path)
    print(f"{args.label}: staged 946 videos ({len(names)} prompts, {frames} frames each), {len(jobs)} shards")


def _clip_lengths(vbench, cache={}):
    if not cache:
        import yaml
        cache.update(yaml.safe_load(open(os.path.join(vbench, "vbench2_beta_long", "configs", "clip_length_mix.yaml"))))
    return cache


if __name__ == "__main__":
    main()
