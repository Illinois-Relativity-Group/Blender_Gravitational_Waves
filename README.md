# Blender GW-mesh renderer

Renders the gravitational-wave "fabric" mesh — the dialed-in grazing view with the central
black-hole/disk hole, optionally with the accretion disk composited into the hole — from the
`.vtk` strain frames produced by the GW pipeline (`gravity_wave_generation`).

**The flow** (the disk-prep line is only needed when `WITH_DISK=1`, the default):

```sh
sbatch submit_convert_objs_shared.sh                            # 1. VTK -> OBJ  (once per dataset)
python3 build_disk_manifest.py "$DISK_FOLDER" "$DISK_MANIFEST"  #    disk prep   (once, if WITH_DISK=1)
./submit_render.sh fullmovie                                    # 2. OBJ -> PNG  (the one launcher)
```

Everything you tune lives in **`config.sh`**. The fixed part of the look — camera
angle/distance/lens and the grid-shader scale — stays **locked** in `lib/plot_single.py` +
`lib/shader_grid_solidlightblue.py` so the dialed-in view reproduces exactly. The top-level
scripts are the entry points; the workers they call live in **`lib/`** (you never invoke those
directly).

## Requirements

- **Blender 5.0** (CPU Cycles) — path in `config.sh`
- **Python 3** with `numpy`, `PIL` (`module load anaconda/2024.02-py311`) and **`meshio`**
  (`requirements.txt`; the convert scripts auto-install it into your user site on first run)
- `.vtk` strain frames at `VTK_DIR` (`gravity_wave_generation/VTKdata/2D/hplus_*.vtk`)

## Setup — edit `config.sh` only

The defaults reproduce the team's **current** movie (new-opacity disk, 7.5 M_sun hole, 128 samples;
camera dollied in to distance 125 for a faithful 2x-magnified, single-ruler look — see the camera note below):

```sh
export OBJ_DIR=$GW_ROOT/obj_data            # OBJ set (the ±200 M_sun mesh the locked camera needs)
export STRIDE=2                             # cadence: 2 = even frames (matches disk & 1D), 1 = every frame

export FRAMES=all                          # what to render: all | "0 5000" | "0-200" | "0-200:10"
export MAX_TASKS=48                        # SLURM array cap (array auto-sizes to min(#frames, MAX_TASKS))

export WITH_DISK=1                         # 1 = composite disk in-render, 0 = mesh-only
export DISK_FOLDER=...   # <-- PER-USER: point at YOUR disk PNGs (input to build_disk_manifest.py)
export DISK_MANIFEST=... # <-- PER-USER: where build_disk_manifest.py writes / the renderer reads
export HOLE_RADIUS=7.5  export ZSCALE=0.7   export DISK_MARGIN=0   export SAMPLES=128
```

> **`DISK_FOLDER` / `DISK_MANIFEST` are per-user paths.** The values checked into `config.sh` are
> one person's local render and **will not exist on your machine** — repoint `DISK_FOLDER` at *your
> own* disk PNG set (rendered at VisIt `imageZoom=2` / the meshmatch view) and `DISK_MANIFEST` at
> wherever you want the manifest, then build it (next section). Everything else in `config.sh` is a
> portable default. (Mesh-only renders, `WITH_DISK=0`, need neither.)

## Step 1 — VTK → OBJ (resumable)

```sh
sbatch submit_convert_objs_shared.sh      # cluster job (Pool-parallel, skips existing .obj)
./make_objs.sh                            # or run locally
```
Output: `$OBJ_DIR/hplus_NNNNNN.obj` (one per frame).

## Disk prep — only if `WITH_DISK=1` (once per disk-frame set)

Build the disk manifest from a folder of disk PNGs (sorts them, maps frame = `STRIDE`×index, and
adds the per-frame size-normalization scale via `lib/measure_disk_scale.py`):

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

### Continuous relabeling (optional; for any gappy names — STRIDE > 1 or a frame subset)

At `STRIDE=2` the frames are `hplus_000000, 000002, …` (gaps of 2; a frame subset is gappy too). For a gapless `0,1,2,…`
sequence, run **once after the render finishes** (renames in place, writes `mapping.txt` with the
true frame# and t/M):

```sh
./relabel_continuous.sh MOVIES/<run>/frames     # -> frame_000000.png, frame_000001.png, ...
```

## Examples

```sh
# --- quick tests (array auto-sizes to the # of frames) ---
FRAMES="0 5000" ./submit_render.sh test            # 2-frame smoke test, current look -> 2-task array
WITH_DISK=0 FRAMES="0 5000" ./submit_render.sh meshtest   # same frames, mesh-only
FRAMES="0-200" ./submit_render.sh rangetest        # strided range 0,2,4,...,200
FRAMES="0-8000:50" ./submit_render.sh coarse       # every 50th frame, a fast whole-movie preview

# --- look tuning (override a knob on a few frames) ---
HOLE_RADIUS=12 FRAMES="5000" ./submit_render.sh hole12     # try a different hole size
ZSCALE=1.0 FRAMES="2000 4000 6000" ./submit_render.sh zs   # bigger wave height
SAMPLES=32 FRAMES="0 5000" ./submit_render.sh fastlook     # cheap/noisy preview
for r in 10 12 15 18; do HOLE_RADIUS=$r FRAMES=5000 ./submit_render.sh hole_$r; done  # sweep

# --- production ---
./submit_render.sh fullmovie                       # whole movie, current settings (48 tasks)
WITH_DISK=0 ./submit_render.sh meshonly            # whole movie, mesh-only
SAMPLES=256 ./submit_render.sh fullmovie_hq        # higher quality
CAP=10 ./submit_render.sh fullmovie                # 48 tasks queued, only 10 active at once

# --- different data ---
OBJ_DIR=/path/to/other_obj_set ./submit_render.sh altobj   # render from a different OBJ set
python3 build_disk_manifest.py /path/to/new_disk_pngs $PWD/new_manifest.txt
DISK_MANIFEST=$PWD/new_manifest.txt ./submit_render.sh newdisk

# --- cold start, end to end ---
sbatch submit_convert_objs_shared.sh                            # 1. VTK -> OBJ
module load anaconda/2024.02-py311
python3 build_disk_manifest.py "$DISK_FOLDER" "$DISK_MANIFEST"  # 2. disk manifest (once)
./submit_render.sh fullmovie                                    # 3. render
./relabel_continuous.sh MOVIES/<ts>_fullmovie/frames           # 4. relabel (after it finishes)
```

If you specify no flags, every knob falls back to its **`config.sh`** default (disk ON, hole 7.5,
samples 128, etc.). `lib/plot_single.py`'s bare defaults are kept in sync with `config.sh`, so the
look is identical however the renderer is invoked.

**Camera (locked in `lib/plot_single.py`, not a `config.sh` knob).** The view is dollied in to
`DOLLY_DIST=125` with the wide `50 mm` lens (`ZOOM=1`). That gives a 2x magnification — so the
accretion disk (VisIt-rendered at `imageZoom=2`) sits at its *true* physical size on the mesh and
**one ruler measures both the grid and the disk** (the disk no longer reads 2x too big). The 2x is
done by *dollying in*, not telephoto, so the converging-grid perspective is preserved; a telephoto
(`ZOOM>1`) gives the same magnification but flattens the perspective. The disk billboard, time label,
and grid cell size all auto-track `DOLLY_DIST`/`ZOOM`, so the scale stays consistent. Both are
env-overridable for experiments but locked by default.

## Pitfalls & fixes

- **Disk needs its manifest.** With `WITH_DISK=1`, the launcher *errors out* if `DISK_MANIFEST`
  doesn't exist (build it, or pass `WITH_DISK=0`), and *warns* if some selected frames have no entry
  (those render mesh-only). It will not silently hand you a diskless movie you asked to have a disk.
- **Keep `STRIDE` consistent with the manifest.** The manifest maps `frame = STRIDE×index`. Building
  it at `STRIDE=2` then rendering at `STRIDE=1` makes the odd frames fall outside the manifest →
  they render mesh-only (you'll see the warning above). Use `STRIDE=1` for *mesh-only* fine renders,
  or rebuild the manifest at the STRIDE you render.
- **Disk frames must sort chronologically.** `build_disk_manifest.py` pairs frames by
  `sorted(*.png)`, so filenames must be **zero-padded** (e.g. `..._007_003_...`, not `..._7_3_...`)
  or the disk gets paired to the wrong frame. Check the `first/last` lines the builder prints.
- **Resuming a full run.** A run-name makes a *new* timestamped dir each launch, so re-running
  `./submit_render.sh fullmovie` starts fresh. To resume an interrupted run, re-target the same dir
  instead: `RENDER_DIR=$PWD/MOVIES/<ts>_fullmovie/frames ./submit_render.sh` (no run-name).
- **The OBJ set must be the ±200 M_sun mesh** (`XY_MAX=200`). The locked camera (`DOLLY_DIST=125`,
  wide 50 mm) needs that extent so the frame corners stay covered; regenerating `obj_data` at a
  smaller `XY_MAX` would leave them uncovered.

## Notes

- **Trim the flat tail.** The mesh is rendered over the *full* simulation time, so after the last
  wave leaves the grid the trailing frames go flat (no waves) — the mesh sequence outlasts the disk
  and 1D-overlay sequences. Cut the waveless tail in your editor to match.
- **Quick test = a small `FRAMES` on the farm**, e.g. `FRAMES="0 5000" ./submit_render.sh test`
  (auto-sizes to a 2-task array; finishes in ~a minute of compute). There is no login-node render
  path — rendering always goes through SLURM.
- `lib/` holds the workers the top-level scripts call (`plot_single.py`, the shaders,
  `render_{array_job,node,one}.sh`, `convert_objs_parallel.py`, `measure_disk_scale.py`,
  `white_plane.blend`). You drive everything through the top-level entry points — never call these
  directly.
- `legacy/` holds tuning/diagnostic one-offs (camera dumpers, single-file converters, old drivers).
  Not needed for the clean path.
- Generated data (`obj_data*/`, `render_*/`, `MOVIES/`, `frames_*/`, manifests, logs) is gitignored;
  the clone ships source only.
