"""CPU-only checks for Commit Forcing read counts (latent frames)."""
from collections import Counter


def expected_read_counts(blocks, layers, window, chunk=3):
    """Current block at startup, then the available trajectory capped by the window."""
    return {n: count * layers for n, count in
            Counter(min((b + 1) * chunk, window) for b in range(blocks)).items()}


def read_count_delta(after, before):
    return {n: count - before.get(n, 0) for n, count in after.items()
            if count != before.get(n, 0)}


def check_read_counts(counts, blocks, layers, window):
    want = expected_read_counts(blocks, layers, window) if window is not None else {}
    if counts != want:
        raise RuntimeError(f"commit read counts {counts}, expected {want}")
