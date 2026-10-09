"""LongLive commit-window arms: the commit pass reads the newest N real frames and no sink (N = 3, 6, 9, 12).

    python analysis/commit_window/generate.py --commit-frames 6 --code /path/to/LongLive \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window

Needs LongLive at e52d9ef with integrations/longlive/commit_rule.patch applied. N = 12 is the commit rule.
Outputs: <out>/commit<N>/seed<seed>/<i:03d>.mp4 with a JSON sidecar."""
import argparse
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "longlive_pass_context", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "longlive_sink",
                                          "generate.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def main():
    parser = argparse.ArgumentParser(description="LongLive: commit pass reads the newest N frames")
    parser.add_argument("--commit-frames", type=int, required=True, choices=[3, 6, 9, 12])
    args = base.add_args(parser).parse_args()
    n = args.commit_frames
    base.run(args, f"commit{n}", denoise_sink=True, commit_sink=False, commit_frames=n)


if __name__ == "__main__":
    main()
