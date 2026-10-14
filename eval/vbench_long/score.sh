#!/bin/bash
# Score the shards in WORK/jobs.txt with VBench-Long on one GPU; run one copy per GPU.
#   bash eval/vbench_long/score.sh /path/to/VBench vb_work 0
# --dev_flag fuses the in-clip and clip-to-clip parts of subject and background consistency.
set -u
VBENCH=$(cd "$1" && pwd); WORK=$(cd "$2" && pwd); GPU=$3
PY=${PYTHON:-python}
# sitecustomize.py: import fixes for VBench
export PYTHONPATH=$(cd "$(dirname "$0")/../../setup/vbench_compat" && pwd)${PYTHONPATH:+:$PYTHONPATH}
mkdir -p "$WORK/locks" "$WORK/results"
while true; do
  did=0
  for S in q6 bg; do
    case $S in
      q6) DIMS="subject_consistency motion_smoothness dynamic_degree aesthetic_quality imaging_quality temporal_flickering" ;;
      bg) DIMS="background_consistency" ;;
    esac
    while read -r J; do
      [ -z "$J" ] && continue
      O=$WORK/results/${J}_$S
      [ -f "$O/done.txt" ] && continue
      mkdir "$WORK/locks/${J}_$S" 2>/dev/null || continue
      mkdir -p "$O"; did=1
      echo "$(date +%H:%M) GPU $GPU: $J $S"
      if (cd "$VBENCH" && CUDA_VISIBLE_DEVICES=$GPU $PY vbench2_beta_long/eval_long.py --videos_path "$WORK/shards/$J" \
            --dimension $DIMS --mode long_custom_input --dev_flag --load_ckpt_from_local True \
            --output_path "$O/" > "$O/eval.log" 2>&1); then
        touch "$O/done.txt"
      else
        echo "$(date +%H:%M) failed: $J $S (see $O/eval.log)"; rmdir "$WORK/locks/${J}_$S"; exit 1
      fi
    done < "$WORK/jobs.txt"
  done
  [ $did -eq 0 ] && break
done
