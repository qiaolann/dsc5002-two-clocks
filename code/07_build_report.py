"""Step 7: build the Word report from report/report.md.

Minimal markdown subset supported: #/##/### headings, paragraphs, bullet lists,
> blockquote (rendered as a centred model line), **bold**, *italic*, `code`,
![alt](file) figure blocks followed by a **Figure N.** caption paragraph, and
<!-- table:T1 --> / <!-- table:T2 --> table placeholders filled from the CSVs.
"""
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
from docx import Document  # noqa: E402
from docx.enum.section import WD_SECTION  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPORT = os.path.join(ROOT, "report")
FIGS = os.path.join(ROOT, "output", "figures")
TABLES = os.path.join(ROOT, "output", "tables")

BODY_FONT = "Times New Roman"
HEAD_FONT = "Arial"
BODY_PT = 10

DQ = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


def add_runs(par, text, size=BODY_PT, italic=False, color=None):
    """Add text to a paragraph, honouring **bold**, *italic* and `code`."""
    for tok in DQ.split(text):
        if not tok:
            continue
        bold = italic_ = code = False
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            tok, bold = tok[2:-2], True
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            tok, italic_ = tok[1:-1], True
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            tok, code = tok[1:-1], True
        r = par.add_run(tok)
        r.font.name = "Consolas" if code else BODY_FONT
        r.font.size = Pt(size if not code else size - 0.5)
        r.bold = bold
        r.italic = italic or italic_
        if color:
            r.font.color.rgb = color
    return par


def set_cell(cell, text, bold=False, size=8.4, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.font.name = BODY_FONT
    r.font.size = Pt(size)
    r.bold = bold


def shade(cell, hex_color="F2F2F2"):
    tcPr = cell._tc.get_or_add_tcPr()
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:color"), "auto")
    el.set(qn("w:fill"), hex_color)
    tcPr.append(el)


def thin_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "BFBFBF")
        borders.append(el)
    tblPr.append(borders)


def add_page_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)
    r = p.add_run("")
    r.font.size = Pt(8)


def table_t1(doc):
    t = pd.read_csv(os.path.join(TABLES, "T1_sample_by_round.csv"))
    cols = ["Round", "Country", "n", "Mean age", "% 65+", "% female",
            "ADL", "IADL", "% tertiary"]
    tab = doc.add_table(rows=1, cols=len(cols))
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    thin_borders(tab)
    for i, c in enumerate(cols):
        set_cell(tab.rows[0].cells[i], c, bold=True)
        shade(tab.rows[0].cells[i])
    for _, r in t.iterrows():
        row = tab.add_row().cells
        vals = [str(r.round_label), str(r.country), f"{int(r.n):,}", f"{r.age_mean:.1f}",
                f"{r.age65plus*100:.0f}", f"{r.female*100:.0f}",
                f"{r.adl:.2f}", f"{r.iadl:.2f}", f"{r.edu_tertiary*100:.1f}"]
        for i, v in enumerate(vals):
            set_cell(row[i], v, align=WD_ALIGN_PARAGRAPH.CENTER if i else None)
    widths = [1.5, 1.9, 1.6, 1.7, 1.4, 1.7, 1.3, 1.3, 1.7]
    for row in tab.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    cap = doc.add_paragraph()
    cap.paragraph_format.space_before = Pt(3)
    cap.paragraph_format.space_after = Pt(8)
    add_runs(cap, "**Table 1.** Analytic sample by country and round, ages 50–79. "
                  "Percentages are of the round's respondents; ADL and IADL are mean "
                  "counts (0–5 and 0–4). Unweighted.", size=8.4)


def table_t2(doc):
    rows = [
        ("ADL (0–5)", "China", "0.0221 (0.0207, 0.0235)", "0.22", ""),
        ("", "England", "0.0094 (0.0078, 0.0110)", "0.09", ""),
        ("", "Difference", "−0.0128 (−0.0149, −0.0107)", "−0.13", "<0.001"),
        ("IADL (0–4)", "China", "0.0207 (0.0194, 0.0219)", "0.21", ""),
        ("", "England", "0.0047 (0.0036, 0.0058)", "0.05", ""),
        ("", "Difference", "−0.0159 (−0.0176, −0.0142)", "−0.16", "<0.001"),
    ]
    cols = ["Outcome", "Group", "Slope per year (95% CI)", "Per decade",
            "p (difference)"]
    tab = doc.add_table(rows=1, cols=len(cols))
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    thin_borders(tab)
    for i, c in enumerate(cols):
        set_cell(tab.rows[0].cells[i], c, bold=True)
        shade(tab.rows[0].cells[i])
    for r in rows:
        cells = tab.add_row().cells
        for i, v in enumerate(r):
            set_cell(cells[i], v, bold=(r[1] == "Difference"),
                     align=WD_ALIGN_PARAGRAPH.CENTER if i else None)
    widths = [2.6, 2.4, 5.6, 2.4, 2.6]
    for row in tab.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
    cap = doc.add_paragraph()
    cap.paragraph_format.space_before = Pt(3)
    cap.paragraph_format.space_after = Pt(8)
    add_runs(cap, "**Table 2.** Age slopes from the within-country models (round fixed "
                  "effects, standard errors clustered on the person). Difference is the "
                  "age × country interaction from the pooled model; its p-value is from "
                  "the cluster-robust Wald test.", size=8.4)


def build():
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.1)
    sec.left_margin = sec.right_margin = Cm(2.2)
    add_page_footer(sec)

    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = Pt(BODY_PT)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.line_spacing = 1.06
    st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    lines = open(os.path.join(REPORT, "report.md"), encoding="utf-8").read().split("\n")
    i = 0
    pending_caption = False
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue

        if ln.startswith("<!-- pagebreak -->"):
            doc.add_page_break()
        elif ln.startswith("<!-- table:T1 -->"):
            table_t1(doc)
        elif ln.startswith("<!-- table:T2 -->"):
            table_t2(doc)
        elif ln.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(7)
            p.paragraph_format.space_after = Pt(3)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(ln[4:])
            r.font.name = HEAD_FONT
            r.font.size = Pt(10)
            r.bold = True
        elif ln.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(ln[3:])
            r.font.name = HEAD_FONT
            r.font.size = Pt(11.5)
            r.bold = True
            r.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
        elif ln.startswith("# "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(ln[2:])
            r.font.name = HEAD_FONT
            r.font.size = Pt(15)
            r.bold = True
        elif ln.startswith("!["):
            m = re.match(r"!\[.*?\]\((.+?)\)", ln)
            img = os.path.join(FIGS, m.group(1))
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(img, width=Cm(15.6))
            pending_caption = True
        elif ln.startswith("> "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run(ln[2:])
            r.font.name = BODY_FONT
            r.font.size = Pt(10)
            r.italic = True
        elif ln.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_runs(p, ln[2:])
        elif ln.startswith("**Figure") or ln.startswith("**Table"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(9)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_runs(p, ln, size=8.4)
            pending_caption = False
        else:
            p = doc.add_paragraph()
            if ln.startswith("**Group members") or ln.startswith("**DSC5002"):
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_after = Pt(2)
                add_runs(p, ln, size=9, italic=False,
                         color=RGBColor(0x44, 0x44, 0x44))
            else:
                add_runs(p, ln)
        i += 1

    out = os.path.join(REPORT, "DSC5002_Group_Project_Report.docx")
    doc.save(out)
    print("saved:", out)


if __name__ == "__main__":
    build()
