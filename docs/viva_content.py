"""
The words for the viva sheet.
Owner: Docs and Research Lead (member 10).

Kept apart from the layout code so any member can fix their own page without
reading a single line of reportlab.

Writing rule for this file: short sentences and plain words. The reader is
nervous and standing up. Keep the real technical terms, but explain each one
the first time it appears.

Each member entry has:
    built       what this person actually made
    files       the files they own
    tools       what they used, and why that one
    steps       how their algorithm works
    cost        the big O, and where it comes from
    connects    how their part fits with everyone else
    problem     something that went wrong, and what they did
    qa          questions to expect, with answers
    show        what to open on the screen
"""

SHARED = {
    "what": (
        "GhostNet is hiring without names. A company posts a real problem "
        "instead of a job advert. Anyone can send an answer under a fake name "
        "called a ghost id. The system scores every answer and puts them in "
        "order. Only then does it show who wrote the winning one."
    ),
    "why_daa": (
        "The website is not the interesting part. The interesting part is this: "
        "how do you put fifty answers in a fair order when all you have is the "
        "work itself? That takes nine algorithms. Each of us owns one."
    ),
    "stack": [
        ["Backend", "Python 3.12, FastAPI, Uvicorn, Pydantic"],
        ["Database", "PostgreSQL 16, psycopg 3, a small connection pool"],
        ["Frontend", "Next.js 15, React 19, TypeScript, plain CSS"],
        ["Testing", "pytest, 14 tests, and none of them needs the database"],
        ["Automation", "GitHub Actions, three jobs, runs on every push"],
        ["Algorithms", "All written by hand. No library does the work for us"],
    ],
    "formula": (
        "final = (0.45 x relevance + 0.25 x quality + 0.30 x structure) "
        "x (1 - plagiarism)"
    ),
    "flow": [
        "A company posts a challenge. It is saved in the challenges table.",
        "People send answers. Each one gets a ghost id. The real name is saved in a column that the scoring never reads.",
        "Someone clicks Rank. That one request runs five algorithms over every answer and saves the scores.",
        "Merge sort puts the rows in order. The table appears, one column per algorithm.",
        "The company clicks Reveal. The real name shows for the first time, and the win is hashed into the proof chain.",
    ],
    "rules": [
        "Know your own algorithm well. The big O, why it is that, and one tiny example you can do on the board.",
        "Point at your file. Everyone owns at least one and it is listed on your page.",
        "Be ready to say what you built, not only what your algorithm does. Half the marks are in the first one.",
        "If you do not know, say you do not know and say how you would find out. That is better than guessing.",
        "Do not call your own work simple. Say what it costs instead.",
    ],
}


MEMBERS = [
    # ------------------------------------------------------------------ 1
    {
        "n": 1,
        "role": "Algorithm Engineer",
        "algorithm": "Cosine similarity with tf idf",
        "opening": (
            "I wrote the relevance score. It is the biggest part of the final "
            "mark. It answers one question: how close is this answer to what "
            "the company asked for?"
        ),
        "built": [
            "A function that breaks text into words. It removes punctuation and makes everything lowercase.",
            "Term frequency, or tf: how many times each word appears, divided by the length of the text.",
            "Inverse document frequency, or idf: how rare a word is across all the answers. Common words lose their weight.",
            "The vector builder and the cosine function. Both are about ten lines.",
            "One function, relevance_scores, that takes the problem and all the answers and gives back a score for each.",
        ],
        "files": [
            ["backend/algorithms/tfidf.py", "all of it, about 70 lines"],
        ],
        "tools": (
            "Python and nothing else. I import math for log and sqrt. I did not "
            "use numpy or scikit learn. A library would have done the work for "
            "me, and this is the work the course is marking."
        ),
        "steps": [
            "Break each text into words. Count each word. Divide by the number of words in that text. This is tf.",
            "Count how many texts each word appears in. Rare words get a high weight. Words in everything get almost zero. This is idf.",
            "Multiply tf by idf. Each text is now a list of numbers, one number per word. We call that a vector.",
            "Score is the dot product of two vectors divided by both their lengths. That is the cosine of the angle between them. It is always between 0 and 1.",
        ],
        "cost": (
            "O(N x L) to build all the vectors. N is how many answers there "
            "are, L is how long each one is. Comparing two vectors is O(V), "
            "where V is the number of words they share."
        ),
        "connects": (
            "ranker.py calls my function once with all the answers together. It "
            "has to be together, because idf needs to see the whole set. My "
            "number becomes the Relevance column and is 45 percent of the score."
        ),
        "problem": (
            "My first version just counted words. Long answers won, because "
            "they had more words. I fixed it by dividing by the text length. "
            "Then common words like the and and took over every comparison. "
            "That is the exact problem idf solves, so I added idf next."
        ),
        "qa": [
            ("Why cosine and not straight line distance?",
             "Straight line distance gets bigger when a text is longer. So a long answer would look far away from a short problem, even if it says the same thing. Cosine only looks at the angle, so length does not matter."),
            ("Why do you add 1 inside the log?",
             "It is called smoothing. A word that is in every text would give log of 1, which is 0. That would delete the word. Adding 1 keeps a small weight instead."),
            ("What is weak about this method?",
             "It only looks at which words appear, not their order. So it cannot tell a right answer from the same words in the wrong order. That is why it is 45 percent of the score and not all of it."),
            ("Why work out idf over all the answers instead of one at a time?",
             "idf describes the whole group, not one text. If you did it for one text alone the answer would always be the same number, so it would do nothing."),
        ],
        "show": (
            "The Relevance column in the ranking table. Ghost 001 is highest "
            "because it uses the same words as the problem. Then open tfidf.py "
            "and point at the cosine function."
        ),
    },

    # ------------------------------------------------------------------ 2
    {
        "n": 2,
        "role": "Backend Developer",
        "algorithm": "Levenshtein edit distance",
        "opening": (
            "I built the API. Everything else talks to it. My algorithm is edit "
            "distance. It counts the smallest number of letter changes that turn "
            "one text into another, and I use it for two jobs: how close an "
            "entry is to the brief, and catching copies that changed a few words."
        ),
        "built": [
            "The API. Accounts and sessions, challenges, entries, ranking, closing, paid unmasking, practice, messages, questions, the leaderboard and the proof chain.",
            "Pydantic models. A bad request is rejected with a clear message before any of our code runs.",
            "The lifespan handler. It opens the database pool when the server starts and closes it when the server stops.",
            "Role checks. A candidate cannot post, a company cannot enter, and a company can only touch a challenge it posted.",
            "Edit distance, using two rows instead of a full table, and the second stage of the copy check that uses it.",
        ],
        "files": [
            ["backend/main.py", "the API, about 700 lines, no logic"],
            ["backend/algorithms/levenshtein.py", "edit distance, similarity, copy_similarity"],
        ],
        "tools": (
            "FastAPI, because it writes the API documentation for us from the "
            "type hints, so /docs is never out of date. Uvicorn runs it. Pydantic "
            "checks the input. psycopg 3 talks to PostgreSQL through a pool."
        ),
        "steps": [
            "Make a table. Cell i, j holds the distance between the first i letters of one text and the first j letters of the other.",
            "Fill each cell with the smallest of three choices: insert a letter, delete a letter, or replace a letter. Replace is free if the two letters already match.",
            "The answer is the bottom right cell. Row i only needs row i minus 1, so we keep two rows and throw the rest away.",
            "Turn the distance into a score: one minus the distance divided by the longer text. Same text gives 1, nothing in common gives 0.",
        ],
        "cost": (
            "O(m x n) time. Every cell is filled once and there are m times n "
            "cells. O(n) memory, because only two rows exist at a time. This is "
            "the slowest algorithm in the project, which is exactly why it only "
            "runs on pairs that a cheaper check has already flagged."
        ),
        "connects": (
            "Copied is a two stage check. Rabin Karp sweeps every pair of entries "
            "looking for exact shared text, which is fast. Wherever it finds any, "
            "my edit distance asks how much of the text is still the same after a "
            "few words were changed. The higher of the two becomes the Copied "
            "score. Each entry is only compared against entries that arrived "
            "before it, so the first person to submit is never blamed for being "
            "copied."
        ),
        "problem": (
            "Rabin Karp only matches exact text. Somebody copied an answer and "
            "renamed two variables, and the exact check dropped from 100 percent "
            "to 61 percent, because every window that touched a renamed word "
            "missed. Edit distance still saw 83 percent of the letters unchanged. "
            "Running it on every pair would have been too slow, so it only runs "
            "where the fast check found something. That is a filter then confirm "
            "pattern, and it is how spam filters and virus scanners work too."
        ),
        "qa": [
            ("Show kitten turning into sitting.",
             "Replace k with s. Replace e with i. Add g at the end. Three changes. There is a test that checks this exact example."),
            ("Why dynamic programming and not simple recursion?",
             "Recursion solves the same small problem again and again. That is exponential time. The table solves each small problem once, which gives m times n."),
            ("Why run Rabin Karp first and edit distance second?",
             "Rabin Karp is linear in the text. Edit distance is m times n, so on fifty entries and a thousand pairs it would be the slow part of the whole ranking. Running it only on the pairs Rabin Karp flagged keeps the cost down and still catches the reworded copy."),
            ("Why is there a floor of 0.6 on the copy score?",
             "Any two pieces of code share letters. def, return, colons, spaces. Two completely unrelated entries still come out about 0.25 similar. Below the floor that is noise and counts as zero. Above it, the two texts really are the same text with edits."),
            ("What if the original author gets flagged too?",
             "They do not. Each entry is compared only against entries submitted before it. Whoever submitted first cannot have copied someone who came later, so their Copied score stays at zero and the copier takes the hit."),
            ("Why is your API so thin?",
             "Each route checks who is asking, calls one module, and returns JSON. Because there is no logic in it, all fourteen tests run with no server and no database."),
        ],
        "show": (
            "Open http://localhost:8000/docs, which FastAPI made from the type "
            "hints. Then the Copied column on the ranking table: Swift Heron at "
            "88 percent, and Pale Otter, who was copied from, at 13 percent."
        ),
    },

    # ------------------------------------------------------------------ 3
    {
        "n": 3,
        "role": "Frontend Developer",
        "algorithm": "Merge sort, written twice",
        "opening": (
            "I built every screen. I also own the sort that turns a list of "
            "scores into a leaderboard. It runs on the server for the first "
            "ranking, and again in the browser when you click a column."
        ),
        "built": [
            "Five screens. The challenge list, one challenge with submit and ranking, matching, schedule, and the proof chain.",
            "A typed API client, so every call to the backend goes through one file and errors are handled in one place.",
            "types.ts, which copies the shapes from the backend. If the backend changes, my editor shows a red line instead of the page going blank.",
            "The ranking table, where each column header also names the algorithm that made that number.",
            "Merge sort in TypeScript, used when you click a header.",
        ],
        "files": [
            ["frontend/src/app/", "the five screens"],
            ["frontend/src/lib/mergeSort.ts", "the algorithm"],
            ["frontend/src/lib/api.ts", "every call to the backend"],
            ["frontend/src/lib/types.ts", "the shapes the API sends back"],
        ],
        "tools": (
            "Next.js and React for the pages. TypeScript, because it catches a "
            "wrong field name while I type instead of during the demo. Plain "
            "CSS from our own design system. No component library and no chart "
            "library."
        ),
        "steps": [
            "Cut the list in half. Keep cutting until every piece has one item. One item is already in order.",
            "Join two ordered halves back together. Walk both with one pointer each and always take the bigger one first.",
            "There are log n levels of cutting, and each level touches all n items. That is where n log n comes from.",
            "If two scores are equal, take the left one first. This is what makes the sort stable.",
        ],
        "cost": (
            "O(n log n) every time. Best case, average case and worst case are "
            "all the same, which is the main reason we chose it. It needs O(n) "
            "extra space to hold the joined list."
        ),
        "connects": (
            "The backend sends rows already in order. Clicking a header sorts "
            "them again in the browser with no network call, so the table "
            "reorders instantly. types.ts is the agreement between my code and "
            "the backend developer's code."
        ),
        "problem": (
            "Next.js 15 changed how route parameters arrive. They come as a "
            "promise now, not a plain object, and the challenge page broke. I "
            "unwrap it with the React use hook. Separately, my first version "
            "used the built in sort. It is not guaranteed stable, so rows with "
            "equal scores jumped around on every click. Writing merge sort "
            "fixed that, and it is also the part the course marks."
        ),
        "qa": [
            ("Why merge sort and not quicksort?",
             "Quicksort can be O(n squared) in the worst case, and it is not stable. Rows with the same score would swap places every time the table redraws, which looks broken."),
            ("Why does stable matter here?",
             "Equal scores must keep the order the answers arrived in. If they do not, the ranking looks random and we cannot defend it."),
            ("Why write the same algorithm in two languages?",
             "To show that the cost belongs to the algorithm, not the language. Both versions are n log n."),
            ("Why not just use the built in sort?",
             "Because the algorithm is what the course is marking. The built in sort would hide it, and it is not guaranteed stable."),
        ],
        "show": (
            "Click any column header in the ranking table. It reorders with no "
            "network request. Then show mergeSort.ts next to merge_sort.py."
        ),
    },

    # ------------------------------------------------------------------ 4
    {
        "n": 4,
        "role": "Database Engineer",
        "algorithm": "Rabin Karp with a rolling hash",
        "opening": (
            "I designed the database, and I own the copying check. Hiding names "
            "is a database decision before it is anything else. My algorithm is "
            "what stops copied work from winning."
        ),
        "built": [
            "The three tables. challenges, submissions and results, with real types, foreign keys, and cascade delete.",
            "Two indexes. PostgreSQL does not index a foreign key by itself, and we filter on both of ours all the time.",
            "A unique rule on challenge id and ghost id in results. Running the ranking twice now updates the scores instead of adding a second copy.",
            "The connection pool, and the two helpers query and execute that the whole API uses.",
            "Rabin Karp, and the chunking that turns it into a copying percentage.",
        ],
        "files": [
            ["backend/db.py", "tables, pool, query and execute"],
            ["backend/algorithms/rabin_karp.py", "the search and the overlap score"],
        ],
        "tools": (
            "PostgreSQL 16, for real types and real rules. psycopg 3 as the "
            "driver, with a connection pool. Rows come back as dictionaries, "
            "which is what keeps the API file short."
        ),
        "steps": [
            "Treat a run of letters as one big number in base 256, kept small using modulo a large prime.",
            "Hash the pattern once. Hash the first window of the text once.",
            "Slide the window by one letter. Take away the letter that left, multiply by the base, add the letter that arrived. That is one step, not m steps.",
            "If two hashes match, still compare the real letters. Two different texts can share a hash by accident.",
        ],
        "cost": (
            "O(n + m) on average. The worst case is O(n x m), which happens if "
            "every window has the same hash as the pattern by accident and we "
            "have to check the letters every time."
        ),
        "connects": (
            "The copying score multiplies the final mark instead of being added "
            "to it. So a copied answer cannot win by being good in the other "
            "columns. Every other member's data goes through db.py."
        ),
        "problem": (
            "Running the ranking twice added a second set of rows, and the "
            "table showed every answer twice. I added a unique rule on "
            "challenge id and ghost id. Now the database makes it impossible "
            "instead of us hoping the code remembers to clean up."
        ),
        "qa": [
            ("Why is a matching hash not enough on its own?",
             "Two different texts can give the same hash. That is called a collision. Checking the real letters turns a maybe into a yes."),
            ("Why modulo a large prime?",
             "It keeps the numbers small enough for the computer to handle, and it spreads the hashes out so collisions are rare."),
            ("How do the tables hide the name?",
             "The real name is in a column that the scoring queries never ask for. So nobody has to remember the rule. The name is simply not in the SQL."),
            ("Why those two indexes?",
             "PostgreSQL indexes a primary key by itself but not a foreign key. We filter on both foreign keys in nearly every query. Without the indexes, every read has to scan the whole table."),
            ("What does the connection pool save?",
             "Opening a connection and logging in takes longer than most of our queries. The pool keeps a few open and lends them out, so we pay that cost once at startup instead of on every request."),
            ("How do you know the database side actually works?",
             "CI runs the whole API against a real PostgreSQL container on every push. It loads the demo data, ranks a challenge, reveals the winner and reads the proof chain. If any of that breaks, the build fails before anyone sees it."),
        ],
        "show": (
            "The Copied column. Ghost 003 is at 87 percent and comes last, even "
            "though its other scores are normal. Then open db.py and show the "
            "tables and the unique rule."
        ),
    },

    # ------------------------------------------------------------------ 5
    {
        "n": 5,
        "role": "QA Engineer",
        "algorithm": "Suffix array and longest common substring",
        "opening": (
            "I test what the team writes. My algorithm finds the exact piece of "
            "text that was copied. Rabin Karp says how much was copied. Mine "
            "says what was copied, word for word."
        ),
        "built": [
            "Twelve tests, one per algorithm. Every input is small enough to check by hand on the board.",
            "A test that proves changing an old win breaks every hash after it. That is the claim the whole proof chain rests on.",
            "A test that proves copied work scores 1.0 and unrelated work scores under 0.2.",
            "The suffix array, and the search for the longest shared piece of text.",
            "The test run that GitHub does on every push.",
        ],
        "files": [
            ["backend/tests/test_algorithms.py", "twelve tests, no database"],
            ["backend/algorithms/suffix_array.py", "suffix sort and the search"],
        ],
        "tools": (
            "pytest. A test is just a function with an assert in it, so there "
            "is nothing extra to learn. The tests import the algorithms "
            "directly, so they finish in under a second with no server and no "
            "database."
        ),
        "steps": [
            "Join the two texts with a separator character that is in neither of them.",
            "Take every suffix of the joined text. A suffix is what is left from a point to the end. Sort them all.",
            "Similar text now sits next to each other. Walk the sorted list and compare neighbours, but only pairs that came from different sides of the separator.",
            "The longest shared start among those pairs is the longest copied piece.",
        ],
        "cost": (
            "O(n log n x log n) to sort the suffixes. There are n log n "
            "comparisons and each one can compare up to n letters. Then O(n) to "
            "walk the sorted list once."
        ),
        "connects": (
            "The piece of text my algorithm finds is printed in the last column "
            "of the ranking table. So the copying percentage is not something "
            "the examiner has to take our word for."
        ),
        "problem": (
            "I found a real bug. An essay with no code was getting a perfect "
            "structure mark and coming first. The reason was that cyclomatic "
            "complexity only punished code that was too complicated. I reported "
            "it. Member 6 changed the score to a healthy range of 3 to 10, so "
            "an answer with no branching loses marks too. There is now a test "
            "that fails if anyone undoes it."
        ),
        "qa": [
            ("Why sort the suffixes at all?",
             "Sorting puts texts that start the same way next to each other. Then the longest shared piece is always between two neighbours, so one walk through the list finds it."),
            ("Why do you need the separator character?",
             "Without it, a match could start in the first text and run into the second. That would report a piece of text that is in neither of them."),
            ("Why are your test inputs so small?",
             "So every test can be checked by hand. If the examiner asks why a number is right, the answer is readable in the test instead of hidden in a debugger."),
            ("What would you improve?",
             "My suffix sort compares whole strings, which adds a factor of n. There are faster methods called DC3 and SA IS that give true O(n), but they are much harder to read and this is a teaching project."),
        ],
        "show": (
            "Run python -m pytest tests -v. Twelve tests, under a second, no "
            "database needed. Then the last column of the ranking table."
        ),
    },

    # ------------------------------------------------------------------ 6
    {
        "n": 6,
        "role": "DevOps Engineer",
        "algorithm": "Cyclomatic complexity",
        "opening": (
            "I make the project run the same way on ten different laptops, and "
            "I get it checked automatically on every push. My algorithm counts "
            "how tangled a piece of code is."
        ),
        "built": [
            "setup_db.py. It creates the user, the database and the tables, and prints a readable message when PostgreSQL is not running.",
            "Settings through the DATABASE_URL environment variable. The same code runs on a laptop, on a free cloud database, and in CI with no edits.",
            "A GitHub Actions pipeline with three jobs: algorithms, api and frontend.",
            "The health endpoint, which CI and any hosting service can check.",
            "Cyclomatic complexity, and the scoring range built on top of it.",
        ],
        "files": [
            ["backend/setup_db.py", "one command database setup"],
            [".github/workflows/ci.yml", "three jobs on every push"],
            ["backend/algorithms/complexity.py", "the measure"],
        ],
        "tools": (
            "GitHub Actions for the automatic checks. PostgreSQL installed the "
            "normal way instead of through Docker, because the team is on "
            "Windows laptops and one more heavy tool was not worth it. The CI "
            "job gets its own database from GitHub, so nobody installs it."
        ),
        "steps": [
            "Picture the code as a graph. Each statement is a node. Each jump between statements is an edge.",
            "The number of separate paths through it is E minus N plus 2. E is edges and N is nodes.",
            "For one function this becomes simpler: count the decision points and add 1. Every branch adds exactly one path.",
            "We count if, elif, for, while, case, catch, except, and, or, and the question mark operator.",
        ],
        "cost": "O(n) over the letters of the code, in one pass.",
        "connects": (
            "My score becomes the Structure column, worth 30 percent. My CI "
            "pipeline runs the QA tests and the frontend build, so a broken "
            "algorithm is caught before the demo, not during it."
        ),
        "problem": (
            "My first version gave full marks to anything under ten. So an "
            "essay with no code scored 1.0 and nearly won. QA found it. I "
            "changed it to a healthy range of 3 to 10. Too little branching "
            "means nothing was really built. Too much means it is a mess. Both "
            "ends now lose marks."
        ),
        "qa": [
            ("Why punish low complexity as well as high?",
             "A score of 1 or 2 means there is almost no branching. For a coding challenge that means nothing was really built. Without the lower limit, an essay beats working code. We saw that happen."),
            ("Why is 10 the upper limit?",
             "It is the number the industry normally uses for one function. Above it there are too many paths to test and it gets hard to read."),
            ("Why count keywords instead of properly reading the code?",
             "A proper reader only works for one language, and answers can be in any language. Counting keywords works for all of them. We are honest that it is an estimate."),
            ("Why did you drop Docker?",
             "It is one more tool for ten people to install on Windows laptops, and all it was doing was starting PostgreSQL. A setup script does the same job in code anyone on the team can read."),
            ("What does CI actually catch?",
             "Three things. The algorithm tests. A full check that the copied answer still comes last. And the frontend type check and build. If someone changes the scoring and copied work climbs, the build fails."),
        ],
        "show": (
            "The Structure column, with the path count under each score. Then "
            "ci.yml, and the line in the api job that says the copied answer "
            "must still come last."
        ),
    },

    # ------------------------------------------------------------------ 7
    {
        "n": 7,
        "role": "Blockchain Developer",
        "algorithm": "Merkle tree and a SHA 256 chain",
        "opening": (
            "A win has to be provable without trusting us. I built the Skill "
            "Proof record. Every win is hashed into a tree, and anyone can "
            "check one win using only a few hashes instead of the whole list."
        ),
        "built": [
            "The Merkle tree builder. It hashes the wins, then joins them in pairs going up until one hash is left.",
            "Proof making. It returns only the partner hashes on the path from one win up to the top, and remembers which side each one is on.",
            "Checking. It rebuilds the top hash from one win and its path.",
            "The hash chain, where every block carries the hash of the block before it.",
            "The proof chain screen, which prints the previous hash right above each block hash so you can see the link.",
        ],
        "files": [
            ["backend/algorithms/merkle.py", "tree, proof, check and chain"],
            ["frontend/src/app/chain/", "the screen"],
        ],
        "tools": (
            "hashlib for SHA 256, and nothing else. The tree, the proof, the "
            "checking and the chain are all written by hand. There is no "
            "network and no mining, and that is on purpose."
        ),
        "steps": [
            "Hash every win. These hashes are the bottom row of the tree, called the leaves.",
            "Hash each pair of neighbours together to make the row above. Repeat until one hash is left. That one is the root.",
            "To prove one win is in the tree, hand over the partner hash at each level. That is log n hashes, not n.",
            "The checker rebuilds the root from the win and the partners. If it matches the published root, the win is real.",
        ],
        "cost": (
            "O(n) to build the tree, because each node is hashed once. O(log n) "
            "to make or check one proof, because the tree has log n rows."
        ),
        "connects": (
            "The reveal endpoint returns the root, the winning leaf, and its "
            "proof. The chain endpoint links all revealed wins into blocks. "
            "This is what turns a ranking into a credential you can carry."
        ),
        "problem": (
            "If there is an odd number of wins, one node at some level has no "
            "partner. I pair that node with itself, which is what most real "
            "systems do. I also had to record whether each partner is on the "
            "left or the right. Hashing them in the wrong order gives a "
            "different root and the check fails."
        ),
        "qa": [
            ("Why a tree and not just a list of hashes?",
             "A list needs all n hashes to check one entry. A tree needs log n. With a thousand wins that is ten hashes instead of a thousand."),
            ("What stops someone changing an old win?",
             "Every block holds the hash of the block before it. Change block 0 and its hash changes, which changes block 1, and so on all the way down. There is a test that proves this."),
            ("Is this a real blockchain?",
             "No, and that is on purpose. A network needs mining and many computers. That takes weeks and shows nothing extra. The part that matters is that changes are visible, and the tree gives us that."),
            ("Why SHA 256 and not something faster?",
             "If someone could find a different input with the same hash, they could fake a win. SHA 256 makes that practically impossible. Something like MD5 would not."),
        ],
        "show": (
            "Reveal a winner, then read the root, the leaf and the proof path. "
            "Then the Proof chain page, where each block shows the previous "
            "hash above its own."
        ),
    },

    # ------------------------------------------------------------------ 8
    {
        "n": 8,
        "role": "Product Manager",
        "algorithm": "Gale Shapley stable matching",
        "opening": (
            "I decided what we would build, and just as importantly what we "
            "would not. My algorithm handles the last step. Several winners, "
            "several companies, and a pairing that nobody wants to walk away "
            "from."
        ),
        "built": [
            "The scope. One claim, tested end to end: work can be put in order without knowing whose work it is.",
            "A four sprint plan, showing what is done and what is still open.",
            "A decisions table that records every cut and the reason for it.",
            "The preference lists for both sides of the match.",
            "The proposal log, which records every offer, rejection and swap. The log is the explanation.",
        ],
        "files": [
            ["docs/ROADMAP.md", "sprints, decisions, and what we cut"],
            ["backend/algorithms/gale_shapley.py", "the matching"],
        ],
        "tools": (
            "Markdown for the roadmap, so it sits in the repository next to the "
            "code and changes with it, instead of living in a chat nobody can "
            "find later."
        ),
        "steps": [
            "Every free candidate makes an offer to the best company they have not asked yet.",
            "A company with no offer holds the one it just got.",
            "A company that already has an offer keeps whichever candidate it likes more and lets the other one go.",
            "Anyone let go goes back in the pool and offers further down their list. It always ends, because nobody asks the same company twice.",
        ],
        "cost": (
            "O(n squared). There are n candidates and each asks at most n "
            "companies, so at most n squared offers, and each one is quick. It "
            "always finishes, and the answer is always stable."
        ),
        "connects": (
            "Ranking picks the best answer. Matching handles what happens when "
            "several winners and several companies all have preferences. The "
            "Matching screen shows the log so you can argue with the result."
        ),
        "problem": (
            "My first version only returned the final pairs, and nobody could "
            "tell whether it was right. Adding the proposal log turned it from "
            "a black box into something you can follow line by line. That is "
            "also what makes it possible to present."
        ),
        "qa": [
            ("What does stable mean here?",
             "There is no candidate and company who both like each other more than what they got. If there were, those two would leave and pair up on their own, and the whole matching would fall apart."),
            ("Does it matter which side makes the offers?",
             "Yes. The side that offers gets the best stable result it can. The side that receives gets the worst. We let candidates offer, which fits the whole point of the product."),
            ("Why did you cut login and payments?",
             "Neither one proves the claim we are making. Both are in the out of scope list in the roadmap with the reason written down."),
            ("What would you build next?",
             "Company accounts, so a real company can post a challenge without us adding it by hand. Everything else on the cut list is further away."),
        ],
        "show": (
            "The Matching page. Click Run matching and read the log line by "
            "line. Then the decisions table in ROADMAP.md."
        ),
    },

    # ------------------------------------------------------------------ 9
    {
        "n": 9,
        "role": "UI and UX Designer",
        "algorithm": "Greedy interval scheduling",
        "opening": (
            "I decided how the product looks and how it reads. There is one "
            "rule: no screen ever shows a name next to a score. My algorithm "
            "picks which challenge time slots can run without clashing."
        ),
        "built": [
            "The screen order. Challenges, then one challenge, then the ranking, then the reveal. That is also the order we walk the demo.",
            "The design system for this project, built on tokens, so the whole app can be restyled from one block of CSS.",
            "The ranking table layout, where every column header also names the algorithm that made the number.",
            "The timeline on the schedule screen. It draws the time slots as bars instead of listing numbers.",
            "The accessibility rules. Colour only where it carries meaning, aria current on the active menu item, and a real label on every input.",
        ],
        "files": [
            ["docs/DESIGN.md", "the rules and the reasons"],
            ["frontend/src/app/ghostnet.css", "what the base system did not cover"],
            ["backend/algorithms/scheduling.py", "the greedy choice"],
        ],
        "tools": (
            "Plain CSS with variables. No framework and no component library. "
            "The look is called brutalist. It is black and white, and shapes "
            "come from thick black borders instead of from colour."
        ),
        "steps": [
            "Sort every time slot by when it ends, earliest first.",
            "Take the first one.",
            "Go through the rest. Take a slot only if it starts at or after the last one you took ended.",
            "That is the greedy choice. Finishing early leaves the most room for everything after it.",
        ],
        "cost": (
            "O(n log n). Walking the list is only O(n), so the sorting is the "
            "whole cost of this algorithm."
        ),
        "connects": (
            "Names are hidden in two places, and one of them is mine. The API "
            "never asks for the name column, and the TypeScript type says the "
            "name can be empty. So the compiler complains if a screen tries to "
            "show it before the reveal."
        ),
        "problem": (
            "At first the schedule was a list of numbers and nobody could see "
            "why a slot had been dropped. Drawing the slots as bars on one "
            "timeline made the overlap obvious. The greedy choice became "
            "something you can see instead of something we claim."
        ),
        "qa": [
            ("Why sort by end time and not start time, or shortest first?",
             "Sorting by start time can pick one long slot that blocks everything else. Shortest first can pick a small slot sitting across the middle of two others. Sorting by end time is the only one of the three we can prove is best."),
            ("How do you prove it is best?",
             "Take any best possible schedule. Swap its first slot for the one that ends earliest. The schedule is still valid and still the same size. So the greedy choice is never worse."),
            ("Where does the time go?",
             "The walk is O(n) and the sort is O(n log n), so the sort is what counts."),
            ("Why hide names in the design and not just in the API?",
             "Because hiding names is the product, not a rule. If a screen shows a name, the screen is wrong. That is why the type says the name can be empty."),
        ],
        "show": (
            "The Schedule page. Two slots kept in green, one dropped in grey, "
            "and you can see the overlap on the timeline."
        ),
    },

    # ------------------------------------------------------------------ 10
    {
        "n": 10,
        "role": "Docs and Research Lead",
        "algorithm": "Measuring the cost of all nine",
        "opening": (
            "Everyone else claims a big O. My job is to run the code and show "
            "whether the claim is true, and to write the whole thing down."
        ),
        "built": [
            "A benchmark that runs every algorithm at four growing input sizes and prints the measured milliseconds next to the claimed cost.",
            "The README, including the seven step demo we follow on presentation day.",
            "This viva sheet. The words come from a separate file so any member can fix their own page.",
            "The notes under the benchmark table, including the places where the measurement and the theory do not agree.",
        ],
        "files": [
            ["backend/benchmark.py", "the measuring"],
            ["README.md", "how to run it and how to demo it"],
            ["docs/viva_content.py", "the words on this sheet"],
        ],
        "tools": (
            "reportlab to build this PDF. Markdown for the report, so it lives "
            "in the repository. time.perf_counter for timing, because it only "
            "goes forwards and does not jump if the system clock changes."
        ),
        "steps": [
            "Make random input at four sizes: 100, 200, 400 and 800.",
            "Time every algorithm at each size and print it next to the claimed cost.",
            "Compare the growth. Doubling the input should roughly double an O(n log n) algorithm and roughly quadruple an O(n squared) one.",
            "Write down anywhere the measurement and the theory do not agree, and say why.",
        ],
        "cost": (
            "The benchmark runs ten algorithms at four sizes. The slowest "
            "column is edit distance, and that is what makes the point."
        ),
        "connects": (
            "Every other member quotes a cost on their page. This is the "
            "evidence for all of them, in one table."
        ),
        "problem": (
            "The Merkle proof is described as O(log n) but it measures as O(n). "
            "Our version rebuilds the whole tree before walking it, so the time "
            "is linear even though the proof it gives back is still only log n "
            "hashes. Instead of quietly relabelling it, the benchmark prints "
            "the note."
        ),
        "qa": [
            ("Which result is clearest?",
             "Edit distance. About 13, 51, 218 and 967 milliseconds at the four sizes. Every time the input doubles, the time goes up about four times. That is exactly what O(m x n) predicts."),
            ("Where does the measurement disagree with the theory?",
             "The Merkle proof, for the reason printed under the table. The theory is right about the proof size. Our code is just slower than it needs to be."),
            ("Why do the small sizes look noisy?",
             "At 100 items several algorithms finish in under a tenth of a millisecond. At that point the timer itself is most of what you are measuring. The growth only becomes clear at the bigger sizes."),
            ("What is the most expensive part of the ranking?",
             "Edit distance, by a long way. Everything else is linear or n log n. If this had to handle real traffic, that is the first thing to replace."),
        ],
        "show": (
            "Run python benchmark.py and read the table, then the notes printed "
            "under it."
        ),
    },
]
