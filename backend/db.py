"""
Member 4  Database Engineer owns this file.

PostgreSQL, reached through psycopg 3 and a small connection pool.
Three tables and nothing else.

challenges   what a company posted
submissions  anonymous work. The real name sits in a column that the ranking
             queries never select, so anonymity is not a rule somebody has to
             remember, it is simply absent from the SQL
results      the scores produced by one ranking run

The connection string comes from the DATABASE_URL environment variable, so the
same code runs against a local database, a container, and CI without edits.
"""

import os

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://ghostnet:ghostnet@localhost:5432/ghostnet",
)

# Opening a TCP connection and authenticating costs more than most of our
# queries do, so the pool keeps a few open and hands them out. open=False means
# nothing connects at import time, which keeps the tests importable offline.
pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=10, open=False)

SCHEMA = """
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
    -- One row per submission per ranking run. Running the ranking twice must
    -- update the scores, not add a second set of them.
    UNIQUE (challenge_id, ghost_id)
);

-- Both foreign keys are filtered on constantly and neither is indexed by
-- default in PostgreSQL, so these two indexes are the difference between an
-- index scan and a sequential scan of the whole table.
CREATE INDEX IF NOT EXISTS idx_sub_challenge ON submissions(challenge_id);
CREATE INDEX IF NOT EXISTS idx_res_challenge ON results(challenge_id, rank);
"""

DROP_ALL = "DROP TABLE IF EXISTS results, submissions, challenges CASCADE;"


def init():
    """Create the tables if they are not there yet. Safe to run repeatedly."""
    pool.open()
    with pool.connection() as conn:
        conn.execute(SCHEMA)


def reset():
    """Drop everything and build it again. Used by the seed script."""
    pool.open()
    with pool.connection() as conn:
        conn.execute(DROP_ALL)
        conn.execute(SCHEMA)


def query(sql, args=()):
    """Read rows back as plain dicts, which keeps the API layer short."""
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, args)
            return cur.fetchall()


def execute(sql, args=()):
    """
    Write. If the statement ends in RETURNING, the first returned value comes
    back, which is how a new id is read. PostgreSQL has no lastrowid.
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            if cur.description is None:
                return None
            row = cur.fetchone()
            return row[0] if row else None
