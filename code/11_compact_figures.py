"""Two merged figures for the compact LLNCS version."""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xj_common as C  # noqa: E402

C.setup_style()
CC = C.COLORS
panel = C.load_panel()
ROUNDS = [1, 2, 3, 4]
LABELS = ["2011", "2013", "2015", "2018"]
AGES = np.arange(50, 80)
OUT = os.path.join(C.ROOT, "report", "figures")


def save(fig, name):
    for ext in ("png",):
        p = os.path.join(OUT, f"{name}.{ext}")
        fig.savefig(p, bbox_inches="tight", facecolor="white")
        C.strip_alpha(p)
    plt.close(fig)
    print("  saved", name)


def composition_flow():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5),
                             gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    bands = [(50, 60), (60, 70), (70, 80)]
    shades = [0.28, 0.55, 0.95]
    xpos = {"China": np.arange(4.0), "England": np.arange(4.0) + 4.6}
    for country in C.COUNTRIES:
        for i, r in enumerate(ROUNDS):
            d = panel[(panel["country"] == country) & (panel["round"] == r)]
            bottom = 0.0
            for (lo, hi), sh in zip(bands, shades):
                s = ((d["age"] >= lo) & (d["age"] < hi)).mean()
                ax.bar(xpos[country][i], s, bottom=bottom, width=0.72,
                       color=CC[country], alpha=sh, edgecolor="white", lw=0.4)
                bottom += s
        ax.text(xpos[country].mean(), -0.30, country, ha="center", va="top",
                fontsize=7, color=CC[country], fontweight="bold")
    ax.set_xticks(np.concatenate([xpos["China"], xpos["England"]]))
    ax.set_xticklabels(["R1", "R2", "R3", "R4"] * 2, fontsize=6.5)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["0", "50%", "100%"], fontsize=7)
    ax.set_xlim(-1.35, 8.0)
    ax.set_ylabel("Age-band share", fontsize=7.5)
    ax.set_title("Age composition", loc="left", fontsize=8.5)
    ax.grid(axis="y", color="#EEEEEE")

    ax = axes[1]
    for country in C.COUNTRIES:
        d = panel[panel["country"] == country]
        ns = [len(set(d.loc[d["round"] == r, "pid"])) for r in ROUNDS]
        ax.plot(ROUNDS, ns, color=CC[country], marker="o", ms=4, lw=1.5,
                label=country)
        ax.annotate(country, (ROUNDS[-1], ns[-1]), xytext=(5, 0),
                    textcoords="offset points", va="center", fontsize=7,
                    color=CC[country], fontweight="bold")
    ax.set_xticks(ROUNDS); ax.set_xticklabels(LABELS, fontsize=6.5)
    ax.set_xlim(0.75, 5.0)
    ax.set_ylabel("Respondents aged 50-79", fontsize=7.5)
    ax.set_title("Sample size by round", loc="left", fontsize=8.5)
    ax.set_yticks([0, 8000, 16000])
    ax.set_yticklabels(["0", "8k", "16k"], fontsize=7)
    ax.tick_params(axis="y", labelsize=7)
    save(fig, "figC_composition_flow")


def binned(var, country, bins=np.arange(50, 82, 5)):
    d = panel[panel["country"] == country].dropna(subset=[var, "age"]).copy()
    d["bin"] = pd.cut(d["age"], bins, right=False)
    g = d.groupby("bin", observed=True)[var].agg(["mean", "count", "std"])
    g["mid"] = [iv.left + 2.5 for iv in g.index]
    g["ci"] = 1.96 * g["std"] / np.sqrt(g["count"])
    return g.reset_index(drop=True)


def age_curves():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4), sharex=True)
    for ax, var, lab in zip(axes, ["adlfive", "iadlfour"],
                            ["ADL limitations (0-5)", "IADL limitations (0-4)"]):
        lev = np.load(os.path.join(C.DATA_CLEAN, f"predlev_{var}.npy"))
        for k, country in enumerate(C.COUNTRIES):
            g = binned(var, country)
            ax.errorbar(g["mid"], g["mean"], yerr=g["ci"], fmt="o", ms=3.6,
                        color=CC[country], mfc="white", mew=1.0, capsize=1.8,
                        elinewidth=0.8, zorder=3)
            med = np.median(lev[:, k, :], axis=0)
            lo = np.percentile(lev[:, k, :], 2.5, axis=0)
            hi = np.percentile(lev[:, k, :], 97.5, axis=0)
            ax.fill_between(AGES, lo, hi, color=CC[country], alpha=0.15, lw=0)
            ax.plot(AGES, med, color=CC[country], lw=1.6, label=country)
        ax.set_xlim(49.3, 80)
        ax.set_ylim(0, 0.95)
        ax.set_xlabel("Age at interview", fontsize=7.5)
        ax.set_title(lab, loc="left", fontsize=8.5)
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=6.5, loc="upper left")
    axes[0].set_ylabel("Mean count", fontsize=7.5)
    save(fig, "figD_age_curves")


if __name__ == "__main__":
    composition_flow()
    age_curves()
