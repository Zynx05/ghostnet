"""
Member 6  DevOps Engineer
Cyclomatic complexity, counted from the decision points in the code.

Question it answers: how tangled is the submitted code?
Formula: M equals E minus N plus 2 on the control flow graph, which for a
single function reduces to decision points plus 1.
Complexity: O(n) over the characters of the source.
"""

DECISION_KEYWORDS = [
    "if", "elif", "for", "while", "case", "catch",
    "except", "and", "or", "&&", "||", "?",
]


def count_decisions(source):
    """Count every branch keyword. Each one adds an independent path."""
    found = {}
    lowered = source.lower()
    for keyword in DECISION_KEYWORDS:
        count = 0
        start = 0
        while True:
            at = lowered.find(keyword, start)
            if at == -1:
                break
            before = lowered[at - 1] if at > 0 else " "
            after_at = at + len(keyword)
            after = lowered[after_at] if after_at < len(lowered) else " "
            word_like = keyword[0].isalpha()
            # Word keywords need clean boundaries so that format is not read as for.
            if not word_like or (not before.isalnum() and not after.isalnum()):
                count += 1
            start = at + len(keyword)
        if count:
            found[keyword] = count
    return found


def cyclomatic(source):
    """One path already exists before any branching, so the count starts at 1."""
    return 1 + sum(count_decisions(source).values())


HEALTHY_LOW = 3
HEALTHY_HIGH = 10


def quality_score(source):
    """
    Turn the raw number into a 0 to 1 score.

    The healthy band is 3 to 10. Ten is the usual industry ceiling for one
    function. The floor matters just as much here: a submission with a score
    of 1 or 2 has almost no branching, which for a coding challenge means
    nothing was really implemented. Both ends are penalised, so an essay and
    an unreadable function are treated as the two failures they are.
    """
    value = cyclomatic(source)
    if HEALTHY_LOW <= value <= HEALTHY_HIGH:
        return 1.0
    if value < HEALTHY_LOW:
        return value / HEALTHY_LOW
    return max(0.0, 1 - ((value - HEALTHY_HIGH) / 30))
