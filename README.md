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
export STRIDE=1                          # movie frame step (4 = every 4th frame)
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

## Notes

- `legacy/` holds the tuning/diagnostic one-offs (camera/view dumpers, single-file converters,
  the disk-composite and green-screen movie tools, old drivers). Not needed for the clean path.
- Generated data (`obj_data*/`, `render_*/`, `frames_*/`, logs) is gitignored; clone ships source.
- Downstream disk-density compositing onto the hole is a separate movie step (in `legacy/`).
