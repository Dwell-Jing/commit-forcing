# Prompts

`rollf200.txt` holds the 200 MovieGen prompts of Rolling Forcing App. B (arXiv 2509.25161), the evaluation set of
Recency Forcing Tab. 3, one prompt per line. `rollf200_indices.txt` lists their 0-based line numbers in the extended
MovieGen prompts that Self-Forcing ships (`prompts/MovieGenVideoBench_extended.txt`, Apache-2.0).
`make_rollf200.py` rebuilds the list from a Self-Forcing checkout and checks it against `rollf200.txt`:

```bash
python eval/prompts/make_rollf200.py /path/to/Self-Forcing/prompts/MovieGenVideoBench_extended.txt
```
