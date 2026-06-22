#!/bin/bash
#SBATCH -J gwmesh_render
#SBATCH -A mca99s008        # EDIT for your allocation
#SBATCH -p shared          # EDIT for your cluster
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -t 10:00:00
#SBATCH -a 0-47
#SBATCH -o render_%A_%a.log
#SBATCH --export=ALL
# Full GW-mesh render on shared: 48 small (24-core) array tasks backfill fast. Each task runs
# 2 concurrent Blender (12 threads each) over its round-robin shard. Resumable (skips done PNGs).
# For a coarser movie, set STRIDE in config.sh. Config (paths, look) from config.sh.
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"
source ./config.sh
NNODES=48                              # = number of array tasks (0-47)
export NCONC=2 BLENDER_THREADS=12      # 2 x 12 = 24 cores (small task; overrides config NCONC)
. ${MODULESHOME}/init/bash 2>/dev/null || true
module load anaconda/2024.02-py311 2>/dev/null || true
echo "ARRAY TASK $SLURM_ARRAY_TASK_ID / NNODES=$NNODES STRIDE=$STRIDE on $(hostname) $(date)"
bash render_node.sh "$SLURM_ARRAY_TASK_ID" "$NNODES" "$STRIDE" "$RENDER_DIR"
