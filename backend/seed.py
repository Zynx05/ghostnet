"""
Demo data.
Run this before the presentation so the ranking has something to chew on.
One of the submissions copies a block from another on purpose, so the
plagiarism column is not a row of zeros during the demo.

    python seed.py
"""

import db

SHARED_BLOCK = (
    "def validate_cart(items):\n"
    "    total = 0\n"
    "    for item in items:\n"
    "        if item.quantity > 0 and item.price > 0:\n"
    "            total += item.quantity * item.price\n"
    "    return total\n"
)

CHALLENGES = [
    {
        "title": "Fix the cart total bug",
        "company": "Northwind Retail",
        "statement": (
            "Our shopping cart returns the wrong total when an item quantity is "
            "zero or the price is missing. Write a function that validates the "
            "cart items and returns a correct total. Handle empty carts and "
            "invalid prices without crashing."
        ),
        "reward": "PKR 40000 and an interview",
        "start_day": 0,
        "end_day": 5,
    },
    {
        "title": "Rate limit the public API",
        "company": "Vega Logistics",
        "statement": (
            "Design and implement a rate limiter for a public API. It should "
            "allow sixty requests per minute per client and reject the rest "
            "with a clear message. Explain the data structure you picked."
        ),
        "reward": "Contract role",
        "start_day": 3,
        "end_day": 9,
    },
    {
        "title": "Onboarding screen copy",
        "company": "Meridian Bank",
        "statement": (
            "Write the copy for a three screen onboarding flow for a savings "
            "app aimed at first time savers. Plain language, no jargon, and "
            "each screen under forty words."
        ),
        "reward": "Skill Proof token",
        "start_day": 6,
        "end_day": 8,
    },
]

SUBMISSIONS = [
    (1, "Bilal Ahmed",
     "def validate_cart_total(items):\n"
     "    # An empty cart is a valid cart, so it returns a zero total.\n"
     "    if not items:\n"
     "        return 0\n"
     "    total = 0\n"
     "    for item in items:\n"
     "        # A missing price falls back to zero instead of crashing.\n"
     "        price = item.price or 0\n"
     "        quantity = max(0, item.quantity)\n"
     "        total += price * quantity\n"
     "    return round(total, 2)\n"
     "# One pass over the cart items, so the cost is O(n) in the item count.\n"
     "# Zero quantity and invalid price are both handled by the guards above.\n"),

    (1, "Ayesha Khan",
     SHARED_BLOCK +
     "\n"
     "def cart_summary(items):\n"
     "    # Wraps the validation above and reports what was skipped.\n"
     "    skipped = [i for i in items if i.price is None]\n"
     "    return {\n"
     "        'total': validate_cart(items),\n"
     "        'skipped': len(skipped),\n"
     "    }\n"
     "# An empty cart never enters the loop, so the total stays zero.\n"
     "# Nothing raises on a missing price, the item is simply not counted.\n"),

    (1, "Hira Sheikh",
     SHARED_BLOCK +
     "# Submitted as is.\n"),

    (1, "Usman Tariq",
     "I would fix this by checking every item first. The quantity and the "
     "price both need to be valid numbers before they are multiplied, "
     "otherwise the answer comes out wrong."),

    (2, "Sana Malik",
     "class RateLimiter:\n"
     "    def __init__(self, limit=60, window=60):\n"
     "        self.limit = limit\n"
     "        self.window = window\n"
     "        self.hits = {}\n"
     "    def allow(self, client, now):\n"
     "        seen = self.hits.get(client, [])\n"
     "        seen = [t for t in seen if now - t < self.window]\n"
     "        if len(seen) >= self.limit:\n"
     "            return False\n"
     "        seen.append(now)\n"
     "        self.hits[client] = seen\n"
     "        return True\n"
     "# A sliding window per client, held in a deque style list.\n"
     "# Sixty requests per minute, anything above that is rejected.\n"),

    (2, "Farhan Qureshi",
     "Use a token bucket. Each client gets sixty tokens per minute and every "
     "request spends one. The bucket refills at a steady rate, which smooths "
     "out short bursts instead of rejecting them outright."),
]


def run():
    # Drop and rebuild, so running this twice never leaves half the old demo
    # data behind and the row ids stay predictable for the presentation.
    db.reset()

    for c in CHALLENGES:
        db.execute(
            "INSERT INTO challenges (title, company, statement, reward, start_day, end_day)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (c["title"], c["company"], c["statement"], c["reward"],
             c["start_day"], c["end_day"]),
        )

    for i, (challenge_id, name, content) in enumerate(SUBMISSIONS, start=1):
        db.execute(
            "INSERT INTO submissions (challenge_id, ghost_id, content, real_name)"
            " VALUES (%s, %s, %s, %s)",
            (challenge_id, "ghost_%03d" % i, content, name),
        )

    print("seeded", len(CHALLENGES), "challenges and", len(SUBMISSIONS), "submissions")
    print("database:", db.DATABASE_URL)


if __name__ == "__main__":
    run()
