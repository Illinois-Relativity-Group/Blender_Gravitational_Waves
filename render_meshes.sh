#!/bin/bash
# Render the GW-mesh frames at the LOCKED look (camera/ZSCALE/hole/shader fixed in plot_single.py).
# Edit config.sh first. Runs on ONE node here (NCONC concurrent Blender procs).
# For a few frames or the full movie on the cluster:  ./submit_render.sh <run-name>  (reads FRAMES)
set -e
cd "$(dirname "$0")"
source ./config.sh
mkdir -p "$RENDER_DIR/logs"
echo "render OBJ ($OBJ_DIR) -> PNG ($RENDER_DIR)   stride=$STRIDE, NCONC=$NCONC, locked camera/ZSCALE/hole"
bash render_node.sh 0 1 "$STRIDE" "$RENDER_DIR"
echo "frames: $(ls "$RENDER_DIR"/hplus_*.obj.png 2>/dev/null | wc -l)"
