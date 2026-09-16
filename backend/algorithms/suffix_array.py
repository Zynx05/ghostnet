"""
Member 5  QA Engineer
Suffix array plus longest common substring.

Question it answers: what is the single longest copied passage between two texts?
Complexity: O(n log n * log n) to sort the suffixes, O(n) to scan neighbours.
"""


def build(text):
    """Sort every suffix of the text and return their starting positions."""
    suffixes = sorted(range(len(text)), key=lambda i: text[i:])
    return suffixes


def longest_common_prefix(a, b):
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return n


def longest_common_substring(a, b):
    """
    Join both texts with a separator that appears in neither, sort the suffixes,
    then compare only neighbours that came from different sides of the join.
    """
    if not a or not b:
        return ""
    joined = a + "\x01" + b
    split_at = len(a)
    order = build(joined)

    best_length = 0
    best_start = 0
    for k in range(1, len(order)):
        i, j = order[k - 1], order[k]
        from_different_texts = (i < split_at) != (j < split_at)
        if not from_different_texts:
            continue
        length = longest_common_prefix(joined[i:], joined[j:])
        if length > best_length:
            best_length = length
            best_start = i
    return joined[best_start:best_start + best_length]


def longest_copied_passage(candidate, others):
    """The worst passage this submission shares with any other one."""
    best = ""
    for other in others:
        found = longest_common_substring(candidate, other)
        if len(found) > len(best):
            best = found
    return best
