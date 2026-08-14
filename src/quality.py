"""Data-quality checks for a transformed weather DataFrame."""

import pandas as pd

REQUIRED_COLUMNS = ["timestamp", "temperature_c", "humidity_pct"]


def check_not_empty(df: pd.DataFrame) -> None:
    """Raise ValueError if the DataFrame has zero rows."""
    if len(df) == 0:
        raise ValueError("Data-quality check failed: DataFrame is empty")


def check_no_nulls(df: pd.DataFrame, cols: list[str]) -> None:
    """Raise ValueError if any of the given columns contain nulls."""
    for col in cols:
        if df[col].isnull().any():
            raise ValueError(
                f"Data-quality check failed: column '{col}' contains null values"
            )


def check_ranges(df: pd.DataFrame) -> None:
    """Raise ValueError if temperature or humidity fall outside valid ranges.

    Temperature must be between -90 and 60 degrees Celsius. Humidity must
    be between 0 and 100 percent.
    """
    if (df["temperature_c"] < -90).any() or (df["temperature_c"] > 60).any():
        raise ValueError(
            "Data-quality check failed: temperature_c out of range (-90..60)"
        )

    if (df["humidity_pct"] < 0).any() or (df["humidity_pct"] > 100).any():
        raise ValueError(
            "Data-quality check failed: humidity_pct out of range (0..100)"
        )


def run_all_checks(df: pd.DataFrame) -> list[str]:
    """Run every data-quality check, raising on the first failure.

    Returns the list of check names that passed.
    """
    passed = []

    check_not_empty(df)
    passed.append("not_empty")

    check_no_nulls(df, REQUIRED_COLUMNS)
    passed.append("no_nulls")

    check_ranges(df)
    passed.append("ranges")

    return passed
