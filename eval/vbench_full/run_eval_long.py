#!/usr/bin/env python3
"""VBench-Long's eval_long.py with one fix for mode long_vbench_standard. Run it from the VBench checkout.

VBenchLong.build_full_info_json takes the video suffix from the first os.listdir entry; if that is split_clip/, the
suffix is '' and every clip is dropped. The replacement fixes the suffix to .mp4; other modes use VBench's method."""
import os
import sys

VBENCH = os.getcwd()
sys.path.insert(0, os.path.join(VBENCH, "vbench2_beta_long"))
sys.path.insert(0, VBENCH)

import vbench2_beta_long as vbl  # noqa: E402
from vbench.utils import load_json, save_json  # noqa: E402

_vbench_build = vbl.VBenchLong.build_full_info_json


def build_full_info_json(self, videos_path, name, dimension_list, prompt_list=[], special_str='', verbose=False,
                         mode='vbench_standard', **kwargs):
    if mode != 'long_vbench_standard':
        return _vbench_build(self, videos_path, name, dimension_list, prompt_list, special_str, verbose, mode, **kwargs)
    postfix = '.mp4'
    video_names = [n[:-len(postfix)] for n in os.listdir(videos_path) if n.endswith(postfix)]
    cur_full_info_list = []
    for prompt_dict in load_json(self.full_info_dir):
        if set(dimension_list) & set(prompt_dict["dimension"]):
            prompt = prompt_dict['prompt_en']
            prompt_dict['video_list'] = []
            for i in range(kwargs['num_of_samples_per_prompt']):
                folder = os.path.join(videos_path, "split_clip", f'{prompt}{special_str}-{i}')
                if not os.path.exists(folder):
                    print(f'WARNING!!! missing video clips folder: {folder}')
                    continue
                for clip in os.listdir(folder):
                    if clip.split('_')[0] in video_names:
                        prompt_dict['video_list'].append(os.path.join(folder, clip))
            cur_full_info_list.append(prompt_dict)
    path = os.path.join(self.output_path, name + '_full_info.json')
    save_json(cur_full_info_list, path)
    print(f'Evaluation meta data saved to {path} ({sum(len(d["video_list"]) for d in cur_full_info_list)} clips, '
          f'{len(cur_full_info_list)} prompts)')
    return path


vbl.VBenchLong.build_full_info_json = build_full_info_json

import eval_long  # noqa: E402  (needs the patch above)

if __name__ == "__main__":
    eval_long.main()
