import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

def scatter_3d_points_only(muB, Y, T, color="green", title=None, out=None,
                           elev=24, azim=-35, y_label_text=r"$Y_I$"):
    fig = plt.figure(figsize=(7.6,5.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(muB, Y, T, s=12, marker="o", facecolors=color, edgecolors="none",
               alpha=0.98, depthshade=False, zorder=5)

    xmin, xmax = float(np.min(muB)), float(np.max(muB))
    ymin, ymax = float(np.min(Y)), float(np.max(Y))
    zmin, zmax = 0.0, 160.0
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax); ax.set_zlim(zmin, zmax)
    ax.set_xlabel(""); ax.set_ylabel(""); ax.set_zlabel("")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    try:
        ax.w_xaxis.set_pane_color((1,1,1,0))
        ax.w_yaxis.set_pane_color((1,1,1,0))
        ax.w_zaxis.set_pane_color((1,1,1,0))
    except Exception:
        pass
    ax.grid(False)

    ax.text(xmin, ymin, zmin, r"$\mu_B$ [MeV]", ha="left",  va="top",    fontsize=12)
    ax.text(xmax, ymin, zmin, y_label_text,     ha="right", va="top",    fontsize=12)
    ax.text(xmin, ymin, zmax, r"$T$ [MeV]",     ha="left",  va="bottom", fontsize=12)
    for tv in (0,40,80,120,160):
        ax.text(xmin, ymin, float(tv), f"{int(tv)}", ha="right", va="center", fontsize=10)

    if title: ax.set_title(title, pad=10)
    ax.view_init(elev=elev, azim=azim)
    fig.tight_layout()
    if out: fig.savefig(out, dpi=260)
    return fig

def fig_3d_from_eos(df: pd.DataFrame, outdir: str):
    outdir = str(outdir)
    scatter_3d_points_only(df["muB_H"].values, df["YQ"].values, df["T"].values,
                           color="green", title="Hadron", out=f"{outdir}/3d_points_hadron.png")
    scatter_3d_points_only(df["muB_Q"].values, df["YQ"].values, df["T"].values,
                           color="red", title="Quark", out=f"{outdir}/3d_points_quark.png")
