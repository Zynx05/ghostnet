"""
Builds the viva sheet.
Owner: Docs and Research Lead (member 10).

The words live in viva_content.py. This file only lays them out, so a member
correcting their own page never has to read reportlab.

    pip install reportlab
    python make_viva_pdf.py

Output: GhostNet Viva Sheet.pdf
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether,
)

from viva_content import MEMBERS, SHARED

INK = colors.HexColor("#0a0a0a")
MUTED = colors.HexColor("#404040")
FAINT = colors.HexColor("#737373")
WELL = colors.HexColor("#f2f2ee")
LINE = colors.HexColor("#d4d4d0")

PAGE_W, PAGE_H = A4
MARGIN = 16 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=16, leading=19,
                    textColor=INK, spaceAfter=2)
ROLE = ParagraphStyle("ROLE", fontName="Courier-Bold", fontSize=7.5, leading=10,
                      textColor=FAINT, spaceAfter=7)
H2 = ParagraphStyle("H2", fontName="Courier-Bold", fontSize=7.2, leading=9,
                    textColor=INK, spaceBefore=6.5, spaceAfter=3)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=8.6, leading=11.4,
                      textColor=INK, alignment=TA_LEFT)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=7.9, leading=10.5,
                       textColor=MUTED)
KEY = ParagraphStyle("KEY", fontName="Courier-Bold", fontSize=7.5, leading=10,
                     textColor=INK)
QUESTION = ParagraphStyle("Q", fontName="Helvetica-Bold", fontSize=7.9,
                          leading=10.5, textColor=INK)
MONO = ParagraphStyle("MONO", fontName="Courier", fontSize=7.5, leading=10,
                      textColor=INK)
LEAD = ParagraphStyle("LEAD", fontName="Helvetica", fontSize=10, leading=14,
                      textColor=MUTED, spaceAfter=8)

GRID = [
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOX", (0, 0), (-1, -1), 0.9, INK),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 3.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
]


def two_column(pairs, first_w, left_style=KEY, right_style=SMALL):
    """A table of label and value, with the label column shaded."""
    rows = [[Paragraph(a, left_style), Paragraph(b, right_style)] for a, b in pairs]
    t = Table(rows, colWidths=[first_w, CONTENT_W - first_w], hAlign="LEFT")
    t.setStyle(TableStyle(GRID + [("BACKGROUND", (0, 0), (0, -1), WELL)]))
    return t


def listing(items, numbered=False):
    out = []
    for i, text in enumerate(items, start=1):
        marker = ("%d.&nbsp;&nbsp;" % i) if numbered else "&bull;&nbsp;&nbsp;"
        out.append(Paragraph(marker + text, BODY))
        out.append(Spacer(1, 1.8))
    return out


def note(text):
    """A single shaded block, used for the thing that went wrong."""
    t = Table([[Paragraph(text, SMALL)]], colWidths=[CONTENT_W], hAlign="LEFT")
    t.setStyle(TableStyle(GRID + [("BACKGROUND", (0, 0), (-1, -1), WELL)]))
    return t


def heading(text):
    return Paragraph(text, H2)


def cover(story):
    story.append(Paragraph("GhostNet", H1))
    story.append(Paragraph("VIVA SHEET  ::  DESIGN AND ANALYSIS OF ALGORITHMS", ROLE))
    story.append(Paragraph(SHARED["what"], LEAD))
    story.append(Paragraph(SHARED["why_daa"], LEAD))

    story.append(heading("HOW THE SYSTEM ACTUALLY RUNS"))
    story.extend(listing(SHARED["flow"], numbered=True))

    story.append(heading("THE STACK"))
    story.append(two_column(SHARED["stack"], 30 * mm))

    story.append(heading("HOW A SUBMISSION IS SCORED"))
    story.append(Paragraph(SHARED["formula"], MONO))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Plagiarism multiplies instead of adding, so copied work cannot win on "
        "the strength of the other three columns. The weights sit at the top of "
        "algorithms/ranker.py where anyone can read them.", SMALL))

    story.append(heading("WHO OWNS WHAT"))
    rows = [[Paragraph(str(m["n"]), KEY),
             Paragraph(m["role"], QUESTION),
             Paragraph(m["algorithm"], SMALL)] for m in MEMBERS]
    t = Table(rows, colWidths=[7 * mm, 38 * mm, CONTENT_W - 45 * mm], hAlign="LEFT")
    t.setStyle(TableStyle(GRID + [
        ("BACKGROUND", (0, 0), (1, -1), WELL),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    story.append(heading("RULES FOR THE ROOM"))
    story.extend(listing(SHARED["rules"]))


def member_page(story, m):
    story.append(Paragraph(m["role"], H1))
    story.append(Paragraph("MEMBER %d  ::  %s" % (m["n"], m["algorithm"].upper()), ROLE))

    story.append(Paragraph(m["opening"], BODY))

    story.append(heading("WHAT I BUILT"))
    story.extend(listing(m["built"]))

    story.append(heading("THE FILES I OWN"))
    story.append(two_column(m["files"], 62 * mm, left_style=MONO))

    story.append(heading("TOOLS I USED, AND WHY THOSE"))
    story.append(Paragraph(m["tools"], BODY))

    story.append(heading("SOMETHING THAT WENT WRONG"))
    story.append(note(m["problem"]))

    story.append(heading("HOW MY ALGORITHM WORKS"))
    story.extend(listing(m["steps"], numbered=True))

    story.append(KeepTogether([
        heading("COMPLEXITY"),
        Paragraph(m["cost"], BODY),
    ]))

    story.append(heading("HOW MY PART CONNECTS TO EVERYBODY ELSE"))
    story.append(Paragraph(m["connects"], BODY))

    story.append(heading("LIKELY QUESTIONS"))
    story.append(two_column(m["qa"], 52 * mm, left_style=QUESTION))

    story.append(heading("SHOW THIS ON SCREEN"))
    story.append(Paragraph(m["show"], BODY))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    canvas.setFont("Courier", 7)
    canvas.setFillColor(FAINT)
    canvas.drawString(MARGIN, 9 * mm, "GHOSTNET  ::  VIVA SHEET")
    canvas.drawRightString(PAGE_W - MARGIN, 9 * mm, "PAGE %d" % doc.page)
    canvas.restoreState()


def build():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "GhostNet Viva Sheet.pdf")
    doc = BaseDocTemplate(out, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=15 * mm, bottomMargin=18 * mm,
                          title="GhostNet Viva Sheet",
                          author="GhostNet team")
    frame = Frame(MARGIN, 18 * mm, CONTENT_W, PAGE_H - 33 * mm, id="body")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=footer)])

    story = []
    cover(story)
    for m in MEMBERS:
        story.append(PageBreak())
        member_page(story, m)

    doc.build(story)
    print("written:", out)


if __name__ == "__main__":
    build()
