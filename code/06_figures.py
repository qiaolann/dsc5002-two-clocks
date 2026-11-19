"""Step 6: figures for the report (revision 2 after visual review)."""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import patheffects as pe
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xj_common as COMMON  # noqa: E402

COMMON.setup_style()
CC = COMMON.COLORS
LC = COMMON.LIGHT

panel = COMMON.load_panel()
ROUNDS = [1, 2, 3, 4]
LABELS = ["2011", "2013", "2015", "2018"]
AGES = np.arange(50, 80)


# =========================================================== Figure 1: design
def fig_design():
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ch_spans = [(2011.42, 2012.25, "W1"), (2013.50, 2014.08, "W2"),
                (2015.50, 2016.08, "W3"), (2018.50, 2018.92, "W4")]
    el_spans = [(2010.42, 2011.58, "W5"), (2012.42, 2013.50, "W6"),
                (2014.42, 2015.42, "W7"), (2018.42, 2019.58, "W9")]
    ch_mid = [0.5 * (a + b) for a, b, _ in ch_spans]
    el_mid = [0.5 * (a + b) for a, b, _ in el_spans]

    for (a, b, lab) in ch_spans:
        ax.plot([a, b], [1, 1], lw=10, color=CC["China"], solid_capstyle="butt",
                alpha=0.9)
        ax.text((a + b) / 2, 1.18, lab, ha="center", va="bottom", fontsize=7.5,
                color=CC["China"], fontweight="bold")
    for (a, b, lab) in el_spans:
        ax.plot([a, b], [0, 0], lw=10, color=CC["England"], solid_capstyle="butt",
                alpha=0.9)
        ax.text((a + b) / 2, 0.82, lab, ha="center", va="top", fontsize=7.5,
                color=CC["England"], fontweight="bold")

    for i, (cm, em) in enumerate(zip(ch_mid, el_mid)):
        ax.plot([em, cm], [0.10, 0.90], ls=(0, (2, 2)), lw=0.9, color="#999999",
                zorder=1)
        ax.text((cm + em) / 2, 0.50, f"R{i+1}", ha="center", va="center",
                fontsize=7, color="#555555",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none"))

    ax.set_ylim(-0.55, 1.65)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(["CHARLS\n(China)", "ELSA\n(England)"], fontsize=8)
    ax.set_xlim(2009.6, 2020.4)
    ax.set_xlabel("Calendar year")
    ax.set_title("Four calendar-matched rounds", loc="left")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#E8E8E8")
    return fig


# ================================================ Figure 2: calendar-anchored
def fig_calendar():
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.7), sharey=True)
    for ax, var, lab in zip(axes, ["adlfive", "iadlfour"],
                            ["ADL limitations (0-5)", "IADL limitations (0-4)"]):
        for country in COMMON.COUNTRIES:
            xs, ms, hs = [], [], []
            for r in ROUNDS:
                d = panel[(panel["country"] == country) & (panel["round"] == r)][var]
                m, hw = COMMON.ci_mean(d)
                xs.append(r); ms.append(m); hs.append(hw)
            ax.errorbar(xs, ms, yerr=hs, color=CC[country], marker="o", ms=4.5,
                        lw=1.6, capsize=2.5, elinewidth=0.9, label=country)
            ax.annotate(country, (xs[-1], ms[-1]), xytext=(7, 0),
                        textcoords="offset points", va="center", fontsize=8,
                        color=CC[country], fontweight="bold")
        ax.set_xticks(ROUNDS)
        ax.set_xticklabels(LABELS)
        ax.set_xlim(0.6, 5.1)
        ax.set_ylim(0, 0.55)
        ax.set_title(lab, loc="left")
        ax.set_xlabel("Round (calendar anchored)")
    axes[0].set_ylabel("Mean count per person")
    fig.suptitle("Calendar-anchored view: both series look flat",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    return fig


# ================================================= Figure 3: age composition
def fig_composition():
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 2.9))

    # (a) age-band composition: 4 stacked bars per country
    ax = axes[0]
    bands = [(50, 60, "50-59"), (60, 70, "60-69"), (70, 80, "70-79")]
    shades = [0.28, 0.55, 0.95]
    xpos = {"China": np.arange(4.0), "England": np.arange(4.0) + 5.4}
    for country in COMMON.COUNTRIES:
        for i, r in enumerate(ROUNDS):
            d = panel[(panel["country"] == country) & (panel["round"] == r)]
            shares = [((d["age"] >= lo) & (d["age"] < hi)).mean() for lo, hi, _ in bands]
            bottom = 0.0
            for s, sh in zip(shares, shades):
                ax.bar(xpos[country][i], s, bottom=bottom, width=0.74,
                       color=CC[country], alpha=sh, edgecolor="white", lw=0.6)
                if s > 0.09:
                    ax.text(xpos[country][i], bottom + s / 2, f"{s*100:.0f}",
                            ha="center", va="center", fontsize=6,
                            color="white" if sh > 0.5 else "#333333")
                bottom += s
        ax.text(xpos[country].mean(), -0.175, country, ha="center", va="top",
                fontsize=7.5, color=CC[country], fontweight="bold")
    ax.set_xticks(np.concatenate([xpos["China"], xpos["England"]]))
    ax.set_xticklabels(["R1", "R2", "R3", "R4"] * 2, fontsize=7)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["0", "50%", "100%"])
    ax.set_ylabel("Share of respondents")
    ax.set_title("Age composition by round", loc="left")
    # direct band labels to the left of the first bar instead of a legend
    d0 = panel[(panel["country"] == "China") & (panel["round"] == 1)]
    run, centres = 0.0, []
    for lo, hi, lab in bands:
        s = ((d0["age"] >= lo) & (d0["age"] < hi)).mean()
        centres.append(run + s / 2)
        run += s
    for c, (_, _, lab) in zip(centres, bands):
        ax.text(-0.55, c, lab, ha="right", va="center", fontsize=6.5,
                color="#666666")
    ax.set_xlim(-1.55, 8.95)

    # (b) share aged 65+
    ax = axes[1]
    for country in COMMON.COUNTRIES:
        full, base = [], []
        base_ids = set(panel.loc[(panel["round"] == 1) & (panel["country"] == country), "pid"])
        for r in ROUNDS:
            d = panel[(panel["country"] == country) & (panel["round"] == r)]
            full.append((d["age"] >= 65).mean())
            base.append((d[d["pid"].isin(base_ids)]["age"] >= 65).mean())
        lb, = ax.plot(ROUNDS, base, color=CC[country], marker="s", ms=3.5,
                      lw=1.1, alpha=0.85, ls=(0, (3, 2)), zorder=2)
        lb.set_path_effects([pe.Stroke(linewidth=3.4, foreground="white"),
                             pe.Normal()])
        ax.plot(ROUNDS, full, color=CC[country], marker="o", ms=4, lw=1.7,
                zorder=3)
        ax.annotate(country, (ROUNDS[-1], full[-1]), xytext=(6, -2),
                    textcoords="offset points", va="top", fontsize=8,
                    color=CC[country], fontweight="bold")
    ax.set_xticks(ROUNDS); ax.set_xticklabels(LABELS)
    ax.set_xlim(0.75, 5.0)
    ax.set_ylim(0, 0.88)
    ax.set_xlabel("Round")
    ax.set_ylabel("Share aged 65+")
    ax.set_title("Refreshment samples shift the age mix", loc="left")
    handles = [Line2D([], [], color="#555555", marker="o", lw=1.4, ms=4,
                      label="all respondents"),
               Line2D([], [], color="#555555", marker="s", lw=1.2, ms=3.5,
                      ls=(0, (3, 2)), label="2011 cohort only")]
    ax.legend(handles=handles, fontsize=7, loc="lower left")
    return fig


# ================================================== Figure 4/5: age-anchored
def binned(var, country, bins=np.arange(50, 82, 5)):
    d = panel[panel["country"] == country].dropna(subset=[var, "age"]).copy()
    d["bin"] = pd.cut(d["age"], bins, right=False)
    g = d.groupby("bin", observed=True)[var].agg(["mean", "count", "std"])
    g["mid"] = [iv.left + 2.5 for iv in g.index]
    g["ci"] = 1.96 * g["std"] / np.sqrt(g["count"])
    return g.reset_index(drop=True)


def fig_age(var, title, ylab, ymax):
    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    lev = np.load(os.path.join(COMMON.DATA_CLEAN, f"predlev_{var}.npy"))
    for k, country in enumerate(COMMON.COUNTRIES):
        g = binned(var, country)
        ax.errorbar(g["mid"], g["mean"], yerr=g["ci"], fmt="o", ms=5,
                    color=CC[country], mfc="white", mew=1.3, capsize=2.5,
                    elinewidth=1, zorder=3)
        med = np.median(lev[:, k, :], axis=0)
        lo = np.percentile(lev[:, k, :], 2.5, axis=0)
        hi = np.percentile(lev[:, k, :], 97.5, axis=0)
        ax.fill_between(AGES, lo, hi, color=CC[country], alpha=0.15, lw=0)
        ax.plot(AGES, med, color=CC[country], lw=2, label=country)
    ax.set_xlim(49.3, 80)
    ax.set_ylim(0, ymax)
    ax.set_xlabel("Age at interview (years)")
    ax.set_ylabel(ylab)
    ax.set_title(title, loc="left")
    ax.legend(fontsize=8, loc="upper left")
    ax.text(0.985, 0.965,
            "hollow points: 5-year bin means (95% CI)   line: linear fit, averaged over rounds",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.4,
            color="#666666")
    return fig


# ==================================================== Figure 6: gap by age
def fig_gap():
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.9))
    t_all = pd.read_csv(os.path.join(COMMON.TABLES, "T4_age_contrasts.csv"))
    cal = pd.read_csv(os.path.join(COMMON.TABLES, "T2_calendar_means.csv"))
    for ax, var, lab in zip(axes, ["adlfive", "iadlfour"],
                            ["ADL limitations", "IADL limitations"]):
        t = t_all[t_all["var"] == var]
        ax.fill_between(t["age"], t["lo"], t["hi"], color="#9E9E9E", alpha=0.25, lw=0)
        ax.plot(t["age"], t["gap"], color="#2B2B2B", lw=1.9, label="age-anchored gap")

        c = cal[cal["var"] == var].pivot(index="round", columns="country", values="mean")
        gaps = c["China"] - c["England"]
        m, hw = gaps.mean(), 3.18 * gaps.std(ddof=1) / np.sqrt(len(gaps))
        ax.axhspan(m - hw, m + hw, color=CC["England"], alpha=0.13, lw=0)
        ax.axhline(m, color=CC["England"], lw=1.3, ls=(0, (4, 2)),
                   label="calendar-anchored gap")

        ax.axhline(0, color="#B03A2E", lw=0.9)
        ax.set_title(lab, loc="left")
        ax.set_xlabel("Age at interview")
        ax.set_xlim(50, 79)
        if var == "adlfive":
            cross = int(t.loc[t["gap"] > 0, "age"].min())
            ax.axvline(cross, color="#777777", lw=0.8, ls=":")
            ax.annotate(f"crossover at {cross}", xy=(cross, 0), xytext=(5, -13),
                        textcoords="offset points", fontsize=6.8,
                        color="#555555")
    axes[0].set_ylabel("China minus England\n(mean count)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=7.5,
               bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Reading the same comparison along the age axis",
                 x=0.01, ha="left", fontsize=10, fontweight="bold")
    return fig


# ================================================= Figure 9: slope robustness
def fig_slopes():
    rob = pd.read_csv(os.path.join(COMMON.TABLES, "T5_robustness.csv"))
    main = pd.read_csv(os.path.join(COMMON.TABLES, "T3_age_slopes.csv"))
    ratios = pd.read_csv(os.path.join(COMMON.TABLES, "T6b_link_ratios.csv"))

    fig, axes = plt.subplots(1, 3, figsize=(6.9, 3.0), sharex=False,
                            gridspec_kw={"width_ratios": [1, 1, 0.95]})
    order = ["main", "excl. round 1", "+ education", "within-person FE"]
    for ax, var, lab in zip(axes[:2], ["adlfive", "iadlfour"],
                            ["ADL limitations (0-5)", "IADL limitations (0-4)"]):
        ypos = {k: i for i, k in enumerate(order[::-1])}
        for country, off in [("China", 0.15), ("England", -0.15)]:
            m = main[(main["outcome"] == var) & (main["model"] == country)].iloc[0]
            ax.errorbar(m["est"], ypos["main"] + off,
                        xerr=[[m["est"] - m["ci_lo"]], [m["ci_hi"] - m["est"]]],
                        fmt="o", color=CC[country], ms=5.5, capsize=2.5, lw=1.1)
            for k in order[1:]:
                r = rob[(rob["outcome"] == var) & (rob["check"] == f"{country} {k}")]
                if not len(r):
                    continue
                r = r.iloc[0]
                ax.errorbar(r["est"], ypos[k] + off,
                            xerr=[[r["est"] - r["ci_lo"]], [r["ci_hi"] - r["est"]]],
                            fmt="o", color=CC[country], ms=4, mfc="white",
                            mew=1.1, capsize=2, lw=0.9)
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels(order[::-1], fontsize=7.5)
        ax.set_xlabel("Limitations per year\n(linear model)", fontsize=8)
        ax.set_title(lab, loc="left")
        ax.set_xlim(0, 0.042)
        ax.grid(axis="y", color="#F0F0F0")
    handles = [Line2D([], [], marker="o", color=CC[c], lw=1.1, ms=5.5, label=c)
               for c in COMMON.COUNTRIES]
    axes[0].legend(handles=handles, fontsize=7, loc="upper right")

    # third panel: the China/England multiplier depends on the scale
    ax = axes[2]
    links = ["linear", "poisson", "logit"]
    ypos = {"linear": 2, "poisson": 1, "logit": 0}
    styles = {"adlfive": ("o", "#3D3D3D", "ADL"),
              "iadlfour": ("s", "#8C8C8C", "IADL")}
    for var, (marker, col, lab) in styles.items():
        sub = ratios[ratios["outcome"] == var]
        off = 0.16 if var == "adlfive" else -0.16
        for _, r in sub.iterrows():
            ax.errorbar(r["ratio"], ypos[r["link"]] + off,
                        xerr=[[r["ratio"] - r["ci_lo"]], [r["ci_hi"] - r["ratio"]]],
                        fmt=marker, color=col, ms=5, capsize=2.2, lw=1.9)
    ax.axvline(1, color="#B03A2E", lw=1, ls=(0, (4, 2)))
    ax.set_xscale("log")
    ax.set_xlim(1, 6)
    ax.set_xticks([1, 1.5, 2, 3, 4, 6])
    ax.set_xticklabels(["1", "1.5", "2", "3", "4", "6"], fontsize=7.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["logit\n(any)", "Poisson\n(count)", "linear\n(count)"],
                       fontsize=7.5)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel("China ÷ England multiplier", fontsize=8)
    ax.set_title("Same contrast, different scale", loc="left")
    ax.grid(axis="y", color="#F0F0F0")
    ax.legend(handles=[Line2D([], [], marker=m, color=c, ls="none", ms=5, label=l)
                       for m, c, l in styles.values()], fontsize=7,
              loc="lower right", bbox_to_anchor=(1.02, 0.02))

    fig.suptitle("Age slopes under four specifications, and how the contrast "
                 "depends on the scale", x=0.01, ha="left", fontsize=9.5,
                 fontweight="bold")
    return fig


# ============================================ Figure 4: sample flow by round
def fig_flow():
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    xpos = {"China": np.arange(4.0), "England": np.arange(4.0) + 5.2}
    for country in COMMON.COUNTRIES:
        d = panel[panel["country"] == country]
        prev = set()
        for i, r in enumerate(ROUNDS):
            ids = set(d.loc[d["round"] == r, "pid"])
            returning = len(ids & prev)
            new = len(ids - prev)
            x = xpos[country][i]
            if i == 0:
                ax.bar(x, len(ids), width=0.72, color=CC[country], alpha=0.55,
                       zorder=3)
                ax.annotate("baseline", (x, len(ids) + 350), ha="center",
                            va="bottom", fontsize=6.4, color="#555555")
            else:
                ax.bar(x, returning, width=0.72, color=CC[country], zorder=3)
                ax.bar(x, new, bottom=returning, width=0.72, color=CC[country],
                       alpha=0.35, hatch="///", edgecolor="white", lw=0.4,
                       zorder=3)
                net = len(ids) - len(prev)
                ax.annotate(f"{net:+,}", (x, len(ids) + 350), ha="center",
                            va="bottom", fontsize=6.6,
                            color="#B2182B" if net < 0 else "#2E6B34")
            prev = ids
        ax.text(xpos[country].mean(), -0.17, country, ha="center", va="top",
                transform=ax.get_xaxis_transform(), fontsize=7.5,
                color=CC[country], fontweight="bold")
    ax.set_xticks(np.concatenate([xpos["China"], xpos["England"]]))
    ax.set_xticklabels(["R1", "R2", "R3", "R4"] * 2, fontsize=7)
    ax.set_ylim(0, 20500)
    ax.set_yticks([0, 5000, 10000, 15000])
    ax.set_yticklabels(["0", "5k", "10k", "15k"])
    ax.set_ylabel("Respondents aged 50–79")
    ax.set_title("Sample flow: attrition versus refreshment", loc="left")
    handles = [Patch(facecolor="#777777", label="returning respondents"),
               Patch(facecolor="#BBBBBB", hatch="///", edgecolor="white",
                     label="new entrants")]
    ax.legend(handles=handles, fontsize=7, loc="upper center", ncol=2,
              bbox_to_anchor=(0.5, 1.02))
    return fig


# ======================================== Figure 8: within-person change
def fig_within():
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.7),
                            gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    trans = [("1", "2"), ("2", "3"), ("3", "4")]
    width = 0.34
    for k, country in enumerate(COMMON.COUNTRIES):
        d = panel[panel["country"] == country]
        w = d.pivot_table(index="pid", columns="round", values="adlfive")
        vals, errs, xs = [], [], []
        for i, (a, b) in enumerate(trans):
            delta = (w[int(b)] - w[int(a)]).dropna()
            share = (delta > 0).mean() * 100
            se = np.sqrt(share / 100 * (1 - share / 100) / len(delta)) * 100
            vals.append(share); errs.append(1.96 * se)
            xs.append(i + (k - 0.5) * width)
        ax.bar(xs, vals, width=width, color=CC[country], label=country)
        ax.errorbar(xs, vals, yerr=errs, fmt="none", ecolor="#333333",
                    capsize=2, lw=0.9)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["R1→R2", "R2→R3", "R3→R4"], fontsize=7.5)
    ax.set_ylabel("% whose ADL count rose")
    ax.set_title("Worsening is a minority event", loc="left")
    ax.set_ylim(0, 20)
    ax.legend(fontsize=7, loc="upper right")

    ax = axes[1]
    seg_colors = ["#B2182B", "#D9D9D9", "#2166AC"]
    seg_labels = ["worse", "unchanged", "better"]
    for j, country in enumerate(COMMON.COUNTRIES):
        d = panel[panel["country"] == country]
        w = d.pivot_table(index="pid", columns="round", values="adlfive")
        delta = (w[4] - w[1]).dropna()
        shares = [(delta > 0).mean(), (delta == 0).mean(), (delta < 0).mean()]
        left = 0.0
        for share, col, lab in zip(shares, seg_colors, seg_labels):
            ax.barh(j, share * 100, left=left, color=col, height=0.55,
                    edgecolor="white", lw=0.8)
            if share > 0.06:
                ax.text(left + share * 50, j, f"{share*100:.0f}",
                        ha="center", va="center", fontsize=6.8,
                        color="white" if lab != "unchanged" else "#333333")
            left += share * 100
    ax.set_yticks([0, 1])
    ax.set_yticklabels(COMMON.COUNTRIES, fontsize=8)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of respondents (%)")
    ax.set_title("Cumulative change, round 1 → round 4", loc="left")
    handles = [Patch(facecolor=c, label=l) for c, l in zip(seg_colors, seg_labels)]
    ax.legend(handles=handles, fontsize=7, loc="upper center", ncol=3,
              bbox_to_anchor=(0.5, -0.28))
    return fig


# ==================================== Figure 10: diabetes, the counter-example
def fig_diabetes():
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6))
    ax = axes[0]
    d = panel.dropna(subset=["diabe"]).copy()
    d["bin"] = pd.cut(d["age"], np.arange(50, 85, 5), right=False)
    g = d.groupby(["bin", "country"], observed=True)["diabe"].agg(["mean", "count"])
    mids = [iv.left + 2.5 for iv in g.index.get_level_values(0).unique()]
    for country in COMMON.COUNTRIES:
        m = g.xs(country, level=1)["mean"].values * 100
        n = g.xs(country, level=1)["count"].values
        se = np.sqrt((m / 100) * (1 - m / 100) / n) * 100
        ax.errorbar(mids, m, yerr=1.96 * se, color=CC[country], marker="o",
                    ms=4.5, lw=1.6, capsize=2.5, elinewidth=0.9, label=country)
    ax.set_xlabel("Age at interview (years)")
    ax.set_ylabel("% reporting diabetes")
    ax.set_ylim(0, 20)
    ax.set_title("The age gradient differs in shape", loc="left")
    ax.legend(fontsize=7, loc="upper left")

    ax = axes[1]
    ref = d["age"].value_counts(normalize=True)
    for country in COMMON.COUNTRIES:
        vals = []
        for r in ROUNDS:
            x = d[(d["country"] == country) & (d["round"] == r)]
            by_age = x.groupby("age")["diabe"].mean()
            w = ref.reindex(by_age.index).fillna(0)
            vals.append((by_age * w).sum() / w.sum() * 100)
        ax.plot(ROUNDS, vals, color=CC[country], marker="o", ms=4.5, lw=1.7,
                label=country)
        ax.annotate(country, (ROUNDS[-1], vals[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8,
                    color=CC[country], fontweight="bold")
    ax.set_xticks(ROUNDS); ax.set_xticklabels(LABELS)
    ax.set_xlim(0.75, 5.0)
    ax.set_ylim(0, 20)
    ax.set_xlabel("Round")
    ax.set_ylabel("% with diabetes")
    ax.set_title("Here the calendar axis moves (age-standardised)", loc="left")
    return fig


if __name__ == "__main__":
    COMMON.save(fig_design(), "F1_design")
    COMMON.save(fig_calendar(), "F2_calendar_anchored")
    COMMON.save(fig_composition(), "F3_composition")
    COMMON.save(fig_flow(), "F4_sample_flow")
    COMMON.save(fig_age("adlfive",
                        "Age-anchored view: ADL limitations rise about twice as fast in China",
                        "ADL limitations (0-5)", 0.95), "F5_age_adl")
    COMMON.save(fig_age("iadlfour",
                        "Age-anchored view: IADL limitations diverge even more sharply",
                        "IADL limitations (0-4)", 0.95), "F6_age_iadl")
    COMMON.save(fig_gap(), "F7_gap_by_age")
    COMMON.save(fig_within(), "F8_within_person")
    COMMON.save(fig_slopes(), "F9_slope_robustness")
    COMMON.save(fig_diabetes(), "F10_diabetes")
