"""
Member 7  Blockchain Developer
Merkle tree plus a SHA 256 hash chain for the Skill Proof record.

Question it answers: can a win be proved without handing over the whole list,
and can an old record be edited without anyone noticing?
Complexity: O(n) to build the tree, O(log n) to produce or verify one proof.
"""

import hashlib


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def build_tree(leaves):
    """
    Hash every leaf, then pair them up level by level until one root is left.
    A lonely node at the end of a level is paired with itself.
    """
    if not leaves:
        return [[sha256("")]]
    levels = [[sha256(leaf) for leaf in leaves]]
    while len(levels[-1]) > 1:
        current = levels[-1]
        parent = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            parent.append(sha256(left + right))
        levels.append(parent)
    return levels


def root(leaves):
    return build_tree(leaves)[-1][0]


def proof_for(leaves, index):
    """
    The sibling hashes needed to walk from one leaf up to the root.
    There are only log n of them, which is the whole point of the structure.
    """
    levels = build_tree(leaves)
    path = []
    for level in levels[:-1]:
        pair = index ^ 1
        sibling = level[pair] if pair < len(level) else level[index]
        path.append({"hash": sibling, "side": "right" if index % 2 == 0 else "left"})
        index //= 2
    return path


def verify(leaf, path, expected_root):
    """Rebuild the root from one leaf plus its path, then compare the two."""
    current = sha256(leaf)
    for step in path:
        if step["side"] == "right":
            current = sha256(current + step["hash"])
        else:
            current = sha256(step["hash"] + current)
    return current == expected_root


def chain(records):
    """
    Every block carries the hash of the block before it, so editing an old win
    changes every hash that follows and the break becomes obvious.
    """
    blocks = []
    previous = "0" * 64
    for i, record in enumerate(records):
        block_hash = sha256(previous + record)
        blocks.append({
            "index": i,
            "record": record,
            "previous_hash": previous,
            "hash": block_hash,
        })
        previous = block_hash
    return blocks
