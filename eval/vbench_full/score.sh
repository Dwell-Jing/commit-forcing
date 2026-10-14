#!/bin/bash
# Score the full-VBench shards in WORK/jobs.txt on one GPU; run one copy per GPU.
#   bash eval/vbench_full/score.sh /path/to/VBench vbs_work 0
# SEMANTIC_PYTHONPATH: ':'-separated folders with VBench's pinned transformers, timm and detectron2,
# prepended to PYTHONPATH for the 9 semantic dimensions only.
set -u
VBENCH=$(cd "$1" && pwd); WORK=$(cd "$2" && pwd); GPU=$3
# absolute paths: runs start in the VBench folder
SEM=""
if [ -n "${SEMANTIC_PYTHONPATH:-}" ]; then
  IFS=: read -r -a PARTS <<< "$SEMANTIC_PYTHONPATH"
  for D in "${PARTS[@]}"; do
    [ -n "$D" ] || continue
    A=$(cd "$D" 2>/dev/null && pwd) || { echo "SEMANTIC_PYTHONPATH: no folder $D" >&2; exit 1; }
    SEM=${SEM:+$SEM:}$A
  done
fi
PY=${PYTHON:-python}
HERE=$(cd "$(dirname "$0")" && pwd)
# sitecustomize.py: import fixes for VBench
export PYTHONPATH=$(cd "$(dirname "$0")/../../setup/vbench_compat" && pwd)${PYTHONPATH:+:$PYTHONPATH}
SEMANTIC="object_class multiple_objects human_action color spatial_relationship scene appearance_style temporal_style overall_consistency"
mkdir -p "$WORK/locks" "$WORK/results"
while true; do
  did=0
  while read -r L DIM S; do
    [ -z "$L" ] && continue
    J=${L}__${DIM}__s$S; O=$WORK/results/$J; SH=$WORK/$L/${DIM}__s$S
    [ -f "$O/done.txt" ] && continue
    mkdir "$WORK/locks/$J" 2>/dev/null || continue
    mkdir -p "$O"; did=1
    echo "$(date +%H:%M) GPU $GPU: $J"
    # clear leftovers of a failed run
    rm -rf "$SH/subject_consistency_cat_firstframes_videos" "$SH/background_consistency_cat_firstframes_videos" \
      "$SH/temporal_filtered_cilps"
    EXTRA=""; [ "$DIM" = temporal_flickering ] && EXTRA=--static_filter_flag
    PP=${PYTHONPATH:-}
    case " $SEMANTIC " in *" $DIM "*) PP=$SEM${SEM:+:}$PP ;; esac
    if (cd "$VBENCH" && CUDA_VISIBLE_DEVICES=$GPU PYTHONPATH=$PP $PY "$HERE/run_eval_long.py" --videos_path "$SH" \
          --dimension "$DIM" --mode long_vbench_standard --dev_flag --load_ckpt_from_local True \
          --num_of_samples_per_prompt 1 $EXTRA --full_json_dir "$SH.full_info.json" --output_path "$O/" \
          < /dev/null > "$O/eval.log" 2>&1); then
      touch "$O/done.txt"
    else
      echo "$(date +%H:%M) failed: $J (see $O/eval.log)"; rmdir "$WORK/locks/$J"; exit 1
    fi
  done < "$WORK/jobs.txt"
  [ $did -eq 0 ] && break
done
