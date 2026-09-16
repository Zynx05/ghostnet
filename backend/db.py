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

Three tables and nothing else.

challenges   what a company posted
submissions  anonymous work. The real name sits in a column the ranking
             queries never select, so hiding names is not a rule somebody has
             to remember, it is simply absent from the SQL
results      the scores produced by one ranking run
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
# The same three tables in both dialects. The differences are only in the
# type names and in how an auto incrementing id is declared.

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS challenges (
    id          SERIAL PRIMARY KEY,
    title       TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    statement   TEXT    NOT NULL,
    reward      TEXT    NOT NULL DEFAULT '',
    start_day   INTEGER NOT NULL DEFAULT 0,
    end_day     INTEGER NOT NULL DEFAULT 7,
    revealed    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS submissions (
    id            SERIAL PRIMARY KEY,
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id      TEXT    NOT NULL UNIQUE,
    content       TEXT    NOT NULL,
    real_name     TEXT    NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS results (
    id              SERIAL PRIMARY KEY,
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id        TEXT    NOT NULL,
    relevance       DOUBLE PRECISION,
    quality         DOUBLE PRECISION,
    structure       DOUBLE PRECISION,
    cyclomatic      INTEGER,
    plagiarism      DOUBLE PRECISION,
    longest_copied  TEXT,
    final_score     DOUBLE PRECISION,
    rank            INTEGER,
    UNIQUE (challenge_id, ghost_id)
);

CREATE INDEX IF NOT EXISTS idx_sub_challenge ON submissions(challenge_id);
CREATE INDEX IF NOT EXISTS idx_res_challenge ON results(challenge_id, rank);
"""

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS challenges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    statement   TEXT    NOT NULL,
    reward      TEXT    NOT NULL DEFAULT '',
    start_day   INTEGER NOT NULL DEFAULT 0,
    end_day     INTEGER NOT NULL DEFAULT 7,
    revealed    BOOLEAN NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS submissions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id  INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id      TEXT    NOT NULL UNIQUE,
    content       TEXT    NOT NULL,
    real_name     TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    ghost_id        TEXT    NOT NULL,
    relevance       REAL,
    quality         REAL,
    structure       REAL,
    cyclomatic      INTEGER,
    plagiarism      REAL,
    longest_copied  TEXT,
    final_score     REAL,
    rank            INTEGER,
    UNIQUE (challenge_id, ghost_id)
);

CREATE INDEX IF NOT EXISTS idx_sub_challenge ON submissions(challenge_id);
CREATE INDEX IF NOT EXISTS idx_res_challenge ON results(challenge_id, rank);
"""

SCHEMA = SQLITE_SCHEMA if IS_SQLITE else POSTGRES_SCHEMA

DROP_ALL = (
    ["DROP TABLE IF EXISTS results",
     "DROP TABLE IF EXISTS submissions",
     "DROP TABLE IF EXISTS challenges"]
    if IS_SQLITE else
    ["DROP TABLE IF EXISTS results, submissions, challenges CASCADE"]
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
