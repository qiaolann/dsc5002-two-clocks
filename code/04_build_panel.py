"""Step 4: build the analysis panel (long format, four calendar rounds x 2 countries)."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xj_common as C  # noqa: E402

ch = pd.read_parquet(os.path.join(C.DATA_CLEAN, "charls_extract.parquet"))
el = pd.read_parquet(os.path.join(C.DATA_CLEAN, "elsa_extract.parquet"))

VARS = ["adlfive", "iadlfour", "imrc", "dlrc", "shlt", "diabe", "hearte",
        "cancre", "mstat", "cesdl10"]


def clean_edu(s):
    return s.where(s.isin([1, 2, 3]))


def build(df, country, waves, edu_col):
    frames = []
    for rnd, label, w, year, *_ in waves:
        d = df[df[f"inw{w}"] == 1].copy()
        out = pd.DataFrame({
            "pid": d["ID"] if country == "China" else d["idauniq"].astype(str),
            "country": country,
            "round": rnd,
            "round_label": label,
            "wave": w,
            "year": year,
            "age": d[f"r{w}agey"],
            "female": np.where(d["ragender"] == 2, 1.0,
                               np.where(d["ragender"] == 1, 0.0, np.nan)),
            "edu": clean_edu(d[edu_col]) if edu_col in d else np.nan,
        })
        for v in VARS:
            col = f"r{w}{v}"
            out[v] = d[col] if col in d else np.nan
        frames.append(out)
    return pd.concat(frames, ignore_index=True)


ch_waves = [(r, l, cw, cy) for (r, l, cw, cy, ew, ey) in C.ROUNDS]
el_waves = [(r, l, ew, ey) for (r, l, cw, cy, ew, ey) in C.ROUNDS]

panel = pd.concat([
    build(ch, "China", ch_waves, "raeducl"),
    build(el, "England", el_waves, "raeducl"),
], ignore_index=True)

n0 = len(panel)
panel = panel[panel["age"].between(C.AGE_MIN, C.AGE_MAX)].copy()
panel["age_c"] = panel["age"] - 65
panel["female"] = pd.to_numeric(panel["female"], errors="coerce")

print(f"rows: {n0} -> {len(panel)} after age {C.AGE_MIN}-{C.AGE_MAX}")

cover = (panel.groupby(["country", "round", "round_label"])
         .agg(n=("pid", "size"),
              n_unique=("pid", "nunique"),
              age_mean=("age", "mean"),
              age_sd=("age", "std"),
              age65plus=("age", lambda s: (s >= 65).mean()),
              female=("female", "mean"),
              edu_tertiary=("edu", lambda s: (s == 3).mean()),
              adl=("adlfive", "mean"),
              adl_miss=("adlfive", lambda s: s.isna().mean()),
              iadl=("iadlfour", "mean"),
              diabe=("diabe", "mean"),
              hearte=("hearte", "mean"))
         .round(3))
cover.to_csv(os.path.join(C.TABLES, "T1_sample_by_round.csv"))
print(cover)

panel.to_parquet(os.path.join(C.DATA_CLEAN, "panel.parquet"), index=False)

# who is observed in all four rounds (balanced panel) - used for the
# within-person robustness check
cnt = panel.groupby(["country", "pid"])["round"].nunique()
bal = cnt[cnt == 4].reset_index()[["country", "pid"]]
bal.to_parquet(os.path.join(C.DATA_CLEAN, "balanced_ids.parquet"), index=False)
print("\nbalanced (all 4 rounds):")
print(bal.groupby("country").size())
print("\npanel saved:", panel.shape)
