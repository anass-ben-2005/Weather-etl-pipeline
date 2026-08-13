"""Load a transformed weather DataFrame into SQLite."""

import sqlite3

import pandas as pd

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS {table} (
    timestamp TEXT,
    temperature_c REAL,
    humidity_pct REAL
)
"""


def load_to_sqlite(df: pd.DataFrame, db_path: str, table: str = "weather") -> int:
    """Write a weather DataFrame to a SQLite table.

    Creates the table with an explicit schema if it doesn't already exist,
    then appends the DataFrame's rows. Returns the number of rows inserted.
    """
    out = df.copy()
    if pd.api.types.is_datetime64_any_dtype(out["timestamp"]):
        out["timestamp"] = out["timestamp"].astype(str)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(CREATE_TABLE_SQL.format(table=table))
        out.to_sql(table, conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()

    return len(out)
