import httpx

from datetime import datetime

from app.services.cache_service import (
    rainfall_cache,
)


HISTORICAL_WEATHER_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
)


async def get_annual_rainfall(
    latitude: float,
    longitude: float,
    year: int | None = None,
):
    """
    Automatically obtains annual rainfall
    from Open-Meteo historical weather data.

    Uses async HTTP and a 24-hour cache.

    By default, uses the previous completed year.
    """

    if year is None:
        year = datetime.now().year - 1

    cache_key = (
        f"rainfall:"
        f"{round(latitude, 4)}:"
        f"{round(longitude, 4)}:"
        f"{year}"
    )

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    cached = rainfall_cache.get(
        cache_key
    )

    if cached is not None:
        return cached

    # -------------------------------------------------
    # REQUEST
    # -------------------------------------------------

    timeout = httpx.Timeout(
        connect=5.0,
        read=15.0,
        write=5.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        response = await client.get(
            HISTORICAL_WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": (
                    f"{year}-01-01"
                ),
                "end_date": (
                    f"{year}-12-31"
                ),
                "daily": "precipitation_sum",
                "timezone": "auto",
            },
        )

        response.raise_for_status()

        data = response.json()

    # -------------------------------------------------
    # EXTRACT RAINFALL
    # -------------------------------------------------

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

        result = {
            "available": False,
            "message": (
                "Annual rainfall data "
                "is unavailable."
            ),
            "year": year,
            "annual_rainfall": None,
        }

    else:

        annual_rainfall = sum(
            valid_values
        )

        result = {
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

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    rainfall_cache.set(
        cache_key,
        result,
    )

    return result