# weather-etl-pipeline

A lightweight, dependency-minimal **batch ETL pipeline** for weather data.
It extracts hourly forecast data from the public [Open-Meteo](https://open-meteo.com/)
API, transforms it into a clean tabular format, validates it against a set
of data-quality checks, and loads it into a local SQLite database.

Built to be simple to read, simple to run, and fully reproducible —
Python only, no cloud accounts, no API keys.

## Project status

✅ **Complete.** The full pipeline — extract, transform, validate, load —
runs via the `main.py` CLI, is fully type-hinted, covered by unit and
integration tests, linted, and CI-enforced on every push. See
[plan.md](plan.md) for the full build history.

| Stage | Status |
|---|---|
| Extract (Open-Meteo → JSON) | ✅ Implemented |
| Transform (JSON → DataFrame) | ✅ Implemented |
| Load (DataFrame → SQLite) | ✅ Implemented |
| Data-quality checks | ✅ Implemented |
| CLI entry point | ✅ Implemented |

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

Run the pipeline end-to-end for any latitude/longitude:

```bash
python main.py --lat 33.57 --lon -7.59
```

This fetches the current hourly forecast from Open-Meteo, cleans it,
runs data-quality checks, and writes the result into `weather.db` in
the current directory. On success it prints a one-line summary:

```
Loaded 168 rows into weather.db
```

### CLI arguments

| Flag | Required | Default | Description |
|---|---|---|---|
| `--lat` | ✅ | — | Latitude of the location to fetch |
| `--lon` | ✅ | — | Longitude of the location to fetch |
| `--db` | ❌ | `weather.db` | Path to the SQLite database file to write to |

### Example: custom coordinates and database path

```bash
python main.py --lat 40.71 --lon -74.01 --db new_york.db
```

### Inspecting the results

```bash
sqlite3 weather.db "SELECT * FROM weather LIMIT 5;"
```

## Testing

```bash
pytest -q
ruff check .
```

Both are also run automatically on every push via GitHub Actions.

## Contributing

This is a personal learning project and isn't actively seeking outside
contributions, but issues and suggestions are welcome.

## License

TBD.
