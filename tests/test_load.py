"""Tests for src.load.load_to_sqlite."""

import sqlite3

import pandas as pd

from src.load import load_to_sqlite

EXPECTED_SCHEMA = {
    "timestamp": "TEXT",
    "temperature_c": "REAL",
    "humidity_pct": "REAL",
}


def _sample_df():
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01T00:00:00", "2024-01-01T01:00:00"],
            "temperature_c": [10.5, 11.0],
            "humidity_pct": [50, 55],
        }
    )


def test_load_to_sqlite_returns_row_count(tmp_path):
    db_path = tmp_path / "weather.db"

    inserted = load_to_sqlite(_sample_df(), str(db_path))

    assert inserted == 2


def test_load_to_sqlite_creates_explicit_schema(tmp_path):
    db_path = tmp_path / "weather.db"

    load_to_sqlite(_sample_df(), str(db_path))

    conn = sqlite3.connect(str(db_path))
    try:
        columns = conn.execute("PRAGMA table_info(weather)").fetchall()
    finally:
        conn.close()

    actual_schema = {col[1]: col[2].upper() for col in columns}

    assert actual_schema == EXPECTED_SCHEMA


def test_load_to_sqlite_appends_on_repeated_calls(tmp_path):
    db_path = tmp_path / "weather.db"

    load_to_sqlite(_sample_df(), str(db_path))
    inserted_second = load_to_sqlite(_sample_df(), str(db_path))

    assert inserted_second == 2

    conn = sqlite3.connect(str(db_path))
    try:
        row_count = conn.execute("SELECT COUNT(*) FROM weather").fetchone()[0]
    finally:
        conn.close()

    assert row_count == 4
