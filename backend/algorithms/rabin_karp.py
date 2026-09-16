"""
Member 4  Database Engineer
Rabin Karp substring search using a rolling hash.

Question it answers: did this submission copy a chunk from another submission?
Complexity: O(n + m) on average, O(n * m) in the worst case when hashes collide.
"""

BASE = 256
MOD = 1_000_000_007


def find(text, pattern):
    """Return every index where the pattern appears inside the text."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []

    high = pow(BASE, m - 1, MOD)
    pattern_hash = 0
    window_hash = 0
    for i in range(m):
        pattern_hash = (BASE * pattern_hash + ord(pattern[i])) % MOD
        window_hash = (BASE * window_hash + ord(text[i])) % MOD

    hits = []
    for i in range(n - m + 1):
        # Hashes matching is only a hint, so the characters are checked too.
        if pattern_hash == window_hash and text[i:i + m] == pattern:
            hits.append(i)
        if i < n - m:
            window_hash = (window_hash - ord(text[i]) * high) % MOD
            window_hash = (window_hash * BASE + ord(text[i + m])) % MOD
    return hits


def shingles(text, size=12):
    """Cut the text into overlapping windows of a fixed size."""
    return [text[i:i + size] for i in range(0, max(0, len(text) - size + 1), size)]


def overlap_ratio(candidate, other, size=12):
    """Share of the candidate windows that also appear in the other text."""
    windows = shingles(candidate, size)
    if not windows:
        return 0.0
    copied = sum(1 for w in windows if find(other, w))
    return copied / len(windows)


def plagiarism_score(candidate, others, size=12):
    """Worst case against any other submission. 0 is clean, 1 is a full copy."""
    if not others:
        return 0.0
    return max(overlap_ratio(candidate, o, size) for o in others)
