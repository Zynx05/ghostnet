# GhostNet

Hiring based on what you can do, not who you are.

A company posts a real problem instead of a job advert. Anyone answers it under
a ghost name. The system scores every submission, ranks them, and only then
reveals who wrote the winning one.

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

## The demo, in order

1. **Challenges.** Open *Fix the cart total bug*. Four people answered it.
2. **Submissions.** Every one is a ghost id. No name anywhere on the screen.
3. **Rank submissions.** Every scoring algorithm runs in that one request.
   Read the table left to right: relevance, quality, structure, copied, final.
4. **Ghost 003 is buried.** Its plagiarism score is high because it copied a
   block from ghost 002, and the longest copied passage column shows the exact
   text that was lifted.
5. **Reveal the winner.** The name appears for the first time, together with a
   Merkle proof of the win.
6. **Proof chain.** The win is now a block, linked by hash to the one before it.
7. **Matching** and **Schedule** are shown on their own.

## Layout

```
ghostnet/
  backend/
    main.py            the API, thin on purpose
    db.py              three tables. SQLite locally, PostgreSQL deployed
    seed.py            demo data, including one deliberate copy
    benchmark.py       measured growth for the report
    algorithms/        nine algorithms, written by hand
    tests/             one test per algorithm
  frontend/
    src/app/           five screens
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
* **plagiarism** the worst overlap against any other submission, found with a
  rolling hash. It multiplies rather than adds, so copied work cannot win on
  the strength of the other columns

The weights sit at the top of `algorithms/ranker.py` where anyone can read them.

## Who owns what

| Member | Role | File they own | Algorithm |
| --- | --- | --- | --- |
| 1 | Algorithm Engineer | `algorithms/tfidf.py` | Cosine similarity over tf idf |
| 2 | Backend Developer | `main.py`, `algorithms/levenshtein.py` | Edit distance |
| 3 | Frontend Developer | `frontend/src/`, `lib/mergeSort.ts` | Merge sort |
| 4 | Database Engineer | `db.py`, `algorithms/rabin_karp.py` | Rabin Karp |
| 5 | QA Engineer | `tests/`, `algorithms/suffix_array.py` | Suffix array |
| 6 | DevOps | `setup_db.py`, `ci.yml`, `algorithms/complexity.py` | Cyclomatic complexity |
| 7 | Blockchain Developer | `algorithms/merkle.py`, `app/chain` | Merkle tree and hash chain |
| 8 | Product Manager | `docs/ROADMAP.md`, `algorithms/gale_shapley.py` | Stable matching |
| 9 | UI and UX Designer | `docs/DESIGN.md`, `app/schedule` | Greedy interval scheduling |
| 10 | Docs and Research | `README.md`, `benchmark.py` | Complexity analysis of all nine |

## What this is not

No login, no payments, no real blockchain network, and no machine learning. The
MVP proves one claim only, that work can be ranked without knowing whose work it
is, and everything that does not serve that claim was left out.
