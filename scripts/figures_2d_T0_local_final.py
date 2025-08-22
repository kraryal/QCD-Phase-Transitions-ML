# T=0 two-panel figure (paper style, fixed ranges, no grid)
# Uses low-T files: achargecode_nonstrange_l, bchargecode_strange_2d_l

import os, numpy as np, pandas as pd, matplotlib.pyplot as plt

# ---- inputs ----
NS_FILE = r".\data\achargecode_nonstrange_l"
S_FILE  = r".\data\bchargecode_strange_2d_l"
OUT_DIR = r".\figures"

# low-T column map you specified
YQ_COL, MUB_H_COL, MUB_Q_COL, MUQ_Q_COL, MUQ_H_COL = 0, 7, 6, 8, 9

# axis limits to match the paper
Y_LIM       = (1320, 1460)
X_LIM_YQ    = (0.0, 0.5)
X_LIM_MUQ   = (-450, 10)

ROSE = "rosybrown"   # \tilde{\mu} non-strange

def finite_xy(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    return x[m], y[m]

def style_axes(ax, title_inside=True):
    # thicker spines + inwards ticks like the paper
    for s in ax.spines.values(): s.set_linewidth(1.4)
    ax.tick_params(direction="in", length=6, width=1.2, top=True, right=True)
    if title_inside:
        ax.text(0.97, 0.07, "T = 0 MeV", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=11)

def simple_clean_yq(x, y, max_x):
    """Very simple cleaning for YQ curves - just truncate"""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    
    if len(x) == 0:
        return x, y
    
    # Basic filtering
    mask = np.isfinite(x) & np.isfinite(y) & (x <= max_x)
    x, y = x[mask], y[mask]
    
    if len(x) < 2:
        return x, y
    
    # Sort by x
    sort_idx = np.argsort(x)
    x, y = x[sort_idx], y[sort_idx]
    
    return x, y

def simple_clean_muq(x, y):
    """Simple cleaning for muQ curves"""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    
    # Remove invalid points
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    
    if len(x) == 0:
        return x, y
    
    # Basic bounds
    mask = (x >= -450) & (x <= 10) & (y >= 1320) & (y <= 1460)
    x, y = x[mask], y[mask]
    
    if len(x) == 0:
        return x, y
    
    # Sort
    sort_idx = np.argsort(x)
    x, y = x[sort_idx], y[sort_idx]
    
    return x, y

def simple_extend(x, y, target_x=-400):
    """Simple extension without overcomplication"""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    
    if len(x) < 2 or x[0] <= target_x:
        return x, y
    
    # Just linear extrapolation from first two points
    slope = (y[1] - y[0]) / (x[1] - x[0]) if x[1] != x[0] else 0
    target_y = y[0] + slope * (target_x - x[0])
    
    # Add just one point
    x_new = np.concatenate([[target_x], x])
    y_new = np.concatenate([[target_y], y])
    
    return x_new, y_new

def collapse_duplicates(x, y, tol=1e-9):
    """Average y when consecutive x are (nearly) identical to avoid vertical segments."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) == 0:
        return x, y
    order = np.argsort(x)
    x = x[order]; y = y[order]
    xs = [x[0]]; ys = [y[0]]; c = 1
    for i in range(1, len(x)):
        if abs(x[i] - xs[-1]) < tol:
            ys[-1] = (ys[-1] * c + y[i]) / (c + 1)
            c += 1
        else:
            xs.append(x[i]); ys.append(y[i]); c = 1
    return np.array(xs), np.array(ys)

def remove_tail_spikes(x, y, tail_from=0.46, max_drop=18.0):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3:
        return x, y
    order = np.argsort(x)
    x = x[order]; y = y[order]

    dy = np.diff(y)
    bad = np.zeros_like(y, dtype=bool)

    # mark only the last one or two points if they plunge
    for i in range(1, len(y)):
        if x[i] >= tail_from and (y[i] - y[i-1]) < -abs(max_drop):
            bad[i] = True

    # never mask them all
    if bad.sum() >= len(y) - 2:
        bad[:] = False
        if len(y) >= 1: bad[-1] = True

    y = y.copy()
    y[bad] = np.nan
    return x, y


def break_outside_ylim(y, ylim):
    """Replace values outside y-limits with NaN so no line is drawn to the bound."""
    y = np.asarray(y, float).copy()
    y[(y < ylim[0]) | (y > ylim[1])] = np.nan
    return y

import numpy as np

def yq_fix(x, y, y_range=(1320, 1460), right_cut=0.5, tail_from=0.47):
    """Conservative cleanup for YQ curves.
    - keep points in range
    - sort by x
    - drop ONLY the last 1–2 tail spikes (sharp negative jumps past ~0.47)
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]

    # keep the plotting window (slightly loose on the upper y bound)
    m = (x >= 0.0) & (x <= right_cut) & (y >= y_range[0]) & (y <= y_range[1] + 20)
    x, y = x[m], y[m]
    if x.size < 3:
        return x, y

    order = np.argsort(x)
    x, y = x[order], y[order]

    dy = np.diff(y)
    mad = np.median(np.abs(dy - np.median(dy))) if dy.size else 0.0
    thr = max(8.0, 6*mad)  # robust threshold in MeV

    bad = np.zeros_like(y, dtype=bool)
    for i in range(1, len(y)):
        if x[i] > tail_from and (y[i] - y[i-1]) < -thr:
            bad[i] = True

    # never mask almost-everything
    if bad.sum() >= len(y) - 2:
        bad[:] = False
        bad[-1] = True

    y = y.copy()
    y[bad] = np.nan
    return x, y



def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    a = pd.read_csv(NS_FILE, sep=r"\s+", header=None, engine="python")
    b = pd.read_csv(S_FILE,  sep=r"\s+", header=None, engine="python")

    # series (low T)
    YQ_ns    = a.iloc[:,YQ_COL].to_numpy()
    muB_ns_H = a.iloc[:,MUB_H_COL].to_numpy()
    muB_ns_Q = a.iloc[:,MUB_Q_COL].to_numpy()
    muQ_ns_Q = a.iloc[:,MUQ_Q_COL].to_numpy()
    muQ_ns_H = a.iloc[:,MUQ_H_COL].to_numpy() if a.shape[1]>MUQ_H_COL else muQ_ns_Q

    YQ_s     = b.iloc[:,YQ_COL].to_numpy()
    muB_s_H  = b.iloc[:,MUB_H_COL].to_numpy()
    muB_s_Q  = b.iloc[:,MUB_Q_COL].to_numpy()
    muQ_s_Q  = b.iloc[:,MUQ_Q_COL].to_numpy()
    muQ_s_H  = b.iloc[:,MUQ_H_COL].to_numpy() if b.shape[1]>MUQ_H_COL else muQ_s_Q

    muhat_ns = muB_ns_Q + YQ_ns*muQ_ns_Q
    muhat_s  = muB_s_Q  + YQ_s *muQ_s_Q

    fig, axes = plt.subplots(2, 1, figsize=(8, 10))
    
    # ---------- TOP: YQ panel (try without markers first) ----------
    # ---------- TOP: YQ panel ----------
    ax = axes[0]

    curves = [
        (YQ_ns, muB_ns_H, 'Green', '',  '*', 9, r"$\mu_B$ H non-strange"),
        (YQ_s,  muB_s_H,  'Black', '',  '*', 9, r"$\mu_B$ H strange"),
        (YQ_ns, muB_ns_Q, 'red',   '--', 's', 3, r"$\mu_B$ Q non-strange"),
        (YQ_s,  muB_s_Q,  'black', '-.', 'o', 3, r"$\mu_B$ Q strange"),
        (YQ_ns, muhat_ns, ROSE,    '-',  'D', 3, r"$\tilde{\mu}$ H/Q non-strange"),
        (YQ_s,  muhat_s,  'black', '-',  'D', 3, r"$\tilde{\mu}$ H/Q strange"),
    ]

    for X, Y, c, ls, m, ms, lbl in curves:
        xs, ys = yq_fix(X, Y, y_range=Y_LIM, right_cut=0.5, tail_from=0.47)
        if xs.size > 1:
            ax.plot(xs, ys,
                    color=c, linestyle=ls, linewidth=2,
                    marker=m, markersize=ms, markevery=max(1, xs.size // 12),
                    label=lbl,
                    markerfacecolor='none' if m in ('o', 'D') else None,
                    markeredgewidth=1.2, zorder=3)

        ax.set_xlim(*X_LIM_YQ)
        ax.set_ylim(*Y_LIM)
        ax.set_xlabel(r"$Y_Q$", fontsize=12)
        ax.set_ylabel(r"$\mu_B, \tilde{\mu}$ [MeV]", fontsize=12)
        style_axes(ax)
        ax.legend(fontsize=9, loc="upper left", frameon=True, framealpha=0.9)


    # ---------- BOTTOM: muQ panel ----------
    ax = axes[1]
    
    curves_data = [
        (muQ_ns_H, muB_ns_H, "Green", "",  "*", 9, r"$\mu_B$ H non-strange", False),
        (muQ_s_H,  muB_s_H,  "Black", "",  "*", 9, r"$\mu_B$ H strange", False),
        (muQ_ns_Q, muB_ns_Q, "red",   "--", "s", 3, r"$\mu_B$ Q non-strange", True), 
        (muQ_s_Q,  muB_s_Q,  "black", "-.", "o", 3, r"$\mu_B$ Q strange", True),
        (muQ_ns_Q, muhat_ns, "green", "-",  "", 2, r"$\tilde{\mu}$ H non-strange", False),
        (muQ_s_Q,  muhat_s,  "black", "-",  "", 2, r"$\tilde{\mu}$ Q strange", False),
    ]
    
    for x, y, color, ls, marker, ms, label, extend_it in curves_data:
        xs, ys = simple_clean_muq(x, y)
        
        if extend_it and len(xs) > 0:
            xs, ys = simple_extend(xs, ys, target_x=-400)
        
        if len(xs) > 0:
            if marker == "":  # Lines without markers
                ax.plot(xs, ys, color=color, linestyle=ls, linewidth=2, label=label)
            else:  # Lines with markers
                # Very sparse markers here too
                markevery = max(10, len(xs)//5)  # Only 5 markers per curve
                ax.plot(xs, ys, color=color, linestyle=ls, linewidth=2,
                        marker=marker, markersize=ms, markevery=markevery, 
                        label=label, 
                        markerfacecolor='none' if marker=='o' else None,
                        markeredgewidth=1.2)

    ax.set_xlim(*X_LIM_MUQ)
    ax.set_ylim(*Y_LIM)
    ax.set_xlabel(r"$\mu_Q$ [MeV]", fontsize=12)
    ax.set_ylabel(r"$\mu_B, \tilde{\mu}$ [MeV]", fontsize=12)
    style_axes(ax)
    ax.legend(fontsize=9, loc="upper right", frameon=True, framealpha=0.9)

    plt.tight_layout()
    
    png = os.path.join(OUT_DIR, "T0_2panels_paperstyle_v2.png")
    pdf = os.path.join(OUT_DIR, "T0_2panels_paperstyle_v2.pdf")
    fig.savefig(png, dpi=300, bbox_inches='tight')
    fig.savefig(pdf, dpi=300, bbox_inches='tight')
    print("Saved:", os.path.abspath(png))
    print("Saved:", os.path.abspath(pdf))

if __name__ == "__main__":
    main()