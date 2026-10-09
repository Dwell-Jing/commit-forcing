#!/usr/bin/env python3
"""Stage the videos of one arm for VBench-Long: link, split into clips once, cut into shards.

    python eval/vbench_long/prep.py --vbench /path/to/VBench --videos outputs/sgf/rule_on --label sgf_rule_on \
        --seeds 0 --num-prompts 200 --work vb_work [--shards 8]

Input: <videos>/seed<s>/<prompt:03d>.mp4 and its .json sidecar, as written by integrations/<base>/generate.py.
Output in --work: <label>/ (links, split_clip/, videos.json), shards/<label>__k<j>/, jobs.txt (read by score.sh)."""
import argparse
import json
import os
import sys


def link(src, dst):
    if not os.path.lexists(dst):
        os.symlink(os.path.abspath(src), dst)
    assert os.path.realpath(dst) == os.path.realpath(src), f"{dst} links elsewhere: use another --label"


def finished(mp4):
    js = mp4[:-len(".mp4")] + ".json"
    assert os.path.exists(mp4) and os.path.exists(js), f"missing video {mp4}"
    meta = json.load(open(js))
    assert "frames_md5" in meta, f"unfinished video {mp4}"
    return meta


def stage(args):
    d = os.path.join(args.work, args.label)
    os.makedirs(d, exist_ok=True)
    src, md5, seconds = {}, {}, set()
    for s in args.seeds:
        assert 0 <= s <= 9, "the staged name p<seed><prompt:03d> holds one seed digit"
        for i in range(args.num_prompts):
            name = f"p{s}{i:03d}-0.mp4"
            src[name] = os.path.join(args.videos, f"seed{s}", f"{i:03d}.mp4")
            meta = finished(src[name])
            md5[name] = meta["frames_md5"]
            seconds.add(meta.get("settings", {}).get("seconds"))
    assert len(seconds) == 1, f"videos of different lengths (s): {sorted(map(str, seconds))}"
    manifest = os.path.join(d, "videos.json")
    if os.path.exists(manifest):
        assert json.load(open(manifest)) == md5, \
            f"{d} was staged from other videos: use another --label, or delete it with its shards and results"
    for name, f in src.items():
        link(f, os.path.join(d, name))
    with open(manifest + ".tmp", "w") as fh:
        json.dump(md5, fh, indent=1)
    os.replace(manifest + ".tmp", manifest)
    return d


def split(d, vbench):
    sys.path.insert(0, vbench)
    import torch
    from vbench2_beta_long import VBenchLong
    vb = VBenchLong(torch.device("cpu"), os.path.join(vbench, "vbench2_beta_long", "VBench_full_info.json"), "/tmp")
    vb.preprocess(d, "long_custom_input", use_semantic_splitting=False, preprocess_dimension_flag=["subject_consistency"],
                  clip_length_config="clip_length_mix.yaml", static_filter_flag=False)


def shard(d, args):
    vids = sorted(f for f in os.listdir(d) if f.endswith(".mp4"))
    assert len(vids) == len(args.seeds) * args.num_prompts == len(os.listdir(os.path.join(d, "split_clip")))
    clips = {f: sum(c.endswith(".mp4") for c in os.listdir(os.path.join(d, "split_clip", f[:-4]))) for f in vids}
    most = max(clips.values())
    short = sorted(f[:-4] for f, n in clips.items() if n < most)
    assert not short, f"interrupted clip split: delete {d}/split_clip/<name> for {short[:5]} and run again"
    jobs = []
    for j in range(args.shards):
        sh = os.path.join(args.work, "shards", f"{args.label}__k{j}")
        os.makedirs(os.path.join(sh, "split_clip"), exist_ok=True)
        for f in vids[j::args.shards]:
            link(os.path.join(d, f), os.path.join(sh, f))
            link(os.path.join(d, "split_clip", f[:-4]), os.path.join(sh, "split_clip", f[:-4]))
        jobs.append(f"{args.label}__k{j}")
    path = os.path.join(args.work, "jobs.txt")
    old = open(path).read().split() if os.path.exists(path) else []
    with open(path + ".tmp", "w") as f:
        f.write("\n".join(old + [j for j in jobs if j not in old]) + "\n")
    os.replace(path + ".tmp", path)
    print(f"{args.label}: staged {len(vids)} videos in {args.shards} shards")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vbench", required=True, help="VBench checkout (commit 45e79ec)")
    p.add_argument("--videos", required=True, help="<out>/rule_<on|off> folder of a generate.py run")
    p.add_argument("--label", required=True, help="arm name used in the CSV and the tables")
    p.add_argument("--seeds", default="0", type=lambda s: [int(x) for x in s.split(",")])
    p.add_argument("--num-prompts", type=int, default=200)
    p.add_argument("--work", required=True, help="VBench-Long work folder, shared by all arms")
    p.add_argument("--shards", type=int, default=8)
    args = p.parse_args()
    d = stage(args)
    split(d, os.path.abspath(args.vbench))
    shard(d, args)


if __name__ == "__main__":
    main()
