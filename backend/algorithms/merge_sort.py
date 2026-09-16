"""
Member 3  Frontend Developer
Merge sort, kept here as the reference version.
The frontend ships the same algorithm in TypeScript, so the member can show
both files and point out that the complexity does not change with the language.

Complexity: O(n log n) in the best, average and worst case.
It is also stable, which matters here because two submissions with an equal
score should keep the order they arrived in.
"""


def merge_sort(items, key):
    """Split until single items are left, then merge the halves back in order."""
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    return merge(left, right, key)


def merge(left, right, key):
    """
    Walk both halves once, always taking the larger head so the result is
    highest score first. A tie keeps the left item, and that is what makes
    this sort stable.
    """
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) >= key(right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
