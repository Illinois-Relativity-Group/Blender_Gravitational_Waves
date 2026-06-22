#!/bin/bash
# Render the GW-mesh frames at the LOCKED look (camera/ZSCALE/hole/shader fixed in plot_single.py).
# Edit config.sh first. Runs on ONE node here (NCONC concurrent Blender procs).
# For the full movie across many nodes on a cluster:  sbatch submit_render_array_shared.sh
set -e
cd "$(dirname "$0")"
source ./config.sh
mkdir -p "$RENDER_DIR/logs"
echo "render OBJ ($OBJ_DIR) -> PNG ($RENDER_DIR)   stride=$STRIDE, NCONC=$NCONC, locked camera/ZSCALE/hole"
bash render_node.sh 0 1 "$STRIDE" "$RENDER_DIR"
echo "frames: $(ls "$RENDER_DIR"/hplus_*.obj.png 2>/dev/null | wc -l)"
