# Human evaluation

The paper reports three blinded comparisons on 60-second videos. Each comparison uses 18 prompt-matched pairs
from `rollf200`. Five participants contributed three response units: two individual responses and one joint response
from three people. The joint response counts once. Each comparison therefore has 54 responses per question.

## Recorded results

Win share is Commit Forcing wins divided by wins plus losses; ties are excluded from that denominator.
Intervals are the recorded 95% prompt-bootstrap intervals. Bold shares have an interval excluding 50%.

| Comparison | Criterion | CF wins | Other wins | Ties | CF win share | 95% interval |
|:---|:---|--:|--:|--:|--:|:---|
| SGF + Commit Forcing vs. SGF | Subject and scene consistency | 39 | 13 | 2 | **75.00%** | [56.60%, 90.57%] |
| SGF + Commit Forcing vs. SGF | Overall preference | 35 | 12 | 7 | **74.47%** | [56.00%, 89.80%] |
| LongLive + Commit Forcing vs. LongLive | Subject and scene consistency | 19 | 25 | 10 | 43.18% | [22.22%, 65.12%] |
| LongLive + Commit Forcing vs. LongLive | Overall preference | 20 | 24 | 10 | 45.45% | [25.00%, 67.57%] |
| LongLive + Commit Forcing vs. ID-Forcing | Subject and scene consistency | 47 | 5 | 2 | **90.38%** | [75.00%, 100.00%] |
| LongLive + Commit Forcing vs. ID-Forcing | Overall preference | 45 | 6 | 3 | **88.24%** | [70.59%, 100.00%] |

The LongLive-versus-base intervals include 50%; these comparisons do not show a significant preference.

## Presentation and sampling

Prompts were sampled without replacement before viewing. SGF versus base SGF and LongLive versus base LongLive
share an 18-prompt subset; the comparison with complete ID-Forcing uses a separate subset. All pairs share a prompt.
SGF and base-framework LongLive videos use generation seed 0. Complete ID-Forcing uses the prompt index as its
rollout seed. LongLive + Commit Forcing uses six-frame committing; the two LongLive base-framework arms store
15 physical cache frames and retain 12-frame denoising reads.

Participants viewed synchronized, side-by-side five-second excerpts from the beginning, middle and end. Method
identities were hidden and left/right positions randomized. They judged subject and scene consistency relative
to each video's own opening and overall preference from prompt alignment, visual quality and motion. Either
side or a tie was allowed. Two identical-video catch pairs were excluded from the comparison counts.

The original target was at least five independent response units. The recorded sample has three, including the
joint response described above. A protocol addendum records an organiser exclusion of one response set after
interim results, beyond the original catch-pair rule. The table uses the latest retained aggregate summary.

The recorded analysis resamples the 18 prompt clusters 4,000 times, moving all response units of a prompt together.
The participant count is not used as five independent responses per pair.

## Data and reproduction

[`summary.json`](summary.json) contains anonymous aggregate counts and the recorded intervals, transcribed from
the final author-provided summary retrieved on 2026-10-18. Individual responses and respondent identities are not
part of this release. The current protocol key and prompt selection match the earlier frozen protocol.

```bash
python results/human_evaluation/reproduce.py
```

This checks the count totals, computes win shares and verifies the stored interval-based decisions. It does not
reconstruct intervals from aggregate counts or rerun the human evaluation.

Frozen summary SHA-256: `872b367dad5abb6e84a19940f8646e7740669bac90dd8cf20539436f3eb48273`.
