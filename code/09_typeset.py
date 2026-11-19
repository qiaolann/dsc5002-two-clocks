"""Step 9: typeset the report to A4 PDF with PyMuPDF's Story engine.

Each heading, paragraph, figure and table is placed as one atomic block, so a
figure or table is never split across pages.
"""
import base64
import os
import re
import sys

import pandas as pd
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPORT = os.path.join(ROOT, "report")
FIGS = os.path.join(ROOT, "output", "figures")

LEFT, RIGHT = 51, 51
TOP, BOTTOM = 52, 50

CSS = """
body { font-family: "Times New Roman", serif; font-size: 9.7pt; line-height: 1.30;
       color: #111111; text-align: justify; }
h1 { font-family: "Arial", sans-serif; font-size: 16pt; line-height: 1.2;
     margin: 0 0 4pt 0; text-align: left; }
h2 { font-family: "Arial", sans-serif; font-size: 11.5pt; margin: 0; text-align: left; }
h3 { font-family: "Arial", sans-serif; font-size: 10pt; margin: 0; text-align: left; }
p { margin: 0; }
p.meta { font-size: 8.6pt; color: #555555; text-align: left; }
p.cap { font-size: 8.2pt; line-height: 1.26; text-align: justify; }
blockquote { margin: 0; text-align: center; font-style: italic; }
figure { margin: 0; text-align: center; }
img { width: 92%; }
code { font-family: "Courier New", monospace; font-size: 9pt; }
"""

# vertical rhythm (points) between blocks
SPACE = {"h1": 2, "h2": 11, "h3": 8, "p": 4.0, "meta": 1, "cap": 8,
         "figure": 5, "quote": 7}


def b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def inline(text):
    out = []
    for tok in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)", text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            out.append(f"<b>{tok[2:-2]}</b>")
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            out.append(f"<i>{tok[1:-1]}</i>")
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            out.append(f"<code>{tok[1:-1]}</code>")
        else:
            out.append(tok)
    return "".join(out)


def build_blocks():
    """Return a list of (kind, html) blocks in document order."""
    lines = open(os.path.join(REPORT, "report.md"), encoding="utf-8").read().split("\n")
    blocks, pending_fig = [], None
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            continue
        if s.startswith("<!-- table:T1 -->"):
            img = b64(os.path.join(FIGS, "table1.png"))
            cap = ("<p class='cap'><b>Table 1.</b> Analytic sample by country and "
                   "round, ages 50–79. Percentages are of the round's respondents; "
                   "ADL and IADL are mean counts (0–5 and 0–4). Unweighted.</p>")
            blocks.append(("figure", f'<figure><img src="{img}"></figure>{cap}'))
        elif s.startswith("<!-- table:T2 -->"):
            img = b64(os.path.join(FIGS, "table2.png"))
            cap = ("<p class='cap'><b>Table 2.</b> Age slopes from the within-country "
                   "models (round fixed effects, standard errors clustered on the "
                   "person). Difference is the age × country interaction from the "
                   "pooled model; its p-value is from the cluster-robust Wald test.</p>")
            blocks.append(("figure", f'<figure><img src="{img}"></figure>{cap}'))
        elif s.startswith("### "):
            blocks.append(("h3", f"<h3>{inline(s[4:])}</h3>"))
        elif s.startswith("## "):
            blocks.append(("h2", f"<h2>{inline(s[3:])}</h2>"))
        elif s.startswith("# "):
            blocks.append(("h1", f"<h1>{inline(s[2:])}</h1>"))
        elif s.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.+?)\)", s)
            pending_fig = ("figure", m.group(2))
        elif s.startswith("**Figure"):
            if pending_fig:
                kind, name = pending_fig
                img = b64(os.path.join(FIGS, name))
                blocks.append(("figure",
                               f'<figure><img src="{img}"></figure>'
                               f'<p class="cap">{inline(s)}</p>'))
                pending_fig = None
            else:
                blocks.append(("cap", f'<p class="cap">{inline(s)}</p>'))
        elif s.startswith("**Table"):
            if pending_fig:
                kind, name = pending_fig
                img = b64(os.path.join(FIGS, f"{name}.png"))
                blocks.append(("figure",
                               f'<figure><img src="{img}"></figure>'
                               f'<p class="cap">{inline(s)}</p>'))
                pending_fig = None
            else:
                blocks.append(("cap", f'<p class="cap">{inline(s)}</p>'))
        elif s.startswith("<!-- pagebreak -->"):
            blocks.append(("pagebreak", ""))
        elif s.startswith("> "):
            blocks.append(("quote", f"<blockquote>{inline(s[2:])}</blockquote>"))
        elif s.startswith("- "):
            blocks.append(("p", f"<p>• {inline(s[2:])}</p>"))
        elif (s.startswith("**DSC5002") or s.startswith("**Group members")
              or s.startswith("Submitted ") or s.startswith("Student IDs:")):
            blocks.append(("meta", f'<p class="meta">{inline(s)}</p>'))
        else:
            blocks.append(("p", f"<p>{inline(s)}</p>"))
    return blocks


def typeset():
    blocks = build_blocks()
    mediabox = fitz.paper_rect("a4")
    content = fitz.Rect(LEFT, TOP, mediabox.width - RIGHT, mediabox.height - BOTTOM)

    out = os.path.join(REPORT, "DSC5002_Group_Project_Report.pdf")
    tmp = os.path.join(REPORT, "_flow.pdf")
    if os.path.exists(tmp):
        try:
            os.remove(tmp)
        except OSError:
            pass

    # MuPDF's Story adds a fixed 10pt padding above and below the flowed
    # content of every placement; PAD compensates for it so blocks stack tightly.
    PAD = 10.0
    writer = fitz.DocumentWriter(tmp)
    device = None
    y = TOP
    width = mediabox.width

    def new_page():
        """Close the open page, open a fresh one, reset the cursor."""
        nonlocal device, y
        if device is not None:
            writer.end_page()
        device = writer.begin_page(mediabox)
        y = TOP

    def try_place(html, start_y):
        story = fitz.Story(html=html, user_css=CSS)
        rect = fitz.Rect(LEFT, start_y - PAD, width - RIGHT,
                         mediabox.height - BOTTOM - PAD)
        more, filled = story.place(rect)
        return story, more, filled

    deferred = []          # figures pushed to the top of the next page

    def flush_deferred():
        """Draw floated figures at the top of the current (fresh) page."""
        nonlocal y
        while deferred:
            html = deferred.pop(0)
            story, more, filled = try_place(html, y)
            if more:                       # cannot happen for a figure; be safe
                new_page()
                story, more, filled = try_place(html, y)
            story.draw(device)
            y = float(filled[3]) - PAD if filled else y + 12

    new_page()
    for kind, html in blocks:
        if kind == "pagebreak":
            new_page()
            flush_deferred()
            continue
        gap_before = 0 if (kind == "h1" or y <= TOP) else SPACE[kind]
        story, more, filled = try_place(html, y + gap_before)

        if more and y > TOP + 2:
            if kind == "figure":          # float it, keep the text flowing
                deferred.append(html)
                continue
            new_page()
            flush_deferred()
            story, more, filled = try_place(html, y + (0 if y <= TOP else 0))

        # keep a heading together with whatever follows it
        if (kind in ("h2", "h3") and not more and y > TOP + 2
                and filled and mediabox.height - BOTTOM - float(filled[3]) < 42):
            new_page()
            flush_deferred()
            story, more, filled = try_place(html, y)

        story.draw(device)
        y = float(filled[3]) - PAD if filled else y + 12

    if deferred:
        new_page()
        flush_deferred()
    if device is not None:
        writer.end_page()
    writer.close()

    doc = fitz.open(tmp)
    n = doc.page_count
    for i, page in enumerate(doc, 1):
        r = fitz.Rect(LEFT, mediabox.height - 42, mediabox.width - RIGHT,
                      mediabox.height - 26)
        page.insert_textbox(r, f"{i} / {n}", fontsize=8, fontname="helv",
                            color=(0.42, 0.42, 0.42), align=fitz.TEXT_ALIGN_CENTER)
    # make the images as boring as possible for in-browser viewers:
    # plain DeviceRGB, Flate, no soft mask, no ICC profile indirection
    for pno in range(doc.page_count):
        for im in doc[pno].get_images(full=True):
            xref, smask, _w, _h, _bpc, cs = im[:6]
            if cs == "ICCBased":
                doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
            if smask:
                doc.xref_set_key(xref, "SMask", "null")

    doc.set_metadata({
        "title": "Two clocks, one comparison: calendar- and age-anchored views "
                 "of functional health in China and England, 2011-2018",
        "author": "DSC5002 Group Project",
        "subject": "Exploratory data analysis of CHARLS and ELSA harmonized data",
        "keywords": "CHARLS; ELSA; ADL; IADL; age-period-cohort; cross-national comparison",
    })
    doc.save(out, garbage=4, deflate=True)
    doc.close()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print(f"pages={n}")
    return out, n


if __name__ == "__main__":
    out, n = typeset()
    doc = fitz.open(out)
    prev = os.path.join(REPORT, "preview")
    os.makedirs(prev, exist_ok=True)
    for i, page in enumerate(doc, 1):
        page.get_pixmap(dpi=110).save(os.path.join(prev, f"page{i:02d}.png"))
    print("saved", out, "pages", n)
