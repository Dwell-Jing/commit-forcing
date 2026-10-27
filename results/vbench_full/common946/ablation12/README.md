# Previous LongLive 12-frame committing control

The main LongLive variant now commits from 6 latent frames and uses 12 physical cache frames. This archive retains
the previous committing-12 comparison, whose recent-context arm stored 15 physical frames versus the base arm's 12.

| Configuration | Quality | Semantic | Total |
|---|---:|---:|---:|
| Base | 84.70 | 76.43 | 83.05 |
| Recent-context, 12-frame control | 84.91 | 76.58 | 83.25 |
| Paired change | +0.21 | +0.15 | +0.20 |

Quality's interval spans zero; Total's interval excludes zero. The unchanged original package contains all eight
configurations, their full component scores, paired intervals, per-prompt contributions, coverage, protocol, prompt
identities, data manifest and README. It is stored once as [original_package.zip](original_package.zip), with the
original file hashes in [archive_manifest.json](archive_manifest.json). Every archive entry retains its original
bytes, including line endings.

```bash
unzip results/vbench_full/common946/ablation12/original_package.zip -d /tmp/commit-forcing-common946-control12
python eval/vbench_full/reproduce_common946.py --data /tmp/commit-forcing-common946-control12 --models LL
```

The current [LongLive source report](../longlive6_source_results.json) also compares committing-6 with this
committing-12 control under the same 946-entry scoring protocol. The [main package](../README.md) uses committing-6.
