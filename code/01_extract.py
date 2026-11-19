"""Step 1: extract the analysis variables from the two harmonized files.

CHARLS: Stata file, all 4 waves (2011, 2013, 2015, 2018).
ELSA  : tab-delimited text, 10 waves (2002/03 ... 2021/23); all waves are kept
        and the four calendar-matched rounds are selected downstream.

Run:  python -u code/01_extract.py
Output: data_clean/charls_extract.parquet, data_clean/elsa_extract.parquet
"""
import os
import csv
import sys
import time
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CH = os.path.join(ROOT, "Group project", "harmonized_CHARLS", "GH_CHARLS_d2.dta")
EL = os.path.join(ROOT, "Group project", "harmonized_ELSA", "gh_elsa_h.tab")
OUT = os.path.join(ROOT, "data_clean")
os.makedirs(OUT, exist_ok=True)


def log(*a):
    print(*a, flush=True)


FAMILIES = [
    "agey", "iwstat", "inw",
    "adlfive", "adlwa", "iadlfour", "iadlza",
    "imrc", "dlrc",
    "shlt", "diabe", "hearte", "cancre", "mstat",
    "cesd", "cesdl10",
]


def charls_columns(have):
    cols = ["ID", "rabyear", "ragender", "raeduc_c", "raeducl"]
    for w in range(1, 5):
        for fam in FAMILIES:
            cols.append(f"inw{w}" if fam == "inw" else f"r{w}{fam}")
    return [c for c in cols if c in have]


def elsa_columns(have):
    cols = ["idauniq", "idauniqc", "rabyear", "ragender", "raeduc_c", "raeducl"]
    for w in range(1, 11):
        for fam in FAMILIES:
            cols.append(f"inw{w}" if fam == "inw" else f"r{w}{fam}")
    return [c for c in cols if c in have]


def extract_charls():
    t0 = time.time()
    log("CHARLS: header ...")
    have = set(pd.read_stata(CH, iterator=True).variable_labels())
    cols = charls_columns(have)
    log(f"  cols={len(cols)}  ({time.time()-t0:.0f}s)")
    df = pd.read_stata(CH, columns=cols, convert_categoricals=False)
    df.to_parquet(os.path.join(OUT, "charls_extract.parquet"), index=False)
    log(f"  CHARLS shape={df.shape}  ({time.time()-t0:.0f}s)")


def extract_elsa():
    t0 = time.time()
    log("ELSA: header ...")
    with open(EL, encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
    cols = elsa_columns(set(header))
    idx = [header.index(c) for c in cols]
    maxi = max(idx)
    log(f"  cols={len(cols)} max_index={maxi}")

    out = {c: [] for c in cols}
    with open(EL, encoding="utf-8", errors="replace", newline="") as f:
        rdr = csv.reader(f, delimiter="\t")
        next(rdr, None)
        n = 0
        for row in rdr:
            n += 1
            if len(row) <= maxi:
                row = row + [""] * (maxi + 1 - len(row))
            for c, j in zip(cols, idx):
                out[c].append(row[j])
            if n % 5000 == 0:
                log(f"  ... {n} rows ({time.time()-t0:.0f}s)")

    df = pd.DataFrame(out)
    for c in df.columns:
        if c in ("idauniq", "idauniqc"):
            continue
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.to_parquet(os.path.join(OUT, "elsa_extract.parquet"), index=False)
    log(f"  ELSA shape={df.shape}  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("both", "charls"):
        extract_charls()
    if which in ("both", "elsa"):
        extract_elsa()
