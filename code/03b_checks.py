"""Step 3b: missingness and the wave-4 word-recall break."""
import os
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "data_clean")
ch = pd.read_parquet(os.path.join(D, "charls_extract.parquet"))
el = pd.read_parquet(os.path.join(D, "elsa_extract.parquet"))

print("== missing among respondents (inw==1), age 50-79 ==")
for name, df, waves in [("CH", ch, range(1, 5)), ("EL", el, [5, 6, 7, 9])]:
    for w in waves:
        d = df[(df[f"inw{w}"] == 1) & df[f"r{w}agey"].between(50, 79)]
        row = [w, len(d)]
        for v in ["adlfive", "iadlfour", "imrc"]:
            row.append(round(100 * d[f"r{w}{v}"].isna().mean(), 1))
        print(name, "wave", row)

print("\n== imrc by wave, age-adjusted (50-54 and 60-64) ==")
for name, df, waves in [("CH", ch, range(1, 5)), ("EL", el, [5, 6, 7, 9])]:
    for w in waves:
        d = df[(df[f"inw{w}"] == 1) & df[f"r{w}agey"].between(50, 79)]
        a = d.loc[d[f"r{w}agey"].between(50, 55), f"r{w}imrc"].mean()
        b = d.loc[d[f"r{w}agey"].between(60, 65), f"r{w}imrc"].mean()
        print(f"{name} w{w}: 50-54={a:.2f}  60-64={b:.2f}  overall={d[f'r{w}imrc'].mean():.2f}")

print("\n== imrc missing by wave (share) ==")
for name, df, waves in [("CH", ch, range(1, 5)), ("EL", el, [5, 6, 7, 9])]:
    vals = []
    for w in waves:
        d = df[(df[f"inw{w}"] == 1) & df[f"r{w}agey"].between(50, 79)]
        vals.append(round(100 * d[f"r{w}imrc"].isna().mean(), 1))
    print(name, vals)
