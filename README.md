# weather-etl-pipeline

A lightweight, dependency-minimal **batch ETL pipeline** for weather data.
It extracts hourly forecast data from the public [Open-Meteo](https://open-meteo.com/)
API, transforms it into a clean tabular format, validates it against a set
of data-quality checks, and loads it into a local SQLite database.

Built to be simple to read, simple to run, and fully reproducible —
Python only, no cloud accounts, no API keys.

## Project status

🚧 **In development.** Extraction is implemented; transform, load, and
data-quality modules are being built incrementally. See [plan.md](plan.md)
for the full build sequence and current progress.

| Stage | Status |
|---|---|
| Extract (Open-Meteo → JSON) | ✅ Implemented |
| Transform (JSON → DataFrame) | ✅ Implemented |
| Load (DataFrame → SQLite) | ✅ Implemented |
| Data-quality checks | ✅ Implemented |
| CLI entry point | ⬜ Not started |

## Tech stack

| Concern | Choice |
|---|---|
| Language | Python 3.11+ |
| HTTP client | [`requests`](https://pypi.org/project/requests/) |
| Data handling | [`pandas`](https://pypi.org/project/pandas/) |
| Storage | SQLite (`sqlite3`, standard library) |
| Testing | [`pytest`](https://pypi.org/project/pytest/) |
| Linting | [`ruff`](https://pypi.org/project/ruff/) |
| CI | GitHub Actions |
| Data source | [Open-Meteo API](https://open-meteo.com/) (free, no API key) |

## Project structure

```
weather-etl-pipeline/
├── .github/workflows/ci.yml   # lint + test on every push/PR
├── src/
│   ├── extract.py             # fetch raw JSON from Open-Meteo
│   ├── transform.py           # JSON → clean pandas DataFrame
│   ├── load.py                # DataFrame → SQLite table
│   └── quality.py             # data-quality assertions
├── tests/                     # pytest suite, mirrors src/
├── main.py                    # CLI entry point wiring E→T→L→Q
├── requirements.txt
├── ruff.toml
└── plan.md                    # build plan and progress checklist
```

## Installation

```bash
git clone <repo-url>
cd weather-etl-pipeline
pip install -r requirements.txt
```

## Usage

Not yet available — the CLI entry point (`main.py`) is still being built.
Once complete, the pipeline will be run as:

```bash
python main.py --lat 33.57 --lon -7.59 --db weather.db
```

This section will be updated with full usage instructions once the
pipeline is functional end-to-end.

## Testing

```bash
pytest -q
ruff check .
```

Both are also run automatically on every push via GitHub Actions.

## License

TBD.
