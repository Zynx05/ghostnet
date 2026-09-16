"""
Member 8  Product Manager
Gale Shapley stable matching.

Question it answers: which candidate goes to which company when both sides have
ranked preferences and nobody should want to swap once the round is over?
Complexity: O(n squared). The loop always ends because each candidate proposes
to each company at most once, and the result is always stable.
"""


def stable_match(candidate_prefs, company_prefs):
    """
    Candidates propose, companies hold the best offer seen so far.
    candidate_prefs: candidate name to list of companies, best first.
    company_prefs:   company name to list of candidates, best first.
    """
    free = list(candidate_prefs.keys())
    next_choice = {c: 0 for c in candidate_prefs}
    engaged = {}
    log = []

    # Turn each preference list into a lookup so comparing two offers is O(1).
    rank = {
        company: {name: i for i, name in enumerate(order)}
        for company, order in company_prefs.items()
    }

    while free:
        candidate = free.pop(0)
        options = candidate_prefs[candidate]
        if next_choice[candidate] >= len(options):
            continue
        company = options[next_choice[candidate]]
        next_choice[candidate] += 1

        if company not in engaged:
            engaged[company] = candidate
            log.append(candidate + " proposed to " + company + ", held")
        else:
            current = engaged[company]
            if rank[company].get(candidate, 999) < rank[company].get(current, 999):
                engaged[company] = candidate
                free.append(current)
                log.append(company + " swapped " + current + " for " + candidate)
            else:
                free.append(candidate)
                log.append(company + " rejected " + candidate)

    pairs = [{"company": k, "candidate": v} for k, v in engaged.items()]
    return {"pairs": pairs, "log": log}
