"""CLI entry point wiring extract -> transform -> quality -> load."""

import argparse
from typing import Any

from src.extract import fetch_weather
from src.load import load_to_sqlite
from src.quality import run_all_checks
from src.transform import to_dataframe


def build_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Fetch, validate, and store weather data from Open-Meteo."
    )
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument(
        "--db", type=str, default="weather.db", help="Path to the SQLite database"
    )
    return parser


def main() -> None:
    parser: argparse.ArgumentParser = build_parser()
    args: argparse.Namespace = parser.parse_args()

    raw: dict[str, Any] = fetch_weather(args.lat, args.lon)
    df = to_dataframe(raw)
    run_all_checks(df)
    inserted: int = load_to_sqlite(df, args.db)

    print(f"Loaded {inserted} rows into {args.db}")


if __name__ == "__main__":
    main()
