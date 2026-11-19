"""Step 10: draw Table 1 and Table 2 as clean print-quality images."""
import os

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TABLES = os.path.join(ROOT, "output", "tables")
OUT = os.path.join(ROOT, "output", "figures")

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 8.6,
                     "savefig.dpi": 300})

ROW_IN = 0.185          # inches per data row
HEAD_IN = 0.26          # inches for the header block


def draw_table(headers, rows, widths, aligns, fname, fig_w=6.5):
    fig_h = HEAD_IN + ROW_IN * len(rows) + 0.12
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_axis_off()
    ax.set_xlim(-0.004, 1.004)
    ax.set_ylim(0, fig_h)

    xs = [0.0]
    for w in widths:
        xs.append(xs[-1] + w)

    y_top = fig_h
    ax.plot([0, 1], [y_top - 0.02, y_top - 0.02], color="black", lw=1.0)
    y_head = y_top - HEAD_IN / 2 - 0.01
    ax.plot([0, 1], [y_top - HEAD_IN, y_top - HEAD_IN], color="black", lw=0.6)

    for j, h in enumerate(headers):
        x = xs[j] + 0.008 if aligns[j] == "left" else xs[j + 1] - 0.008
        ax.text(x, y_head, h, ha=aligns[j], va="center", fontsize=8.5,
                fontweight="bold")

    y = y_top - HEAD_IN - ROW_IN / 2
    for row in rows:
        for j, v in enumerate(row):
            x = xs[j] + 0.008 if aligns[j] == "left" else xs[j + 1] - 0.008
            ax.text(x, y, str(v), ha=aligns[j], va="center", fontsize=8.3)
        y -= ROW_IN
    ax.plot([0, 1], [y + ROW_IN / 2 - 0.01, y + ROW_IN / 2 - 0.01],
            color="black", lw=1.0)
    out = os.path.join(OUT, fname)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    from PIL import Image
    with Image.open(out) as im:
        if im.mode not in ("RGB", "L"):
            im.convert("RGB").save(out, optimize=True)
    plt.close(fig)
    print("  table image:", fname)


def table1():
    t = pd.read_csv(os.path.join(TABLES, "T1_sample_by_round.csv"))
    rows = [[str(r.round_label), r.country, f"{int(r.n):,}", f"{r.age_mean:.1f}",
             f"{r.age65plus*100:.0f}", f"{r.female*100:.0f}", f"{r.adl:.2f}",
             f"{r.iadl:.2f}", f"{r.edu_tertiary*100:.1f}"] for _, r in t.iterrows()]
    draw_table(["Round", "Country", "n", "Mean age", "% 65+", "% female", "ADL",
                "IADL", "% tertiary"], rows,
               [0.10, 0.13, 0.115, 0.125, 0.10, 0.115, 0.09, 0.10, 0.125],
               ["left", "left", "right", "right", "right", "right", "right",
                "right", "right"], "table1.png")


def table2():
    rows = [
        ["ADL (0–5)", "China", "0.0221", "0.0207, 0.0235", "0.22", ""],
        ["", "England", "0.0094", "0.0078, 0.0110", "0.09", ""],
        ["", "Difference", "−0.0128", "−0.0149, −0.0107", "−0.13", "<0.001"],
        ["IADL (0–4)", "China", "0.0207", "0.0194, 0.0219", "0.21", ""],
        ["", "England", "0.0047", "0.0036, 0.0058", "0.05", ""],
        ["", "Difference", "−0.0159", "−0.0176, −0.0142", "−0.16", "<0.001"],
    ]
    draw_table(["Outcome", "Group", "Slope per year", "95% CI", "Per decade", "p"],
               rows, [0.155, 0.145, 0.155, 0.225, 0.155, 0.09],
               ["left", "left", "right", "right", "right", "right"], "table2.png")


if __name__ == "__main__":
    table1()
    table2()
