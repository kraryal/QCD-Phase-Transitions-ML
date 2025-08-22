# qcd_eos_ml/scripts/figures_appendix_yi.py
import os, argparse
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

OFF_X = 0.16
OFF_Y = 0.14
TICK_LEN = 3.0

def _clean(ax):
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([]); ax.grid(False)
    for a in (ax.xaxis, ax.yaxis, ax.zaxis):
        try: a.set_pane_color((1,1,1,0))
        except Exception: pass

def _axes(ax, xmin, xmax, ymin, ymax, zmin, zmax,
          x_ticks, y_ticks, z_ticks, label_x, label_y, label_z):
    ax.plot([xmin, xmax], [ymin, ymin], [zmin, zmin], color="k", lw=1.0)
    ax.plot([xmax, xmax], [ymin, ymax], [zmin, zmin], color="k", lw=1.0)
    ax.plot([xmin, xmin], [ymin, ymin], [zmin, zmax], color="k", lw=1.0)

    off_x = OFF_X * (xmax - xmin)
    off_y = OFF_Y * (ymax - ymin)
    xmid = xmin + 0.5*(xmax - xmin)
    ymid = ymin + 0.5*(ymax - ymin)
    zmid = zmin + 0.3*(zmax - zmin)

    ax.text(xmid, ymin - off_y*1.8, zmin, label_x, ha="center", va="top", fontsize=12, clip_on=False)
    ax.text(xmax + off_x*1.12, ymid, zmin, label_y, ha="right", va="center", fontsize=12, clip_on=False)
    ax.text(xmin - 0.4*(xmax - xmin), ymin, zmid, label_z, ha="right", va="center", fontsize=12, clip_on=False)

    for tx in x_ticks:
        if xmin <= tx <= xmax:
            ax.plot([tx, tx], [ymin, ymin], [zmin, zmin+TICK_LEN], color="k", lw=0.8)
            ax.text(tx, ymin - off_y*0.6, zmin, f"{tx:g}", ha="center", va="top", fontsize=10, clip_on=False)
    for ty in y_ticks:
        if ymin <= ty <= ymax:
            ax.plot([xmax, xmax], [ty, ty], [zmin, zmin+TICK_LEN], color="k", lw=0.8)
            ax.text(xmax + off_x*0.6, ty, zmin, f"{ty:g}", ha="right", va="center", fontsize=10, clip_on=False)
    for tz in z_ticks:
        if zmin <= tz <= zmax:
            ax.plot([xmin, xmin + 0.02*(xmax - xmin)], [ymin, ymin], [tz, tz], color="k", lw=0.8)
            ax.text(xmin - 0.02*(xmax - xmin), ymin, tz, f"{int(tz)}", ha="right", va="center", fontsize=10, clip_on=False)

def _panel(ax, X, YI, T, color, title, xlim, ylim, zlim,
           xt, yt, zt, lx, ly, lz, elev=24, azim=-35):
    ax.scatter(X, YI, T, s=12, marker="o", facecolors=color, edgecolors="none", alpha=0.98, depthshade=False)
    xmin, xmax = xlim; ymin, ymax = ylim; zmin, zmax = zlim
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax); ax.set_zlim(zmin, zmax)
    _clean(ax); _axes(ax, xmin, xmax, ymin, ymax, zmin, zmax, xt, yt, zt, lx, ly, lz)
    if title: ax.set_title(title, pad=8)
    ax.view_init(elev=elev, azim=azim)

def _save(path, *args, **kwargs):
    fig = plt.figure(figsize=(7.6, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    _panel(ax, *args, **kwargs)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.07, top=0.93)
    fig.savefig(path, dpi=260); plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="ifs1_oct (same layout as eos.skrishna)")
    ap.add_argument("--yi-col", type=int, default=24, help="0-based column index for YI (e.g., 24=p25, 27=p28)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    df = pd.read_csv(args.data, sep=r"\s+", header=None)

    # ifs1_oct mapping for shared fields
    ren = {1:"T", 6:"muB_Q", 7:"muB_H", 8:"muQ_Q", 9:"muQ_H"}
    df = df.rename(columns=ren)

    # pick YI from requested column (p25->24 for quark, p28->27 for hadron)
    df["YI"] = df.iloc[:, args.yi_col]

    # μ̂ using YI
    df["muhat_Q"] = df["muB_Q"] + df["YI"] * df["muQ_Q"]
    df["muhat_H"] = df["muB_H"] + df["YI"] * df["muQ_H"]

    YI = df["YI"].to_numpy()
    T  = df["T"].to_numpy()

    # appendix-style ticks/limits (YI ∈ [-0.5, 0])
    xlim = (500.0, 1500.0); ylim = (-0.5, 0.0); zlim = (0.0, 160.0)
    xt = (500, 1000, 1500); yt = (-0.5, -0.3, -0.1); zt = (0, 50, 100, 150)

    # Hadronic & Quark: X = μB vs YI
    _save(os.path.join(args.out, "appendix_YI_muB_H.png"),
          df["muB_H"].to_numpy(), YI, T, "green", "Hadronic",
          xlim, ylim, zlim, xt, yt, zt, r"$\mu_B$ (MeV)", r"$Y_I$", r"$T$ (MeV)")
    _save(os.path.join(args.out, "appendix_YI_muB_Q.png"),
          df["muB_Q"].to_numpy(), YI, T, "red", "Quark",
          xlim, ylim, zlim, xt, yt, zt, r"$\mu_B$ (MeV)", r"$Y_I$", r"$T$ (MeV)")

    # Purple: μ̂ (quark) vs YI
    _save(os.path.join(args.out, "appendix_YI_muhat_Q.png"),
          df["muhat_Q"].to_numpy(), YI, T, "purple", "Quark ($\\tilde{\\mu}$) vs $Y_I$",
          xlim, ylim, zlim, xt, yt, zt, r"$\tilde{\mu}$ (MeV)", r"$Y_I$", r"$T$ (MeV)")

if __name__ == "__main__":
    main()
