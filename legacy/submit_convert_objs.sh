#!/bin/bash
#SBATCH -J obj_convert
#SBATCH -A mca99s008
#SBATCH -p wholenode
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -t 00:40:00
#SBATCH -o /anvil/scratch/x-yguo11/blender_gw_dev/obj_convert_%j.log
#SBATCH --export=ALL
# VTK -> OBJ for all 8694 GW-mesh frames (radius 1.0 inner cut, +-200, 500x500).
# Reproduces the test OBJs bit-for-bit (validated). Resumable (skips existing .obj).
# Output: obj_data_zoom200/hplus_NNNNNN.obj (~20 MB each, ~174 GB total).
set -e
cd /anvil/scratch/x-yguo11/blender_gw_dev
. ${MODULESHOME}/init/bash
module load anaconda/2024.02-py311
export NPROC=128
echo "START $(date) on $(hostname)"
python3 convert_objs_parallel.py
echo "EXIT rc=$? $(date)"
echo "OBJs in obj_data_zoom200: $(ls obj_data_zoom200/*.obj 2>/dev/null | wc -l)  (expect 8694)"
