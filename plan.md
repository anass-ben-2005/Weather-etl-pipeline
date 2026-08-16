# plan.md — weather-etl-pipeline build plan

Source spec: [PROJECT_A_weather-etl-pipeline.md](PROJECT_A_weather-etl-pipeline.md)

This file is my working checklist. I check off one step at a time, in order.
After I finish a step, I ask for the git commands and run them myself —
nothing gets committed automatically.

---

## 0. Ground rules (read before starting)

1. **20 commits, exact order, exact messages.** The commit sequence in
   section 2 below is the deliverable, not just the code. Do not reorder,
   merge, or skip commits.
2. **Push failing commits as failing.** Several commits are *supposed* to
   break CI. Do NOT fix the bug locally before committing — commit the
   broken version first, let CI go red, then commit the fix separately.
   Fixing-then-committing-green defeats the whole point of this repo.
3. **No shortcuts on the bugs.** Each intentional bug (wrong JSON key,
   missing schema, off-by-one bound, argparse typo, unmocked API call in a
   test) must be the literal bug described — not a different bug that also
   happens to fail.
4. **Spread commits across ~6 days.** Either commit for real over several
   days, or backdate with `GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE` (see
   spec §6). Push each day's batch (or each commit) so GitHub Actions
   records a separate run per push.
5. **Python-only, no cloud accounts, no API keys.** Data source is the
   Open-Meteo public API (no key needed).
6. **I (the agent) never run `git add` / `git commit` / `git push`.** After
   each finished step I hand you the exact command(s) to run yourself.
7. **Repo must end up public** so CI/telemetry tooling can read it.
8. **Definition of done** (spec §8):
   - 20 commits, in order, spread across ~6 days.
   - Actions tab shows the intended red → green pattern.
   - Final `HEAD` is green: `pytest -q` and `ruff check .` both pass.
   - README explains `python main.py --lat 33.57 --lon -7.59`.
   - Repo is public.

---

## 1. Tech stack (fixed, do not substitute)

| Concern | Choice |
|---|---|
| Language | Python 3.11+ |
| HTTP | `requests` |
| Data | `pandas` |
| Storage | SQLite (`sqlite3`, stdlib) |
| Tests | `pytest` |
| Lint | `ruff` |
| CI | GitHub Actions |
| Data source | Open-Meteo API (no key) |

Open-Meteo endpoint:
`https://api.open-meteo.com/v1/forecast?latitude=33.57&longitude=-7.59&hourly=temperature_2m,relative_humidity_2m`

---

## 2. Final file structure (target)

```
weather-etl-pipeline/
├── .github/workflows/ci.yml
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── quality.py
├── tests/
│   ├── __init__.py
│   ├── test_transform.py
│   ├── test_load.py
│   └── test_quality.py
├── main.py
├── requirements.txt
├── ruff.toml
├── .gitignore
└── README.md
```

---

## 3. Module contracts

**`src/extract.py`**
- `fetch_weather(latitude: float, longitude: float) -> dict` — GET the
  Open-Meteo endpoint, return parsed JSON. Small retry (3 attempts,
  backoff). Raise a clear exception on non-200.

**`src/transform.py`**
- `to_dataframe(raw: dict) -> pd.DataFrame` — pull `hourly.time`,
  `hourly.temperature_2m`, `hourly.relative_humidity_2m` into columns
  `["timestamp", "temperature_c", "humidity_pct"]`. Parse `timestamp` to
  real datetimes. Drop rows where temperature is null.

**`src/load.py`**
- `load_to_sqlite(df, db_path: str, table: str = "weather") -> int` —
  write DataFrame to SQLite, return inserted row count. Create table if
  absent. Explicit schema: `timestamp TEXT, temperature_c REAL,
  humidity_pct REAL`.

**`src/quality.py`**
- `check_not_empty(df)` — raise if zero rows.
- `check_no_nulls(df, cols)` — raise if any listed column has nulls.
- `check_ranges(df)` — temperature -90..60 °C, humidity 0..100 %.
- `run_all_checks(df) -> list[str]` — run every check, return passed
  check names (or raise on first failure — pick one and be consistent).

**`main.py`**
- `argparse` CLI: `--lat`, `--lon`, `--db` (default `weather.db`).
- Wire: extract → transform → quality checks → load. Print
  `"Loaded N rows into weather.db"`.

---

## 4. The 20-commit build sequence — build in THIS order

Checklist format: `[ ]` step not started, mark done as I go.

- [x] **1.** `chore: project skeleton and README` — *(no CI yet)*
  dirs, empty `__init__.py` files, README stub, `.gitignore`
  (ignore `*.db`, `__pycache__`, `.venv`)

- [x] **2.** `feat: extract weather data from Open-Meteo` — *(no CI yet)*
  `extract.py` with `fetch_weather` + retry; `requirements.txt`
  (requests, pandas, pytest, ruff)

- [x] **3.** `chore: add GitHub Actions CI` — **expect FAIL**
  `ci.yml` runs `pytest` — no tests exist yet → red

- [x] **4.** `test: transform tests` — **expect FAIL**
  `test_transform.py` written against `transform.py` that doesn't exist
  yet → import error

- [x] **5.** `feat: transform raw JSON to dataframe` — **expect FAIL**
  write `transform.py` with a deliberate bug: reference
  `hourly["temp_2m"]` (wrong key; real key is `temperature_2m`) → tests
  fail

- [x] **6.** `fix: correct temperature column key` — **expect PASS**
  fix the key → first green. **1st break→fix cycle.**

- [x] **7.** `feat: load dataframe into SQLite` — **expect PASS**
  `load.py` + `load_to_sqlite`

- [x] **8.** `test: load tests` — **expect FAIL**
  `test_load.py` expects a table schema that `load.py` doesn't create
  correctly (schema mismatch)

- [x] **9.** `fix: explicit table schema on load` — **expect PASS**
  2nd break→fix cycle

- [x] **10.** `feat: data-quality null checks` — **expect PASS**
  `quality.py` with `check_not_empty`, `check_no_nulls` + tests

- [x] **11.** `feat: data-quality range checks` — **expect FAIL**
  add `check_ranges`, but off-by-one bound (e.g. humidity `> 100`
  allowed) makes a test fail

- [x] **12.** `fix: correct humidity upper bound` — **expect PASS**
  3rd break→fix cycle

- [x] **13.** `refactor: extract retry with backoff` — **expect PASS**
  tidy the retry logic, no behaviour change

- [x] **14.** `feat: CLI arguments in main` — **expect FAIL**
  `argparse` typo (`add_arguemnt`) → main crashes, a smoke test fails

- [x] **15.** `fix: argparse typo` — **expect PASS**
  4th break→fix cycle

- [x] **16.** `docs: usage instructions in README` — **expect PASS**
  README run instructions

- [x] **17.** `test: integration test end-to-end` — **expect FAIL**
  integration test calls the real API → flaky/timeout in CI

- [x] **18.** `fix: mock the API in integration test` — **expect PASS**
  mock `requests.get` → deterministic → 5th break→fix cycle

- [x] **19.** `refactor: add type hints across modules` — **expect PASS**
  annotations only

- [x] **20.** `chore: pin dependency versions` — **expect PASS**
  pin versions in `requirements.txt`; clean ending

Expected result: ~7 red commits, each followed by a green fix — five
clean break→fix cycles, plus recurring error *types* (wrong-key bug,
schema bug, bounds bug, typo, flaky-test fix).

---

## 5. Commit spacing (do NOT skip)

Do not land all 20 in one hour. Spread across **~6 days**.

**Option 1 — commit for real over several days.** Most honest, preferred.

**Option 2 — backdate while committing in one sitting:**
```bash
GIT_AUTHOR_DATE="2026-08-04T09:30:00" GIT_COMMITTER_DATE="2026-08-04T09:30:00" \
  git commit -m "chore: project skeleton and README"
```

Suggested spread:

| Commits | Day |
|---|---|
| 1–3 | Day 1 |
| 4–6 | Day 2 |
| 7–9 | Day 3 |
| 10–13 | Day 4 |
| 14–16 | Day 5 |
| 17–20 | Day 6 |

Push after each day's batch (or after each commit) so GitHub Actions
records a separate run per push — that's what creates distinct CI run
history.

---

## 6. `ci.yml` (reference implementation)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest -q
```

Both `ruff check .` and `pytest` run, so a lint error OR a test failure
turns the run red — that's intended on the "FAIL" commits.

---

## 7. Workflow for every step in this session

1. I implement exactly one commit's worth of change (per the table in
   §4), including the intentional bug if that row calls for one.
2. I tell you what changed and why, and confirm whether this row is
   supposed to be red or green.
3. I give you the exact commands to run yourself, e.g.:
   ```bash
   git add -A
   git commit -m "feat: transform raw JSON to dataframe"
   git push
   ```
   (using `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` prefix if we're
   backdating per §5)
4. You run it, confirm CI result on the Actions tab matches the
   "expect FAIL / expect PASS" column.
5. I mark the step `[x]` in this file's checklist and move to the next
   row.
6. I never run git commands myself in this project — that's always
   your action, on your machine, under your GitHub account.

---

## 8. Open items before commit #1

- [x] Confirm GitHub repo exists (or needs `git init` + remote add) —
  repo created at `github.com/anass-ben-2005/Weather-etl-pipeline`.
- [ ] Confirm repo is set to **public** (required by spec §8 for
  read-only telemetry collection) — check under repo Settings → General.
- [x] Confirm which lat/lon to use as the default in README/CLI examples
  — used `--lat 33.57 --lon -7.59` (Casablanca) throughout.

## 9. Build complete

All 20 commits from §4 have been made, in order, matching the intended
red/green CI pattern (7 red commits, each followed by a green fix — 5
break→fix cycles). `HEAD` is green: `pytest -q` and `ruff check .` both
pass. Remaining: confirm the repo visibility item above, and verify the
Actions tab shows the full red→green history end to end.
