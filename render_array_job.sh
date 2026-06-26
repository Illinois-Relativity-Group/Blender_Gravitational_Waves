#!/bin/bash
#SBATCH -J gwrender
#SBATCH -A mca99s008        # EDIT for your allocation
#SBATCH -p shared          # EDIT for your cluster
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -t 10:00:00
#SBATCH --export=ALL
# Inner render job -- ONE small (24-core) array task. NOT launched directly: submit_render.sh
# supplies --array, -o, the frame list (FRAMES_FILE / ARRAY_SIZE) and the disk switch
# (WITH_DENSITY). Each task runs 2 concurrent Blender (12 threads each) over its round-robin
# shard via render_node.sh. Resumable (skips done PNGs). Mesh-vs-disk = WITH_DISK in config.sh.
set -u
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"
source ./config.sh                              # OBJ_DIR/RENDER_DIR/look knobs survive (launcher-exported, config uses :- defaults)
export NCONC=2 BLENDER_THREADS=12               # 2 x 12 = 24 cores (small task; overrides config)
export WITH_DENSITY="${WITH_DENSITY:-$WITH_DISK}"   # launcher sets WITH_DENSITY; fall back to config WITH_DISK
. ${MODULESHOME}/init/bash 2>/dev/null || true
module load anaconda/2024.02-py311 2>/dev/null || true
echo "ARRAY TASK $SLURM_ARRAY_TASK_ID / ${ARRAY_SIZE:?need ARRAY_SIZE from submit_render.sh} WITH_DENSITY=$WITH_DENSITY HOLE_RADIUS=$HOLE_RADIUS SAMPLES=$SAMPLES on $(hostname) $(date)"
bash render_node.sh "$SLURM_ARRAY_TASK_ID" "$ARRAY_SIZE" "$STRIDE" "$RENDER_DIR"
