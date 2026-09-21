"""
GhostNet API.
Member 2 owns this file. It stays thin on purpose: every route validates the
input, calls one module, and returns JSON. No logic lives here.

Run it with:  uvicorn main:app --reload

Who is who
    A person is a ghost. The browser sends X-Ghost-Token and that is the
    whole login. There are no passwords and no email addresses.
    A company is whoever is looking at a challenge page. This is an MVP, so
    the company side has no login either.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import ghosts
from algorithms import ranker, merkle, gale_shapley, scheduling


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The connection pool is opened once when the server starts and closed when
    it stops. Opening a pool per request would throw away the point of a pool.
    """
    db.init()
    yield
    db.pool.close()


app = FastAPI(title="GhostNet API", version="2.0", lifespan=lifespan)

# A browser blocks a page on one address from calling an API on another unless
# the API says that address is allowed. Locally that is port 3000. Once the
# frontend is deployed its address is added through ALLOWED_ORIGINS, which is a
# comma separated list, so the deployed URL never has to be hardcoded here.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request shapes ───────────────────────────────────────────────────────

class NewChallenge(BaseModel):
    title: str
    company: str
    statement: str
    reward: str = ""
    start_day: int = 0
    end_day: int = 7


class Content(BaseModel):
    content: str


class NameUpdate(BaseModel):
    real_name: str


class NewMessage(BaseModel):
    ghost_id: str
    kind: str
    body: str = ""


class NewQuestion(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str


class MatchInput(BaseModel):
    candidates: dict
    companies: dict


# ── Helpers ──────────────────────────────────────────────────────────────

def me(token):
    """The ghost behind this request, or a 401 if the token is missing or wrong."""
    if not token:
        raise HTTPException(401, "no ghost token")
    ghost = ghosts.by_token(token)
    if not ghost:
        raise HTTPException(401, "unknown ghost")
    return ghost


def challenge_or_404(challenge_id):
    rows = db.query("SELECT * FROM challenges WHERE id = %s", (challenge_id,))
    if not rows:
        raise HTTPException(404, "challenge not found")
    return rows[0]


def with_names(rows):
    """Attach the display name to every row that has a ghost_id."""
    names = ghosts.names_for(sorted({r["ghost_id"] for r in rows}))
    for r in rows:
        r["ghost_name"] = names.get(r["ghost_id"], r["ghost_id"])
    return rows


# ── Health ───────────────────────────────────────────────────────────────

# Member 6 owns this one. CI and the hosting platform poll it.
@app.get("/health")
def health():
    return {"status": "ok", "service": "ghostnet"}


# ── Ghosts ───────────────────────────────────────────────────────────────

@app.post("/ghosts")
def new_ghost():
    """A browser calls this once and keeps the token."""
    return ghosts.create()


@app.get("/me")
def my_page(x_ghost_token: str = Header(default="")):
    """Everything on the My Ghost page in one call."""
    g = me(x_ghost_token)

    entries = with_names(db.query(
        "SELECT s.challenge_id, c.title, c.company, c.revealed, s.ghost_id,"
        " r.rank, r.final_score"
        " FROM submissions s"
        " JOIN challenges c ON c.id = s.challenge_id"
        " LEFT JOIN results r ON r.challenge_id = s.challenge_id"
        "   AND r.ghost_id = s.ghost_id"
        " WHERE s.ghost_id = %s ORDER BY s.id DESC",
        (g["ghost_id"],),
    ))

    practice = db.query(
        "SELECT p.challenge_id, c.title, p.would_rank, p.out_of, p.final_score"
        " FROM practice p JOIN challenges c ON c.id = p.challenge_id"
        " WHERE p.ghost_id = %s ORDER BY p.id DESC",
        (g["ghost_id"],),
    )

    wins = [e for e in entries if e["rank"] == 1 and e["revealed"]]
    leaves = [w["ghost_id"] + " won " + w["title"] + " at " + w["company"] for w in wins]

    return {
        "ghost": g,
        "entries": entries,
        "practice": practice,
        "proofs": [
            {**w, "seal": block["hash"]}
            for w, block in zip(wins, merkle.chain(leaves))
        ],
        "check_code": merkle.root(leaves) if leaves else "",
    }


@app.patch("/me")
def set_name(body: NameUpdate, x_ghost_token: str = Header(default="")):
    """The real name is optional and is only ever shown if the ghost wins."""
    g = me(x_ghost_token)
    db.execute(
        "UPDATE ghosts SET real_name = %s WHERE ghost_id = %s",
        (body.real_name.strip(), g["ghost_id"]),
    )
    return {"ok": True}


# ── Challenges ───────────────────────────────────────────────────────────

@app.get("/challenges")
def list_challenges():
    rows = db.query(
        "SELECT c.*, COUNT(s.id) AS entries"
        " FROM challenges c LEFT JOIN submissions s ON s.challenge_id = c.id"
        " WHERE NOT c.practice"
        " GROUP BY c.id ORDER BY c.id DESC"
    )
    return rows


@app.get("/challenges/{challenge_id}")
def get_challenge(challenge_id: int):
    return challenge_or_404(challenge_id)


@app.post("/challenges")
def create_challenge(body: NewChallenge):
    if not body.title.strip() or not body.statement.strip():
        raise HTTPException(400, "a title and a problem are both needed")
    new_id = db.execute(
        "INSERT INTO challenges (title, company, statement, reward, start_day, end_day)"
        " VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (body.title, body.company, body.statement, body.reward,
         body.start_day, body.end_day),
    )
    return {"id": new_id}


@app.get("/challenges/{challenge_id}/submissions")
def list_submissions(challenge_id: int):
    """
    Note the column list. Nothing here joins to the ghosts table for a real
    name, so anonymity is not a rule someone has to remember, it is simply
    absent from the query.
    """
    return with_names(db.query(
        "SELECT id, ghost_id, content FROM submissions WHERE challenge_id = %s"
        " ORDER BY id",
        (challenge_id,),
    ))


@app.post("/challenges/{challenge_id}/submissions")
def add_submission(challenge_id: int, body: Content,
                   x_ghost_token: str = Header(default="")):
    g = me(x_ghost_token)
    c = challenge_or_404(challenge_id)
    if c["revealed"]:
        raise HTTPException(400, "this challenge is closed. Try it under Practice")
    if not body.content.strip():
        raise HTTPException(400, "the entry is empty")

    already = db.query(
        "SELECT 1 FROM submissions WHERE challenge_id = %s AND ghost_id = %s",
        (challenge_id, g["ghost_id"]),
    )
    if already:
        raise HTTPException(400, "you already entered this one")

    db.execute(
        "INSERT INTO submissions (challenge_id, ghost_id, content) VALUES (%s, %s, %s)",
        (challenge_id, g["ghost_id"], body.content),
    )
    return {"ghost_id": g["ghost_id"], "ghost_name": g["name"]}


# ── Ranking and reveal ───────────────────────────────────────────────────

@app.post("/challenges/{challenge_id}/rank")
def rank(challenge_id: int):
    """The demo button. Every scoring algorithm runs inside this one call."""
    challenge = challenge_or_404(challenge_id)
    subs = db.query(
        "SELECT ghost_id, content FROM submissions WHERE challenge_id = %s",
        (challenge_id,),
    )
    if not subs:
        raise HTTPException(400, "nothing has been entered yet")

    rows = ranker.score_all(challenge["statement"], subs)

    db.execute("DELETE FROM results WHERE challenge_id = %s", (challenge_id,))
    for r in rows:
        db.execute(
            "INSERT INTO results (challenge_id, ghost_id, relevance, quality,"
            " structure, cyclomatic, plagiarism, longest_copied, final_score, rank)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (challenge_id, r["ghost_id"], r["relevance"], r["quality"],
             r["structure"], r["cyclomatic"], r["plagiarism"],
             r["longest_copied"], r["final_score"], r["rank"]),
        )
    return {"weights": ranker.WEIGHTS, "results": with_names(rows)}


@app.get("/challenges/{challenge_id}/results")
def get_results(challenge_id: int):
    return with_names(db.query(
        "SELECT * FROM results WHERE challenge_id = %s ORDER BY rank",
        (challenge_id,),
    ))


@app.post("/challenges/{challenge_id}/reveal")
def reveal(challenge_id: int):
    """
    The winner is unmasked, if they chose to be, and the win is sealed.
    The Merkle proof returned here lets anyone check the win on their own.
    """
    results = get_results(challenge_id)
    if not results:
        raise HTTPException(400, "run the ranking first")

    winner = results[0]
    # The one query in the whole codebase that reads a real name.
    row = db.query(
        "SELECT real_name FROM ghosts WHERE ghost_id = %s", (winner["ghost_id"],)
    )
    real_name = row[0]["real_name"] if row else ""
    db.execute("UPDATE challenges SET revealed = TRUE WHERE id = %s", (challenge_id,))

    leaves = [r["ghost_id"] + ":" + str(r["final_score"]) for r in results]
    return {
        "winner": winner,
        "real_name": real_name,
        "masked": real_name == "",
        "merkle_root": merkle.root(leaves),
        "leaf": leaves[0],
        "proof": merkle.proof_for(leaves, 0),
        "leaf_count": len(leaves),
    }


# ── Practice ─────────────────────────────────────────────────────────────

@app.get("/practice")
def practice_list():
    """Closed challenges plus the warm ups. Anything you can try without stakes."""
    return db.query(
        "SELECT c.*, COUNT(s.id) AS entries"
        " FROM challenges c LEFT JOIN submissions s ON s.challenge_id = c.id"
        " WHERE c.revealed OR c.practice"
        " GROUP BY c.id ORDER BY c.practice DESC, c.id DESC"
    )


@app.post("/challenges/{challenge_id}/practice")
def practice_attempt(challenge_id: int, body: Content,
                     x_ghost_token: str = Header(default="")):
    """
    Score this entry against the real ones and say where it would have landed.
    Nothing is written to results, so the real ranking is untouched.
    """
    g = me(x_ghost_token)
    c = challenge_or_404(challenge_id)
    if not (c["revealed"] or c["practice"]):
        raise HTTPException(400, "this one is still open. Enter it for real")
    if not body.content.strip():
        raise HTTPException(400, "the entry is empty")

    subs = db.query(
        "SELECT ghost_id, content FROM submissions WHERE challenge_id = %s",
        (challenge_id,),
    )
    subs.append({"ghost_id": "__you__", "content": body.content})
    rows = ranker.score_all(c["statement"], subs)
    mine = next(r for r in rows if r["ghost_id"] == "__you__")

    db.execute(
        "INSERT INTO practice (challenge_id, ghost_id, would_rank, out_of, final_score)"
        " VALUES (%s, %s, %s, %s, %s)",
        (challenge_id, g["ghost_id"], mine["rank"], len(rows), mine["final_score"]),
    )
    return {"would_rank": mine["rank"], "out_of": len(rows), "scores": mine}


# ── Inbox, taps, whispers ────────────────────────────────────────────────

@app.get("/inbox")
def inbox(x_ghost_token: str = Header(default="")):
    g = me(x_ghost_token)
    return db.query(
        "SELECT m.id, m.kind, m.body, m.created_at, m.challenge_id,"
        " c.title, c.company"
        " FROM messages m JOIN challenges c ON c.id = m.challenge_id"
        " WHERE m.ghost_id = %s ORDER BY m.id DESC",
        (g["ghost_id"],),
    )


@app.post("/challenges/{challenge_id}/messages")
def send_message(challenge_id: int, body: NewMessage):
    """
    A company reaches a ghost. A tap says we would like to talk. A whisper is
    one line of feedback. Either way the ghost decides what happens next.
    """
    challenge_or_404(challenge_id)
    if body.kind not in ("tap", "whisper"):
        raise HTTPException(400, "kind must be tap or whisper")
    entered = db.query(
        "SELECT 1 FROM submissions WHERE challenge_id = %s AND ghost_id = %s",
        (challenge_id, body.ghost_id),
    )
    if not entered:
        raise HTTPException(400, "that ghost did not enter this challenge")

    text = body.body.strip() or (
        "We would like to talk. Reply here if you want to unmask."
        if body.kind == "tap" else ""
    )
    if not text:
        raise HTTPException(400, "a whisper needs some words")

    db.execute(
        "INSERT INTO messages (ghost_id, challenge_id, kind, body) VALUES (%s, %s, %s, %s)",
        (body.ghost_id, challenge_id, body.kind, text),
    )
    return {"ok": True}


# ── Questions on a challenge ─────────────────────────────────────────────

@app.get("/challenges/{challenge_id}/questions")
def list_questions(challenge_id: int):
    return with_names(db.query(
        "SELECT id, ghost_id, question, answer FROM questions"
        " WHERE challenge_id = %s ORDER BY id",
        (challenge_id,),
    ))


@app.post("/challenges/{challenge_id}/questions")
def ask(challenge_id: int, body: NewQuestion, x_ghost_token: str = Header(default="")):
    g = me(x_ghost_token)
    challenge_or_404(challenge_id)
    if not body.question.strip():
        raise HTTPException(400, "ask something")
    db.execute(
        "INSERT INTO questions (challenge_id, ghost_id, question) VALUES (%s, %s, %s)",
        (challenge_id, g["ghost_id"], body.question.strip()),
    )
    return {"ok": True}


@app.post("/questions/{question_id}/answer")
def answer(question_id: int, body: Answer):
    """The company answers. Everyone sees it, and the asker also gets it in their inbox."""
    rows = db.query("SELECT * FROM questions WHERE id = %s", (question_id,))
    if not rows:
        raise HTTPException(404, "question not found")
    q = rows[0]
    db.execute(
        "UPDATE questions SET answer = %s WHERE id = %s",
        (body.answer.strip(), question_id),
    )
    db.execute(
        "INSERT INTO messages (ghost_id, challenge_id, kind, body) VALUES (%s, %s, %s, %s)",
        (q["ghost_id"], q["challenge_id"], "answer",
         "You asked: " + q["question"] + "\n\nAnswer: " + body.answer.strip()),
    )
    return {"ok": True}


# ── Leaderboard ──────────────────────────────────────────────────────────

@app.get("/leaderboard")
def leaderboard():
    """Ghosts by verified wins, then by entries. Names only, never people."""
    return db.query(
        "SELECT g.ghost_id, g.name,"
        " COUNT(DISTINCT s.id) AS entries,"
        " COUNT(DISTINCT CASE WHEN r.rank = 1 AND c.revealed THEN r.id END) AS wins"
        " FROM ghosts g"
        " LEFT JOIN submissions s ON s.ghost_id = g.ghost_id"
        " LEFT JOIN results r ON r.ghost_id = g.ghost_id AND r.challenge_id = s.challenge_id"
        " LEFT JOIN challenges c ON c.id = s.challenge_id"
        " GROUP BY g.ghost_id, g.name"
        " HAVING COUNT(DISTINCT s.id) > 0"
        " ORDER BY wins DESC, entries DESC, g.name"
        " LIMIT 50"
    )


# ── Skill proof chain ────────────────────────────────────────────────────

@app.get("/chain")
def proof_chain():
    """Every revealed win so far, linked block by block."""
    wins = with_names(db.query(
        "SELECT c.title, c.company, r.ghost_id, r.final_score"
        " FROM results r JOIN challenges c ON c.id = r.challenge_id"
        " WHERE r.rank = 1 AND c.revealed ORDER BY c.id",
    ))
    records = [w["ghost_id"] + " won " + w["title"] + " at " + w["company"] for w in wins]
    blocks = [
        {**block, "ghost_id": w["ghost_id"], "ghost_name": w["ghost_name"],
         "title": w["title"], "company": w["company"], "score": w["final_score"]}
        for block, w in zip(merkle.chain(records), wins)
    ]
    return {
        "blocks": blocks,
        "merkle_root": merkle.root(records),
        "holders": sorted({w["ghost_id"] for w in wins}),
    }


# ── Side pages, kept for the viva ────────────────────────────────────────

@app.post("/match")
def match(body: MatchInput):
    """Member 8. Candidates propose, companies hold their best offer."""
    return gale_shapley.stable_match(body.candidates, body.companies)


@app.get("/schedule")
def schedule():
    """Member 9. Picks the challenge windows that fit without overlapping."""
    rows = db.query("SELECT id, title, start_day, end_day FROM challenges WHERE NOT practice")
    windows = [
        {"id": r["id"], "title": r["title"], "start": r["start_day"], "end": r["end_day"]}
        for r in rows
    ]
    return scheduling.select_windows(windows)
