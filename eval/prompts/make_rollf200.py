#!/usr/bin/env python3
"""Rebuild rollf200.txt from a Self-Forcing checkout.

    python eval/prompts/make_rollf200.py /path/to/Self-Forcing/prompts/MovieGenVideoBench_extended.txt

Picks the lines listed in rollf200_indices.txt (0-based, 200 of them) from the prompt file.
Writes rollf200.txt next to this script, or checks the existing file against the rebuilt list."""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
prompts = open(sys.argv[1]).read().split("\n")
indices = [int(x) for x in open(os.path.join(here, "rollf200_indices.txt")).read().split()]
assert len(indices) == len(set(indices)) == 200
out = [prompts[i] for i in indices]
target = os.path.join(here, "rollf200.txt")
if os.path.exists(target):
    assert open(target).read() == "\n".join(out) + "\n", "rollf200.txt differs from the rebuilt list"
    print("rollf200.txt matches the rebuilt list")
else:
    open(target, "w").write("\n".join(out) + "\n")
    print("wrote", target)
