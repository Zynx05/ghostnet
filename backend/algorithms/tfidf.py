"""
Member 1  Algorithm Engineer
Term frequency times inverse document frequency, then cosine similarity.

Question it answers: how close is a submission to the problem statement?
Complexity: O(N * L) to build the vectors, O(V) for one cosine score.
"""

import math


def tokenize(text):
    """Lowercase the text and keep only word characters."""
    word = ""
    tokens = []
    for ch in text.lower():
        if ch.isalnum():
            word += ch
        elif word:
            tokens.append(word)
            word = ""
    if word:
        tokens.append(word)
    return tokens


def term_frequency(tokens):
    """How often each word appears in one document, divided by its length."""
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    total = len(tokens) or 1
    return {word: c / total for word, c in counts.items()}


def inverse_document_frequency(all_documents):
    """Rare words score high, words present everywhere score near zero."""
    n = len(all_documents)
    seen_in = {}
    for tokens in all_documents:
        for word in set(tokens):
            seen_in[word] = seen_in.get(word, 0) + 1
    return {word: math.log((n + 1) / (count + 1)) + 1 for word, count in seen_in.items()}


def build_vector(tokens, idf):
    tf = term_frequency(tokens)
    return {word: value * idf.get(word, 0.0) for word, value in tf.items()}


def cosine_similarity(a, b):
    """Dot product divided by the product of both magnitudes. Range 0 to 1."""
    shared = set(a) & set(b)
    dot = sum(a[word] * b[word] for word in shared)
    mag_a = math.sqrt(sum(v * v for v in a.values()))
    mag_b = math.sqrt(sum(v * v for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def relevance_scores(problem_statement, submissions):
    """Score every submission against the problem statement in one pass."""
    docs = [tokenize(problem_statement)] + [tokenize(s) for s in submissions]
    idf = inverse_document_frequency(docs)
    problem_vector = build_vector(docs[0], idf)
    return [cosine_similarity(problem_vector, build_vector(d, idf)) for d in docs[1:]]
