"""Static sanity checks for report.tex (no TeX installation available)."""
import collections
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEX = os.path.join(ROOT, "report", "report.tex")

src = open(TEX, encoding="utf-8").read()

begins = re.findall(r"\\begin\{(\w+)\}", src)
ends = re.findall(r"\\end\{(\w+)\}", src)
print("environments: begin=%d end=%d" % (len(begins), len(ends)))
cb, ce = collections.Counter(begins), collections.Counter(ends)
diff = {k: (cb[k], ce[k]) for k in set(cb) | set(ce) if cb[k] != ce[k]}
print("unbalanced:", diff if diff else "none")

# brace balance, ignoring \{ and \}
depth = 0
for ch in re.sub(r"\\[{}]", "", src):
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
print("brace depth at end:", depth)

refs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", src)
missing = [r for r in refs if not os.path.exists(os.path.join(ROOT, "report", "figures", r))]
print("figures referenced: %d | missing: %s" % (len(refs), missing or "none"))

labels = set(re.findall(r"\\label\{([^}]+)\}", src))
used = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", src))
print("labels:", len(labels), "| refs used:", len(used))
print("refs without label:", sorted(used - labels) or "none")
print("labels never referenced:", sorted(labels - used) or "none")

bad = []
for i, line in enumerate(src.split("\n"), 1):
    stripped = re.sub(r"\\%", "", line)
    if "%" in stripped and not stripped.lstrip().startswith("%"):
        bad.append((i, line.strip()[:70]))
print("suspicious unescaped '%':", bad or "none")

for tok in ["&", "_", "#"]:
    hits = []
    for i, line in enumerate(src.split("\n"), 1):
        if line.lstrip().startswith("%"):
            continue
        s = re.sub(r"\\[&_#]", "", line)
        s = re.sub(r"\$[^$]*\$", "", s)
        if tok in s:
            hits.append((i, line.strip()[:70]))
    print("suspicious '%s':" % tok, hits or "none")
