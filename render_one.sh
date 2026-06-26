#!/bin/bash
# Render ONE GW-mesh frame at the LOCKED look (camera/ZSCALE/hole/shader fixed in plot_single.py).
# Args: FRAME(6-digit zero-padded)  [OUTDIR]
#
# Optional disk overlay -- the "switch": export WITH_DENSITY=1 and DISK_MANIFEST=<file> whose lines
# are "<6-digit frame> <disk_png>". When on AND this frame has a manifest entry, the disk is
# composited IN-RENDER as a camera-facing billboard at the disk's depth (true 3D occlusion -- the
# waves interleave with it; NOT a post-process overlay). Frames with no entry render mesh-only.
# Default (no WITH_DENSITY) is mesh-only, byte-for-byte the same call as before.
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/config.sh"
FRAME=$1; OUT=${2:-$RENDER_DIR}
OBJ="$OBJ_DIR/hplus_${FRAME}.obj"
PNG="$OUT/hplus_${FRAME}.obj.png"                 # Blender swaps .jpeg->.png (PNG format)
[[ -s "$PNG" ]] && { echo "skip $FRAME (exists)"; exit 0; }      # resume
[[ -s "$OBJ" ]] || { echo "MISSING OBJ $OBJ"; exit 0; }
mkdir -p "$OUT/logs"

# --- disk switch (off unless WITH_DENSITY=1 and the frame is in the manifest) ---
# Manifest line: "<6-digit frame> <disk_png> [scale]". Col 3 (scale, from measure_disk_scale.py)
# is the per-frame gauge-shrink size normalization; absent -> 1.0 (old behavior).
WD=0; export DISK_IMAGE=""; export DISK_SCALE="1.0"
if [[ "${WITH_DENSITY:-0}" == "1" && -f "${DISK_MANIFEST:-/nonexistent}" ]]; then
  read -r d s < <(awk -v f="$FRAME" '$1==f{print $2, $3; exit}' "$DISK_MANIFEST")
  if [[ -n "$d" ]]; then WD=1; export DISK_IMAGE="$d"; [[ -n "$s" ]] && export DISK_SCALE="$s"; fi
fi

# plot_single.py args: filename frame# out blendfile framedir shaderdir memdir densitydir bhfile \
#                      plot_mem with_blend with_density with_bh save zero_plane
"$BLENDER" --background --python "$GW_ROOT/plot_single.py" -- \
  "hplus_${FRAME}.obj" "$FRAME" "$OUT" "$GW_ROOT/white_plane.blend" "$OBJ_DIR/" "$GW_ROOT" \
  "$GW_ROOT/texturemap" "$GW_ROOT/density_movies" "$GW_ROOT/bh_data/update_bh_radius.txt" \
  0 1 "$WD" 0 0 0 > "$OUT/logs/render_${FRAME}.log" 2>&1
rc=$?
[[ -s "$PNG" ]] && echo "done $FRAME (disk=$WD)" || echo "FAIL $FRAME rc=$rc (see logs/render_${FRAME}.log)"
