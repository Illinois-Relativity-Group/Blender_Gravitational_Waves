# Blender GW-mesh renderer

Renders the gravitational-wave "fabric" mesh — the dialed-in grazing view with the central
black-hole/disk hole, optionally with the accretion disk composited into the hole — from the
`.vtk` strain frames produced by the GW pipeline (`gravity_wave_generation`).

**Two steps, two commands:**

```sh
sbatch submit_convert_objs_shared.sh     # 1. VTK -> OBJ   (once per dataset)
./submit_render.sh fullmovie             # 2. OBJ -> PNG   (the one render launcher)
```

Everything you tune lives in **`config.sh`**. The fixed part of the look — camera
angle/distance/lens and the grid-shader scale — stays **locked** in `plot_single.py` +
`shader_grid_solidlightblue.py` so the dialed-in view reproduces exactly.

## Requirements

- **Blender 5.0** (CPU Cycles) — path in `config.sh`
- **Python 3** with `numpy`, `PIL` (`module load anaconda/2024.02-py311`) and **`meshio`**
  (`requirements.txt`; the convert scripts auto-install it into your user site on first run)
- `.vtk` strain frames at `VTK_DIR` (`gravity_wave_generation/VTKdata/2D/hplus_*.vtk`)

## Setup — edit `config.sh` only

The defaults reproduce the team's **current** movie (new-opacity disk, 15 M_sun hole, 128 samples):

```sh
export OBJ_DIR=$GW_ROOT/obj_data_zoom200    # OBJ set (the ±200 M_sun mesh the locked camera needs)
export STRIDE=2                             # cadence: 2 = even frames (matches disk & 1D), 1 = every frame

export FRAMES=all                          # what to render: all | "0 5000" | "0-200" | "0-200:10"
export MAX_TASKS=48                        # SLURM array cap (array auto-sizes to min(#frames, MAX_TASKS))

export WITH_DISK=1                         # 1 = composite disk in-render, 0 = mesh-only
export DISK_FOLDER=...full_density_movie_newopa   # disk PNGs (input to build_disk_manifest.py)
export DISK_MANIFEST=$GW_ROOT/disk_manifest_newopa.txt  # built manifest (the renderer reads this)
export HOLE_RADIUS=15   export ZSCALE=0.7   export DISK_MARGIN=0   export SAMPLES=128
```

## Step 1 — VTK → OBJ (resumable)

```sh
sbatch submit_convert_objs_shared.sh      # cluster job (Pool-parallel, skips existing .obj)
./make_objs.sh                            # or run locally
```
Output: `$OBJ_DIR/hplus_NNNNNN.obj` (one per frame).

## Disk prep — only if `WITH_DISK=1` (once per disk-frame set)

Build the disk manifest from a folder of disk PNGs (sorts them, maps frame = `STRIDE`×index, and
adds the per-frame size-normalization scale via `measure_disk_scale.py`):

```sh
module load anaconda/2024.02-py311
python3 build_disk_manifest.py "$DISK_FOLDER" "$DISK_MANIFEST"
```

## Step 2 — render (the one launcher)

`submit_render.sh` reads `config.sh`, expands `FRAMES` into a frame list, **auto-sizes the SLURM
array** to exactly that many frames (no idle tasks), and submits. A run-name gives the output its
own timestamped dir `MOVIES/<ts>_<name>/frames/`.

```sh
FRAMES="0 5000" ./submit_render.sh test        # quick 2-frame test  -> a 2-task array
./submit_render.sh fullmovie                    # FRAMES=all -> the whole movie (48 tasks)
WITH_DISK=0 FRAMES="0-200" ./submit_render.sh meshonly   # mesh-only, frames 0..200 at STRIDE
```

- **FRAMES** syntax: `all`, a list (`"0 5000"` / `"0,5000"`), or a range `A-B[:step]` (step
  defaults to `STRIDE`). Any config knob can be overridden inline, e.g. `HOLE_RADIUS=12 ...`.
- **Disk on/off** is just `WITH_DISK`; **frame subset vs all** is just `FRAMES`. They compose.
- Resumable: re-running skips already-produced PNGs. Frames land in `RENDER_DIR` (or the run dir);
  SLURM logs in `<dir>/logs/`.

Output: `hplus_NNNNNN.obj.png` (1920×1080).

### Continuous relabeling (optional, only for STRIDE ≠ 1)

At `STRIDE=2` the frames are `hplus_000000, 000002, …` (gaps of 2). For a gapless `0,1,2,…`
sequence, run **once after the render finishes** (renames in place, writes `mapping.txt` with the
true frame# and t/M):

```sh
./relabel_continuous.sh MOVIES/<run>/frames     # -> frame_000000.png, frame_000001.png, ...
```

## Notes

- **Trim the flat tail.** The mesh is rendered over the *full* simulation time, so after the last
  wave leaves the grid the trailing frames go flat (no waves) — the mesh sequence outlasts the disk
  and 1D-overlay sequences. Cut the waveless tail in your editor to match.
- **Quick local smoke test** (no queue): `./render_meshes.sh` renders the full strided set on one
  node. For a few frames, prefer `FRAMES="0 5000" ./submit_render.sh test`.
- `legacy/` holds tuning/diagnostic one-offs (camera dumpers, single-file converters, old drivers).
  Not needed for the clean path.
- Generated data (`obj_data*/`, `render_*/`, `MOVIES/`, `frames_*/`, manifests, logs) is gitignored;
  the clone ships source only.
