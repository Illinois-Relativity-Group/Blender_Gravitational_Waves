#!/bin/bash
#SBATCH -J obj_convert
#SBATCH -A mca99s008        # EDIT for your allocation
#SBATCH -p shared          # EDIT for your cluster
#SBATCH -N 1
#SBATCH -n 32
#SBATCH -t 00:40:00
#SBATCH -o obj_convert_%j.log
#SBATCH --export=ALL
# VTK -> OBJ on the shared partition (backfills fast). ~few min. Resumable. Config from config.sh.
set -e
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")}"
source ./config.sh
. ${MODULESHOME}/init/bash 2>/dev/null || true
module load anaconda/2024.02-py311 2>/dev/null || true
# meshio is NOT in the base module -> auto-install it (once) into the user site if missing.
python3 -c "import meshio" 2>/dev/null || pip install --user -q -r requirements.txt
export NPROC=${SLURM_NTASKS:-32}
mkdir -p "$OBJ_DIR"
echo "START $(date) on $(hostname); NPROC=$NPROC"
python3 "$GW_ROOT/lib/convert_objs_parallel.py"
echo "EXIT rc=$? $(date); OBJs in $OBJ_DIR: $(ls "$OBJ_DIR"/*.obj 2>/dev/null | wc -l)"
