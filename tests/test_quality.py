"""Tests for src.quality checks."""

import pandas as pd
import pytest

from src.quality import check_no_nulls, check_not_empty, check_ranges, run_all_checks


def _good_df():
    return pd.DataFrame(
        {
            "timestamp": ["2024-01-01T00:00:00", "2024-01-01T01:00:00"],
            "temperature_c": [10.5, 11.0],
            "humidity_pct": [50, 55],
        }
    )


def test_check_not_empty_passes_on_nonempty_df():
    check_not_empty(_good_df())  # should not raise


def test_check_not_empty_raises_on_empty_df():
    empty_df = pd.DataFrame(columns=["timestamp", "temperature_c", "humidity_pct"])

    with pytest.raises(ValueError):
        check_not_empty(empty_df)


def test_check_no_nulls_passes_when_no_nulls():
    check_no_nulls(_good_df(), ["temperature_c", "humidity_pct"])  # should not raise


def test_check_no_nulls_raises_on_null_column():
    df = _good_df()
    df.loc[0, "temperature_c"] = None

    with pytest.raises(ValueError):
        check_no_nulls(df, ["temperature_c"])


def test_run_all_checks_returns_passed_names():
    passed = run_all_checks(_good_df())

    assert "not_empty" in passed
    assert "no_nulls" in passed
    assert "ranges" in passed


def test_check_ranges_passes_on_valid_values():
    check_ranges(_good_df())  # should not raise


def test_check_ranges_raises_on_temperature_out_of_bounds():
    df = _good_df()
    df.loc[0, "temperature_c"] = 65.0

    with pytest.raises(ValueError):
        check_ranges(df)


def test_check_ranges_raises_on_humidity_above_100():
    df = _good_df()
    df.loc[0, "humidity_pct"] = 101

    with pytest.raises(ValueError):
        check_ranges(df)
