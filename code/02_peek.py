"""Step 2: quick look at the extracted variables before building the panel."""
import os
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 60)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "data_clean")

ch = pd.read_parquet(os.path.join(D, "charls_extract.parquet"))
el = pd.read_parquet(os.path.join(D, "elsa_extract.parquet"))

print("CHARLS", ch.shape)
print("ELSA  ", el.shape)

print("\n--- CHARLS column list ---")
print(list(ch.columns))
print("\n--- ELSA column list ---")
print(list(el.columns))

for name, df, waves in [("CHARLS", ch, range(1, 5)), ("ELSA", el, range(1, 11))]:
    print(f"\n================ {name} ================")
    print(f"{'wave':>4} {'inw':>6} {'n_age':>7} {'age_mean':>9} {'adlfive_n':>9} "
          f"{'adlfive_mean':>12} {'imrc_n':>7} {'imrc_mean':>10} {'iadl4_n':>8} {'iadl4_mean':>10}")
    for w in waves:
        inw = df.get(f"inw{w}")
        age = df.get(f"r{w}agey")
        adl = df.get(f"r{w}adlfive")
        imr = df.get(f"r{w}imrc")
        iad = df.get(f"r{w}iadlfour")
        def s(x, f):
            return f(x) if x is not None else float("nan")
        print(f"{w:>4} {s(inw, lambda x: int((x == 1).sum())):>6} "
              f"{s(age, lambda x: int(x.notna().sum())):>7} "
              f"{s(age, lambda x: round(x.mean(), 1)):>9} "
              f"{s(adl, lambda x: int(x.notna().sum())):>9} "
              f"{s(adl, lambda x: round(x.mean(), 2)):>12} "
              f"{s(imr, lambda x: int(x.notna().sum())):>7} "
              f"{s(imr, lambda x: round(x.mean(), 2)):>10} "
              f"{s(iad, lambda x: int(x.notna().sum())):>8} "
              f"{s(iad, lambda x: round(x.mean(), 2)):>10}")

print("\n--- CHARLS adlfive value counts ---")
print(ch["r1adlfive"].value_counts(dropna=False).sort_index().head(10))
print("\n--- ELSA adlfive value counts (w5) ---")
print(el["r5adlfive"].value_counts(dropna=False).sort_index().head(10))
print("\n--- CHARLS imrc describe ---")
print(ch[["r1imrc", "r4imrc"]].describe())
print("\n--- ELSA imrc describe ---")
print(el[["r5imrc", "r9imrc"]].describe())
print("\n--- iwstat codes ---")
print("CH r1iwstat:", ch["r1iwstat"].value_counts(dropna=False).sort_index().to_dict())
print("EL r5iwstat:", el["r5iwstat"].value_counts(dropna=False).sort_index().to_dict())
print("\n--- gender/birth year ---")
print("CH ragender:", ch["ragender"].value_counts(dropna=False).to_dict())
print("EL ragender:", el["ragender"].value_counts(dropna=False).to_dict())
print("CH rabyear:", ch["rabyear"].describe().round(1).to_dict())
print("EL rabyear:", el["rabyear"].describe().round(1).to_dict())
