# Human evaluation

The paper reports three blinded comparisons on 60-second videos and a separate 120-second LongLive comparison.

## 60-second study

Each 60-second comparison uses 18 prompt-matched pairs
from `rollf200`. Five participants contributed three response units: two individual responses and one joint response
from three people. The joint response counts once. Each comparison therefore has 54 responses per question.

### Recorded results

Win share is recent-context wins divided by wins plus losses; ties are excluded from that denominator.
Intervals are the recorded 95% prompt-bootstrap intervals. Bold shares have an interval excluding 50%.

| Comparison | Criterion | Recent-context wins | Other wins | Ties | Recent-context win share | 95% interval |
|:---|:---|--:|--:|--:|--:|:---|
| SGF, 9-frame recent-context control vs. SGF | Subject and scene consistency | 39 | 13 | 2 | **75.00%** | [56.60%, 90.57%] |
| SGF, 9-frame recent-context control vs. SGF | Overall preference | 35 | 12 | 7 | **74.47%** | [56.00%, 89.80%] |
| LongLive + Recent-Context Committing vs. LongLive | Subject and scene consistency | 19 | 25 | 10 | 43.18% | [22.22%, 65.12%] |
| LongLive + Recent-Context Committing vs. LongLive | Overall preference | 20 | 24 | 10 | 45.45% | [25.00%, 67.57%] |
| LongLive + Recent-Context Committing vs. ID-Forcing | Subject and scene consistency | 47 | 5 | 2 | **90.38%** | [75.00%, 100.00%] |
| LongLive + Recent-Context Committing vs. ID-Forcing | Overall preference | 45 | 6 | 3 | **88.24%** | [70.59%, 100.00%] |

The LongLive-versus-base intervals include 50%; these comparisons do not show a significant preference.

### Presentation and sampling

Prompts were sampled without replacement before viewing. SGF versus base SGF and LongLive versus base LongLive
share an 18-prompt subset; the comparison with complete ID-Forcing uses a separate subset. All pairs share a prompt.
SGF and base-framework LongLive videos use generation seed 0. Complete ID-Forcing uses the prompt index as its
rollout seed. SGF uses the 9-frame recent-context supporting control; these rates do not evaluate the updated
6-frame SGF main arm. LongLive + Recent-Context Committing uses the current and preceding blocks (6 frames);
the two LongLive base-framework arms store 15 physical cache frames and retain 12-frame denoising reads.

Participants viewed synchronized, side-by-side five-second excerpts from the beginning, middle and end. Method
identities were hidden and left/right positions randomized. They judged subject and scene consistency relative
to each video's own opening and overall preference from prompt alignment, visual quality and motion. Either
side or a tie was allowed. Two identical-video catch pairs were excluded from the comparison counts.

The reported evaluation contains the three response units described above. Pilot/test submissions are separate from these counts.

The recorded analysis resamples the 18 prompt clusters 4,000 times, moving all response units of a prompt together.
The participant count is not used as five independent responses per pair.

### Data and reproduction

[`summary.json`](summary.json) contains anonymous aggregate counts and the recorded intervals, transcribed from
the final author-provided summary retrieved on 2026-10-18. Individual responses and respondent identities are not
part of this release. The current protocol key and prompt selection match the earlier frozen protocol.

```bash
python results/human_evaluation/reproduce.py
```

This checks the count totals, computes win shares and verifies the stored interval-based decisions. It does not
reconstruct intervals from aggregate counts or rerun the human evaluation.

Frozen summary SHA-256: `872b367dad5abb6e84a19940f8646e7740669bac90dd8cf20539436f3eb48273`.

## 120-second LongLive study

This separately sampled study compares current-plus-previous-block committing with base LongLive on 30 paired
120-second videos, drawn without replacement from ID-Forcing's 128-prompt MovieGen list using a fixed random seed
before packaging. Generation seed is 0. Five people not involved in the project answer independently, giving
150 judgments per criterion. These counts are not pooled with the 60-second study.

| Criterion | Recent-context wins | Base wins | Ties | Win share | Reported 95% interval |
|:---|--:|--:|--:|--:|:---|
| Subject and scene consistency | 111 | 22 | 17 | **83.5%** | [73.2%, 92.2%] |
| Overall preference | 107 | 22 | 21 | **82.9%** | [72.6%, 92.1%] |

Each participant sees an independently randomized order, with recent-context committing on the left in 15 pairs
and on the right in 15. The presentation and two questions use synchronized five-second excerpts from the beginning,
middle and end, with method identities hidden. Two additional identical-video check pairs are outside the reported
counts. The preregistered exclusion rule requires non-tie consistency answers on both check pairs; all five
participants are retained.

The recorded 4,000-draw prompt-cluster bootstrap resamples the 30 prompts, retaining all five responses of a sampled
prompt. Win shares exclude ties, and both reported intervals exclude 50%. Intervals retain the source's one-decimal
percentage precision. The prompt pool and sampling differ from the 60-second study; these results do not establish
a duration-only effect or a combined ten-person sample.

### Aggregate record

[`longlive120_summary.json`](longlive120_summary.json) records the counts, reported intervals, protocol and source
hashes for Overleaf commit `727782779988ca22cf79f3417a1ec033afa83d30`. It contains no individual answers, respondent
identifiers or per-prompt scores. The original 60-second [`summary.json`](summary.json) remains unchanged.

```bash
python results/human_evaluation/reproduce.py --summary results/human_evaluation/longlive120_summary.json
```

This checks coverage and win-share arithmetic against the aggregate record. It does not reconstruct confidence
intervals from counts or rerun bootstrap sampling.
