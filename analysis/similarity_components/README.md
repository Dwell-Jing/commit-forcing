# DINOv2 similarity components

The appearance-consistency diagnostic is `Own − Sibling`. Own compares a video's late frames with its own opening;
Sibling compares the same late frames with other generation seeds' openings for the same prompt and arm.
Both terms use full-frame DINOv2 embeddings. Own alone is not a subject-identity score: changes in color, scene
layout or other shared appearance can also raise it.

| Intervention | Δ Consistency [95% CI] | Δ Own [95% CI] | Δ Sibling [95% CI] |
|---|---|---|---|
| LongLive: exclude sink during committing | −0.0081 [−0.0180, +0.0006] | +0.0112\* [+0.0025, +0.0219] | +0.0193\* [+0.0073, +0.0322] |
| LongLive: exclude sink during denoising | −0.0853\* [−0.1215, −0.0528] | −0.3093\* [−0.3650, −0.2546] | −0.2240\* [−0.2808, −0.1711] |
| LongLive: exclude sink in both stages | −0.0676\* [−0.0910, −0.0459] | −0.1575\* [−0.1956, −0.1223] | −0.0898\* [−0.1218, −0.0623] |
| Rolling Sink: recent trajectory during committing | +0.0106\* [+0.00002, +0.0234] | +0.0236\* [+0.0085, +0.0409] | +0.0130 [−0.0003, +0.0313] |
| SF: distant history during committing | −0.0237\* [−0.0392, −0.0102] | −0.0805\* [−0.1117, −0.0547] | −0.0568\* [−0.0802, −0.0374] |
| SF: distant history during the first half | −0.0105 [−0.0246, +0.0023] | −0.0257\* [−0.0461, −0.0044] | −0.0152\* [−0.0269, −0.0041] |
| SF: distant history during the second half | −0.0102\* [−0.0146, −0.0058] | −0.0338\* [−0.0475, −0.0214] | −0.0236\* [−0.0347, −0.0138] |

Values retain the original diagnostic scale. `*` means the paired 95% interval excludes zero. Rolling Sink's
unrounded consistency lower endpoint is `0.000017281547188758977`; rounding it to four decimal places does not
change its significance.

Excluding sink reads during LongLive committing raises similarity to both its own opening and the other seeds'
openings, while their difference has no significant change. Rolling Sink's recent-trajectory context raises Own
and gives a small positive consistency change. These readouts separate shared appearance similarity from the
contrast across generation seeds; they do not isolate an internal identity representation.

## Protocol and reproduction

Each study has 20 prompts and nominal 48-second videos. LongLive and Rolling Sink use two generation seeds;
SF uses three. The opening embedding averages frames at 0.5, 0.75, …, 1.75 seconds. The tail embedding averages
six evenly spaced frames from 38 to 47.5 seconds, capped at video end minus 0.4 seconds. Frame embeddings and
their temporal means are L2-normalized. DINOv2 ViT-B/14 uses float32 CLS embeddings with the image processor
described in [diagnostic metrics](../metrics/README.md).

The released NPZ files contain the actual opening and tail vectors, keyed by `(arm, prompt, generation seed)`.
The CPU script checks complete arm coverage, computes both similarity terms, and reproduces the saved changes
with 4,000 prompt-cluster bootstrap draws (`default_rng(0)`), retaining every generation seed of a prompt.
It requires NumPy and does not load a model or generate videos.

```bash
python analysis/similarity_components/reproduce.py
```

[Feature arrays and numerical summaries](data/) · [provenance and hashes](provenance.json)

Related experiments: [LongLive stage interventions](../longlive_sink/README.md),
[Rolling Sink committing sources](../committing_source/README.md), and
[committing-context switches](../commit_switch/README.md).
