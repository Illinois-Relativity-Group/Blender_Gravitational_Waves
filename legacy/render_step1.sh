#!/bin/bash
# Step 1: mesh-only camera-tuning render (10 M_sun hole, NO disk).
# Reusable for the camera-lock loop: edit camera params in plot_single.py, rerun this.
# Login-node throttled. Renders frames 0 and 5000 to render_step1/.
set -e
ROOT=/anvil/scratch/x-yguo11/blender_gw_dev
BLENDER=/anvil/scratch/x-yguo11/software/blender-5.0.0-linux-x64/blender
OUT="$ROOT/render_step1"
FRAME_DIR="$ROOT/obj_data_zoom200/"
mkdir -p "$OUT"

module load anaconda/2024.02-py311 >/dev/null 2>&1 || true

# args: filename frame# out blendfile framedir shaderdir memdir densitydir bhfile \
#       plot_mem with_blend with_density with_bh save zero_plane
# mesh-only -> with_blend=1 (WHITE plane shows through hole), with_density=0, with_bh=0, plot_mem=0, save=0, zero_plane=0
for f in 000000 005000; do
  echo "START frame $f: $(date)"
  taskset -c 0-11 nice -n 19 "$BLENDER" --background --python "$ROOT/plot_single.py" -- \
    "hplus_$f.obj" "$f" "$OUT" "$ROOT/white_plane.blend" "$FRAME_DIR" "$ROOT" \
    "$ROOT/texturemap" "$ROOT/density_movies" "$ROOT/bh_data/update_bh_radius.txt" \
    0 1 0 0 0 0 \
    > "$OUT/render_$f.log" 2>&1
  echo "EXIT rc=$? frame $f: $(date)"
done
ls -la "$OUT"/*.png
