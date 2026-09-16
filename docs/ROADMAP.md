# GhostNet roadmap

Owner: Product Manager (member 8)

## What the MVP proves

One claim, tested end to end: a company can pick the best submission without
ever seeing who wrote it, and the pick can be defended with numbers.

Everything not needed for that claim was left out on purpose. That list is at
the bottom, because being able to say what you cut, and why, is worth more in a
viva than a longer feature list.

## Sprints

### Sprint 1, week 2. Foundation
Status: done

* Roles fixed, one algorithm assigned per member
* Problem statement and scope agreed
* Repository laid out as backend, frontend, docs

### Sprint 2, week 3. Algorithms
Status: done

* Nine algorithms written by hand, no external library
* One unit test per algorithm, each checkable on paper
* Benchmark script comparing measured time against the claimed big O

### Sprint 3, week 4. Product
Status: done

* FastAPI routes over PostgreSQL
* Ranking pipeline joins the scoring algorithms into one score
* Frontend built on the design system, five screens

### Sprint 4, week 5. Presentation
Status: in progress

* Seed data that makes plagiarism visible during the demo
* Viva sheet, one page per member
* Dry run of the demo, timed

## Priority calls we made

| Decision | Why |
| --- | --- |
| SQLite on a laptop, PostgreSQL deployed | Nobody has to install a database to run the project, and the deployed site still gets real types and real constraints. The cost is that two paths exist. CI runs the API against real PostgreSQL on every push so they cannot drift apart |
| No Docker | One more tool to install, and the team is on Windows laptops where it is heavy. A setup script against a normal PostgreSQL install does the same job in a way everyone can read |
| No login | Authentication proves nothing about ranking, which is what is graded |
| No real blockchain | A Merkle tree and a hash chain show the same property without a network |
| Seeded data, not live users | A demo needs a known answer, otherwise nothing can be checked |
| Weights hardcoded and visible | The examiner will ask why the winner won, and the answer should be readable |

## Deliberately out of scope

Payments, email, file upload, company accounts, a mobile app, and any machine
learning model. Each of these is a week of work that adds nothing to the claim
the MVP is making.
