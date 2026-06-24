#!/bin/bash
# Launch a full GW-mesh movie render into a fresh, timestamped MOVIES/ run directory.
#
# Usage:  ./run_movie.sh <run-name> [--disk]
#   <run-name>   short label for this run, e.g. meshonly_z07
#                -> output dir becomes  MOVIES/<YYMMDD_HHMM>_<run-name>/
#   --disk       composite the accretion disk in-render (needs disk_manifest.txt). Off = mesh only.
#
# Honors anything you pre-export: OBJ_DIR (this workspace: obj_data_zoom200), ZSCALE, etc.
# Frames land in <run>/frames/ ; SLURM logs in <run>/ ; a run_info.txt records the settings.
# The timestamp is computed ONCE here (before sbatch) so all 48 array tasks share one dir.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
NAME="${1:?usage: ./run_movie.sh <run-name> [--disk]}"; shift || true
MODE_DISK=0; [[ "${1:-}" == "--disk" ]] && MODE_DISK=1

TS=$(date +%y%m%d_%H%M)
RUN="$HERE/MOVIES/${TS}_${NAME}"
export RENDER_DIR="$RUN/frames"
mkdir -p "$RENDER_DIR" "$RUN/logs"

source "$HERE/config.sh"                         # for the effective STRIDE / OBJ_DIR (both env-overridable)
if [[ "$MODE_DISK" == "1" ]]; then
  export WITH_DENSITY=1 DISK_MANIFEST="$HERE/disk_manifest.txt"
fi

{ echo "run_name  = $NAME"
  echo "timestamp = $TS"
  echo "disk      = $MODE_DISK"
  echo "ZSCALE    = ${ZSCALE:-0.7 (plot_single default)}"
  echo "STRIDE    = ${STRIDE}"
  echo "OBJ_DIR   = ${OBJ_DIR}"
  echo "frames    = $RENDER_DIR"
} > "$RUN/run_info.txt"

jid=$(sbatch --parsable -o "$RUN/logs/slurm_%A_%a.log" --export=ALL submit_render_array_shared.sh)
echo "submitted array job $jid"
echo "RUN DIR : $RUN"
cat "$RUN/run_info.txt"
echo
echo "when the job finishes, OPTIONAL continuous relabel (only needed if STRIDE != 1):"
echo "    ./relabel_continuous.sh \"$RENDER_DIR\""
