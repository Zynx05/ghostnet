"""
Member 9  UI and UX Designer
Greedy interval scheduling.

Question it answers: which challenge windows can run without clashing, so that
the largest number of them fit on the calendar?
Complexity: O(n log n), and the sort is the expensive part.
Greedy choice: always take the window that finishes earliest, because it leaves
the most room for everything that comes after it.
"""


def select_windows(windows):
    """
    windows: list of dicts with title, start and end, where start and end are
    plain numbers such as day counts.
    Returns the picked windows, the dropped ones, and the sorted order, so the
    UI can show why each decision was made.
    """
    ordered = sorted(windows, key=lambda w: w["end"])
    chosen = []
    dropped = []
    last_end = float("-inf")

    for w in ordered:
        if w["start"] >= last_end:
            chosen.append(w)
            last_end = w["end"]
        else:
            dropped.append(w)

    return {
        "sorted_by_finish": ordered,
        "chosen": chosen,
        "dropped": dropped,
    }
