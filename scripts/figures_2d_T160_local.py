# qcd_eos_ml/scripts/figures_2d_T160_local.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- EDIT THESE PATHS IF NEEDED (relative to your project root) ----
NS_FILE = r".\data\achargecode_nonstrange"      # non-strange (high T)
S_FILE  = r".\data\bchargecode_strange_2d"      # strange (high T)
OUT_DIR = r".\figures"                          # where to save PNGs

# Columns (match what you used earlier)
# 0: YQ, 2: muB_H, 3: muB_Q, 8: muQ_Q
YQ_COL = 0
MUB_H_COL = 7
MUB_Q_COL = 6
MUQ_Q_COL = 8

def smooth_trim(x, y, window=5, trim=2):
    order = np.argsort(x)
    x = x[order]; y = y[order]
    if window < 3: window = 3
    if window % 2 == 0: window += 1
    kernel = np.ones(window) / window
    y_sm = np.convolve(y, kernel, mode="same")
    if trim > 0 and 2*trim < len(x):
        x = x[trim:-trim]
        y_sm = y_sm[trim:-trim]
    return x, y_sm

def mark_every(n):  # sparse markers
    return max(1, n // 12)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load data from your local folder
    a = pd.read_csv(NS_FILE, sep=r"\s+", header=None, engine="python")
    b = pd.read_csv(S_FILE,  sep=r"\s+", header=None, engine="python")

    # Non-strange (quark branch @ T=160)
    YQ_ns         = a.iloc[:, YQ_COL].to_numpy()
    muB_ns_Q160   = a.iloc[:, MUB_Q_COL].to_numpy()
    muQ_ns_Q160   = a.iloc[:, MUQ_Q_COL].to_numpy()
    muB_ns_H160   = a.iloc[:, MUB_H_COL].to_numpy()

    # Strange (quark branch @ T=160)
    YQ_s          = b.iloc[:, YQ_COL].to_numpy()
    muB_s_Q160    = b.iloc[:, MUB_Q_COL].to_numpy()
    muQ_s_Q160    = b.iloc[:, MUQ_Q_COL].to_numpy()
    muB_s_H160    = b.iloc[:, MUB_H_COL].to_numpy()

    # μ̃ = μB + YQ * μQ  (use quark branch for smoothness)
    muhat_ns = muB_ns_Q160 + YQ_ns * muQ_ns_Q160
    muhat_s  = muB_s_Q160  + YQ_s  * muQ_s_Q160

    # -------- Panel 1: μB & μ̃ vs YQ (T = 160 MeV) --------
    x_nsH, y_nsH = smooth_trim(YQ_ns, muB_ns_H160, window=5, trim=2)
    x_nsQ, y_nsQ = smooth_trim(YQ_ns, muB_ns_Q160, window=5, trim=2)
    x_sH,  y_sH  = smooth_trim(YQ_s,  muB_s_H160,  window=5, trim=2)
    x_sQ,  y_sQ  = smooth_trim(YQ_s,  muB_s_Q160,  window=5, trim=2)
    x_nsM, y_nsM = smooth_trim(YQ_ns, muhat_ns,    window=5, trim=2)
    x_sM,  y_sM  = smooth_trim(YQ_s,  muhat_s,     window=5, trim=2)

    plt.figure(figsize=(7.8,5.6))
    plt.plot(x_nsH, y_nsH, color="green", linewidth=2, marker="*", markevery=mark_every(len(x_nsH)),
             label=r"$\mu_B$ H non-strange")
    plt.plot(x_nsQ, y_nsQ, color="red",   linewidth=2, linestyle="--", marker="s", markevery=mark_every(len(x_nsQ)),
             label=r"$\mu_B$ Q non-strange")
    plt.plot(x_sH,  y_sH,  color="black", linewidth=2, marker="*", markevery=mark_every(len(x_sH)),
             label=r"$\mu_B$ H strange")
    plt.plot(x_sQ,  y_sQ,  color="black", linewidth=2, linestyle="--", marker="o", markevery=mark_every(len(x_sQ)),
             label=r"$\mu_B$ Q strange")
    plt.plot(x_nsM, y_nsM, color="magenta",  linewidth=2.2, label=r"$\tilde{\mu}$ H/Q non-strange")
    plt.plot(x_sM,  y_sM,  color="black", linewidth=2.2,  label=r"$\tilde{\mu}$ H/Q strange")

    plt.xlabel(r"$Y_Q$")
    plt.ylabel(r"$\mu_B,\ \tilde{\mu}\ \mathrm{[MeV]}$")
    plt.title("T = 160 MeV")
    plt.xlim(0, 0.5)
    plt.ylim(475, 600)
    plt.legend(fontsize=9, ncol=2, framealpha=0.8, loc="lower right")
    plt.tight_layout()
    out1 = os.path.join(OUT_DIR, "2D_YQ_T160_muB_muhat.png")
    plt.savefig(out1, dpi=260)
    plt.close()
    print("Saved:", os.path.abspath(out1), flush=True)

    # -------- Panel 2: μB & μ̃ vs μQ (T = 160 MeV) --------
    x_ns,  y_nsH2 = smooth_trim(muQ_ns_Q160, muB_ns_H160, window=5, trim=2)
    x_ns2, y_nsQ2 = smooth_trim(muQ_ns_Q160, muB_ns_Q160, window=5, trim=2)
    x_s,   y_sH2  = smooth_trim(muQ_s_Q160,  muB_s_H160,  window=5, trim=2)
    x_s2,  y_sQ2  = smooth_trim(muQ_s_Q160,  muB_s_Q160,  window=5, trim=2)
    x_nsM2, y_nsM2 = smooth_trim(muQ_ns_Q160, muhat_ns, window=5, trim=2)
    x_sM2,  y_sM2  = smooth_trim(muQ_s_Q160,  muhat_s,  window=5, trim=2)

    plt.figure(figsize=(7.8,5.6))
    plt.plot(x_ns,  y_nsH2, color="green", linewidth=2, marker="*", markevery=mark_every(len(x_ns)),
             label=r"$\mu_B$ H non-strange")
    plt.plot(x_ns2, y_nsQ2, color="red",   linewidth=2, linestyle="--", marker="s", markevery=mark_every(len(x_ns2)),
             label=r"$\mu_B$ Q non-strange")
    plt.plot(x_s,   y_sH2,  color="black", linewidth=2, marker="*", markevery=mark_every(len(x_s)),
             label=r"$\mu_B$ H strange")
    plt.plot(x_s2,  y_sQ2,  color="black", linewidth=2, linestyle="--", marker="o", markevery=mark_every(len(x_s2)),
             label=r"$\mu_B$ Q strange")
    plt.plot(x_nsM2, y_nsM2, color="magenta",  linewidth=2.2, label=r"$\tilde{\mu}$ H/Q non-strange")
    plt.plot(x_sM2,  y_sM2,  color="black", linewidth=2.2,  label=r"$\tilde{\mu}$ H/Q strange")

    plt.xlabel(r"$\mu_Q$ [MeV]")
    plt.ylabel(r"$\mu_B,\ \tilde{\mu}\ \mathrm{[MeV]}$")
    plt.title("T = 160 MeV")
    plt.xlim(-120, 120)
    plt.ylim(475, 600)
    plt.legend(fontsize=9, ncol=2, framealpha=0.8, loc="lower right")
    plt.tight_layout()
    out2 = os.path.join(OUT_DIR, "2D_muQ_T160_muB_muhat.png")
    plt.savefig(out2, dpi=260)
    plt.close()
    print("Saved:", os.path.abspath(out2), flush=True)

if __name__ == "__main__":
    main()
