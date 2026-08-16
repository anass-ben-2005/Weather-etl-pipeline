"""Transform raw Open-Meteo JSON into a clean pandas DataFrame."""

from typing import Any

import pandas as pd


def to_dataframe(raw: dict[str, Any]) -> pd.DataFrame:
    """Convert raw Open-Meteo API JSON into a tidy DataFrame.

    Returns a DataFrame with columns ["timestamp", "temperature_c",
    "humidity_pct"]. Rows with a null temperature are dropped.
    """
    hourly: dict[str, Any] = raw["hourly"]

    df: pd.DataFrame = pd.DataFrame(
        {
            "timestamp": hourly["time"],
            "temperature_c": hourly["temperature_2m"],
            "humidity_pct": hourly["relative_humidity_2m"],
        }
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.dropna(subset=["temperature_c"])

    return df
