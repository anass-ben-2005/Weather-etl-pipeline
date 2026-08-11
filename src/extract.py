"""Extract raw weather data from the Open-Meteo API."""

import time

import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 2


def fetch_weather(latitude: float, longitude: float) -> dict:
    """Fetch hourly temperature and humidity data for a location.

    Retries up to MAX_ATTEMPTS times with a linear backoff if the request
    fails. Raises RuntimeError if all attempts fail or the API returns a
    non-200 status.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m",
    }

    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
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
