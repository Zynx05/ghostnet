"""
The backend developer's own viva sheet.

Written for somebody standing up and nervous, not for somebody studying at a
desk. Rules followed here:

    one idea per block
    nothing longer than three lines
    the thing to say out loud comes first, not last
    four pages, one job each

    python make_backend_pdf.py

Output: GhostNet Backend Developer Notes.pdf
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak,
)

INK = colors.HexColor("#0b0b0b")
MUTED = colors.HexColor("#444444")
FAINT = colors.HexColor("#8a8a8a")
PAPER = colors.HexColor("#f4efe4")
YELLOW = colors.HexColor("#ffdf3d")
LINE = colors.HexColor("#cccccc")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
W = PAGE_W - 2 * MARGIN

TITLE = ParagraphStyle("TITLE", fontName="Helvetica-Bold", fontSize=26, leading=28,
                       textColor=INK, spaceAfter=4)
KICKER = ParagraphStyle("KICKER", fontName="Courier-Bold", fontSize=9, leading=12,
                        textColor=FAINT, spaceAfter=16)
H = ParagraphStyle("H", fontName="Helvetica-Bold", fontSize=14, leading=17,
                   textColor=INK, spaceBefore=16, spaceAfter=7)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=11, leading=15.5,
                      textColor=INK, alignment=TA_LEFT)
SAY = ParagraphStyle("SAY", fontName="Helvetica", fontSize=12, leading=18,
                     textColor=INK)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=10, leading=14,
                       textColor=MUTED)
LABEL = ParagraphStyle("LABEL", fontName="Helvetica-Bold", fontSize=10, leading=14,
                       textColor=INK)
MONO = ParagraphStyle("MONO", fontName="Courier", fontSize=10, leading=14.5,
                      textColor=INK)
BIG = ParagraphStyle("BIG", fontName="Helvetica-Bold", fontSize=13, leading=17,
                     textColor=INK)

BOX = [
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("BOX", (0, 0), (-1, -1), 1.4, INK),
    ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]


def h(text):
    return Paragraph(text, H)


def facts(rows, first=34 * mm):
    """Label on the left, value on the right."""
    data = [[Paragraph(a, LABEL), Paragraph(b, SMALL)] for a, b in rows]
    t = Table(data, colWidths=[first, W - first], hAlign="LEFT")
    t.setStyle(TableStyle(BOX + [("BACKGROUND", (0, 0), (0, -1), PAPER),
                                 ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def panel(text, fill=YELLOW, style=SAY):
    t = Table([[Paragraph(text, style)]], colWidths=[W], hAlign="LEFT")
    t.setStyle(TableStyle(BOX + [("BACKGROUND", (0, 0), (-1, -1), fill),
                                 ("TOPPADDING", (0, 0), (-1, -1), 12),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                                 ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def steps(items):
    """Numbered, one line each, with a black number block."""
    data = []
    for i, text in enumerate(items, start=1):
        num = Paragraph('<font color="#ffffff"><b>%d</b></font>' % i, BIG)
        data.append([num, Paragraph(text, BODY)])
    t = Table(data, colWidths=[12 * mm, W - 12 * mm], hAlign="LEFT")
    t.setStyle(TableStyle(BOX + [
        ("BACKGROUND", (0, 0), (0, -1), INK),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def qa(pairs):
    data = [[Paragraph(q, LABEL), Paragraph(a, SMALL)] for q, a in pairs]
    t = Table(data, colWidths=[62 * mm, W - 62 * mm], hAlign="LEFT")
    t.setStyle(TableStyle(BOX + [("BACKGROUND", (0, 0), (0, -1), PAPER),
                                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                 ("TOPPADDING", (0, 0), (-1, -1), 8),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


def grid(rows, widths, header=True):
    data = [[Paragraph(c, LABEL if (header and i == 0) else SMALL) for c in row]
            for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = list(BOX) + [("VALIGN", (0, 0), (-1, -1), "TOP")]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), PAPER))
    t.setStyle(TableStyle(style))
    return t


# ═════════════════════════════════════════════════════════════════════════
# PAGE 1  ::  what to say
# ═════════════════════════════════════════════════════════════════════════

def page_one(s):
    s.append(Paragraph("Backend Developer", TITLE))
    s.append(Paragraph("UZAIR HUSSAIN SIDDIQUI  ::  B23110106078", KICKER))

    s.append(h("Say this first"))
    s.append(panel(
        "I built the API, and my algorithm is <b>Levenshtein edit distance</b>.<br/><br/>"
        "It counts the smallest number of letter changes needed to turn one text into "
        "another. I use it to catch people who copy an answer and rename a few words to "
        "hide it.<br/><br/>"
        "Time is <b>O(m times n)</b>. Space is <b>O(n)</b>."
    ))

    s.append(h("The five facts to memorise"))
    s.append(facts([
        ("Algorithm", "Levenshtein edit distance"),
        ("Method", "Dynamic programming, two rows at a time"),
        ("Time", "O(m times n)"),
        ("Space", "O(n)"),
        ("My files", "main.py and algorithms/levenshtein.py"),
    ]))

    s.append(h("What I built"))
    s.append(facts([
        ("The API", "32 endpoints. Every screen on the site calls them."),
        ("The rule", "Routes are thin. Check who is asking, call one module, "
                     "return JSON. No logic in main.py."),
        ("Why that matters", "All 14 tests run with no server and no database."),
        ("My algorithm", "Edit distance, and the copy check built on it."),
    ], first=40 * mm))


# ═════════════════════════════════════════════════════════════════════════
# PAGE 2  ::  the algorithm
# ═════════════════════════════════════════════════════════════════════════

def page_two(s):
    s.append(Paragraph("The algorithm", TITLE))
    s.append(Paragraph("EDIT DISTANCE  ::  ONE EXAMPLE, FOUR STEPS", KICKER))

    s.append(h("The question it answers"))
    s.append(Paragraph(
        "How many single letter changes turn one text into another? "
        "You may insert a letter, delete a letter, or replace a letter.", BODY))

    s.append(h("The example everybody asks for"))
    s.append(panel(
        '<font face="Courier" size="13"><b>kitten &nbsp;to&nbsp; sitting</b></font><br/><br/>'
        "1. &nbsp;replace <b>k</b> with <b>s</b><br/>"
        "2. &nbsp;replace <b>e</b> with <b>i</b><br/>"
        "3. &nbsp;add <b>g</b> at the end<br/><br/>"
        "<b>Distance = 3.</b> &nbsp;There is a test that checks exactly this.",
        fill=PAPER, style=BODY))

    s.append(h("How the code does it"))
    s.append(steps([
        "Make a table. Each cell holds the distance between the start of one "
        "text and the start of the other.",
        "Fill each cell with the smallest of three options: insert, delete, "
        "replace. Replace is free if the letters already match.",
        "The answer is the bottom right cell.",
        "Only keep two rows, never the whole table. That is why space is O(n).",
    ]))

    s.append(h("Turning distance into a score"))
    s.append(Paragraph(
        '<font face="Courier"><b>score = 1 &minus; (distance / length of the longer text)</b></font>',
        BODY))
    s.append(Spacer(1, 5))
    s.append(Paragraph("Same text gives 1. Nothing in common gives 0.", SMALL))


# ═════════════════════════════════════════════════════════════════════════
# PAGE 3  ::  where it is used
# ═════════════════════════════════════════════════════════════════════════

def page_three(s):
    s.append(Paragraph("Where I use it", TITLE))
    s.append(Paragraph("CATCHING THE COPY THAT CHANGED A FEW WORDS", KICKER))

    s.append(h("The problem"))
    s.append(Paragraph(
        "Rabin Karp finds copied text by matching exact chunks. "
        "Rename one variable and the chunk no longer matches.", BODY))

    s.append(h("A real case from our demo data"))
    s.append(Paragraph(
        "Somebody copied the winning answer and renamed "
        '<font face="Courier">items</font> to <font face="Courier">cart_items</font>, '
        'and <font face="Courier">total</font> to <font face="Courier">sum</font>.', BODY))
    s.append(Spacer(1, 8))
    s.append(grid([
        ["Checker", "Said", "Verdict"],
        ["Rabin Karp, exact chunks", "61 percent", "Missed most of it"],
        ["My edit distance", "83 percent", "Caught it"],
    ], [62 * mm, 32 * mm, W - 94 * mm]))

    s.append(h("So the Copied score is the higher of the two"))
    s.append(panel(
        '<font face="Courier" size="12"><b>Copied = max(Rabin Karp, edit distance)</b></font>'
    ))

    s.append(h("Three things I decided, and why"))
    s.append(facts([
        ("Rabin Karp runs first",
         "Mine is slow. It only runs on pairs the fast check already flagged."),
        ("A floor of 0.6",
         "Any two pieces of code share letters and score about 0.25. "
         "Below the floor is noise, so it counts as zero."),
        ("Only look backwards",
         "Each entry is compared only with entries sent before it. "
         "The first person to submit can never be blamed for being copied."),
    ], first=48 * mm))

    s.append(h("What that looks like on screen"))
    s.append(grid([
        ["Ghost", "Copied", "Final", "Why"],
        ["Quiet Falcon", "0.00", "0.582", "Original, submitted first"],
        ["Pale Otter", "0.13", "0.447", "Was copied from, barely touched"],
        ["Calm Lynx", "0.00", "0.358", "Original, but no code"],
        ["Swift Heron", "0.88", "0.060", "Copied from Pale Otter"],
    ], [34 * mm, 20 * mm, 20 * mm, W - 74 * mm]))


# ═════════════════════════════════════════════════════════════════════════
# PAGE 4  ::  questions and the demo
# ═════════════════════════════════════════════════════════════════════════

def page_four(s):
    s.append(Paragraph("Questions", TITLE))
    s.append(Paragraph("SHORT ANSWERS. SAY THEM AND STOP.", KICKER))

    s.append(qa([
        ("Show kitten to sitting.",
         "Replace k with s. Replace e with i. Add g. Three."),
        ("Why dynamic programming?",
         "Recursion redoes the same work over and over. A table does each piece once."),
        ("Why only two rows?",
         "Each row only needs the one above it. The rest are never read again."),
        ("Why not use your algorithm alone?",
         "It is slow, O(m times n) per pair. The fast check narrows it down first."),
        ("Why the 0.6 floor?",
         "Unrelated code still scores about 0.25 just from shared letters. That is noise."),
        ("Does the original author get punished?",
         "No. Entries are only compared with earlier ones, so whoever submitted first "
         "scores zero."),
        ("Why is your API thin?",
         "No logic in it, so all 14 tests run without a server or a database."),
        ("Two people submit at once?",
         "Each gets its own connection and transaction. The database rejects duplicates."),
        ("Why FastAPI?",
         "It writes the API documentation itself from the type hints."),
    ]))

    s.append(h("What to open, in this order"))
    s.append(steps([
        "The /docs page. Every endpoint, generated automatically.",
        "Log in as the company, open the cart challenge, press Rank entries.",
        "Point at the Copied column: 0.88 for the copier, 0.13 for the original.",
        "Open ranker.py and show the eight lines that combine both checks.",
    ]))

    s.append(h("If they push on the Quality column"))
    s.append(panel(
        "It is the weakest of the four measures and I know it. Comparing an answer to the "
        "question mostly tells you if it reuses the same words, and Relevance already does "
        "that better. It is the lowest weighted of the three positive measures.",
        fill=PAPER, style=SMALL))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.8)
    canvas.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    canvas.setFont("Courier", 7.5)
    canvas.setFillColor(FAINT)
    canvas.drawString(MARGIN, 9 * mm, "GHOSTNET  ::  BACKEND  ::  UZAIR SIDDIQUI")
    canvas.drawRightString(PAGE_W - MARGIN, 9 * mm, "%d OF 4" % doc.page)
    canvas.restoreState()


def build():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "GhostNet Backend Developer Notes.pdf")
    doc = BaseDocTemplate(out, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=18 * mm, bottomMargin=18 * mm,
                          title="GhostNet Backend Developer Notes",
                          author="Uzair Hussain Siddiqui")
    doc.addPageTemplates([PageTemplate(
        id="page",
        frames=[Frame(MARGIN, 18 * mm, W, PAGE_H - 36 * mm, id="body")],
        onPage=footer,
    )])

    story = []
    for i, page in enumerate([page_one, page_two, page_three, page_four]):
        if i:
            story.append(PageBreak())
        page(story)

    doc.build(story)
    print("written:", out)


if __name__ == "__main__":
    build()
