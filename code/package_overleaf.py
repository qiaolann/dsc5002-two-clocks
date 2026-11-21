"""Package report.tex + figures into a zip ready for Overleaf upload."""
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REP = os.path.join(ROOT, "report")
OUT = os.path.join(REP, "dsc5002_llncs_overleaf.zip")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(REP, "report.tex"), "report.tex")
    figdir = os.path.join(REP, "figures")
    for name in sorted(os.listdir(figdir)):
        if name.lower().endswith(".png"):
            z.write(os.path.join(figdir, name), f"figures/{name}")

with zipfile.ZipFile(OUT) as z:
    print("entries:", len(z.namelist()))
    for n in z.namelist():
        print("  ", n)
print("size KB:", round(os.path.getsize(OUT) / 1024))
