"""Read-only data profile: what is actually inside the two files after harmonising."""
import os
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "data_clean")

panel = pd.read_parquet(os.path.join(D, "panel.parquet"))

print("=== A. analytic sample by country x round (ages 50-79) ===")
g = panel.groupby(["country", "round"]).apply(
    lambda d: pd.Series({
        "n": len(d),
        "age_mean": d["age"].mean(),
        "age_sd": d["age"].std(),
        "p65": (d["age"] >= 65).mean() * 100,
        "p70": (d["age"] >= 70).mean() * 100,
        "female": d["female"].mean() * 100,
        "adl": d["adlfive"].mean(),
        "adl_any": (d["adlfive"] > 0).mean() * 100,
        "iadl": d["iadlfour"].mean(),
        "iadl_any": (d["iadlfour"] > 0).mean() * 100,
        "adl_miss": d["adlfive"].isna().mean() * 100,
        "iadl_miss": d["iadlfour"].isna().mean() * 100,
        "diab": d["diabe"].mean() * 100,
        "heart": d["hearte"].mean() * 100,
        "tert": (d["edu"] == 3).mean() * 100,
    }), include_groups=False).round(1)
print(g)

print("\n=== B. panel structure ===")
for c in ["China", "England"]:
    d = panel[panel["country"] == c]
    waves = d.groupby("pid")["round"].nunique()
    print(f"{c}: person-rounds={len(d):,}  unique persons={d['pid'].nunique():,}  "
          f"observed all 4 rounds={int((waves == 4).sum()):,}  "
          f"mean waves per person={waves.mean():.2f}")

print("\n=== C. age profile of ADL / IADL, pooled over rounds ===")
d = panel.copy()
d["bin"] = pd.cut(d["age"], range(50, 85, 5), right=False)
prof = d.groupby(["bin", "country"], observed=True).agg(
    adl=("adlfive", "mean"), iadl=("iadlfour", "mean"),
    n=("adlfive", "count")).round(3)
print(prof.unstack(1))

print("\n=== D. distribution of ADL score (share %), ages 50-79 ===")
for c in ["China", "England"]:
    d = panel[panel["country"] == c]["adlfive"].dropna()
    print(c, {int(k): round(v * 100, 1) for k, v in d.value_counts(normalize=True).sort_index().items()})

print("\n=== E. word recall by round (the break we excluded), ages 50-79 ===")
for c in ["China", "England"]:
    d = panel[panel["country"] == c]
    row = d.groupby("round").apply(lambda x: x.loc[x["age"].between(50, 55), "imrc"].mean(),
                                   include_groups=False).round(2)
    print(c, "imrc ages 50-54 by round:", row.to_dict())
