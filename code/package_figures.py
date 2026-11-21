"""Zip the figure folder so it can be uploaded to Overleaf and auto-extracted."""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REP = os.path.join(ROOT, "report")
FIG = os.path.join(REP, "figures")
OUT = os.path.join(REP, "figures.zip")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for name in sorted(os.listdir(FIG)):
        if name.lower().endswith(".png"):
            z.write(os.path.join(FIG, name), f"figures/{name}")

with zipfile.ZipFile(OUT) as z:
    names = z.namelist()
print("entries:", len(names))
for n in names:
    print("  ", n)
print("size KB:", round(os.path.getsize(OUT) / 1024))
