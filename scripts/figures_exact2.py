# qcd_eos_ml/scripts/figures_exact2.py
import os, argparse
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# --- layout knobs ---
OFF_X = 0.16   # push right-side labels/ticks outward (fraction of μB range)
OFF_Y = 0.14   # push front labels/ticks downward (fraction of Y range)
TICK_LEN = 3.0 # length of little tick marks (in T units)

# -------------------- helpers --------------------
def draw_axes_and_labels(ax, xmin, xmax, ymin, ymax, zmin, zmax,
                         x_ticks, y_ticks, z_ticks,
                         label_x, label_y, label_z):
    # show axis lines
    ax.plot([xmin, xmax], [ymin, ymin], [zmin, zmin], color="k", lw=1.0)  # X base
    ax.plot([xmax, xmax], [ymin, ymax], [zmin, zmin], color="k", lw=1.0)  # Y base (right)
    ax.plot([xmin, xmin], [ymin, ymin], [zmin, zmax], color="k", lw=1.0)  # T vertical (left)

    # offsets
    off_x = OFF_X * (xmax - xmin)
    off_y = OFF_Y * (ymax - ymin)

    # centers for axis titles
    xmid = xmin + 0.5*(xmax - xmin)
    ymid = ymin + 0.5*(ymax - ymin)
    zmid = zmin + 0.3*(zmax - zmin)

    # axis names (centered, outside box)
    ax.text(xmid, ymin - off_y*1.8, zmin, label_x,
            ha="center", va="top", fontsize=12, clip_on=False)
    ax.text(xmax + off_x*1.12, ymid, zmin, label_y,
            ha="right", va="center", fontsize=12, clip_on=False)
    ax.text(xmin - 0.4*(xmax - xmin), ymin, zmid, label_z,
            ha="right", va="center", fontsize=12, clip_on=False)

    # tick marks + numbers
    for tx in x_ticks:  # μB or μ̂ along front base
        ax.plot([tx, tx], [ymin, ymin], [zmin, zmin + TICK_LEN], color="k", lw=0.8)
        ax.text(tx, ymin - off_y*0.6, zmin, f"{tx:g}",
                ha="center", va="top", fontsize=10, clip_on=False)

    for ty in y_ticks:  # Y axis (YQ or μQ) on right base
        ax.plot([xmax, xmax], [ty, ty], [zmin, zmin + TICK_LEN], color="k", lw=0.8)
        ax.text(xmax + off_x*0.6, ty, zmin, f"{ty:g}",
                ha="right", va="center", fontsize=10, clip_on=False)

    for tz in z_ticks:  # T ticks
        ax.plot([xmin, xmin + 0.02*(xmax - xmin)], [ymin, ymin], [tz, tz], color="k", lw=0.8)
        ax.text(xmin - 0.02*(xmax - xmin), ymin, tz, f"{int(tz)}",
                ha="right", va="center", fontsize=10, clip_on=False)

def clean_3d(ax):
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([]); ax.grid(False)
    for a in (ax.xaxis, ax.yaxis, ax.zaxis):
        try: a.set_pane_color((1,1,1,0))
        except Exception: pass

def panel(ax, X, Y, Z, color, title,
          xlim, ylim, zlim,
          x_ticks, y_ticks, z_ticks,
          label_x, label_y, label_z,
          elev=24, azim=-35):
    # points only
    ax.scatter(X, Y, Z, s=12, marker="o", facecolors=color,
               edgecolors="none", alpha=0.98, depthshade=False)
    xmin, xmax = xlim; ymin, ymax = ylim; zmin, zmax = zlim
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax); ax.set_zlim(zmin, zmax)
    clean_3d(ax)
    draw_axes_and_labels(ax, xmin, xmax, ymin, ymax, zmin, zmax,
                         x_ticks, y_ticks, z_ticks,
                         label_x, label_y, label_z)
    if title: ax.set_title(title, pad=8)
    ax.view_init(elev=elev, azim=azim)

def save_panel(path, *args, **kwargs):
    fig = plt.figure(figsize=(7.6, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    panel(ax, *args, **kwargs)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.07, top=0.93)
    fig.savefig(path, dpi=260)
    plt.close(fig)

def lin_ticks(a, b, n):
    vals = np.linspace(a, b, n)
    return tuple(int(round(v/10.0)*10) for v in vals)

# -------------------- main --------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Path to eos.skrishna")
    ap.add_argument("--out", required=True, help="Output folder for figures")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    df = pd.read_csv(args.data, sep=r"\s+", header=None)
    # rename columns (0-indexed). User said μQ in 9th & 10th columns (1-indexed),
    # i.e., indices 8 and 9 here; we map 8→muQ_Q, 9→muQ_H.
    # add μ̂ columns (tilde mu) from data
    if {"YQ", "muB_Q", "muQ_Q"}.issubset(df.columns):
        df["muhat_Q"] = df["muB_Q"] + df["YQ"] * df["muQ_Q"]  # quark

    if {"YQ", "muB_H", "muQ_H"}.issubset(df.columns):
        df["muhat_H"] = df["muB_H"] + df["YQ"] * df["muQ_H"]  # hadron

    ren = {0:"YQ", 1:"T", 2:"$\tilde mu_Q$", 3:"$\tilde mu_H$", 6:"muB_Q", 7:"muB_H"}
    if df.shape[1] >= 10:
        ren.update({8:"muQ_Q", 9:"muQ_H"})
    df = df.rename(columns=ren)

    YQ = df["YQ"].to_numpy()
    T  = df["T"].to_numpy()

    zlim = (0.0, 160.0); z_ticks = (0, 50, 100, 150)

    # --- Main YQ panels (Fig.1 style) ---
    xlim_yq = (500.0, 1500.0); ylim_yq = (0.0, 0.5)
    x_ticks_yq = (500, 1000, 1500); y_ticks_yq = (0.0, 0.2, 0.4)

    # 1) Hadronic: X = μB^H, Y = YQ
    save_panel(os.path.join(args.out, "hadronic_exact.png"),
               df["muB_H"].to_numpy(), YQ, T, color="green", title="Hadronic",
               xlim=xlim_yq, ylim=ylim_yq, zlim=zlim,
               x_ticks=x_ticks_yq, y_ticks=y_ticks_yq, z_ticks=z_ticks,
               label_x=r"$\mu_B$ (MeV)", label_y=r"$Y_Q$", label_z=r"$T$ (MeV)")

    # 2) Quark: X = μB^Q, Y = YQ
    save_panel(os.path.join(args.out, "quark_exact.png"),
               df["muB_Q"].to_numpy(), YQ, T, color="red", title="Quark",
               xlim=xlim_yq, ylim=ylim_yq, zlim=zlim,
               x_ticks=x_ticks_yq, y_ticks=y_ticks_yq, z_ticks=z_ticks,
               label_x=r"$\mu_B$ (MeV)", label_y=r"$Y_Q$", label_z=r"$T$ (MeV)")

    # 3) Purple panel: **μ̂ (quark) vs YQ**  (NOT F_quark)
    has_muQ = {"muQ_Q","muQ_H"}.issubset(df.columns)
    if has_muQ:
        muhat_Q = df["muB_Q"].to_numpy() + YQ * df["muQ_Q"].to_numpy()
        xlim_muhat = (500.0, 1500.0)
        x_ticks_muhat = (500, 1000, 1500)
        save_panel(os.path.join(args.out, "muhat_quark_YQ_exact.png"),
                   muhat_Q, YQ, T, color="purple", title="Quark (μ̂) vs $Y_Q$",
                   xlim=xlim_muhat, ylim=ylim_yq, zlim=zlim,
                   x_ticks=x_ticks_muhat, y_ticks=y_ticks_yq, z_ticks=z_ticks,
                   label_x=r"$\tilde{\mu}$ (MeV)", label_y=r"$Y_Q$", label_z=r"$T$ (MeV)")
    else:
        print("[warn] μQ columns not found; skipping μ̂ quark panel")

    # --- Fig.2 style (μQ on right axis) if μQ present ---
    if has_muQ:
        muQ_H = df["muQ_H"].to_numpy()
        muQ_Q = df["muQ_Q"].to_numpy()

        # X = μB, Y = μQ
        xlim_muB = (500.0, 1500.0)
        ylim_muQ = (-500.0, 0.0)
        x_ticks_muB = (500, 1000, 1500)
        y_ticks_muQ = (-400, -200, 0)

        save_panel(os.path.join(args.out, "muQ_vs_muB_H.png"),
                   df["muB_H"].to_numpy(), muQ_H, T, color="green", title="Hadronic",
                   xlim=xlim_muB, ylim=ylim_muQ, zlim=zlim,
                   x_ticks=x_ticks_muB, y_ticks=y_ticks_muQ, z_ticks=z_ticks,
                   label_x=r"$\mu_B$ (MeV)", label_y=r"$\mu_Q$ (MeV)", label_z=r"$T$ (MeV)")

        save_panel(os.path.join(args.out, "muQ_vs_muB_Q.png"),
                   df["muB_Q"].to_numpy(), muQ_Q, T, color="red", title="Quark",
                   xlim=xlim_muB, ylim=ylim_muQ, zlim=zlim,
                   x_ticks=x_ticks_muB, y_ticks=y_ticks_muQ, z_ticks=z_ticks,
                   label_x=r"$\mu_B$ (MeV)", label_y=r"$\mu_Q$ (MeV)", label_z=r"$T$ (MeV)")

        # X = μ̂, Y = μQ
        muhat_H = df["muB_H"].to_numpy() + YQ * muQ_H
        muhat_Q = df["muB_Q"].to_numpy() + YQ * muQ_Q
        xlim_muhat = (500.0, 1500.0); x_ticks_muhat = (500, 1000, 1500)

        save_panel(os.path.join(args.out, "muQ_vs_muhat_H.png"),
                   muhat_H, muQ_H, T, color="green", title="Hadronic",
                   xlim=xlim_muhat, ylim=ylim_muQ, zlim=zlim,
                   x_ticks=x_ticks_muhat, y_ticks=y_ticks_muQ, z_ticks=z_ticks,
                   label_x=r"$\tilde{\mu}$ (MeV)", label_y=r"$\mu_Q$ (MeV)", label_z=r"$T$ (MeV)")

        save_panel(os.path.join(args.out, "muQ_vs_muhat_Q.png"),
                   muhat_Q, muQ_Q, T, color="red", title="Quark",
                   xlim=xlim_muhat, ylim=ylim_muQ, zlim=zlim,
                   x_ticks=x_ticks_muhat, y_ticks=y_ticks_muQ, z_ticks=z_ticks,
                   label_x=r"$\tilde{\mu}$ (MeV)", label_y=r"$\mu_Q$ (MeV)", label_z=r"$T$ (MeV)")
    else:
        print("[warn] μQ columns not found; skipped μQ/μ̂ panels")

if __name__ == "__main__":
    main()
