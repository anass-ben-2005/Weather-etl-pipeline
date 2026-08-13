"""Load a transformed weather DataFrame into SQLite."""

import sqlite3

import pandas as pd


def load_to_sqlite(df: pd.DataFrame, db_path: str, table: str = "weather") -> int:
    """Write a weather DataFrame to a SQLite table.

    Creates the table if it doesn't already exist and appends the
    DataFrame's rows. Returns the number of rows inserted.
    """
    out = df.copy()
    if pd.api.types.is_datetime64_any_dtype(out["timestamp"]):
        out["timestamp"] = out["timestamp"].astype(str)

    conn = sqlite3.connect(db_path)
    try:
        out.to_sql(table, conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()

    return len(out)
