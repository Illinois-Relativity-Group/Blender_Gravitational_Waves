#!/bin/bash
# Renumber a finished frame directory to CONTINUOUS labels, IN PLACE.
#
# A render at STRIDE>1 leaves gappy names (hplus_000000.obj.png, hplus_000002.obj.png, ...). Some
# movie / video-editing tools want a gapless 0,1,2,... sequence. This renames the frames in place to
#     frame_000000.png, frame_000001.png, ...
# in physical-time order, and writes mapping.txt (new_name <- original <- physical frame# <- t/M) so
# the true frame index / time is still recoverable. Uses a NEW prefix (frame_) so nothing is ever
# overwritten during the renumber.
#
# Run it ONCE, AFTER the render is complete. It changes the filenames, so a later resumed render
# into the same dir would no longer recognize them (it would re-render). Optional -- skip it if your
# tool can read the gappy hplus_*.obj.png names directly.
#
# Usage:  ./relabel_continuous.sh <frames-dir>
set -euo pipefail
DIR="${1:?usage: ./relabel_continuous.sh <frames-dir>}"
cd "$DIR"
shopt -s nullglob
mapfile -t src < <(ls -v hplus_*.obj.png 2>/dev/null)
if [[ ${#src[@]} -eq 0 ]]; then
  echo "no hplus_*.obj.png in $DIR  (already relabeled, or wrong dir?)"; exit 0
fi

# physical frame -> t/M, matching plot_single.py's time label (frame * dt / M_ADM)
DT=0.056325; MADM=0.0603349020955639
: > mapping.txt
echo "# new_name  original  frame#  t/M" >> mapping.txt
i=0
for f in "${src[@]}"; do
  fr=$(sed -E 's/hplus_0*([0-9]+)\.obj\.png/\1/' <<<"$f"); fr=${fr:-0}
  new=$(printf "frame_%06d.png" "$i")
  tm=$(awk -v fr="$fr" -v dt="$DT" -v m="$MADM" 'BEGIN{printf "%.3f", fr*dt/m}')
  mv -n "$f" "$new"
  printf "%s  %s  %s  %s\n" "$new" "$f" "$fr" "$tm" >> mapping.txt
  i=$((i+1))
done
echo "relabeled ${#src[@]} frames in place: frame_000000.png .. $(printf 'frame_%06d.png' $((i-1)))"
echo "physical frame# / t-over-M preserved in $DIR/mapping.txt"
