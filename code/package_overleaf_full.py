"""Package the compact report: tex + only the figures it references + llncs.cls."""
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REP = os.path.join(ROOT, "report")
FIG = os.path.join(REP, "figures")
OUT = os.path.join(REP, "dsc5002_llncs_full.zip")

tex = open(os.path.join(REP, "report.tex"), encoding="utf-8").read()
names = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(REP, "report.tex"), "report.tex")
    z.write(os.path.join(REP, "latex_deps", "llncs.cls"), "llncs.cls")
    for n in names:
        z.write(os.path.join(FIG, n), f"figures/{n}")

with zipfile.ZipFile(OUT) as z:
    entries = z.namelist()
print("figures referenced:", len(names))
print("entries:", len(entries))
for e in entries:
    print("  ", e)
print("size KB:", round(os.path.getsize(OUT) / 1024))
