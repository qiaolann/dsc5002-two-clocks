"""Shared paths, configuration and helper functions for the project."""
import os
import warnings

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_RAW = os.path.join(ROOT, "Group project")
DATA_CLEAN = os.path.join(ROOT, "data_clean")
FIGS = os.path.join(ROOT, "output", "figures")
TABLES = os.path.join(ROOT, "output", "tables")
for d in (DATA_CLEAN, FIGS, TABLES):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- study design
# Four calendar-matched rounds. CHARLS waves 1-4 vs the ELSA waves whose
# fieldwork window is closest in time.
ROUNDS = [
    # round, label, CHARLS wave, CHARLS fieldwork midpoint, ELSA wave, ELSA midpoint
    (1, "2011", 1, 2011.7, 5, 2011.0),
    (2, "2013", 2, 2013.5, 6, 2012.5),
    (3, "2015", 3, 2015.5, 7, 2014.5),
    (4, "2018", 4, 2018.4, 9, 2019.0),
]
AGE_MIN, AGE_MAX = 50, 79

COUNTRIES = ["China", "England"]
COLORS = {"China": "#D55E00", "England": "#0072B2"}
LIGHT = {"China": "#F0B27A", "England": "#7FB3D5"}

OUTCOMES = {
    "adlfive": dict(label="ADL limitations (0-5)", short="ADL", ymax=1.0),
    "iadlfour": dict(label="IADL limitations (0-4)", short="IADL", ymax=1.0),
}


def setup_style():
    plt.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#444444",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": "#E5E5E5",
        "grid.linewidth": 0.6,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "legend.frameon": False,
        "legend.fontsize": 8,
        "figure.constrained_layout.use": True,
    })


def strip_alpha(path):
    """Save PNGs without an alpha channel.

    matplotlib writes RGBA by default; an all-opaque alpha channel becomes a
    CCITT-encoded /SMask in the PDF, which some in-browser viewers (GitHub's
    included) fail to render.
    """
    from PIL import Image
    with Image.open(path) as im:
        if im.mode not in ("RGB", "L"):
            im.convert("RGB").save(path, optimize=True)


def save(fig, name):
    for ext in ("png", "pdf"):
        out = os.path.join(FIGS, f"{name}.{ext}")
        fig.savefig(out, bbox_inches="tight", facecolor="white")
        if ext == "png":
            strip_alpha(out)
    plt.close(fig)
    print("  figure:", name)


def ci_mean(x, z=1.96):
    """Mean and normal-approximation 95% CI half-width."""
    x = pd.Series(x).dropna()
    n = len(x)
    if n < 2:
        return np.nan, np.nan
    m = x.mean()
    se = x.std(ddof=1) / np.sqrt(n)
    return m, z * se


def load_panel():
    return pd.read_parquet(os.path.join(DATA_CLEAN, "panel.parquet"))
