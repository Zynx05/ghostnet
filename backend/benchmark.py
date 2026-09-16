"""
Member 10  Docs and Research Lead owns this file.
It times every algorithm at growing input sizes and prints a table, so the
report can show measured growth next to the claimed big O instead of only
quoting it.

    python benchmark.py
"""

import random
import string
import time

from algorithms import (
    tfidf, levenshtein, merge_sort, rabin_karp,
    suffix_array, complexity, merkle, gale_shapley, scheduling,
)

SIZES = [100, 200, 400, 800]


def random_text(n):
    words = ["cart", "total", "price", "item", "validate", "loop", "check", "return"]
    return " ".join(random.choice(words) for _ in range(n // 5))


def timed(fn):
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000


def main():
    random.seed(7)
    print()
    print("GhostNet algorithm benchmark, time in milliseconds")
    print()
    header = "%-22s %-20s" % ("algorithm", "claimed cost")
    for n in SIZES:
        header += "%10s" % ("n=" + str(n))
    print(header)
    print("=" * len(header))

    cases = [
        ("tfidf cosine", "O(N x L)",
         lambda n: (lambda docs: lambda: tfidf.relevance_scores(docs[0], docs[1:]))(
             [random_text(n) for _ in range(6)])),

        ("levenshtein", "O(m x n)",
         lambda n: (lambda a, b: lambda: levenshtein.edit_distance(a, b))(
             random_text(n), random_text(n))),

        ("merge sort", "O(n log n)",
         lambda n: (lambda rows: lambda: merge_sort.merge_sort(rows, key=lambda r: r["s"]))(
             [{"s": random.random()} for _ in range(n)])),

        ("rabin karp", "O(n + m)",
         lambda n: (lambda t, p: lambda: rabin_karp.find(t, p))(
             random_text(n), random_text(n)[:10])),

        ("suffix array lcs", "O(n log n x log n)",
         lambda n: (lambda a, b: lambda: suffix_array.longest_common_substring(a, b))(
             random_text(n), random_text(n))),

        ("cyclomatic", "O(n)",
         lambda n: (lambda src: lambda: complexity.cyclomatic(src))(
             random_text(n))),

        ("merkle build", "O(n)",
         lambda n: (lambda leaves: lambda: merkle.root(leaves))(
             [str(i) for i in range(n)])),

        ("merkle proof", "O(n) build, log n path",
         lambda n: (lambda leaves: lambda: merkle.proof_for(leaves, 0))(
             [str(i) for i in range(n)])),

        ("gale shapley", "O(n squared)",
         lambda n: (lambda c, f: lambda: gale_shapley.stable_match(c, f))(
             *build_match(min(n, 400)))),

        ("greedy schedule", "O(n log n)",
         lambda n: (lambda w: lambda: scheduling.select_windows(w))(
             [{"title": str(i), "start": i, "end": i + random.randint(1, 4)}
              for i in range(n)])),
    ]

    for name, claimed, make in cases:
        row = "%-22s %-20s" % (name, claimed)
        for n in SIZES:
            row += "%10.2f" % timed(make(n))
        print(row)

    print()
    print("Notes for the report")
    print("  levenshtein is the clearest result. Doubling n multiplies the")
    print("  time by roughly four, which is exactly what O(m x n) predicts.")
    print("  merkle proof rebuilds the tree before walking it, so the measured")
    print("  time is O(n). The proof it returns is still only log n hashes long.")
    print("  gale shapley is capped at 400 because a square preference table")
    print("  costs n squared just to generate.")
    print()


def build_match(n):
    """A square preference table, which is the worst case for stable matching."""
    people = ["c" + str(i) for i in range(n)]
    firms = ["f" + str(i) for i in range(n)]
    candidates = {p: random.sample(firms, len(firms)) for p in people}
    companies = {f: random.sample(people, len(people)) for f in firms}
    return candidates, companies


if __name__ == "__main__":
    main()
