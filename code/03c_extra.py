"""Numbers behind the three new figures: sample flow, within-person change, diabetes."""
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 220)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
panel = pd.read_parquet(os.path.join(ROOT, "data_clean", "panel.parquet"))
ROUNDS = [1, 2, 3, 4]

print("=== A3: sample flow by country-round ===")
for c in ["China", "England"]:
    d = panel[panel["country"] == c]
    seen = {}
    prev_ids = set()
    print(f"\n{c}")
    for r in ROUNDS:
        ids = set(d.loc[d["round"] == r, "pid"])
        returning = len(ids & prev_ids)
        new = len(ids - prev_ids)
        lost = len(prev_ids - ids)
        print(f"  R{r}: n={len(ids):>6}  returning={returning:>6}  new={new:>5}  "
              f"left={lost:>5}  net={len(ids)-len(prev_ids):>+6}")
        prev_ids = ids

print("\n=== B5: within-person change in ADL (consecutive rounds) ===")
for c in ["China", "England"]:
    d = panel[panel["country"] == c]
    w = d.pivot_table(index="pid", columns="round", values="adlfive")
    for a, b in [(1, 2), (2, 3), (3, 4)]:
        delta = (w[b] - w[a]).dropna()
        print(f"  {c} R{a}->R{b}: n={len(delta):>6} mean={delta.mean():+.3f} "
              f"worse={(delta > 0).mean()*100:.1f}%  same={(delta == 0).mean()*100:.1f}%  "
              f"better={(delta < 0).mean()*100:.1f}%")
    cum = (w[4] - w[1]).dropna()
    print(f"  {c} R1->R4 cumulative: n={len(cum):>6} mean={cum.mean():+.3f} "
          f"worse={(cum > 0).mean()*100:.1f}% same={(cum == 0).mean()*100:.1f}% "
          f"better={(cum < 0).mean()*100:.1f}%  p90={cum.quantile(.9):.0f}")

print("\n=== C2: diabetes by age bin, pooled over rounds ===")
d = panel.dropna(subset=["diabe"]).copy()
d["bin"] = pd.cut(d["age"], range(50, 85, 5), right=False)
t = d.groupby(["bin", "country"], observed=True)["diabe"].agg(["mean", "count"])
print((t["mean"].unstack(1) * 100).round(1))
print(t["count"].unstack(1))

print("\n=== C2b: diabetes by round (age-standardised to the pooled age mix) ===")
ref = d["age"].value_counts(normalize=True)
for c in ["China", "England"]:
    for r in ROUNDS:
        x = d[(d["country"] == c) & (d["round"] == r)]
        by_age = x.groupby("age")["diabe"].mean()
        w = ref.reindex(by_age.index).fillna(0)
        std = (by_age * w).sum() / w.sum() if w.sum() else np.nan
        print(f"  {c} R{r}: crude={x['diabe'].mean()*100:.1f}%  age-std={std*100:.1f}%")
