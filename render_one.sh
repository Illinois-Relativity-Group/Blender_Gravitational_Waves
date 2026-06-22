#!/bin/bash
# Render ONE GW-mesh frame at the LOCKED look (camera/ZSCALE/hole/shader fixed in plot_single.py).
# Args: FRAME(6-digit zero-padded)  [OUTDIR]
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/config.sh"
FRAME=$1; OUT=${2:-$RENDER_DIR}
OBJ="$OBJ_DIR/hplus_${FRAME}.obj"
PNG="$OUT/hplus_${FRAME}.obj.png"                 # Blender swaps .jpeg->.png (PNG format)
[[ -s "$PNG" ]] && { echo "skip $FRAME (exists)"; exit 0; }      # resume
[[ -s "$OBJ" ]] || { echo "MISSING OBJ $OBJ"; exit 0; }
mkdir -p "$OUT/logs"
# plot_single.py args: filename frame# out blendfile framedir shaderdir memdir densitydir bhfile \
#                      plot_mem with_blend with_density with_bh save zero_plane
"$BLENDER" --background --python "$GW_ROOT/plot_single.py" -- \
  "hplus_${FRAME}.obj" "$FRAME" "$OUT" "$GW_ROOT/white_plane.blend" "$OBJ_DIR/" "$GW_ROOT" \
  "$GW_ROOT/texturemap" "$GW_ROOT/density_movies" "$GW_ROOT/bh_data/update_bh_radius.txt" \
  0 1 0 0 0 0 > "$OUT/logs/render_${FRAME}.log" 2>&1
rc=$?
[[ -s "$PNG" ]] && echo "done $FRAME" || echo "FAIL $FRAME rc=$rc (see logs/render_${FRAME}.log)"
