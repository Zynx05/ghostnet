"""
GhostNet API.
Member 2 owns this file. It stays thin on purpose: every route validates the
input, calls one algorithm module, and returns JSON. No logic lives here.

Run it with:  uvicorn main:app --reload
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
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


app = FastAPI(title="GhostNet API", version="1.0", lifespan=lifespan)

# The frontend runs on its own port during development, so it needs to be let in.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class NewChallenge(BaseModel):
    title: str
    company: str
    statement: str
    reward: str = ""
    start_day: int = 0
    end_day: int = 7


class NewSubmission(BaseModel):
    content: str
    real_name: str


class MatchInput(BaseModel):
    candidates: dict
    companies: dict


# Member 6 owns this one. CI and the hosting platform poll it.
@app.get("/health")
def health():
    return {"status": "ok", "service": "ghostnet"}


@app.get("/challenges")
def list_challenges():
    return db.query("SELECT * FROM challenges ORDER BY id DESC")


@app.get("/challenges/{challenge_id}")
def get_challenge(challenge_id: int):
    rows = db.query("SELECT * FROM challenges WHERE id = %s", (challenge_id,))
    if not rows:
        raise HTTPException(404, "challenge not found")
    return rows[0]


@app.post("/challenges")
def create_challenge(body: NewChallenge):
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
    Note the column list. real_name is never selected here, so anonymity is not
    a rule someone has to remember, it is simply absent from the query.
    """
    return db.query(
        "SELECT id, ghost_id, content FROM submissions WHERE challenge_id = %s",
        (challenge_id,),
    )


@app.post("/challenges/{challenge_id}/submissions")
def add_submission(challenge_id: int, body: NewSubmission):
    if not body.content.strip():
        raise HTTPException(400, "submission is empty")
    ghost_id = "ghost_" + uuid.uuid4().hex[:6]
    db.execute(
        "INSERT INTO submissions (challenge_id, ghost_id, content, real_name)"
        " VALUES (%s, %s, %s, %s)",
        (challenge_id, ghost_id, body.content, body.real_name),
    )
    return {"ghost_id": ghost_id}


@app.post("/challenges/{challenge_id}/rank")
def rank(challenge_id: int):
    """The demo button. Every scoring algorithm runs inside this one call."""
    challenge = get_challenge(challenge_id)
    subs = db.query(
        "SELECT ghost_id, content FROM submissions WHERE challenge_id = %s",
        (challenge_id,),
    )
    if not subs:
        raise HTTPException(400, "nothing has been submitted yet")

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
    return {"weights": ranker.WEIGHTS, "results": rows}


@app.get("/challenges/{challenge_id}/results")
def get_results(challenge_id: int):
    return db.query(
        "SELECT * FROM results WHERE challenge_id = %s ORDER BY rank",
        (challenge_id,),
    )


@app.post("/challenges/{challenge_id}/reveal")
def reveal(challenge_id: int):
    """
    The winner is unmasked and the win is written into the proof chain.
    The Merkle proof returned here lets anyone check the win on their own.
    """
    results = get_results(challenge_id)
    if not results:
        raise HTTPException(400, "run the ranking first")

    winner = results[0]
    name = db.query(
        "SELECT real_name FROM submissions WHERE ghost_id = %s",
        (winner["ghost_id"],),
    )
    db.execute("UPDATE challenges SET revealed = TRUE WHERE id = %s", (challenge_id,))

    leaves = [r["ghost_id"] + ":" + str(r["final_score"]) for r in results]
    index = 0
    return {
        "winner": winner,
        "real_name": name[0]["real_name"] if name else "unknown",
        "merkle_root": merkle.root(leaves),
        "leaf": leaves[index],
        "proof": merkle.proof_for(leaves, index),
        "leaf_count": len(leaves),
    }


@app.get("/chain")
def proof_chain():
    """Every revealed win so far, linked block by block."""
    wins = db.query(
        "SELECT c.title, c.company, r.ghost_id, r.final_score"
        " FROM results r JOIN challenges c ON c.id = r.challenge_id"
        " WHERE r.rank = 1 AND c.revealed ORDER BY c.id",
    )
    records = [
        w["ghost_id"] + " won " + w["title"] + " at " + w["company"]
        for w in wins
    ]
    return {"blocks": merkle.chain(records), "merkle_root": merkle.root(records)}


@app.post("/match")
def match(body: MatchInput):
    """Member 8. Candidates propose, companies hold their best offer."""
    return gale_shapley.stable_match(body.candidates, body.companies)


@app.get("/schedule")
def schedule():
    """Member 9. Picks the challenge windows that fit without overlapping."""
    rows = db.query("SELECT id, title, start_day, end_day FROM challenges")
    windows = [
        {"id": r["id"], "title": r["title"],
         "start": r["start_day"], "end": r["end_day"]}
        for r in rows
    ]
    return scheduling.select_windows(windows)
