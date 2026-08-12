"""Tests for src.transform.to_dataframe."""

import pandas as pd

from src.transform import to_dataframe


def _raw_payload(times, temps, humidities):
    return {
        "hourly": {
            "time": times,
            "temperature_2m": temps,
            "relative_humidity_2m": humidities,
        }
    }


def test_to_dataframe_has_expected_columns():
    raw = _raw_payload(
        ["2024-01-01T00:00", "2024-01-01T01:00"],
        [10.0, 11.0],
        [50, 55],
    )

    df = to_dataframe(raw)

    assert list(df.columns) == ["timestamp", "temperature_c", "humidity_pct"]
    assert len(df) == 2


def test_to_dataframe_drops_null_temperature_rows():
    raw = _raw_payload(
        ["2024-01-01T00:00", "2024-01-01T01:00"],
        [10.0, None],
        [50, 55],
    )

    df = to_dataframe(raw)

    assert len(df) == 1
    assert df.iloc[0]["temperature_c"] == 10.0


def test_to_dataframe_parses_timestamp_as_datetime():
    raw = _raw_payload(["2024-01-01T00:00"], [10.0], [50])

    df = to_dataframe(raw)

    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
