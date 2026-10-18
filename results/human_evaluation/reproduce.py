"""Check the released anonymous aggregate counts; preserve recorded intervals."""

import json
from pathlib import Path


def main():
    summary = json.loads(Path(__file__).with_name("summary.json").read_text())
    print("Comparison/criterion\tCF\tOther\tTie\tWin share")
    for name, result in summary["results"].items():
        wins, losses, ties = (result[k] for k in ("cf", "other", "tie"))
        expected = result["prompts"] * result["response_units"]
        if wins + losses + ties != expected:
            raise ValueError(f"Count coverage mismatch: {name}")
        share = wins / (wins + losses)
        if abs(share - result["share"]) > 1e-14:
            raise ValueError(f"Win-share mismatch: {name}")
        lo, hi = result["ci"]
        if not 0 <= lo <= share <= hi <= 1:
            raise ValueError(f"Invalid recorded interval: {name}")
        significant = lo > 0.5 or hi < 0.5
        if significant != result["significant_vs_50_percent"]:
            raise ValueError(f"Recorded interval decision mismatch: {name}")
        print(f"{name}\t{wins}\t{losses}\t{ties}\t{share:.2%}")


if __name__ == "__main__":
    main()
