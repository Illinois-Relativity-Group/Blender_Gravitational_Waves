#!/bin/bash
# ============================================================================
#  USER CONFIG for the Blender GW-mesh pipeline.
#  Edit the paths for your setup, then:   ./make_objs.sh   &&   ./render_meshes.sh
#
#  NOTE: the mesh LOOK -- camera angle/distance, ZSCALE, the central hole, the
#  shader -- is intentionally LOCKED in plot_single.py + shader_grid_solidlightblue.py
#  so the dialed-in view reproduces exactly. It is NOT exposed here.
# ============================================================================

export GW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- tools ---
export BLENDER=/anvil/scratch/x-yguo11/software/blender-5.0.0-linux-x64/blender   # Blender 5.0 binary

# --- paths ---
export VTK_DIR=/anvil/scratch/x-yguo11/abid_bot_dev/gravity_wave_generation/VTKdata/2D  # input .vtk (from the GW pipeline)
export OBJ_DIR=$GW_ROOT/obj_data            # OBJ output (make_objs.sh)
export RENDER_DIR=$GW_ROOT/render_mesh      # rendered frames output (render_meshes.sh)

# --- mesh grid (MUST match the GW pipeline's XY_MAX_2D / XY_NUM_2D) ---
export XY_MAX=200                            # mesh half-width (M_sun)
export NDIM=500                              # grid points per side
export CUT_RADIUS=1.0                        # tiny inner OBJ cut; the visible 10 M_sun hole is cut in Blender

# --- movie ---
export STRIDE=1                              # frame stride (1 = every frame, 4 = every 4th, ...)
export NCONC=10                              # concurrent Blender procs per node (render)
export BLENDER_THREADS=12                    # cpu threads per Blender proc
