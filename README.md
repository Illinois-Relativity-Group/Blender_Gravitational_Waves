# Blender GW-mesh renderer

Renders the gravitational-wave "fabric" mesh — the dialed-in grazing view with the central
black-hole/disk hole — from the `.vtk` strain frames produced by the GW pipeline
(`gravity_wave_generation`). Two steps: convert VTK → OBJ, then render OBJ → PNG frames.

The mesh **look** (camera angle/distance, wave height, the hole, the shader/grid) is **locked**
in `plot_single.py` + `shader_grid_solidlightblue.py` so it reproduces exactly. It is not exposed
in `config.sh` (see the `LOCKED LOOK` header in `plot_single.py` if you ever need to re-tune it).

## Requirements

- **Blender 5.0** (CPU Cycles)
- **Python 3** with `numpy`, `meshio`
- `.vtk` strain frames from the GW pipeline (`gravity_wave_generation/VTKdata/2D/hplus_*.vtk`)

## Setup

Edit **`config.sh`** — the only file you change:
```sh
export BLENDER=/path/to/blender-5.0.0/blender
export VTK_DIR=/path/to/gravity_wave_generation/VTKdata/2D   # input frames
export OBJ_DIR=$GW_ROOT/obj_data        # OBJ output
export RENDER_DIR=$GW_ROOT/render_mesh  # rendered PNG output
export XY_MAX=200   export NDIM=500     # MUST match the GW pipeline's XY_MAX_2D / XY_NUM_2D
export STRIDE=2                          # even frames 0,2,4,... to match density/1D cadence (1 = every frame)
```

## Run

```sh
./make_objs.sh        # VTK -> OBJ  (obj_data/hplus_*.obj)
./render_meshes.sh    # OBJ -> PNG  (render_mesh/hplus_*.obj.png), locked look
```
Both are resumable (skip already-produced files). On a cluster, run them as batch jobs instead
of on the login node (edit the `#SBATCH` account/partition):
```sh
sbatch submit_convert_objs_shared.sh      # VTK -> OBJ
sbatch submit_render_array_shared.sh      # full render (48 array tasks)
```

## Outputs

| step | script | output |
|------|--------|--------|
| VTK → OBJ | `convert_objs_parallel.py` (via `make_objs.sh`) | `obj_data/hplus_NNNNNN.obj` |
| OBJ → render | `plot_single.py` (via `render_meshes.sh`) | `render_mesh/hplus_NNNNNN.obj.png` (1920×1080) |

## Movie runs (`MOVIES/`)

Each full render goes into its own **timestamped** directory under `MOVIES/` (gitignored), so runs
don't pile up loose in the repo root. Launch one with:

```sh
# mesh-only:
OBJ_DIR=$PWD/obj_data ./run_movie.sh meshonly_z07
# mesh + disk composited in-render (the disk "switch"):
OBJ_DIR=$PWD/obj_data ./run_movie.sh withdisk_z07 --disk
```

This stamps a dir `MOVIES/<YYMMDD_HHMM>_<run-name>/`, submits the 48-task array into it, and records a
`run_info.txt` (ZSCALE, STRIDE, OBJ source, disk on/off). Frames land in `<run>/frames/`, SLURM logs in
`<run>/`. `--disk` needs `disk_manifest.txt` (lines `<6-digit frame> <disk png>`). Point `OBJ_DIR` at the
full OBJ set — in this workspace that is `obj_data_zoom200`; a fresh clone uses `obj_data` from `make_objs.sh`.

### Continuous relabeling (optional, only for STRIDE ≠ 1)

At `STRIDE=2` the frames are `hplus_000000, 000002, …` (gaps of 2). If your editor wants a gapless
`0,1,2,…` sequence, run this **once, after the render finishes** — it renames the frames **in place**:

```sh
./relabel_continuous.sh MOVIES/<run>/frames     # -> frame_000000.png, frame_000001.png, ...
```

It also writes `frames/mapping.txt` (new name ← original ← physical frame# ← t/M) so the true frame
index and simulation time stay recoverable. Skip it if your tool reads the gappy `hplus_*.obj.png` names.

## Compositing the disk into the hole

`plot_single.py` can drop an accretion-disk render into the central hole via the `with_density`
flag (the 12th positional render arg; `render_meshes.sh` passes `0` = off). Set it to `1` to lay
the disk *image* on a flat plane in the orbital plane (true scale, foreshortened by the grazing
camera). Point the image at your disk render — `plot_single.py:222` `image_path` (currently a
single hardcoded test frame; build the path per-frame for a movie).

## Notes

- **Frame cadence.** `STRIDE=2` (default) renders the even frames `0,2,4,…`, halving the count so
  it matches the density render and the 1D-overlay plots (both step two simulation frames per
  output frame). `STRIDE=1` renders every frame. `STRIDE` strides the frame *list*, which equals
  even frame *numbers* because this pipeline's frames are consecutive.
- **Frames are in simulation time → trim the flat tail.** The mesh is rendered over the *full*
  simulation (coordinate) time, so after the last gravitational wave has passed the extraction
  radius the trailing frames go **flat** (no waves). The mesh sequence is therefore **longer than
  the 1D-overlay sequence** — in a Blender/video-editing session the mesh outlasts the waveform
  overlay. You can safely **cut the waveless trailing frames** at the end to match the overlay
  length (the data isn't wrong — it's just quiet ring-down after the signal leaves the grid).
- `legacy/` holds the tuning/diagnostic one-offs (camera/view dumpers, single-file converters,
  the disk-composite and green-screen movie tools, old drivers). Not needed for the clean path.
- Generated data (`obj_data*/`, `render_*/`, `frames_*/`, logs) is gitignored; clone ships source.
- Downstream disk-density compositing onto the hole is a separate movie step (in `legacy/`).
