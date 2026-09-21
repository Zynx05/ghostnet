"""
Ghost identities.

Every candidate account gets one ghost. The name is generated, two words, and
it is the only identity anyone else ever sees. The candidate never picks it,
which is the point: nothing about it can be gamed or made to sound impressive.
"""

import random

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


def create(user_id):
    """Make a ghost for a new candidate, with a name nobody else has."""
    for _ in range(50):
        name = make_name()
        ghost_id = name.replace(" ", "-")
        if not db.query("SELECT 1 FROM ghosts WHERE ghost_id = %s", (ghost_id,)):
            break
    else:
        # 576 combinations and all taken. Add a number rather than give up.
        ghost_id = ghost_id + "-" + str(random.randint(100, 999))
        name = name + " " + ghost_id[-3:]

    db.execute(
        "INSERT INTO ghosts (ghost_id, user_id, name) VALUES (%s, %s, %s)",
        (ghost_id, user_id, name.title()),
    )
    return {"ghost_id": ghost_id, "name": name.title()}


def for_user(user_id):
    rows = db.query(
        "SELECT ghost_id, name, real_name FROM ghosts WHERE user_id = %s", (user_id,)
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
