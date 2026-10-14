"""LongLive commit-window arms: the commit pass reads the newest N real frames and no sink (N = 3, 6, 9, 12).

    python analysis/commit_window/generate.py --commit-frames 6 --code /path/to/LongLive \
        --prompts eval/prompts/rollf200.txt --ids 0-199 --seconds 60 --seed 0 --out outputs/commit_window

Needs LongLive at e52d9ef with integrations/longlive/commit_rule.patch applied. All these historical ablation arms
retain their 15-frame physical cache; N = 12 is the legacy rule. The main integration defaults to a 6-frame read
with 12-frame physical storage. This generator preserves the historical ablation's cache configuration.
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
    legacy_build = base.integration.build_pipeline

    def build_with_legacy_storage(build_args):
        build_args.commit_profile = "legacy12"
        return legacy_build(build_args)

    base.integration.build_pipeline = build_with_legacy_storage
    base.run(args, f"commit{n}", denoise_sink=True, commit_sink=False, commit_frames=n)


if __name__ == "__main__":
    main()
