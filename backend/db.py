"""
Member 4  Database Engineer owns this file.

Two databases, one set of SQL.

    local        SQLite, a single file, nothing to install
    deployed     PostgreSQL on Railway

Everything else in the project writes PostgreSQL style SQL with percent s
placeholders. This file translates when it is talking to SQLite. That keeps
the choice of database in one file instead of spreading it through the API.

Which one is used depends on DATABASE_URL:

    unset                     SQLite at backend/ghostnet.db
    sqlite:///path/to.db      SQLite at that path
    postgresql://...          PostgreSQL

Railway sets DATABASE_URL to a PostgreSQL address, so deployment is unaffected
by the local default. CI runs the api job against a real PostgreSQL container,
which is what stops the two paths drifting apart.

Nine tables.

users        email, password hash, role. A candidate or a company. Companies
             carry a balance in rupees
ghosts       one per candidate. The ghost id is the only identity the rest of
             the system ever sees. The real name sits here, optional, and the
             ranking queries never join to it, so hiding names is not a rule
             somebody has to remember, it is simply absent from the SQL
challenges   what a company posted, owned by that company. practice marks
             warm ups with no company behind them
unmasks      every time a company paid to see a real name. One row per
             candidate per company per challenge, so nobody is charged twice
submissions  anonymous work, one per ghost per challenge
results      the scores produced by one ranking run
practice     where a ghost would have ranked on a closed challenge. Never
             touches results
messages     the inbox. Taps, whispers and answers from a company, and the
             replies a candidate sends back. One thread per challenge
questions    asked on a challenge, answered by the company, visible to all
"""

import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

# Reads backend/.env when there is one, so a laptop can have its own settings
# without anybody editing code. A real environment variable always wins, which
# is what lets Railway override this in production.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE = "sqlite:///" + os.path.join(HERE, "ghostnet.db").replace("\\", "/")

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE)
IS_SQLITE = DATABASE_URL.startswith("sqlite")


# ── Schema ───────────────────────────────────────────────────────────────
# One schema, written once. The four tokens below are the only places the two
# dialects disagree, so they are filled in at import time.

SCHEMA_TEMPLATE = """
CREATE TABLE IF NOT EXISTS users (
    id            {PK},
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL,
    token         TEXT    UNIQUE,
    company_name  TEXT    NOT NULL DEFAULT '',
    balance_pkr   INTEGER NOT NULL DEFAULT 0,
    created_at    {TS}
);

CREATE TABLE IF NOT EXISTS ghosts (
    id          {PK},
    ghost_id    TEXT    NOT NULL UNIQUE,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    real_name   TEXT    NOT NULL DEFAULT '',
    created_at  {TS}
);

CREATE TABLE IF NOT EXISTS challenges (
    id          {PK},
    company_id  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title       TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    statement   TEXT    NOT NULL,
    reward      TEXT    NOT NULL DEFAULT '',
    start_day   INTEGER NOT NULL DEFAULT 0,
    end_day     INTEGER NOT NULL DEFAULT 7,
    revealed    BOOLEAN NOT NULL DEFAULT {FALSE},
    practice    BOOLEAN NOT NULL DEFAULT {FALSE},
    created_at  {TS}
);

CREATE TABLE IF NOT EXISTS submissions (
    id            {PK},
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id      TEXT    NOT NULL REFERENCES ghosts(ghost_id) ON DELETE CASCADE,
    content       TEXT    NOT NULL,
    created_at    {TS},
    UNIQUE (challenge_id, ghost_id)
);

CREATE TABLE IF NOT EXISTS results (
    id              {PK},
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id        TEXT    NOT NULL,
    relevance       {REAL},
    quality         {REAL},
    structure       {REAL},
    cyclomatic      INTEGER,
    plagiarism      {REAL},
    longest_copied  TEXT,
    final_score     {REAL},
    rank            INTEGER,
    UNIQUE (challenge_id, ghost_id)
);

CREATE TABLE IF NOT EXISTS practice (
    id            {PK},
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id      TEXT    NOT NULL REFERENCES ghosts(ghost_id) ON DELETE CASCADE,
    would_rank    INTEGER NOT NULL,
    out_of        INTEGER NOT NULL,
    final_score   {REAL},
    created_at    {TS}
);

CREATE TABLE IF NOT EXISTS messages (
    id            {PK},
    ghost_id      TEXT    NOT NULL REFERENCES ghosts(ghost_id) ON DELETE CASCADE,
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    kind          TEXT    NOT NULL,
    -- Who wrote it. Everything a company sends is company, a reply is ghost.
    sender        TEXT    NOT NULL DEFAULT 'company',
    body          TEXT    NOT NULL,
    created_at    {TS}
);

CREATE TABLE IF NOT EXISTS unmasks (
    id            {PK},
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    company_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ghost_id      TEXT    NOT NULL REFERENCES ghosts(ghost_id) ON DELETE CASCADE,
    charged_pkr   INTEGER NOT NULL,
    created_at    {TS},
    UNIQUE (challenge_id, company_id, ghost_id)
);

CREATE TABLE IF NOT EXISTS questions (
    id            {PK},
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id      TEXT    NOT NULL REFERENCES ghosts(ghost_id) ON DELETE CASCADE,
    question      TEXT    NOT NULL,
    answer        TEXT    NOT NULL DEFAULT '',
    created_at    {TS}
);

CREATE INDEX IF NOT EXISTS idx_sub_challenge ON submissions(challenge_id);
CREATE INDEX IF NOT EXISTS idx_res_challenge ON results(challenge_id, rank);
CREATE INDEX IF NOT EXISTS idx_msg_ghost ON messages(ghost_id);
CREATE INDEX IF NOT EXISTS idx_q_challenge ON questions(challenge_id);
"""

DIALECT = {
    True: {
        "PK": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "TS": "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP",
        "REAL": "REAL",
        "FALSE": "0",
    },
    False: {
        "PK": "SERIAL PRIMARY KEY",
        "TS": "TIMESTAMPTZ NOT NULL DEFAULT now()",
        "REAL": "DOUBLE PRECISION",
        "FALSE": "FALSE",
    },
}

SCHEMA = SCHEMA_TEMPLATE.format(**DIALECT[IS_SQLITE])

TABLES = ["questions", "unmasks", "messages", "practice", "results",
          "submissions", "challenges", "ghosts", "users"]

DROP_ALL = (
    ["DROP TABLE IF EXISTS " + t for t in TABLES]
    if IS_SQLITE else
    ["DROP TABLE IF EXISTS " + ", ".join(TABLES) + " CASCADE"]
)


# ── Connections ──────────────────────────────────────────────────────────

if IS_SQLITE:
    SQLITE_PATH = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")

    # SQLite stores a boolean as 0 or 1. This converter turns the column back
    # into a real True or False, so the JSON the API returns looks the same as
    # it does on PostgreSQL and the TypeScript type on the frontend stays true.
    sqlite3.register_converter("BOOLEAN", lambda v: v not in (b"0", b"", None))

    class _NoPool:
        """SQLite needs no pool. This exists so main.py can close it either way."""

        def open(self):
            pass

        def close(self):
            pass

    pool = _NoPool()

    @contextmanager
    def connection():
        conn = sqlite3.connect(SQLITE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # SQLite ignores foreign keys unless it is asked not to.
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

else:
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool

    # Opening a TCP connection and authenticating costs more than most of our
    # queries do, so the pool keeps a few open and hands them out. open=False
    # means nothing connects at import time.
    pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=False)

    @contextmanager
    def connection():
        pool.open()
        with pool.connection() as conn:
            yield conn


def _translate(sql):
    """PostgreSQL placeholders are percent s. SQLite wants a question mark."""
    return sql.replace("%s", "?") if IS_SQLITE else sql


# ── The four functions everything else uses ──────────────────────────────

def init():
    """Create the tables if they are not there yet. Safe to run again."""
    with connection() as conn:
        conn.executescript(SCHEMA) if IS_SQLITE else conn.execute(SCHEMA)


def reset():
    """Drop everything and build it again. Used by the seed script."""
    with connection() as conn:
        for statement in DROP_ALL:
            conn.execute(statement)
        conn.executescript(SCHEMA) if IS_SQLITE else conn.execute(SCHEMA)


def query(sql, args=()):
    """Read rows back as plain dicts, which keeps the API layer short."""
    sql = _translate(sql)
    with connection() as conn:
        if IS_SQLITE:
            return [dict(r) for r in conn.execute(sql, args).fetchall()]
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, args)
            return cur.fetchall()


def execute(sql, args=()):
    """
    Write. If the statement ends in RETURNING, the first returned value comes
    back, which is how a new id is read. SQLite has no RETURNING in older
    versions, so the clause is removed and lastrowid is used instead.
    """
    sql = _translate(sql)
    with connection() as conn:
        if IS_SQLITE:
            returning = " RETURNING " in sql
            if returning:
                sql = sql[:sql.index(" RETURNING ")]
            cur = conn.execute(sql, args)
            return cur.lastrowid if returning else None
        with conn.cursor() as cur:
            cur.execute(sql, args)
            if cur.description is None:
                return None
            row = cur.fetchone()
            return row[0] if row else None
