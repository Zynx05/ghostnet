"""
Demo data.
Run this before the presentation so the ranking has something to chew on.
One of the submissions copies a block from another on purpose, so the
plagiarism column is not a row of zeros during the demo.

    python seed.py
"""

import auth
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
    {
        "title": "Warm up: reverse the words",
        "company": "GhostNet",
        "statement": (
            "Write a function that takes a sentence and returns it with the "
            "words in reverse order, but each word itself unchanged. Handle "
            "extra spaces and an empty string without crashing."
        ),
        "reward": "",
        "start_day": 0,
        "end_day": 0,
        "practice": True,
    },
    {
        "title": "Warm up: explain a bug to a customer",
        "company": "GhostNet",
        "statement": (
            "A customer reports that their invoice total is wrong. Write the "
            "reply you would send them in under one hundred words. Be honest "
            "about the cause, say what happens next, and do not use jargon."
        ),
        "reward": "",
        "start_day": 0,
        "end_day": 0,
        "practice": True,
    },
]

# Demo accounts. Every password is demo1234. Names are made up. The real
# name is optional in the product, so one candidate leaves it blank on purpose.
COMPANIES = [
    ("northwind@demo.pk", "Northwind Retail", 10000),
    ("vega@demo.pk", "Vega Logistics", 3000),
    ("meridian@demo.pk", "Meridian Bank", 0),
]

CANDIDATES = [
    ("bilal@demo.pk", "quiet-falcon", "Quiet Falcon", "Bilal Ahmed"),
    ("ayesha@demo.pk", "pale-otter", "Pale Otter", "Ayesha Khan"),
    ("hira@demo.pk", "swift-heron", "Swift Heron", "Hira Sheikh"),
    ("usman@demo.pk", "calm-lynx", "Calm Lynx", "Usman Tariq"),
    ("sana@demo.pk", "sharp-moth", "Sharp Moth", "Sana Malik"),
    ("farhan@demo.pk", "bold-fox", "Bold Fox", ""),
]

PASSWORD = "demo1234"

# Conversations already going, so no demo account opens an empty inbox.
# Challenge 1 belongs to Northwind Retail, challenge 2 to Vega Logistics, and
# a company can only write to somebody who entered that challenge.
CONVERSATION = [
    # Northwind and the winner.
    (1, "quiet-falcon", "tap", "company",
     "You won this one. Your version was the only entry that handled an empty "
     "cart without us having to ask."),
    (1, "quiet-falcon", "reply", "ghost",
     "Thank you. Do you want me to unmask, or can we talk first?"),
    (1, "quiet-falcon", "reply", "company",
     "Talk first, always. We have unmasked you on our side so we can raise a "
     "contract, but nothing goes further without your say so."),
    (1, "quiet-falcon", "reply", "ghost",
     "That works. What does the team look like?"),
    (1, "quiet-falcon", "reply", "company",
     "Four engineers on checkout, mostly Python. Remote three days a week, "
     "office in Karachi the other two."),

    # Northwind and the runner up who wrote prose instead of code.
    (1, "calm-lynx", "whisper", "company",
     "Ranked second. You described the fix well, but we needed working code "
     "and there was none. Send code next time and you would have won this."),
    (1, "calm-lynx", "reply", "ghost",
     "Fair. I read the brief as asking for an approach. I will submit code "
     "next time."),

    # Northwind and the thorough one.
    (1, "pale-otter", "tap", "company",
     "We would like to talk. Your cart summary was the most thorough one we read."),
    (1, "pale-otter", "reply", "ghost",
     "Happy to. What would the role actually involve day to day?"),
    (1, "pale-otter", "reply", "company",
     "Backend work on the checkout team. Four people, mostly Python. "
     "Remote three days a week."),

    # Northwind and the copier. Blunt, because the score was blunt.
    (1, "swift-heron", "whisper", "company",
     "Eighty seven percent of your entry appears word for word in another "
     "one. We are not taking this further. Send your own work and we will "
     "read it properly."),

    # Vega and the winner of the rate limiter challenge.
    (2, "sharp-moth", "tap", "company",
     "Your sliding window was the cleanest of the two. Are you open to a "
     "contract, three months to start?"),
    (2, "sharp-moth", "reply", "ghost",
     "Possibly. Is it remote, and what is the rate?"),
    (2, "sharp-moth", "reply", "company",
     "Fully remote. We pay in dollars, twice a month. Tell us your rate and "
     "we will work from there."),

    # Vega and the one who explained a token bucket but wrote no code.
    (2, "bold-fox", "whisper", "company",
     "Good explanation of a token bucket, and you were right that it handles "
     "bursts better. We went with the entry that shipped working code."),
    (2, "bold-fox", "reply", "ghost",
     "Understood. Are you running more of these?"),
    (2, "bold-fox", "reply", "company",
     "Every few weeks. You are on the list."),
]

# A question asked on the rate limiter challenge, answered by the company.
# The answer also lands in the asker inbox, which is where the answer kind
# of message comes from.
QUESTIONS = [
    (2, "bold-fox",
     "Does the limit need to survive a restart, or is in memory fine?",
     "In memory is fine for this. Say so in your answer if you assume it."),
]

SUBMISSIONS = [
    (1, "quiet-falcon",
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

    (1, "pale-otter",
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

    (1, "swift-heron",
     SHARED_BLOCK +
     "# Submitted as is.\n"),

    (1, "calm-lynx",
     "I would fix this by checking every item first. The quantity and the "
     "price both need to be valid numbers before they are multiplied, "
     "otherwise the answer comes out wrong."),

    (2, "sharp-moth",
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

    (2, "bold-fox",
     "Use a token bucket. Each client gets sixty tokens per minute and every "
     "request spends one. The bucket refills at a steady rate, which smooths "
     "out short bursts instead of rejecting them outright."),
]


def run():
    # Drop and rebuild, so running this twice never leaves half the old demo
    # data behind and the row ids stay predictable for the presentation.
    db.reset()

    # One hash for every demo account. Hashing is deliberately slow, so doing
    # it nine times would make the seed take a few seconds for no reason.
    pw = auth.hash_password(PASSWORD)

    company_ids = {}
    for email, name, balance in COMPANIES:
        company_ids[name] = db.execute(
            "INSERT INTO users (email, password_hash, role, company_name, balance_pkr)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (email, pw, "company", name, balance),
        )

    for email, ghost_id, name, real_name in CANDIDATES:
        user_id = db.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s) RETURNING id",
            (email, pw, "candidate"),
        )
        db.execute(
            "INSERT INTO ghosts (ghost_id, user_id, name, real_name) VALUES (%s, %s, %s, %s)",
            (ghost_id, user_id, name, real_name),
        )

    for c in CHALLENGES:
        db.execute(
            "INSERT INTO challenges (company_id, title, company, statement, reward,"
            " start_day, end_day, practice)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (company_ids.get(c["company"]), c["title"], c["company"], c["statement"],
             c["reward"], c["start_day"], c["end_day"], c.get("practice", False)),
        )

    for challenge_id, ghost_id, content in SUBMISSIONS:
        db.execute(
            "INSERT INTO submissions (challenge_id, ghost_id, content) VALUES (%s, %s, %s)",
            (challenge_id, ghost_id, content),
        )

    for challenge_id, ghost_id, question, answer in QUESTIONS:
        db.execute(
            "INSERT INTO questions (challenge_id, ghost_id, question, answer)"
            " VALUES (%s, %s, %s, %s)",
            (challenge_id, ghost_id, question, answer),
        )
        db.execute(
            "INSERT INTO messages (challenge_id, ghost_id, kind, sender, body)"
            " VALUES (%s, %s, %s, %s, %s)",
            (challenge_id, ghost_id, "answer", "company",
             "You asked: " + question + "\n\nAnswer: " + answer),
        )

    for challenge_id, ghost_id, kind, sender, body in CONVERSATION:
        db.execute(
            "INSERT INTO messages (challenge_id, ghost_id, kind, sender, body)"
            " VALUES (%s, %s, %s, %s, %s)",
            (challenge_id, ghost_id, kind, sender, body),
        )

    print("seeded", len(COMPANIES), "companies,", len(CANDIDATES), "candidates,",
          len(CHALLENGES), "challenges and", len(SUBMISSIONS), "submissions")
    print("every demo account uses the password", PASSWORD)
    print("database:", db.DATABASE_URL)


if __name__ == "__main__":
    run()
