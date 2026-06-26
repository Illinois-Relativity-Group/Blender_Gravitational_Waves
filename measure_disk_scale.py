#!/usr/bin/env python3
"""measure_disk_scale.py -- add a per-frame size-normalization column to a disk manifest.

WHY: the accretion disk shrinks in COORDINATE size over the run -- a pure moving-puncture gauge
effect (the apparent-horizon AREAL radius stays ~constant while its COORDINATE radius collapses
~7.6x in sol_05). The disk sits at larger radii so it shrinks less (~1.4x linear), but enough to
look too small late in the movie. Rather than re-render the disk in corrected coordinates, we
measure each disk frame's apparent size and write a per-frame scale that holds the disk at a
constant TARGET size (default = the first frame's size, the dialed-in "preferred" size). The
renderer (render_one.sh -> plot_single.py) then magnifies the billboard by that scale per frame.

Reads  a disk manifest:  <frame> <image> [oldscale]      (col 3 ignored / recomputed)
Writes the same manifest: <frame> <image> <scale>

Robust measure: area-equivalent radius r_eq = sqrt(opaque_px / pi) over pixels that are both
opaque (alpha) and luminous (brightness) -- area-based, so stray pixels / annotations barely move
it. Scale is clamped so a faint/empty frame can't blow up. Run once after building the manifest;
idempotent (recomputed from the images, col 3 is overwritten not compounded).

Usage:   python3 measure_disk_scale.py [manifest]      (default $DISK_MANIFEST or disk_manifest.txt)
Env:     DISK_TARGET = start | median | <number>   (target r_eq; default "start" = first frame)
         DISK_ALPHA_THRESH=30  DISK_BRIGHT_THRESH=30  DISK_SCALE_MIN=0.4  DISK_SCALE_MAX=3.0
"""
import os, sys, math
import numpy as np
from PIL import Image

MANIFEST = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DISK_MANIFEST", "disk_manifest.txt")
A_THR   = int(os.environ.get("DISK_ALPHA_THRESH", "30"))   # min alpha to count a pixel as disk
B_THR   = int(os.environ.get("DISK_BRIGHT_THRESH", "30"))  # 'extent' metric: min R+G+B over background
WARM    = int(os.environ.get("DISK_WARM_THR", "50"))       # 'core' metric: min (R-B) -> warm/saturated
R_MIN   = int(os.environ.get("DISK_R_MIN", "120"))         # 'core' metric: min R (drop dark warmish noise)
METRIC  = os.environ.get("DISK_SIZE_METRIC", "core")       # "core" (visible orange disk) | "extent" (whole blob)
LO      = float(os.environ.get("DISK_SCALE_MIN", "0.4"))
HI      = float(os.environ.get("DISK_SCALE_MAX", "3.0"))
TARGET  = os.environ.get("DISK_TARGET", "start")           # "start" | "median" | a number (px r_eq)


def r_eq(path):
    """Area-equivalent apparent radius (px) of the disk; None if empty.

    METRIC 'core'   = warm/saturated pixels -- the visible orange disk, ignoring the faint bluish
                      outer halo. This is what reads as 'the disk' and what shrinks with the gauge.
    METRIC 'extent' = all opaque, luminous pixels -- the whole blob incl. the translucent halo.
                      (The halo SPREADS over time, so 'extent' under-counts the core's shrink.)"""
    im = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    R, G, B, Aa = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    if METRIC == "extent":
        mask = (Aa > A_THR) & ((R + G + B) > B_THR)
    else:  # "core"
        mask = (Aa > A_THR) & ((R - B) > WARM) & (R > R_MIN) & (G < R)
    n = int(mask.sum())
    return math.sqrt(n / math.pi) if n > 0 else None


def main():
    rows = []
    with open(MANIFEST) as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            p = s.split()
            rows.append((p[0], p[1]))                       # frame, image (drop any old col3)

    meas = [(frame, img, (r_eq(img) if os.path.exists(img) else None)) for frame, img in rows]
    good = [r for _, _, r in meas if r]
    if not good:
        sys.exit(f"[err] no measurable disk pixels in any image of {MANIFEST}")

    if TARGET == "start":
        r_target = next(r for _, _, r in meas if r)         # first measurable frame = the "start size"
    elif TARGET == "median":
        r_target = float(np.median(good))
    else:
        r_target = float(TARGET)

    out = []
    print(f"{'frame':>8} {'r_eq(px)':>9} {'scale':>7}   image")
    for frame, img, r in meas:
        if r:
            scale = min(HI, max(LO, r_target / r))
        else:
            scale = 1.0
            print(f"  [warn] no disk pixels, scale 1.0: {img}")
        out.append(f"{frame} {img} {scale:.4f}")
        print(f"{frame:>8} {(('%.1f' % r) if r else 'NA'):>9} {scale:>7.4f}   {os.path.basename(img)}")

    with open(MANIFEST, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"\n[done] target r_eq={r_target:.1f}px ({TARGET}); wrote scale column to {MANIFEST}")


if __name__ == "__main__":
    main()
