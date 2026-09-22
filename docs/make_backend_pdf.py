"""
The backend developer's own viva sheet.

Separate from the team sheet on purpose. The team sheet gives every member one
page. This is the long version for one person, with the endpoint table, the
two stage copy check worked through, and every question with an answer.

    pip install reportlab
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
    KeepTogether,
)

INK = colors.HexColor("#0b0b0b")
MUTED = colors.HexColor("#4a4a4a")
FAINT = colors.HexColor("#7a7a7a")
WELL = colors.HexColor("#f4efe4")
YELLOW = colors.HexColor("#ffdf3d")
LINE = colors.HexColor("#d4d4d0")

PAGE_W, PAGE_H = A4
MARGIN = 17 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=20, leading=23,
                    textColor=INK, spaceAfter=2)
SUB = ParagraphStyle("SUB", fontName="Courier-Bold", fontSize=8.5, leading=12,
                     textColor=FAINT, spaceAfter=10)
H2 = ParagraphStyle("H2", fontName="Courier-Bold", fontSize=8.5, leading=11,
                    textColor=INK, spaceBefore=13, spaceAfter=5)
H3 = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=10, leading=13,
                    textColor=INK, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=9.6, leading=13.4,
                      textColor=INK, alignment=TA_LEFT)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=8.8, leading=12.2,
                       textColor=MUTED)
KEY = ParagraphStyle("KEY", fontName="Courier-Bold", fontSize=8, leading=11,
                     textColor=INK)
QUESTION = ParagraphStyle("Q", fontName="Helvetica-Bold", fontSize=8.8,
                          leading=12.2, textColor=INK)
MONO = ParagraphStyle("MONO", fontName="Courier", fontSize=8.2, leading=11.4,
                      textColor=INK)
SAY = ParagraphStyle("SAY", fontName="Helvetica-Oblique", fontSize=9.6,
                     leading=14, textColor=INK)

GRID = [
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOX", (0, 0), (-1, -1), 1.1, INK),
    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]


def heading(text):
    return Paragraph(text, H2)


def table(rows, widths, shade_first=True, left_style=KEY, right_style=SMALL):
    data = [[Paragraph(str(a), left_style)] + [Paragraph(str(c), right_style) for c in rest]
            for a, *rest in rows]
    t = Table(data, colWidths=widths, hAlign="LEFT")
    style = list(GRID)
    if shade_first:
        style.append(("BACKGROUND", (0, 0), (0, -1), WELL))
    t.setStyle(TableStyle(style))
    return t


def note(text, fill=WELL):
    t = Table([[Paragraph(text, SMALL)]], colWidths=[CONTENT_W], hAlign="LEFT")
    t.setStyle(TableStyle(GRID + [("BACKGROUND", (0, 0), (-1, -1), fill),
                                  ("TOPPADDING", (0, 0), (-1, -1), 7),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def bullets(items, numbered=False):
    out = []
    for i, text in enumerate(items, start=1):
        marker = ("%d.&nbsp;&nbsp;" % i) if numbered else "&bull;&nbsp;&nbsp;"
        out.append(Paragraph(marker + text, BODY))
        out.append(Spacer(1, 2.5))
    return out


# ── Content ──────────────────────────────────────────────────────────────

ENDPOINTS = [
    ("Health", "GET /health"),
    ("Accounts", "POST /auth/signup &nbsp; POST /auth/login &nbsp; GET /auth/session &nbsp; POST /auth/logout"),
    ("My Ghost", "GET /me &nbsp; PATCH /me"),
    ("Challenges", "GET /challenges &nbsp; GET /challenges/{id} &nbsp; POST /challenges &nbsp; "
                   "GET /company/challenges &nbsp; POST /company/topup"),
    ("Entries", "GET /challenges/{id}/submissions &nbsp; POST /challenges/{id}/submissions"),
    ("Ranking", "POST /challenges/{id}/rank &nbsp; GET /challenges/{id}/results &nbsp; "
                "POST /challenges/{id}/reveal &nbsp; GET /challenges/{id}/unmasks &nbsp; "
                "POST /challenges/{id}/unmask"),
    ("Practice", "GET /practice &nbsp; POST /challenges/{id}/practice"),
    ("Messages", "GET /inbox &nbsp; POST /inbox/{id}/reply &nbsp; GET /challenges/{id}/threads &nbsp; "
                 "POST /challenges/{id}/messages"),
    ("Questions", "GET /challenges/{id}/questions &nbsp; POST /challenges/{id}/questions &nbsp; "
                  "POST /questions/{id}/answer"),
    ("Other", "GET /leaderboard &nbsp; GET /chain &nbsp; POST /match &nbsp; GET /schedule"),
]

FUNCTIONS = [
    ("edit_distance(a, b)", "The dynamic programming table, kept to two rows."),
    ("similarity(a, b)", "1 minus distance divided by the longer length. This is the Quality column."),
    ("copy_similarity(a, b)", "The same score, but zero below a floor of 0.6. This feeds the Copied column."),
]

QA = [
    ("Show kitten turning into sitting.",
     "Replace k with s. Replace e with i. Add g at the end. Three changes. There is a test "
     "that checks this exact example."),
    ("Why dynamic programming and not simple recursion?",
     "Recursion solves the same small problem again and again, which is exponential time. "
     "The table solves each small problem once, which gives m times n."),
    ("Why keep only two rows?",
     "Row i only needs row i minus 1. Once a row has been used it is never read again, so "
     "the older rows are thrown away. Space goes from O(m x n) down to O(n)."),
    ("Why run Rabin Karp first and edit distance second?",
     "Rabin Karp is linear in the length of the text. Edit distance is m times n. With fifty "
     "entries there are over a thousand pairs, and edit distance on all of them would be the "
     "slowest part of the whole ranking. Running it only on the pairs Rabin Karp already "
     "flagged keeps the cost down and still catches the reworded copy."),
    ("Why is there a floor of 0.6 on the copy score?",
     "Any two pieces of code share letters. def, return, colons, spaces. Two completely "
     "unrelated entries still come out about 0.25 similar. Below the floor that is noise and "
     "counts as zero. Above it, the two texts really are the same text with edits."),
    ("What if the original author gets flagged too?",
     "They do not. Each entry is compared only against entries that arrived before it. "
     "Whoever submitted first cannot have copied somebody who came later, so their Copied "
     "score stays at zero and the copier takes the hit. Before this fix both were punished."),
    ("Why is your API so thin?",
     "Each route checks who is asking, calls one module, and returns JSON. Because there is "
     "no logic in main.py, all fourteen tests run with no server and no database."),
    ("What happens if two people submit at the same moment?",
     "Each request takes its own connection from the pool and its own transaction, so they "
     "do not clash. The submissions table has a unique rule on challenge and ghost, so a "
     "duplicate is rejected by the database rather than silently accepted."),
    ("Why FastAPI?",
     "It writes the API documentation from the type hints, so the /docs page is never out of "
     "date. Pydantic rejects a malformed request with a clear message before any of our code "
     "runs."),
    ("What is the difference between reveal and unmask?",
     "Reveal closes the challenge and names the winning ghost. It is free. Unmask shows the "
     "real person behind a ghost, costs the company Rs 1,500, and is charged once per "
     "candidate per challenge. A candidate who never gave a real name stays masked and "
     "nothing is charged."),
]

SHOW = [
    "Open the API documentation at /docs. Every endpoint, generated from the type hints, and "
    "the examiner can call any of them from that page.",
    "Log in as northwind@demo.pk, open Fix the cart total bug, press Rank entries. Point at "
    "the Copied column: 0.88, 0.13, 0.00, 0.00.",
    "Open ranker.py at the two stage block. Eight lines, and the comments name both members.",
    "Open tests/test_algorithms.py and show the paraphrase test and the arrival order test.",
]

SAY_IT = (
    "I built the API and the second stage of the plagiarism check. The API has thirty two "
    "endpoints and every screen on the frontend calls them. I used FastAPI because it "
    "generates the documentation from the type hints, so the docs page is always current. "
    "My algorithm is Levenshtein edit distance. It is the smallest number of letter "
    "insertions, deletions or substitutions needed to turn one text into another, solved "
    "with a dynamic programming table that I keep to two rows, so time is O(m times n) and "
    "space is O(n). It does two jobs. It scores how close an entry is to the brief, and it "
    "catches copies that Rabin Karp misses, because an exact hash breaks the moment somebody "
    "renames a variable while edit distance still sees eighty three percent of the letters "
    "unchanged. It is the slowest algorithm in the project, so it only runs on pairs the "
    "fast check already flagged, and only against entries that arrived earlier, so the "
    "original author is never blamed for being copied."
)


def build_story():
    s = []

    s.append(Paragraph("Backend Developer", H1))
    s.append(Paragraph("UZAIR HUSSAIN SIDDIQUI  ::  B23110106078  ::  GHOSTNET", SUB))

    s.append(table([
        ("Algorithm", "Levenshtein edit distance, dynamic programming"),
        ("Files", "backend/main.py &nbsp; backend/algorithms/levenshtein.py"),
        ("Complexity", "O(m x n) time, O(n) space"),
        ("Weight", "Quality is 25 percent of the score. Copied multiplies the whole score"),
    ], [26 * mm, CONTENT_W - 26 * mm]))

    s.append(heading("WHAT I OWN"))
    s.append(Paragraph(
        "Two things. The whole FastAPI server, which every screen on the frontend talks to. "
        "And edit distance, which does two jobs in the ranking: it produces the Quality "
        "column, and it is the second stage of the Copied check, catching copies that "
        "changed a few words to slip past an exact match.", BODY))

    s.append(heading("THE API  ::  32 ENDPOINTS, ABOUT 700 LINES"))
    s.append(Paragraph(
        "The rule is that main.py is thin. Every route does three things: check who is "
        "asking, call one module, return JSON. No logic lives in it. That is why all "
        "fourteen tests run with no server and no database.", BODY))
    s.append(Spacer(1, 7))
    s.append(table(ENDPOINTS, [26 * mm, CONTENT_W - 26 * mm], right_style=MONO))

    s.append(heading("WHO CAN CALL WHAT"))
    s.extend(bullets([
        "The browser sends one token. The server reads the role from it.",
        "A candidate cannot post a challenge. A company cannot enter one. Both get a 403.",
        "A company can only rank, close, message or unmask a challenge it posted itself.",
        "Reveal closes a challenge and names the winning ghost, and is free. Unmask shows "
        "the real person and costs Rs 1,500, charged once per candidate.",
    ]))

    s.append(heading("THE OTHER INFRASTRUCTURE"))
    s.extend(bullets([
        "<b>Pydantic models</b> define the exact shape of every request body, so a malformed "
        "request is rejected with a clear message before any of our code runs.",
        "<b>Lifespan handler</b> opens the database pool once when the server starts and "
        "closes it once when it stops. An earlier version opened it per request, which threw "
        "away the whole point of having a pool.",
        "<b>CORS</b> lets the frontend on one address call the API on another. The allowed "
        "address comes from an environment variable, so the deployed URL is never written "
        "into the code.",
    ]))

    s.append(heading("THE ALGORITHM  ::  HOW IT WORKS"))
    s.append(Paragraph(
        "<b>The question it answers.</b> What is the smallest number of single letter changes "
        "that turn text A into text B? Three moves are allowed: insert a letter, delete a "
        "letter, replace a letter.", BODY))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "<b>The textbook example.</b> kitten to sitting. Replace k with s. Replace e with i. "
        "Add g at the end. Distance is three, and there is a test asserting exactly that.", BODY))
    s.append(Spacer(1, 7))
    s.extend(bullets([
        "Build a table where cell i, j holds the distance between the first i letters of one "
        "text and the first j letters of the other.",
        "Fill each cell with the smallest of three choices: insert, delete, or replace. "
        "Replace costs nothing when the two letters already match.",
        "The answer sits in the bottom right cell.",
        "Row i only depends on row i minus 1, so keep two rows and throw the rest away.",
        "Turn the distance into a score: one minus the distance divided by the longer text. "
        "Same text gives 1, nothing in common gives 0.",
    ], numbered=True))

    s.append(heading("THE THREE FUNCTIONS IN levenshtein.py"))
    s.append(table(FUNCTIONS, [42 * mm, CONTENT_W - 42 * mm], left_style=MONO))

    s.append(heading("WHERE IT RUNS  ::  THE TWO STAGE COPY CHECK"))
    s.append(Paragraph(
        "This is the part to spend time on. It lives in ranker.py and it is the reason the "
        "algorithm is on my page.", BODY))

    s.append(Paragraph("The problem", H3))
    s.append(Paragraph(
        "Rabin Karp finds copied text by hashing exact twelve character windows. Rename one "
        "variable and every window touching it misses. Somebody copied the winning cart "
        "answer and renamed items to cart_items and total to sum, then reworded two comments. "
        "The exact check fell from 100 percent to 61 percent. Any human would still call it a "
        "copy.", BODY))

    s.append(Paragraph("The fix", H3))
    s.append(Paragraph(
        "Edit distance sees that 83 percent of the letters never changed. So the Copied score "
        "is the higher of the two.", BODY))
    s.append(Spacer(1, 6))
    s.append(note(
        "<font face='Courier'>exact&nbsp;&nbsp;= Rabin Karp overlap<br/>"
        "fuzzy&nbsp;&nbsp;= edit distance similarity, only if exact &gt;= 0.10, "
        "only if the result &gt;= 0.6<br/>"
        "<b>Copied = max(exact, fuzzy)</b></font>", fill=YELLOW))

    s.append(Paragraph("Three design decisions, and why", H3))
    s.extend(bullets([
        "<b>Rabin Karp runs first, on every pair.</b> It is O(n) per pair. Edit distance is "
        "O(m x n) per pair, and with fifty entries that is over a thousand pairs, each around "
        "a quarter of a million cell operations. It would be the slowest part of the whole "
        "ranking. So it only runs where Rabin Karp already found something, meaning ten "
        "percent overlap or more. A fast rough filter, then a careful check on the survivors. "
        "Spam filters and virus scanners work the same way.",
        "<b>A floor of 0.6.</b> Any two pieces of Python share def, return, colons and "
        "spaces, so two completely unrelated entries still come out about 0.25 similar. Below "
        "the floor that is noise and counts as zero. Above it, the two texts really are the "
        "same text with edits.",
        "<b>Only look backwards.</b> Each entry is compared only against entries submitted "
        "before it. Whoever submitted first cannot have copied somebody who came later, so "
        "the original author keeps a Copied score of zero and the copier takes the hit.",
    ], numbered=True))

    s.append(heading("WHAT THAT LOOKS LIKE ON THE DEMO CHALLENGE"))
    s.append(table([
        ("<b>Ghost</b>", "<b>Copied</b>", "<b>Final</b>", "<b>Why</b>"),
        ("Quiet Falcon", "0.00", "0.582", "Original work, submitted first"),
        ("Pale Otter", "0.13", "0.447", "Was copied from, so barely touched"),
        ("Calm Lynx", "0.00", "0.358", "Original, but prose instead of code"),
        ("Swift Heron", "0.88", "0.060", "Lifted a block from Pale Otter"),
    ], [34 * mm, 20 * mm, 20 * mm, CONTENT_W - 74 * mm], shade_first=False,
        left_style=SMALL))

    s.append(heading("COMPLEXITY"))
    s.append(table([
        ("Time", "O(m x n). Every cell is filled once and there are m times n of them."),
        ("Space", "O(n). Only two rows exist at any moment."),
        ("Measured", "13, 51, 218 and 967 milliseconds at 100, 200, 400 and 800 characters. "
                     "Time roughly quadruples when the input doubles, which is the signature "
                     "of O(m x n)."),
    ], [24 * mm, CONTENT_W - 24 * mm]))
    s.append(Spacer(1, 6))
    s.append(Paragraph(
        "This is the slowest algorithm in the project. That is exactly why the gate in front "
        "of it exists. If GhostNet ever had to handle real traffic, the first move would be "
        "to tighten the gate, not to replace the algorithm.", SMALL))

    s.append(heading("QUESTIONS TO EXPECT"))
    rows = [(q, a) for q, a in QA]
    t = Table([[Paragraph(q, QUESTION), Paragraph(a, SMALL)] for q, a in rows],
              colWidths=[52 * mm, CONTENT_W - 52 * mm], hAlign="LEFT")
    t.setStyle(TableStyle(GRID + [("BACKGROUND", (0, 0), (0, -1), WELL),
                                  ("TOPPADDING", (0, 0), (-1, -1), 5),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    s.append(t)

    s.append(heading("SHOW THIS ON SCREEN"))
    s.extend(bullets(SHOW, numbered=True))

    s.append(heading("SAY THIS, MORE OR LESS"))
    s.append(note(SAY_IT))

    s.append(heading("ONE THING TO BE HONEST ABOUT"))
    s.append(Paragraph(
        "The Quality column, where edit distance is compared against the brief rather than "
        "against another entry, is the weakest of the four measures. Comparing an answer to "
        "the question mostly tells you whether it reuses the same words, and Relevance "
        "already asks that with a better method. It is weighted lowest of the three positive "
        "measures at 25 percent, and Relevance and Structure carry the real load. Saying that "
        "plainly is stronger than defending it.", BODY))

    return s


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.7)
    canvas.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    canvas.setFont("Courier", 7)
    canvas.setFillColor(FAINT)
    canvas.drawString(MARGIN, 9 * mm, "GHOSTNET  ::  BACKEND DEVELOPER  ::  UZAIR SIDDIQUI")
    canvas.drawRightString(PAGE_W - MARGIN, 9 * mm, "PAGE %d" % doc.page)
    canvas.restoreState()


def build():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "GhostNet Backend Developer Notes.pdf")
    doc = BaseDocTemplate(out, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=16 * mm, bottomMargin=18 * mm,
                          title="GhostNet Backend Developer Notes",
                          author="Uzair Hussain Siddiqui")
    frame = Frame(MARGIN, 18 * mm, CONTENT_W, PAGE_H - 34 * mm, id="body")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=footer)])
    doc.build(build_story())
    print("written:", out)


if __name__ == "__main__":
    build()
