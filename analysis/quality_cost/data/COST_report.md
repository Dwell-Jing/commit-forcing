# Wall time and peak GPU memory, Base vs +Commit Forcing (standard-suite configurations)

One 60 s video (240 latent frames, 946-suite prompt 1, after a warm-up video), the two arms of a configuration run at the same time on neighbouring dedicated H20 GPUs of one node. Peak device memory = max nvidia-smi memory.used during the run (weights, activations, allocator cache, CUDA context). Forwards = clean commit / denoising DiT calls per video (engine audit; engine models only).

| config | wall Base (s) | wall +CF (s) | +CF / Base | peak device mem Base (GiB) | +CF (GiB) | torch peak alloc Base / +CF (GiB) | forwards Base / +CF |
|---|---|---|---|---|---|---|---|
| SGF | 218.7 | 216.2 | 0.988 | 34.2 | 34.2 | — | — |
| RF-TF | 288.3 | 287.1 | 0.996 | 37.3 | 37.3 | — | — |
| CF | 158.2 | 146.6 | 0.926 | 26.2 | 26.2 | — | — |
| LongLive | 231.5 | 231.4 | 1.000 | 35.9 | 37.0 | 30.7 / 31.5 | 80+320 / 80+320 |
| SGF+ | 221.3 | 217.7 | 0.984 | 37.1 | 36.8 | 32.8 / 32.8 | 80+320 / 80+320 |
| Rolling Sink | 271.6 | 271.7 | 1.000 | 41.9 | 48.1 | 38.1 / 43.7 | 80+320 / 80+320 |
| IDF-SF | 227.0 | 216.6 | 0.954 | 29.1 | 29.9 | 24.9 / 25.8 | 155+320 / 80+320 |
| IDF-LL | 222.7 | 230.6 | 1.035 | 31.8 | 31.8 | 25.2 / 25.2 | 80+320 / 80+320 |
