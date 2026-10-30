# Prompts

`rollf200.txt` uses Rolling Forcing's 200-prompt selection, with the expanded MovieGen prompts released by
Self-Forcing (`prompts/MovieGenVideoBench_extended.txt`, Apache-2.0), one prompt per line.
`rollf200_indices.txt` records their 0-based line numbers in that file. This selection is not the first 200
extended MovieGen prompts. The `rollf200` filenames are retained for compatibility with the evaluation scripts.
`make_rollf200.py` rebuilds the list from a Self-Forcing checkout and checks it against `rollf200.txt`:

```bash
python eval/prompts/make_rollf200.py /path/to/Self-Forcing/prompts/MovieGenVideoBench_extended.txt
```
