"""End-to-end integration test exercising the full pipeline."""

from src.extract import fetch_weather
from src.load import load_to_sqlite
from src.quality import run_all_checks
from src.transform import to_dataframe


def test_pipeline_end_to_end(tmp_path):
    raw = fetch_weather(33.57, -7.59)
    df = to_dataframe(raw)
    run_all_checks(df)

    db_path = tmp_path / "weather.db"
    inserted = load_to_sqlite(df, str(db_path))

    assert inserted == 168
    assert df.iloc[0]["temperature_c"] == 21.3
