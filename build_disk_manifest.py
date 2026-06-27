#!/usr/bin/env python3
"""build_disk_manifest.py -- turn a folder of disk PNG frames into a render-ready manifest.

Sorts ALL *.png in <disk_folder> by name (frames must sort into time order -- the usual
zero-padded naming does that), maps the i-th disk frame to render frame STRIDE*i (matching the
mesh render's cadence), and writes a 2-column file:  <6-digit frame> <abs png>
Then runs measure_disk_scale.py on it to append the per-frame size-normalization column (col 3),
giving the exact 3-column format render_one.sh expects:  <6-digit frame> <abs png> <scale>

Usage:   python3 build_disk_manifest.py <disk_folder> [out_manifest]
         (out defaults to $DISK_MANIFEST, else disk_manifest.txt)
Env:     STRIDE (default 2)  +  all DISK_* knobs honored by measure_disk_scale.py
         (DISK_TARGET, DISK_SCALE_MIN/MAX, DISK_SIZE_METRIC, ...).
"""
import os, sys, glob, subprocess

if len(sys.argv) < 2:
    sys.exit("usage: python3 build_disk_manifest.py <disk_folder> [out_manifest]")

folder = sys.argv[1]
out    = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("DISK_MANIFEST", "disk_manifest.txt")
STRIDE = int(os.environ.get("STRIDE", "2"))

pngs = sorted(glob.glob(os.path.join(folder, "*.png")))
if not pngs:
    sys.exit(f"[err] no *.png in {folder}")

with open(out, "w") as f:
    for i, p in enumerate(pngs):
        f.write(f"{STRIDE*i:06d} {os.path.abspath(p)}\n")
print(f"[build] {len(pngs)} disk frames -> {out}  (frame = {STRIDE} * sorted_index)")

# reuse measure_disk_scale.py to append column 3 (per-frame gauge-shrink scale); idempotent
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(here, "lib", "measure_disk_scale.py"), out], check=True)
print(f"[ok] manifest ready: {out}")
