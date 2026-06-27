#!/bin/bash
# Launch the GW-mesh render (step 2). ONE entry point for both tests and the full movie.
#
#   ./submit_render.sh [run-name]
#
# Reads config.sh for FRAMES / WITH_DISK / the look knobs, expands FRAMES into an explicit frame
# list, auto-sizes the SLURM array to match (no idle tasks), and submits render_array_job.sh.
# A run-name puts the output in its own timestamped MOVIES/<ts>_<name>/frames/ dir.
#
# Examples:
#   FRAMES="0 5000" ./submit_render.sh test          # 2-frame test  -> 2-task array
#   ./submit_render.sh fullmovie                      # FRAMES=all    -> the whole movie
#   WITH_DISK=0 FRAMES="0-200" ./submit_render.sh meshonly
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/config.sh"

# optional run-name -> its own timestamped MOVIES dir (else the config RENDER_DIR)
NAME="${1:-}"
if [[ -n "$NAME" ]]; then
  export RENDER_DIR="$HERE/MOVIES/$(date +%y%m%d_%H%M)_${NAME}/frames"
fi
mkdir -p "$RENDER_DIR/logs"

# --- expand FRAMES -> explicit 6-digit frame numbers, one per line ---
expand_frames() {
  case "$FRAMES" in
    all|ALL)
      ls "$OBJ_DIR"/hplus_*.obj 2>/dev/null \
        | sed -E 's#.*hplus_0*([0-9]+)\.obj#\1#' | sort -n \
        | awk -v s="$STRIDE" '(NR-1)%s==0{printf "%06d\n",$1}' ;;
    *)
      printf '%s\n' "$FRAMES" | tr ',' ' ' | tr -s ' ' '\n' | while read -r tok; do
        [[ -z "$tok" ]] && continue
        if [[ "$tok" == *-* ]]; then
          rng="${tok%%:*}"; step="${tok#*:}"; [[ "$step" == "$tok" ]] && step="$STRIDE"
          seq "${rng%%-*}" "$step" "${rng##*-}" | awk '{printf "%06d\n",$1}'
        else
          printf '%06d\n' "$((10#$tok))"   # 10# forces base-10 -- a zero-padded token (e.g. 001734) must NOT be parsed as octal
        fi
      done ;;
  esac
}

LIST="$RENDER_DIR/frames.list"
expand_frames > "$LIST" || true
N=$(grep -c . "$LIST" || true)
if (( N == 0 )); then echo "[err] FRAMES='$FRAMES' expanded to 0 frames (OBJ_DIR=$OBJ_DIR)"; exit 1; fi

# --- array auto-sizes to the work; concurrency cap %CAP ---
A=$(( N < MAX_TASKS ? N : MAX_TASKS ))
CAP="${CAP:-$A}"

# --- disk switch -> the name render_one.sh reads ---
WD=$([[ "$WITH_DISK" == "1" ]] && echo 1 || echo 0)

# --- disk pre-flight: don't silently produce a diskless movie you asked to have a disk ---
if (( WD == 1 )); then
  if [[ ! -f "$DISK_MANIFEST" ]]; then
    echo "[ERROR] WITH_DISK=1 but DISK_MANIFEST not found:" >&2
    echo "        $DISK_MANIFEST" >&2
    echo "        build it once:   python3 build_disk_manifest.py \"\$DISK_FOLDER\" \"\$DISK_MANIFEST\"" >&2
    echo "        or render mesh-only:   WITH_DISK=0 ./submit_render.sh ${NAME:-<run-name>}" >&2
    exit 1
  fi
  miss=$(awk 'NR==FNR{have[$1]=1; next} !($1 in have){c++} END{print c+0}' "$DISK_MANIFEST" "$LIST")
  if (( miss > 0 )); then
    echo "[warn] $miss of $N selected frames have NO disk entry in $(basename "$DISK_MANIFEST")"
    echo "       -> those frames will render MESH-ONLY. Expected for the waveless tail / frames beyond the"
    echo "          disk data. If unexpected, check STRIDE matches the manifest, or rebuild the manifest."
  fi
fi

echo "FRAMES='$FRAMES' -> $N frames | array 0-$((A-1))%$CAP | WITH_DISK=$WD HOLE_RADIUS=$HOLE_RADIUS SAMPLES=$SAMPLES"
echo "OBJ_DIR   = $OBJ_DIR"
echo "RENDER_DIR= $RENDER_DIR"
[[ "$WD" == 1 ]] && echo "DISK_MANIFEST= $DISK_MANIFEST"

jid=$(sbatch --parsable \
  --array="0-$((A-1))%${CAP}" \
  -o "$RENDER_DIR/logs/render_%A_%a.log" \
  --export=ALL,FRAMES_FILE="$LIST",ARRAY_SIZE="$A",RENDER_DIR="$RENDER_DIR",OBJ_DIR="$OBJ_DIR",WITH_DENSITY="$WD",DISK_MANIFEST="$DISK_MANIFEST",HOLE_RADIUS="$HOLE_RADIUS",ZSCALE="$ZSCALE",DISK_MARGIN="$DISK_MARGIN",SAMPLES="$SAMPLES",STRIDE="$STRIDE" \
  "$HERE/lib/render_array_job.sh")
echo "submitted job $jid  ($A tasks)"
echo "  watch:  squeue -j $jid"
echo "  count:  ls $RENDER_DIR/hplus_*.obj.png 2>/dev/null | wc -l   (expect $N when done)"
