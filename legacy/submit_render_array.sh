#!/bin/bash
#SBATCH -J gwmesh_render
#SBATCH -A mca99s008
#SBATCH -p wholenode
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 10:00:00
#SBATCH -a 0-7
#SBATCH -o /anvil/scratch/x-yguo11/blender_gw_dev/render_mesh/slurm_%A_%a.log
#SBATCH --export=ALL
# Full GW-mesh movie render. 8 nodes (array 0-7), each runs NCONC=10 Blender procs.
# STRIDE=1 -> all 8694 frames (~6 min movie @24fps). Override: sbatch --export=STRIDE=4 ...
# Resumable: re-submit and finished frames (existing PNGs) are skipped.
ROOT=/anvil/scratch/x-yguo11/blender_gw_dev
OUT=$ROOT/render_mesh
STRIDE=${STRIDE:-1}
NNODES=8
export NCONC=10 BLENDER_THREADS=12
mkdir -p "$OUT/logs"
. ${MODULESHOME}/init/bash
module load anaconda/2024.02-py311 >/dev/null 2>&1 || true
echo "ARRAY TASK $SLURM_ARRAY_TASK_ID / NNODES=$NNODES STRIDE=$STRIDE on $(hostname) $(date)"
bash "$ROOT/render_node.sh" "$SLURM_ARRAY_TASK_ID" "$NNODES" "$STRIDE" "$OUT"
