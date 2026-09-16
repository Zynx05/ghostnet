"""
Member 5  QA Engineer owns this file.
One test per algorithm, each with a case small enough to check by hand on the
whiteboard. That is the point: if the examiner asks why a number is correct,
the answer is in the test, not in a debugger.

    python -m pytest tests -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms import (
    tfidf, levenshtein, merge_sort, rabin_karp,
    suffix_array, complexity, merkle, gale_shapley, scheduling,
)


def test_tfidf_ranks_the_closer_text_higher():
    problem = "fix the shopping cart total bug"
    close = "the shopping cart total is wrong so fix the cart"
    far = "design a poster for a music festival"
    scores = tfidf.relevance_scores(problem, [close, far])
    assert scores[0] > scores[1]


def test_levenshtein_known_distance():
    # kitten to sitting is the textbook example and the answer is 3.
    assert levenshtein.edit_distance("kitten", "sitting") == 3
    assert levenshtein.edit_distance("abc", "abc") == 0
    assert levenshtein.similarity("abc", "abc") == 1.0


def test_merge_sort_is_stable_and_descending():
    rows = [
        {"id": "a", "score": 5},
        {"id": "b", "score": 9},
        {"id": "c", "score": 5},
    ]
    out = merge_sort.merge_sort(rows, key=lambda r: r["score"])
    assert [r["id"] for r in out] == ["b", "a", "c"]


def test_rabin_karp_finds_every_occurrence():
    assert rabin_karp.find("abracadabra", "abra") == [0, 7]
    assert rabin_karp.find("abcdef", "zz") == []


def test_rabin_karp_flags_a_copy():
    original = "the quick brown fox jumps over the lazy dog every single morning"
    copy = original
    clean = "a completely different sentence about weather and rainfall levels"
    assert rabin_karp.plagiarism_score(copy, [original]) == 1.0
    assert rabin_karp.plagiarism_score(clean, [original]) < 0.2


def test_suffix_array_longest_common_substring():
    a = "the report was submitted on friday"
    b = "we saw that the report was submitted late"
    assert "the report was submitted" in suffix_array.longest_common_substring(a, b)


def test_cyclomatic_counts_branches():
    source = "if a:\n    pass\nfor i in x:\n    if b and c:\n        pass\n"
    # One base path, plus if, for, if, and. That is five.
    assert complexity.cyclomatic(source) == 5


def test_quality_score_penalises_both_extremes():
    essay = "I would fix this by checking every item before adding it up."
    healthy = "if a:\n    pass\nfor i in x:\n    if b and c:\n        pass\n"
    tangled = "if a:\n    pass\n" * 30
    assert complexity.quality_score(healthy) == 1.0
    assert complexity.quality_score(essay) < 1.0
    assert complexity.quality_score(tangled) < 1.0


def test_merkle_proof_verifies_and_tampering_fails():
    leaves = ["win_a", "win_b", "win_c", "win_d"]
    root = merkle.root(leaves)
    proof = merkle.proof_for(leaves, 0)
    assert merkle.verify("win_a", proof, root) is True
    assert merkle.verify("win_forged", proof, root) is False


def test_chain_breaks_when_a_record_changes():
    original = merkle.chain(["win one", "win two", "win three"])
    edited = merkle.chain(["win one EDITED", "win two", "win three"])
    assert original[2]["hash"] != edited[2]["hash"]


def test_gale_shapley_produces_a_full_stable_match():
    candidates = {"ghost_1": ["Alpha", "Beta"], "ghost_2": ["Alpha", "Beta"]}
    companies = {"Alpha": ["ghost_2", "ghost_1"], "Beta": ["ghost_1", "ghost_2"]}
    out = gale_shapley.stable_match(candidates, companies)
    assert len(out["pairs"]) == 2
    paired = {p["company"]: p["candidate"] for p in out["pairs"]}
    assert paired["Alpha"] == "ghost_2"
    assert paired["Beta"] == "ghost_1"


def test_greedy_scheduling_picks_the_most_windows():
    windows = [
        {"title": "a", "start": 0, "end": 3},
        {"title": "b", "start": 1, "end": 4},
        {"title": "c", "start": 3, "end": 5},
        {"title": "d", "start": 5, "end": 7},
    ]
    out = scheduling.select_windows(windows)
    assert [w["title"] for w in out["chosen"]] == ["a", "c", "d"]
    assert [w["title"] for w in out["dropped"]] == ["b"]
