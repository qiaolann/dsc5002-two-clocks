"""Step 3: check the age profiles before committing to the outcome variables."""
import os
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "data_clean")

ch = pd.read_parquet(os.path.join(D, "charls_extract.parquet"))
el = pd.read_parquet(os.path.join(D, "elsa_extract.parquet"))

CH_WAVES = {1: 2011.5, 2: 2013.6, 3: 2015.6, 4: 2018.5}
EL_WAVES = {5: 2010.9, 6: 2012.6, 7: 2014.7, 9: 2018.6}


def long(df, waves, country):
    rows = []
    for w, year in waves.items():
        d = df[df[f"inw{w}"] == 1].copy()
        out = pd.DataFrame({
            "id": d["ID"] if country == "China" else d["idauniq"],
            "country": country,
            "wave": w,
            "year": year,
            "age": d[f"r{w}agey"],
            "female": (d["ragender"] == 2).astype(float),
            "adlfive": d[f"r{w}adlfive"],
            "iadlfour": d[f"r{w}iadlfour"],
            "imrc": d[f"r{w}imrc"],
            "dlrc": d[f"r{w}dlrc"],
            "diabe": d[f"r{w}diabe"],
            "hearte": d[f"r{w}hearte"],
        })
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


ch_long = long(ch, CH_WAVES, "China")
el_long = long(el, EL_WAVES, "England")
dat = pd.concat([ch_long, el_long], ignore_index=True)
dat = dat[(dat["age"] >= 50) & (dat["age"] < 80)].copy()
print("analytic rows 50-79:", dat.shape)
print(dat.groupby(["country", "wave"]).size())

for var in ["adlfive", "iadlfour", "imrc", "diabe"]:
    print(f"\n===== {var}: mean by age bin, pooled over the 4 rounds =====")
    sub = dat.dropna(subset=[var, "age"]).copy()
    sub["agebin"] = pd.cut(sub["age"], bins=range(50, 85, 5), right=False)
    t = sub.groupby(["country", "agebin"], observed=True)[var].agg(["mean", "count"]).round(3)
    print(t.unstack(0))

print("\n===== adlfive by wave, age 50-79 =====")
print(dat.groupby(["country", "wave"])["adlfive"].agg(["mean", "count", "std"]).round(3))
print("\n===== mean age by country-wave =====")
print(dat.groupby(["country", "wave"])["age"].agg(["mean", "count"]).round(2))
print("\n===== share age 70+ by wave =====")
print(dat.assign(old=lambda x: x["age"] >= 70).groupby(["country", "wave"])["old"].mean().round(3))
