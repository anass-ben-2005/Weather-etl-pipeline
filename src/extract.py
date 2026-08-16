"""Extract raw weather data from the Open-Meteo API."""

import time
from typing import Any

import requests

BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
MAX_ATTEMPTS: int = 3
BACKOFF_SECONDS: int = 2
REQUEST_TIMEOUT: int = 10


def _get_with_retry(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """GET a URL with retries and linear backoff, returning parsed JSON.

    Raises RuntimeError if every attempt fails or the API returns a
    non-200 status.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            last_error = exc
        else:
            if response.status_code == 200:
                return response.json()
            last_error = RuntimeError(
                f"Open-Meteo request failed with status {response.status_code}: "
                f"{response.text}"
            )

        if attempt < MAX_ATTEMPTS:
            time.sleep(BACKOFF_SECONDS * attempt)

    raise RuntimeError(
        f"Failed to fetch weather data after {MAX_ATTEMPTS} attempts: {last_error}"
    )


def fetch_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch hourly temperature and humidity data for a location."""
    params: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m",
    }
    return _get_with_retry(BASE_URL, params)
