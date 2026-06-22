"""plot_1D_greenscreen.py -- sol_05 green-screen growing-waveform frames, t_ret >= 0.

Adapts the shipped plot_1D_edit.py style (green bg, white trace, t_ret / h_+ axes) to sol_05:
  - data = clm_sum_vs_tret_pos.dat (summed h_+ vs retarded time, already cropped to t_ret >= 0),
  - one frame per data row (matches the mesh's 1-row-per-frame cadence),
  - frames NAMED BY MESH INDEX (offset OFF=2857, the row where t_ret=0) so each
    frame_NNNNNN.png composites 1:1 onto the mesh hplus_NNNNNN.obj.png.

Usage:
  python3 plot_1D_greenscreen.py --test     # 3 sample frames (first/mid/last) to eyeball
  python3 plot_1D_greenscreen.py            # all frames, parallel
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from multiprocessing import Pool

DAT  = "/anvil/scratch/x-yguo11/abid_bot_dev/gravity_wave_generation/VTKdata/clm_sum_vs_tret_pos.dat"
OUT  = "/anvil/scratch/x-yguo11/blender_gw_dev/frames_1D_greenscreen"
OFF  = 2857          # mesh-frame index where t_ret = 0 (first row with u>=0)
NPROC = int(os.environ.get("NPROC", "16"))

d = np.loadtxt(DAT)
x = d[:, 0]          # retarded time t_ret / M (starts at ~0)
y = d[:, 1]          # (R/M_ADM) * h_+ summed
N = len(x)
YMAX = 1.2 * np.max(np.abs(y))


def make_fig():
    fig, ax = plt.subplots(figsize=(12.8, 3.6))            # -> 1920x540 at dpi=150
    ax.set_facecolor("green"); fig.patch.set_facecolor("green")
    ax.set_xlim(x[0], x[-1]); ax.set_ylim(-YMAX, YMAX)
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_xlabel(r"$t_{ret}/M$", fontsize=26, loc="right", color="white")
    ax.set_ylabel(r"$h_+$", fontsize=26, rotation=0, color="white")
    ax.yaxis.set_label_coords(-0.04, 0.78)
    ax.set_xticklabels([]); ax.set_yticklabels([])
    ax.tick_params(axis="both", colors="white")
    for s in ("left", "bottom"): ax.spines[s].set_color("white")
    (line,) = ax.plot([], [], color="white", lw=1.4)
    fig.tight_layout()
    return fig, ax, line


def render_chunk(idxs):
    fig, ax, line = make_fig()
    for i in idxs:
        line.set_data(x[:i + 1], y[:i + 1])
        fig.savefig(f"{OUT}/frame_{OFF + i:06d}.png", facecolor=fig.get_facecolor(), dpi=150)
    plt.close(fig)
    return len(idxs)


def main():
    os.makedirs(OUT, exist_ok=True)
    test = "--test" in sys.argv
    if test:
        idxs = [0, N // 2, N - 1]
        render_chunk(idxs)
        print(f"TEST frames: " + ", ".join(f"frame_{OFF+i:06d}.png (t_ret/M={x[i]:.0f})" for i in idxs))
        return
    chunks = [list(range(k, N, NPROC)) for k in range(NPROC)]   # round-robin chunks
    with Pool(NPROC) as p:
        done = sum(p.map(render_chunk, chunks))
    print(f"wrote {done} frames to {OUT}  (frame_{OFF:06d} .. frame_{OFF+N-1:06d}; t_ret/M 0 .. {x[-1]:.0f})")


if __name__ == "__main__":
    main()
