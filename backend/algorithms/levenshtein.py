"""
Member 2  Backend Developer
Levenshtein edit distance, solved with dynamic programming.

Question it answers: how many single character edits turn one text into another?
Complexity: O(m * n) time. Memory is O(n) because only two rows are kept.
"""


def edit_distance(a, b):
    """Classic DP table, rolled down to two rows to save memory."""
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ch_a in enumerate(a, start=1):
        current = [i]
        for j, ch_b in enumerate(b, start=1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            replace = previous[j - 1] + (0 if ch_a == ch_b else 1)
            current.append(min(insert, delete, replace))
        previous = current
    return previous[-1]


def similarity(a, b):
    """Turn a raw distance into a 0 to 1 score so it can be averaged."""
    longest = max(len(a), len(b))
    if longest == 0:
        return 1.0
    return 1 - (edit_distance(a, b) / longest)


def distance_matrix(texts):
    """Every pair compared once. Used by the report to show the DP cost."""
    n = len(texts)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = edit_distance(texts[i], texts[j])
            matrix[i][j] = d
            matrix[j][i] = d
    return matrix
