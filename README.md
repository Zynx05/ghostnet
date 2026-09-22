# GhostNet

Hiring based on what you can do, not who you are.

A company posts a real problem instead of a job advert. Candidates answer it
under a ghost name. The system scores every entry and ranks them. Closing a
challenge names the winning ghost for free. Seeing the person behind any ghost
costs the company Rs 1,500, once per candidate.

Design and Analysis of Algorithms project. University of Karachi, UBIT.

## Live

| What | Where |
| --- | --- |
| App | https://web-production-4bf9e.up.railway.app |
| API | https://api-production-cdf9.up.railway.app |
| API documentation | https://api-production-cdf9.up.railway.app/docs |
| Code | https://github.com/Zynx05/ghostnet |

All three services run in one Railway project: `web`, `api` and `Postgres`.
The frontend reads the API address from `NEXT_PUBLIC_API` at build time, and
the API reads the allowed browser origins from `ALLOWED_ORIGINS`, so neither
address is written into the code.

## Running it

You need Python 3.10 or newer and Node 20 or newer. No database to install.

### Backend, in its own terminal

```bash
cd backend
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

`seed.py` creates `backend/ghostnet.db` and fills it with the demo data.
Delete that file and run it again whenever you want a clean start.

### Frontend, in a second terminal

```bash
cd frontend
npm install
npm run dev
```

| What | Where |
| --- | --- |
| App | http://localhost:3000 |
| API documentation | http://localhost:8000/docs |

### Which database you get

The backend reads `DATABASE_URL`. If it is not set, it uses SQLite in a single
file, which is why nothing has to be installed.

| `DATABASE_URL` | What runs |
| --- | --- |
| not set | SQLite at `backend/ghostnet.db` |
| `postgresql://...` | PostgreSQL |

Railway sets it to a PostgreSQL address, so the deployed site runs on
PostgreSQL while laptops run on SQLite. The `api` job in CI runs against a real
PostgreSQL container on every push, which is what stops the two drifting apart.

To test against PostgreSQL on your own machine, install it, run
`python setup_db.py`, and put the address in `backend/.env`. See
`backend/.env.example`.

## Checking the work

From the `backend` folder. Neither of these needs a database at all, because
the algorithms do not know a database exists.

```bash
python -m pytest tests -v     # one test per algorithm
python benchmark.py           # measured time next to the claimed big O
```

## Accounts

Two kinds. Sign up takes an email and a password.

| Role | Gets | Can |
| --- | --- | --- |
| Candidate | A ghost name, generated | Enter challenges, practice, ask questions, read the inbox |
| Company | A balance in rupees | Post, rank, close, tap, whisper, answer, unmask |

Demo accounts, every password `demo1234`:

| Email | Who | Note |
| --- | --- | --- |
| bilal@demo.pk | Candidate, Quiet Falcon | Has a real name set |
| farhan@demo.pk | Candidate, Bold Fox | No real name. Stays masked even if unmasked |
| northwind@demo.pk | Company, Northwind Retail | Rs 10,000 balance |
| vega@demo.pk | Company, Vega Logistics | Rs 3,000, enough for two unmasks |
| meridian@demo.pk | Company, Meridian Bank | Rs 0, to show the balance check |

Money is demo money. The Add Rs 10,000 button on My challenges credits the
account and charges nobody. A real launch puts JazzCash or Easypaisa there.

## The demo, in order

1. Log in as **northwind@demo.pk**. My challenges shows the balance and one
   challenge with four entries.
2. Open *Fix the cart total bug*. Every entry is a ghost name. No person
   anywhere on the screen.
3. **Rank entries.** Every scoring algorithm runs in that one request. Read
   the table left to right: relevance, quality, structure, copied, score.
4. **Swift Heron is buried.** Its copied score is 87 percent because it lifted
   a block from Pale Otter.
5. **Close and announce winner.** The winner card names Quiet Falcon. Still
   a ghost.
6. **Unmask for Rs 1,500.** The name blurs in. The balance in the nav drops.
   Press it again, no charge.
7. Log out, log in as **bilal@demo.pk**. My Ghost shows the win sealed into
   the Skill Proof chain, and the Inbox has anything Northwind sent.
8. Practice and Leaderboard are self explanatory. Matching and Calendar are
   at /matching and /schedule, off the nav, for the viva.

## Layout

```
ghostnet/
  backend/
    main.py            the API, thin on purpose
    auth.py            sign up, log in, sessions, the balance
    ghosts.py          ghost names
    db.py              nine tables. SQLite locally, PostgreSQL deployed
    seed.py            demo data, including one deliberate copy
    benchmark.py       measured growth for the report
    algorithms/        nine algorithms, written by hand
    tests/             one test per algorithm
  frontend/
    src/app/           fifteen screens
    src/lib/           api client, shared types, merge sort in TypeScript
    src/components/    design system reused from an earlier project
  docs/                roadmap, design notes, viva sheet
    setup_db.py        creates the role, the database and the tables
  .github/workflows/   tests and build on every push
```

## Ground rule

Everything inside `backend/algorithms` is written by hand with no external
library. No scikit learn, no difflib, no library implementation of a Merkle
tree. That package is what the course grades, so it is the part nobody imports
their way out of.

Outside that package we use whatever is simplest, because none of it is graded.

## How a submission is scored

```
final = (0.45 x relevance + 0.25 x quality + 0.30 x structure) x (1 - plagiarism)
```

* **relevance** how close the text is to the problem statement, by cosine
  similarity over term frequency times inverse document frequency
* **quality** edit distance to the problem statement, normalised
* **structure** cyclomatic complexity, scored inside a healthy band of 3 to 10,
  so an essay with no logic and an unreadable function are both penalised
* **plagiarism** a two stage check against every entry that arrived earlier.
  A rolling hash finds exact shared text fast. Where it finds any, edit
  distance asks how much of the text is the same once a few words have been
  changed, which catches the copy that renamed its variables. The higher of
  the two is used. It multiplies rather than adds, so copied work cannot win
  on the strength of the other columns, and the person who submitted first is
  never blamed for being copied

The weights sit at the top of `algorithms/ranker.py` where anyone can read them.

## Who owns what

| Member | Role | File they own | Algorithm |
| --- | --- | --- | --- |
| 1 | Algorithm Engineer | `algorithms/tfidf.py` | Cosine similarity over tf idf |
| 2 | Backend Developer | `main.py`, `algorithms/levenshtein.py` | Edit distance, for Quality and for catching paraphrased copies |
| 3 | Frontend Developer | `frontend/src/`, `lib/mergeSort.ts` | Merge sort |
| 4 | Database Engineer | `db.py`, `algorithms/rabin_karp.py` | Rabin Karp |
| 5 | QA Engineer | `tests/`, `algorithms/suffix_array.py` | Suffix array |
| 6 | DevOps | `setup_db.py`, `ci.yml`, `algorithms/complexity.py` | Cyclomatic complexity |
| 7 | Blockchain Developer | `algorithms/merkle.py`, `app/chain` | Merkle tree and hash chain |
| 8 | Product Manager | `docs/ROADMAP.md`, `algorithms/gale_shapley.py` | Stable matching |
| 9 | UI and UX Designer | `docs/DESIGN.md`, `app/schedule` | Greedy interval scheduling |
| 10 | Docs and Research | `README.md`, `benchmark.py` | Complexity analysis of all nine |

## What this is not

No real payments, no email verification, no password reset, no real blockchain
network, and no machine learning. The MVP proves one claim, that work can be
ranked and sold on without knowing whose work it is, and everything that does
not serve that claim was left out.
