"""End-to-end integration test exercising the full pipeline.

The Open-Meteo API call is mocked so the test is deterministic and does
not depend on live network access or ever-changing forecast data.
"""

from unittest.mock import Mock, patch

from src.extract import fetch_weather
from src.load import load_to_sqlite
from src.quality import run_all_checks
from src.transform import to_dataframe

MOCK_RESPONSE = {
    "hourly": {
        "time": ["2024-01-01T00:00", "2024-01-01T01:00", "2024-01-01T02:00"],
        "temperature_2m": [18.2, 17.9, 17.5],
        "relative_humidity_2m": [64, 66, 68],
    }
}


def _mock_get(*args, **kwargs):
    response = Mock()
    response.status_code = 200
    response.json.return_value = MOCK_RESPONSE
    return response


@patch("src.extract.requests.get", side_effect=_mock_get)
def test_pipeline_end_to_end(mock_get, tmp_path):
    raw = fetch_weather(33.57, -7.59)
    df = to_dataframe(raw)
    run_all_checks(df)

    db_path = tmp_path / "weather.db"
    inserted = load_to_sqlite(df, str(db_path))

    assert inserted == 3
    assert df.iloc[0]["temperature_c"] == 18.2
    mock_get.assert_called_once()
