"""
Ghost identities.

There is no login. The first time a browser visits, it asks for a ghost and
keeps the token it gets back. From then on that token is the person. The name
is generated, two words, and it is the only identity anyone else ever sees.
"""

import random
import secrets

import db

ADJECTIVES = [
    "quiet", "pale", "swift", "calm", "sharp", "bold", "still", "keen",
    "soft", "wry", "wild", "cool", "dim", "brisk", "shy", "odd",
    "grey", "late", "lone", "mild", "neat", "plain", "rare", "slow",
]

ANIMALS = [
    "falcon", "otter", "heron", "lynx", "moth", "fox", "crane", "wren",
    "hare", "owl", "newt", "vole", "ibis", "pike", "seal", "swan",
    "tern", "elk", "kite", "mole", "puma", "rook", "stag", "toad",
]


def make_name():
    """Two words. Quiet Falcon, Pale Otter. Nothing that sounds like a person."""
    return random.choice(ADJECTIVES) + " " + random.choice(ANIMALS)


def create():
    """Make a new ghost with a name nobody else has, and a secret token."""
    for _ in range(50):
        name = make_name()
        ghost_id = name.replace(" ", "-")
        taken = db.query("SELECT 1 FROM ghosts WHERE ghost_id = %s", (ghost_id,))
        if not taken:
            break
    else:
        # 576 combinations and all taken. Add a number rather than give up.
        ghost_id = ghost_id + "-" + str(random.randint(100, 999))
        name = name + " " + ghost_id[-3:]

    token = secrets.token_urlsafe(24)
    db.execute(
        "INSERT INTO ghosts (ghost_id, name, token) VALUES (%s, %s, %s)",
        (ghost_id, name.title(), token),
    )
    return {"ghost_id": ghost_id, "name": name.title(), "token": token}


def by_token(token):
    """The ghost that owns this token, or None."""
    rows = db.query(
        "SELECT ghost_id, name, real_name FROM ghosts WHERE token = %s", (token,)
    )
    return rows[0] if rows else None


def names_for(ghost_ids):
    """ghost_id to display name, for a list of ids."""
    if not ghost_ids:
        return {}
    marks = ", ".join(["%s"] * len(ghost_ids))
    rows = db.query(
        "SELECT ghost_id, name FROM ghosts WHERE ghost_id IN (" + marks + ")",
        tuple(ghost_ids),
    )
    return {r["ghost_id"]: r["name"] for r in rows}
