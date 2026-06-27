"""convert_objs_parallel.py -- parallel VTK->OBJ for the full GW-mesh movie.

Reproduces convert_vtk_to_obj.py EXACTLY (500x500 grid on [-200,200]^2, GW-FIELD -> z,
inner cut radius 1.27 M_sun, quad faces) but:
  * precomputes the constant grid topology + cut mask ONCE (x,y are frame-independent), and
  * fans the per-frame work (only GW-FIELD changes) across a multiprocessing Pool.

The visible 10 M_sun hole is cut later by Blender's boolean cylinder (plot_single.py:110);
this 1.27 cut only removes the central 1/r divergence, so it must stay well under 10.

Resumable: skips a frame whose .obj already exists.
"""
import os, sys, glob
import numpy as np
import meshio
from multiprocessing import Pool

# config from config.sh (defaults = the sol_05 values)
VTK_DIR = os.environ.get("VTK_DIR", "/anvil/scratch/x-yguo11/abid_bot_dev/gravity_wave_generation/VTKdata/2D")
OUT_DIR = os.environ.get("OBJ_DIR", "/anvil/scratch/x-yguo11/blender_gw_dev/obj_data")
RADIUS  = float(os.environ.get("CUT_RADIUS", "1.0"))   # tiny inner cut; keeps the r~1.265 ring. Blender's boolean cuts the visible 10 M_sun hole.
NDIM    = int(os.environ.get("NDIM", "500"))
XYMAX   = float(os.environ.get("XY_MAX", "200"))
NPROC   = int(os.environ.get("NPROC", str(os.cpu_count() or 16)))

# ---- precompute constant geometry (identical for every frame) ----
x = np.linspace(-XYMAX, XYMAX, NDIM)
y = np.linspace(-XYMAX, XYMAX, NDIM)
X, Y = np.meshgrid(x, y)
Xr, Yr = X.ravel(), Y.ravel()
keep = (Xr*Xr + Yr*Yr) >= (RADIUS*RADIUS)          # process_mesh removes r < radius
new_index = -np.ones(Xr.size, dtype=np.int64)
new_index[keep] = np.arange(int(keep.sum()))
Xk, Yk = Xr[keep], Yr[keep]                         # kept x,y (constant across frames)

# quad faces on the full grid, then keep only fully-surviving quads, renumbered
i, j = np.meshgrid(np.arange(NDIM-1), np.arange(NDIM-1), indexing="ij")
bl = (i*NDIM + j).ravel(); br = (i*NDIM + j+1).ravel()
tl = ((i+1)*NDIM + j).ravel(); tr = ((i+1)*NDIM + j+1).ravel()
quads = np.column_stack((bl, br, tr, tl))
face_keep = keep[quads].all(axis=1)
new_faces = new_index[quads[face_keep]]             # constant for every frame

print(f"[setup] kept {int(keep.sum())}/{Xr.size} verts, {len(new_faces)} quads, radius={RADIUS}", flush=True)


def convert_one(vtk_path):
    base = os.path.splitext(os.path.basename(vtk_path))[0]
    out = os.path.join(OUT_DIR, base + ".obj")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return (base, "skip")
    try:
        mesh = meshio.read(vtk_path)
        z = np.asarray(mesh.point_data["GW-FIELD"]).reshape(NDIM, NDIM).ravel()
        verts = np.column_stack((Xk, Yk, z[keep]))
        meshio.write_points_cells(out, verts, [("quad", new_faces)])
        return (base, "ok")
    except Exception as e:
        return (base, f"ERR {e}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    vtks = sorted(glob.glob(os.path.join(VTK_DIR, "*.vtk")))
    print(f"[main] {len(vtks)} VTKs -> {OUT_DIR} with {NPROC} procs", flush=True)
    ok = skip = err = 0
    with Pool(NPROC) as pool:
        for n, (base, status) in enumerate(pool.imap_unordered(convert_one, vtks, chunksize=8), 1):
            if status == "ok": ok += 1
            elif status == "skip": skip += 1
            else:
                err += 1; print(f"  {base}: {status}", flush=True)
            if n % 1000 == 0:
                print(f"  ...{n}/{len(vtks)} (ok={ok} skip={skip} err={err})", flush=True)
    print(f"[done] ok={ok} skip={skip} err={err}; objs now = "
          f"{len(glob.glob(os.path.join(OUT_DIR,'*.obj')))}", flush=True)


if __name__ == "__main__":
    main()
