"""composite_density_mesh.py -- overlay the disk/density frames onto the GW-mesh frames.

Mapping (user's choice): density frame i (in global order) -> mesh frame 2*i+1 ("odd mesh
frames"), disk ~half as frequent as mesh; small drift from missing/short folders ignored.
Disk PNGs are stu-blue (55,118,255) background -> red-minus-blue CHROMA key to transparent,
then alpha-composite over the white-backdrop mesh frame (disk seats in the 10 M_sun hole).

Output: render_composite_movie/comp_NNNNNN.png  (NNNNNN = density index, sequential for ffmpeg).
"""
import os, glob
import numpy as np
from PIL import Image
from multiprocessing import Pool

ROOT = "/anvil/scratch/x-yguo11"
DENS_DIRS = [   # in chronological folder order: 1, then 2-150, then 151-174
    f"{ROOT}/bhdisk_sol_05/movies/260621_1839_bhdisk_sol05_gw_1-1",
    f"{ROOT}/bhdisk_sol_05/movies/260621_1946_bhdisk_sol05_gw_2-150",
    f"{ROOT}/bhdisk_sol_05/movies/260621_2044_bhdisk_sol05_gw_151-174",
]
MESH_DIR = f"{ROOT}/blender_gw_dev/render_mesh"
OUT      = f"{ROOT}/blender_gw_dev/render_composite_movie"
LO, HI   = -20.0, 70.0          # chroma ramp on (R-B): bg ~ -200, orange disk ~ +190
NPROC    = int(os.environ.get("NPROC", "16"))

# ordered density frame list (lexical sort within each dir = (folder, timestep) order)
DENS = []
for d in DENS_DIRS:
    DENS += sorted(glob.glob(os.path.join(d, "*.png")))
print(f"[setup] {len(DENS)} density frames -> mesh frames 1,3,..,{2*len(DENS)-1}")


def key_chroma(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    rb = a[:, :, 0] - a[:, :, 2]
    alpha = np.clip((rb - LO) / (HI - LO), 0, 1)
    return Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), "RGBA")


def one(i):
    mf = f"{MESH_DIR}/hplus_{2*i+1:06d}.obj.png"
    out = f"{OUT}/comp_{i:06d}.png"
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return "skip"
    if not os.path.exists(mf):
        return f"NO_MESH {2*i+1}"
    try:
        mesh = Image.open(mf).convert("RGBA")
        comp = Image.alpha_composite(mesh, key_chroma(DENS[i]))
        comp.convert("RGB").save(out)
        return "ok"
    except Exception as e:
        return f"ERR {i}: {e}"


def main():
    os.makedirs(OUT, exist_ok=True)
    ok = skip = err = 0
    with Pool(NPROC) as p:
        for n, s in enumerate(p.imap_unordered(one, range(len(DENS)), chunksize=8), 1):
            if s == "ok": ok += 1
            elif s == "skip": skip += 1
            else: err += 1; print(" ", s)
            if n % 500 == 0: print(f"  ...{n}/{len(DENS)} (ok={ok} skip={skip} err={err})", flush=True)
    print(f"[done] ok={ok} skip={skip} err={err}; comps = {len(glob.glob(OUT+'/comp_*.png'))}")


if __name__ == "__main__":
    main()
