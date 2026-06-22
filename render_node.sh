#!/bin/bash
# One node's share of the GW-mesh render. Round-robin shards frames across nodes and runs
# NCONC concurrent Blender procs (each BLENDER_THREADS cores). Resumable. Config from config.sh.
# Args: NODE_ID NNODES [STRIDE] [OUTDIR]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/config.sh"
NODE_ID=$1; NNODES=$2; STRIDE=${3:-$STRIDE}; OUT=${4:-$RENDER_DIR}
export BLENDER_THREADS
mkdir -p "$OUT/logs"

cd "$OBJ_DIR"
mapfile -t ALL < <(ls hplus_*.obj 2>/dev/null | sed -E 's/hplus_0*([0-9]+)\.obj/\1/' | sort -n)
sel=(); n=${#ALL[@]}
for (( idx=0; idx<n; idx+=STRIDE )); do
  pos=$(( idx / STRIDE ))
  if (( pos % NNODES == NODE_ID )); then printf -v f "%06d" "${ALL[idx]}"; sel+=("$f"); fi
done
echo "node $NODE_ID/$NNODES stride=$STRIDE -> ${#sel[@]} frames, NCONC=$NCONC threads=$BLENDER_THREADS  $(date)"
printf "%s\n" "${sel[@]}" | xargs -P "$NCONC" -I{} bash "$HERE/render_one.sh" {} "$OUT"
echo "node $NODE_ID DONE $(date); rendered pngs in OUT = $(ls "$OUT"/hplus_*.obj.png 2>/dev/null | wc -l)"
