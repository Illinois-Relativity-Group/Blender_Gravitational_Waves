#!/bin/bash
# VTK -> OBJ for the GW mesh. Edit config.sh first.
# Runs locally (parallel). For the full set on a cluster:  sbatch submit_convert_objs_shared.sh
set -e
cd "$(dirname "$0")"
source ./config.sh
module load anaconda/2024.02-py311 2>/dev/null || true   # numpy
# meshio is NOT in the base module -> auto-install it (once) into the user site if missing.
python3 -c "import meshio" 2>/dev/null || pip install --user -q -r requirements.txt
mkdir -p "$OBJ_DIR"
echo "VTK ($VTK_DIR) -> OBJ ($OBJ_DIR)   grid ${NDIM}x${NDIM}, +-${XY_MAX} M_sun, inner cut ${CUT_RADIUS}"
python3 convert_objs_parallel.py
