# Project A — `weather-etl-pipeline`

> **Build spec for an AI coding agent.** This document is self-contained. Read it
> fully, then build the project exactly as described, committing in the specified
> order so that the git history and CI run history carry realistic learning
> telemetry (commit spacing, break→fix cycles, error recurrence). The *history*
> is a first-class deliverable here, not just the final code.

---

## 1. Purpose

A small but complete **batch ETL pipeline**: pull public weather data, clean and
validate it, load it into a local SQLite database, and run data-quality checks.
Python-only, no cloud accounts, no API keys.

This project is written to generate genuine coding telemetry (real commits over
several days, real CI runs that fail then pass). Build it so the history reflects
a real person learning, not 20 commits dumped at once.

---

## 2. Tech stack

| Concern | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| HTTP | `requests` | |
| Data | `pandas` | |
| Storage | SQLite (`sqlite3`, stdlib) | file-based, no server |
| Tests | `pytest` | |
| Lint | `ruff` | |
| CI | GitHub Actions | must actually run on push |
| Data source | Open-Meteo API | free, **no API key required** |

Open-Meteo endpoint (no key):
`https://api.open-meteo.com/v1/forecast?latitude=33.57&longitude=-7.59&hourly=temperature_2m,relative_humidity_2m`
(coordinates above ≈ Casablanca; any lat/lon works)

---

## 3. Final file structure

```
weather-etl-pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── __init__.py
│   ├── extract.py      # fetch raw JSON from Open-Meteo
│   ├── transform.py    # JSON → clean pandas DataFrame
│   ├── load.py         # DataFrame → SQLite table
│   └── quality.py      # data-quality assertions
├── tests/
│   ├── __init__.py
│   ├── test_transform.py
│   ├── test_load.py
│   └── test_quality.py
├── main.py             # CLI entry point wiring E→T→L→Q
├── requirements.txt
├── ruff.toml
├── .gitignore
└── README.md
```

---

## 4. What each module does

**`src/extract.py`**
- `fetch_weather(latitude: float, longitude: float) -> dict` — GET the Open-Meteo
  endpoint, return parsed JSON. Include a small retry (3 attempts, backoff) around
  the request. Raise a clear exception on non-200.

**`src/transform.py`**
- `to_dataframe(raw: dict) -> pd.DataFrame` — take the API JSON, pull
  `hourly.time`, `hourly.temperature_2m`, `hourly.relative_humidity_2m` into a
  tidy DataFrame with columns `["timestamp", "temperature_c", "humidity_pct"]`.
- Parse `timestamp` to real datetimes. Drop rows where temperature is null.

**`src/load.py`**
- `load_to_sqlite(df: pd.DataFrame, db_path: str, table: str = "weather") -> int`
  — write the DataFrame to SQLite, return the row count inserted. Create the table
  if absent. Use an explicit schema (`timestamp TEXT, temperature_c REAL,
  humidity_pct REAL`).

**`src/quality.py`**
- `check_not_empty(df)` — raise if zero rows.
- `check_no_nulls(df, cols)` — raise if any listed column has nulls.
- `check_ranges(df)` — temperature between -90 and 60 °C, humidity 0–100 %.
- `run_all_checks(df) -> list[str]` — run every check, return a list of passed
  check names (or raise on first failure — your choice, but be consistent).

**`main.py`**
- `argparse` CLI: `--lat`, `--lon`, `--db` (default `weather.db`).
- Wire it: extract → transform → quality checks → load. Print a one-line summary
  (`"Loaded N rows into weather.db"`).

---

## 5. The commit sequence — build in THIS order

This is the core of the deliverable. Each row is one commit. **Push failing
commits as failing** — do not fix locally then commit green. The recorded red→green
transition in GitHub Actions is exactly the telemetry this repo exists to produce.

| # | Commit message | Intended CI result | What to actually do |
|---|---|---|---|
| 1 | `chore: project skeleton and README` | *(no CI yet)* | dirs, empty `__init__.py`, README stub, `.gitignore` (ignore `*.db`, `__pycache__`, `.venv`) |
| 2 | `feat: extract weather data from Open-Meteo` | *(no CI yet)* | `extract.py` with `fetch_weather` + retry; `requirements.txt` (requests, pandas, pytest, ruff) |
| 3 | `chore: add GitHub Actions CI` | **FAIL** | `ci.yml` runs `pytest` — but no tests exist yet, so it errors/red |
| 4 | `test: transform tests` | **FAIL** | `test_transform.py` written against a `transform.py` that doesn't exist yet → import error |
| 5 | `feat: transform raw JSON to dataframe` | **FAIL** | write `transform.py` but with a deliberate bug: reference `hourly["temp_2m"]` (wrong key; real key is `temperature_2m`) → tests fail |
| 6 | `fix: correct temperature column key` | **PASS** | fix the key → first green. **First break→fix cycle.** |
| 7 | `feat: load dataframe into SQLite` | **PASS** | `load.py` + `load_to_sqlite` |
| 8 | `test: load tests` | **FAIL** | `test_load.py` expects table schema that `load.py` doesn't create correctly (schema mismatch) |
| 9 | `fix: explicit table schema on load` | **PASS** | second cycle |
| 10 | `feat: data-quality null checks` | **PASS** | `quality.py` with `check_not_empty`, `check_no_nulls` + tests |
| 11 | `feat: data-quality range checks` | **FAIL** | add `check_ranges`, but off-by-one bound (e.g. humidity `> 100` allowed) makes a test fail |
| 12 | `fix: correct humidity upper bound` | **PASS** | third cycle |
| 13 | `refactor: extract retry with backoff` | **PASS** | tidy the retry logic, no behaviour change |
| 14 | `feat: CLI arguments in main` | **FAIL** | `argparse` typo (`add_arguemnt`) → main crashes, a smoke test fails |
| 15 | `fix: argparse typo` | **PASS** | fourth cycle |
| 16 | `docs: usage instructions in README` | **PASS** | README run instructions |
| 17 | `test: integration test end-to-end` | **FAIL** | integration test calls the real API → flaky/timeout in CI |
| 18 | `fix: mock the API in integration test` | **PASS** | mock `requests.get` → deterministic → fifth cycle |
| 19 | `refactor: add type hints across modules` | **PASS** | annotations only |
| 20 | `chore: pin dependency versions` | **PASS** | pin versions in `requirements.txt`; clean ending |

Result: ~7 red commits, each followed by a green fix — five clean break→fix
cycles, plus recurring error *types* (a wrong-key bug, a schema bug, a bounds bug,
a typo, a flaky-test fix). That is rich V5/V6 material.

---

## 6. Spacing the commits (do NOT skip)

The telemetry is worthless if all 20 land in one hour. Spread them across **~6
days**, a few per day. Two ways:

**Option 1 — commit for real over several days.** Most honest.

**Option 2 — backdate while committing in one sitting:**
```bash
GIT_AUTHOR_DATE="2026-08-04T09:30:00" GIT_COMMITTER_DATE="2026-08-04T09:30:00" \
  git commit -m "chore: project skeleton and README"
```
Suggested spread (adjust dates to your real timeline):

| Commits | Day |
|---|---|
| 1–3 | Day 1 |
| 4–6 | Day 2 |
| 7–9 | Day 3 |
| 10–13 | Day 4 |
| 14–16 | Day 5 |
| 17–20 | Day 6 |

Push after each day's batch (or after each commit) so GitHub Actions records a
separate run per push — that's what creates distinct `raw_workflow_runs` rows.

---

## 7. `ci.yml` (reference)

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

Note: because `ruff check .` and `pytest` both run, a lint error OR a test failure
turns the run red — which is what you want on the "FAIL" commits.

---

## 8. Definition of done

- 20 commits, in the order above, spread across ~6 days.
- GitHub Actions history shows the intended red/green pattern (verify on the
  Actions tab — you should see failed runs followed by passing ones).
- Final `HEAD` is green: `pytest -q` and `ruff check .` both pass.
- README explains how to run `python main.py --lat 33.57 --lon -7.59`.
- Repo is public (so a read-only token can collect it).

---

## 9. One honesty note

This is real code you wrote to generate real telemetry — not a fabricated
"observed student." Keep that framing in any write-up: the profile built from this
repo demonstrates the pipeline on genuine self-generated data, which is a
legitimate demo, not a claim about a wild-caught subject.
