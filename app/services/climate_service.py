import requests
from datetime import datetime


HISTORICAL_WEATHER_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)


def get_annual_rainfall(
    latitude: float,
    longitude: float,
    year: int | None = None,
):
    """
    Automatically obtains annual rainfall
    from Open-Meteo historical weather data.

    By default, uses the previous completed year.
    """

    if year is None:
        year = datetime.now().year - 1

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    response = requests.get(
        HISTORICAL_WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "precipitation_sum",
            "timezone": "auto",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    daily = data.get(
        "daily",
        {},
    )

    rainfall_values = daily.get(
        "precipitation_sum",
        [],
    )

    valid_values = [
        float(value)
        for value in rainfall_values
        if value is not None
    ]

    if not valid_values:
        return {
            "available": False,
            "message": (
                "Annual rainfall data "
                "is unavailable."
            ),
            "year": year,
            "annual_rainfall": None,
        }

    annual_rainfall = sum(
        valid_values
    )

    return {
        "available": True,
        "source": (
            "Open-Meteo Historical Weather"
        ),
        "year": year,
        "annual_rainfall": round(
            annual_rainfall,
            2,
        ),
        "unit": "mm",
    }