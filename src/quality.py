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


def run_all_checks(df: pd.DataFrame) -> list[str]:
    """Run every data-quality check, raising on the first failure.

    Returns the list of check names that passed.
    """
    passed = []

    check_not_empty(df)
    passed.append("not_empty")

    check_no_nulls(df, REQUIRED_COLUMNS)
    passed.append("no_nulls")

    return passed
