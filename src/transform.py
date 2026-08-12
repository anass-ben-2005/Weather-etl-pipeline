"""Transform raw Open-Meteo JSON into a clean pandas DataFrame."""

import pandas as pd


def to_dataframe(raw: dict) -> pd.DataFrame:
    """Convert raw Open-Meteo API JSON into a tidy DataFrame.

    Returns a DataFrame with columns ["timestamp", "temperature_c",
    "humidity_pct"]. Rows with a null temperature are dropped.
    """
    hourly = raw["hourly"]

    df = pd.DataFrame(
        {
            "timestamp": hourly["time"],
            "temperature_c": hourly["temp_2m"],
            "humidity_pct": hourly["relative_humidity_2m"],
        }
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.dropna(subset=["temperature_c"])

    return df
