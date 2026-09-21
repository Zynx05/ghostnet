"""
Demo data.
Run this before the presentation so the ranking has something to chew on.

Challenge 1 is the one to demo. One of its entries copies a block from
another on purpose, so the plagiarism column is not a row of zeros.

Everything else exists so no screen is empty: six companies, six candidates,
twenty six entries across seven challenges, and a conversation on almost
every one of them.

    python seed.py
"""

import auth
import db

PASSWORD = "demo1234"

SHARED_BLOCK = (
    "def validate_cart(items):\n"
    "    total = 0\n"
    "    for item in items:\n"
    "        if item.quantity > 0 and item.price > 0:\n"
    "            total += item.quantity * item.price\n"
    "    return total\n"
)

# ── Accounts ─────────────────────────────────────────────────────────────

COMPANIES = [
    ("northwind@demo.pk", "Northwind Retail", 10000),
    ("vega@demo.pk", "Vega Logistics", 3000),
    ("meridian@demo.pk", "Meridian Bank", 0),
    ("karachicloud@demo.pk", "Karachi Cloud", 7500),
    ("saffron@demo.pk", "Saffron Foods", 4500),
    ("orbit@demo.pk", "Orbit Health", 6000),
]

# The real name is optional in the product, so one candidate leaves it blank.
CANDIDATES = [
    ("bilal@demo.pk", "quiet-falcon", "Quiet Falcon", "Bilal Ahmed"),
    ("ayesha@demo.pk", "pale-otter", "Pale Otter", "Ayesha Khan"),
    ("hira@demo.pk", "swift-heron", "Swift Heron", "Hira Sheikh"),
    ("usman@demo.pk", "calm-lynx", "Calm Lynx", "Usman Tariq"),
    ("sana@demo.pk", "sharp-moth", "Sharp Moth", "Sana Malik"),
    ("farhan@demo.pk", "bold-fox", "Bold Fox", ""),
]

# ── Challenges ───────────────────────────────────────────────────────────

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
        "title": "Speed up the search page",
        "company": "Karachi Cloud",
        "statement": (
            "Our product search takes four seconds on a list of fifty thousand "
            "items because it scans every row and sorts the whole result. Show "
            "us how you would make it fast, and say what you traded away."
        ),
        "reward": "PKR 60000",
        "start_day": 2,
        "end_day": 11,
    },
    {
        "title": "Write a refund email that keeps the customer",
        "company": "Saffron Foods",
        "statement": (
            "A customer got a cold delivery and asked for a refund. Write the "
            "reply. Give the refund, be honest about what went wrong, and do "
            "not sound like a form letter. Under one hundred and twenty words."
        ),
        "reward": "PKR 15000",
        "start_day": 1,
        "end_day": 7,
    },
    {
        "title": "Remind patients without annoying them",
        "company": "Orbit Health",
        "statement": (
            "Patients miss appointments and our reminders get muted. Design a "
            "reminder schedule and write the messages. Say how you would know "
            "it is working and when you would stop sending."
        ),
        "reward": "Interview",
        "start_day": 4,
        "end_day": 12,
    },
    {
        "title": "A CSV import that does not break",
        "company": "Northwind Retail",
        "statement": (
            "Shop owners upload product spreadsheets and half of them fail. "
            "Rows have missing prices, duplicate codes and commas inside "
            "names. Write an import that accepts good rows, reports bad ones "
            "clearly, and never half imports a file."
        ),
        "reward": "PKR 35000",
        "start_day": 5,
        "end_day": 13,
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

# ── Entries ──────────────────────────────────────────────────────────────

SUBMISSIONS = [
    # Challenge 1. This is the one the demo walks, so leave it alone.
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

    (1, "swift-heron", SHARED_BLOCK + "# Submitted as is.\n"),

    (1, "calm-lynx",
     "I would fix this by checking every item first. The quantity and the "
     "price both need to be valid numbers before they are multiplied, "
     "otherwise the answer comes out wrong."),

    # Challenge 2, rate limiting.
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

    (2, "quiet-falcon",
     "class FixedWindow:\n"
     "    def __init__(self, limit=60):\n"
     "        self.limit = limit\n"
     "        self.counts = {}\n"
     "    def allow(self, client, now):\n"
     "        minute = int(now // 60)\n"
     "        key = (client, minute)\n"
     "        used = self.counts.get(key, 0)\n"
     "        if used >= self.limit:\n"
     "            return False\n"
     "        self.counts[key] = used + 1\n"
     "        return True\n"
     "# A counter per client per minute. Cheap, and old keys can be dropped.\n"
     "# The weakness is the edge: a client can send sixty at 59 seconds and\n"
     "# sixty more at 61, so a sliding window is fairer if you can afford it.\n"),

    (2, "calm-lynx",
     "Sixty a minute per client. I would keep a counter in memory and reset "
     "it every minute, then return a clear message saying when they can try "
     "again."),

    # Challenge 3, onboarding copy.
    (3, "pale-otter",
     "Screen one. Saving starts small.\n"
     "Put aside whatever you can this week. Even two hundred rupees counts.\n\n"
     "Screen two. Pick your amount.\n"
     "Choose a number you will not miss. Change it any time, no questions.\n\n"
     "Screen three. Watch it grow.\n"
     "We add your profit every month. Take your money out whenever you want."),

    (3, "bold-fox",
     "Screen one: Welcome to your savings account.\n"
     "Screen two: Set up a monthly transfer from your bank.\n"
     "Screen three: Track your balance and profit in the app."),

    (3, "swift-heron",
     "Screen one. Start saving today with our easy to use savings solution "
     "designed for first time savers who want to build wealth.\n"
     "Screen two. Configure your automated deposit schedule.\n"
     "Screen three. Monitor your accrued profit."),

    # Challenge 4, search performance.
    (4, "quiet-falcon",
     "Three changes, in the order I would make them.\n\n"
     "1. Index the columns being filtered. A scan of fifty thousand rows\n"
     "   becomes a lookup. This alone is most of the four seconds.\n"
     "2. Sort and page in the database, not in the application. Ask for\n"
     "   twenty rows, not fifty thousand.\n"
     "3. Cache the ten most common searches for a minute.\n\n"
     "What I traded away: writes get slower because every index has to be\n"
     "updated, and the cache means a new product can be up to a minute late."),

    (4, "pale-otter",
     "The problem is that it sorts everything before taking the first page. "
     "Push the sort and the limit into the query so the database only returns "
     "what the page shows. Add an index on the name and category columns. "
     "The trade is slower inserts and more disk used by the indexes."),

    (4, "sharp-moth",
     "def search(term, page=1, size=20):\n"
     "    offset = (page - 1) * size\n"
     "    return db.query(\n"
     "        'SELECT * FROM products WHERE name ILIKE %s'\n"
     "        ' ORDER BY rank DESC LIMIT %s OFFSET %s',\n"
     "        (term, size, offset),\n"
     "    )\n"
     "# Paging in SQL instead of in Python is the whole fix.\n"
     "# A leading wildcard cannot use a normal index, so for real speed\n"
     "# this needs a trigram index or a full text column.\n"),

    # Challenge 5, refund email.
    (5, "quiet-falcon",
     "Hello,\n\n"
     "Your order arrived cold and that is on us. I have refunded the full "
     "amount to your original payment method, and you should see it within "
     "three working days.\n\n"
     "What happened: the order sat at our packing station for eleven minutes "
     "waiting for a rider. Our insulated bags hold heat for about six.\n\n"
     "We have changed the rule so no order leaves the kitchen until a rider "
     "is at the door. Sorry for the bad dinner."),

    (5, "calm-lynx",
     "Dear customer,\n\n"
     "We are sorry your food was cold. Your refund has been processed. We "
     "value your feedback and will use it to improve our service.\n\n"
     "Thank you for choosing Saffron Foods."),

    (5, "swift-heron",
     "Hi,\n\n"
     "Sorry about that. Refund is done. The rider was late. We will try to "
     "do better next time. Let us know if you need anything else."),

    (5, "bold-fox",
     "Hello,\n\n"
     "Refunded in full, no need to send anything back. Your rider was "
     "assigned late and the food sat for a quarter of an hour. That is long "
     "enough to ruin it and I am not going to pretend otherwise.\n\n"
     "If you order again this week, message me first and I will watch it "
     "through myself."),

    # Challenge 6, patient reminders.
    (6, "pale-otter",
     "Schedule: one message three days before, one the morning of, and "
     "nothing else.\n\n"
     "Three days before: Your appointment with Dr Iqbal is on Thursday at "
     "10am. Reply C to confirm or R to move it.\n\n"
     "Morning of: Today at 10am, clinic on the second floor. Bring your card.\n\n"
     "How I would know it works: missed appointments per hundred booked, "
     "compared with the month before. If somebody replies C we stop. If "
     "somebody ignores two in a row we stop messaging and call instead, "
     "because more messages to a person who is not reading them is just noise."),

    (6, "sharp-moth",
     "Two reminders, not five. One at three days so they can move it, one at "
     "twelve hours so they remember. Every message has a one tap way to "
     "confirm or reschedule, and confirming cancels the rest. Measure the no "
     "show rate and the opt out rate together, because you can drive no shows "
     "down and still be losing people who mute you."),

    (6, "calm-lynx",
     "Send a reminder one week before, three days before, one day before and "
     "one hour before so the patient definitely does not forget."),

    (6, "swift-heron",
     "Reminders should be sent by SMS and email. The patient can confirm the "
     "appointment. This reduces missed appointments."),

    # Challenge 7, CSV import.
    (7, "quiet-falcon",
     "def import_products(rows):\n"
     "    good, bad = [], []\n"
     "    seen = set()\n"
     "    for n, row in enumerate(rows, start=2):  # row 1 is the header\n"
     "        if not row.get('code'):\n"
     "            bad.append((n, 'missing product code'))\n"
     "        elif row['code'] in seen:\n"
     "            bad.append((n, 'duplicate code'))\n"
     "        elif not is_number(row.get('price')):\n"
     "            bad.append((n, 'price is not a number'))\n"
     "        else:\n"
     "            seen.add(row['code'])\n"
     "            good.append(row)\n"
     "    return good, bad\n"
     "# Read the whole file and collect problems first, then write the good\n"
     "# rows in one transaction. Nothing is saved if the write fails, so a\n"
     "# file is never half imported.\n"
     "# Commas inside names are handled by the csv module, not by splitting.\n"),

    (7, "pale-otter",
     "def load(path):\n"
     "    import csv\n"
     "    with open(path, newline='', encoding='utf-8-sig') as f:\n"
     "        rows = list(csv.DictReader(f))\n"
     "    errors = [r for r in rows if not r.get('price')]\n"
     "    if errors:\n"
     "        return {'ok': False, 'errors': errors}\n"
     "    save_all(rows)\n"
     "    return {'ok': True, 'count': len(rows)}\n"
     "# utf-8-sig because Excel writes a byte order mark and it breaks the\n"
     "# first column name. DictReader handles quoted commas for us.\n"),

    (7, "sharp-moth",
     "Validate first, write second. Read the file into memory, check every "
     "row for a code, a numeric price and no duplicate, and build a list of "
     "problems with row numbers. If the list is empty, write everything in "
     "one transaction. If it is not, show the owner the row numbers and "
     "import nothing. Half an import is worse than no import."),

    (7, "bold-fox",
     "Use the csv library so quoted commas do not break. Skip rows with no "
     "price and tell the user which line numbers were skipped."),
]

# ── Conversations ────────────────────────────────────────────────────────
# (challenge_id, ghost_id, [(sender, kind, body), ...])
# A company can only write to somebody who entered that challenge.

CONVERSATION = [
    (1, "quiet-falcon", [
        ("company", "tap", "You won this one. Yours was the only entry that handled an empty cart without us having to ask."),
        ("ghost", "reply", "Thank you. Do you want me to unmask, or can we talk first?"),
        ("company", "reply", "Talk first, always. Nothing goes further without your say so."),
        ("ghost", "reply", "That works. What does the team look like?"),
        ("company", "reply", "Four engineers on checkout, mostly Python. Remote three days a week, office in Karachi the other two."),
    ]),
    (1, "pale-otter", [
        ("company", "tap", "We would like to talk. Your cart summary was the most thorough one we read."),
        ("ghost", "reply", "Happy to. What would the role actually involve day to day?"),
        ("company", "reply", "Backend work on the checkout team. Four people, mostly Python."),
    ]),
    (1, "calm-lynx", [
        ("company", "whisper", "Ranked second. You described the fix well, but we needed working code and there was none."),
        ("ghost", "reply", "Fair. I read the brief as asking for an approach. I will send code next time."),
    ]),
    (1, "swift-heron", [
        ("company", "whisper", "Eighty seven percent of your entry appears word for word in another one. We are not taking this further."),
    ]),

    (2, "sharp-moth", [
        ("company", "tap", "Your sliding window was the cleanest of the four. Are you open to a contract, three months to start?"),
        ("ghost", "reply", "Possibly. Is it remote, and what is the rate?"),
        ("company", "reply", "Fully remote. We pay in dollars, twice a month. Tell us your rate and we will work from there."),
    ]),
    (2, "quiet-falcon", [
        ("company", "whisper", "We liked that you named the weakness of a fixed window yourself. Most people hide that."),
        ("ghost", "reply", "It only matters at the boundary, but it matters."),
    ]),
    (2, "bold-fox", [
        ("company", "whisper", "Good explanation of a token bucket, and you were right that it handles bursts better. We went with the entry that shipped code."),
        ("ghost", "reply", "Understood. Are you running more of these?"),
        ("company", "reply", "Every few weeks. You are on the list."),
    ]),
    (2, "calm-lynx", [
        ("company", "whisper", "Right idea, but we could not tell from this whether you have built one."),
    ]),

    (3, "pale-otter", [
        ("company", "tap", "Two hundred rupees. That one line did more than the rest of the entries put together."),
        ("ghost", "reply", "It is the number that makes it feel possible. Everything else sounds like a bank."),
        ("company", "reply", "Exactly. Can we use this copy, and can we talk about more of it?"),
    ]),
    (3, "bold-fox", [
        ("company", "whisper", "Clear and short, but it reads like instructions rather than encouragement."),
    ]),
    (3, "swift-heron", [
        ("company", "whisper", "Accrued profit and automated deposit schedule are the exact words the brief asked you to avoid."),
    ]),

    (4, "quiet-falcon", [
        ("company", "tap", "Numbered, in order, with the trade named at the end. That is how we want our own engineers writing."),
        ("ghost", "reply", "Happy to talk. Is the search on Postgres?"),
        ("company", "reply", "Postgres, about fifty thousand rows now and growing fast."),
        ("ghost", "reply", "Then a trigram index is probably the next step after the basics."),
    ]),
    (4, "pale-otter", [
        ("company", "whisper", "You spotted the sort before the page, which is the real bug. A little thin on the trade off."),
        ("ghost", "reply", "Noted. I should have said the indexes cost us on write."),
    ]),
    (4, "sharp-moth", [
        ("company", "whisper", "The leading wildcard note at the bottom is the most useful sentence anybody wrote. Most entries missed it."),
        ("ghost", "reply", "It is the thing that catches people out. The query looks indexed and is not."),
    ]),

    (5, "quiet-falcon", [
        ("company", "tap", "Eleven minutes at the packing station. You told them the actual number and then what changed. Nobody else did."),
        ("ghost", "reply", "It is what I would want to read."),
    ]),
    (5, "bold-fox", [
        ("company", "whisper", "Strong voice, and offering to watch the next order yourself is a nice touch. Slightly too casual for our brand."),
        ("ghost", "reply", "Fair. I would keep the honesty and lose the last line."),
        ("company", "reply", "That would be exactly right."),
    ]),
    (5, "calm-lynx", [
        ("company", "whisper", "We value your feedback is the form letter the brief asked you not to write."),
    ]),
    (5, "swift-heron", [
        ("company", "whisper", "Short is good. This is short and says nothing, which is not the same thing."),
    ]),

    (6, "pale-otter", [
        ("company", "tap", "Stopping after two ignored messages is the part every other entry missed. When can you talk?"),
        ("ghost", "reply", "This week works. Do you have the current no show rate?"),
        ("company", "reply", "Around eighteen percent. We would like it under ten."),
    ]),
    (6, "sharp-moth", [
        ("company", "whisper", "Measuring no shows and opt outs together is the right instinct. Very close to the top on this one."),
        ("ghost", "reply", "Thanks. Driving one down while the other climbs is the trap."),
    ]),
    (6, "calm-lynx", [
        ("company", "whisper", "Four reminders is how you get muted. The brief was about not annoying people."),
    ]),
    (6, "swift-heron", [
        ("company", "whisper", "This says reminders reduce missed appointments, which is the thing we told you in the brief."),
    ]),

    (7, "quiet-falcon", [
        ("company", "tap", "One transaction, row numbers starting at two because of the header. You have clearly done this before."),
        ("ghost", "reply", "I have cleaned up after an import that failed halfway. Once is enough."),
    ]),
    (7, "sharp-moth", [
        ("company", "whisper", "Half an import is worse than no import. We are putting that sentence in our engineering notes."),
    ]),
    (7, "pale-otter", [
        ("company", "whisper", "The byte order mark catch is real and most people learn it the hard way. Validation is a bit thin though."),
        ("ghost", "reply", "I only checked the price. Codes and duplicates need it too."),
    ]),
    (7, "bold-fox", [
        ("company", "whisper", "Right library, right instinct on the commas. Skipping bad rows silently is the part we cannot ship."),
        ("ghost", "reply", "Understood. Report them rather than skip them."),
    ]),
]

# A question asked on a challenge and answered by the company. The answer also
# lands in the asker inbox, which is where the answer kind of message comes from.
QUESTIONS = [
    (2, "bold-fox",
     "Does the limit need to survive a restart, or is in memory fine?",
     "In memory is fine for this. Say so in your answer if you assume it."),
    (6, "calm-lynx",
     "Is this SMS only, or can we assume the app can send notifications?",
     "Assume SMS. Many of our patients do not have the app installed."),
    (4, "sharp-moth",
     "Is the search on Postgres or MySQL?",
     "Postgres 16. Anything Postgres specific is fair game."),
]


def run():
    # Drop and rebuild, so running this twice never leaves half the old demo
    # data behind and the row ids stay predictable for the presentation.
    db.reset()

    # One hash for every demo account. Hashing is deliberately slow, so doing
    # it a dozen times would make the seed take seconds for no reason.
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

    for challenge_id, ghost_id, messages in CONVERSATION:
        for sender, kind, body in messages:
            db.execute(
                "INSERT INTO messages (challenge_id, ghost_id, kind, sender, body)"
                " VALUES (%s, %s, %s, %s, %s)",
                (challenge_id, ghost_id, kind, sender, body),
            )

    print("seeded", len(COMPANIES), "companies,", len(CANDIDATES), "candidates,",
          len(CHALLENGES), "challenges,", len(SUBMISSIONS), "entries and",
          len(CONVERSATION), "conversations")
    print("every demo account uses the password", PASSWORD)
    print("database:", db.DATABASE_URL)


if __name__ == "__main__":
    run()
