#!/bin/bash
# ============================================================================
#  USER CONFIG for the Blender GW-mesh pipeline.  Edit this file, then:
#      sbatch submit_convert_objs_shared.sh      # step 1: VTK -> OBJ
#      ./submit_render.sh <run-name>             # step 2: OBJ -> PNG (one launcher)
#
#  The fixed part of the LOOK -- the camera (azimuth/elevation, dolly distance
#  DOLLY_DIST=125 in for the 2x magnification, wide 50mm lens) -- is LOCKED in
#  plot_single.py so the dialed-in converging view reproduces exactly; the disk
#  billboard, time label and grid shader all auto-track it. The knobs people
#  actually change -- WHAT frames, disk on/off, hole size, wave height, samples
#  -- live HERE.
# ============================================================================

export GW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- tools ---
export BLENDER=/anvil/scratch/x-yguo11/software/blender-5.0.0-linux-x64/blender   # Blender 5.0 binary

# --- paths ---
export VTK_DIR=/anvil/scratch/x-yguo11/abid_bot_dev/gravity_wave_generation/VTKdata/2D  # input .vtk (step 1 input)
export OBJ_DIR="${OBJ_DIR:-$GW_ROOT/obj_data}"  # OBJ set (step 1 output / step 2 input); the ±200 M_sun mesh (XY_MAX); env-overridable
export RENDER_DIR="${RENDER_DIR:-$GW_ROOT/render_mesh}" # default output (a run-name overrides this); env-overridable

# --- mesh grid (MUST match the GW pipeline's XY_MAX_2D / XY_NUM_2D) ---
export XY_MAX=200                            # mesh half-width (M_sun)
export NDIM=500                              # grid points per side
export CUT_RADIUS=1.0                        # tiny inner OBJ cut (kills the 1/r spike); the VISIBLE hole is cut in Blender (HOLE_RADIUS)

# --- step 2: WHAT to render --------------------------------------------------
# FRAMES picks the frames (space- or comma-separated, mixable):
#   all          every frame in OBJ_DIR at STRIDE cadence  (the full movie)
#   "0 5000"     just those frame numbers                  (a quick test)
#   "0-200"      a range; step defaults to STRIDE
#   "0-200:10"   a range with an explicit step
export FRAMES="${FRAMES:-all}"
export STRIDE="${STRIDE:-2}"                 # cadence for `all` / bare ranges: 2 = even frames (matches disk & 1D), 1 = every frame
export MAX_TASKS="${MAX_TASKS:-48}"          # SLURM array cap; the array auto-sizes to min(#frames, MAX_TASKS)
export NCONC="${NCONC:-10}"                  # concurrent Blender procs per task (the array job overrides to 2)
export BLENDER_THREADS="${BLENDER_THREADS:-12}"  # cpu threads per Blender proc

# --- step 2: the DISK overlay + look knobs (defaults = current production look) ---
export WITH_DISK="${WITH_DISK:-1}"          # 1 = composite the accretion disk in-render, 0 = mesh-only
export DISK_FOLDER="${DISK_FOLDER:-$GW_ROOT/density_test/full_density_movie_newopa}"  # disk PNGs (build_disk_manifest.py input); MUST be the imageZoom=2 (meshmatch) render set
export DISK_MANIFEST="${DISK_MANIFEST:-$GW_ROOT/disk_manifest_newopa.txt}"            # built manifest (the renderer reads this)
export HOLE_RADIUS="${HOLE_RADIUS:-7.5}"    # central cutout radius (PHYSICAL M_sun); current look = 7.5 (was 15; halved so disk & mesh share one ruler and the hole frames the ~7 M_sun disk)
export ZSCALE="${ZSCALE:-0.7}"              # wave-height multiplier
export DISK_MARGIN="${DISK_MARGIN:-0}"      # M_sun lift of the disk billboard toward the camera (0 = in-plane)
export SAMPLES="${SAMPLES:-128}"            # Cycles render samples (quality vs speed)

# NOTE: frames are rendered over the FULL simulation (coordinate) time, so once the last GW has
# passed the extraction radius the TRAILING frames go flat (no waves). The mesh sequence therefore
# outlasts the 1D-overlay sequence -- trim the waveless tail in your editor to match the overlay.
