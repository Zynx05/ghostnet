"""
The scoring pipeline.
This file owns no algorithm of its own. It calls the modules written by
members 1, 2, 4, 5 and 6, then hands the result to member 3 for sorting.

Weights are deliberately visible here so they can be defended in the viva:
relevance matters most, plagiarism is a penalty rather than a score.
"""

from . import tfidf, levenshtein, rabin_karp, suffix_array, complexity, merge_sort

WEIGHTS = {
    "relevance": 0.45,
    "quality": 0.25,
    "structure": 0.30,
}


def score_all(problem_statement, submissions):
    """
    submissions: list of dicts with ghost_id and content.
    Returns one row per submission, already ranked.
    """
    texts = [s["content"] for s in submissions]

    # Member 1: one pass builds the shared vocabulary for every submission.
    relevance = tfidf.relevance_scores(problem_statement, texts)

    rows = []
    for i, s in enumerate(submissions):
        others = texts[:i] + texts[i + 1:]

        # Member 2: distance to the problem statement as a rough quality proxy.
        quality = levenshtein.similarity(s["content"], problem_statement)

        # Member 4: rolling hash sweep against every other submission.
        plagiarism = rabin_karp.plagiarism_score(s["content"], others)

        # Member 5: the single longest passage shared with anyone else.
        copied = suffix_array.longest_copied_passage(s["content"], others)

        # Member 6: branch counting on the submitted code.
        structure = complexity.quality_score(s["content"])
        paths = complexity.cyclomatic(s["content"])

        base = (
            WEIGHTS["relevance"] * relevance[i]
            + WEIGHTS["quality"] * quality
            + WEIGHTS["structure"] * structure
        )
        final = round(max(0.0, base * (1 - plagiarism)), 4)

        rows.append({
            "ghost_id": s["ghost_id"],
            "relevance": round(relevance[i], 4),
            "quality": round(quality, 4),
            "structure": round(structure, 4),
            "cyclomatic": paths,
            "plagiarism": round(plagiarism, 4),
            "longest_copied": copied[:60],
            "final_score": final,
            "rank": 0,
        })

    # Member 3: stable merge sort, highest score first.
    ranked = merge_sort.merge_sort(rows, key=lambda r: r["final_score"])
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
    return ranked
