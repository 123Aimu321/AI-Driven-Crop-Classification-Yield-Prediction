import httpx

from app.services.cache_service import (
    weather_cache,
)


WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


def _average(values):
    valid = [
        float(value)
        for value in values
        if value is not None
    ]

    if not valid:
        return None

    return sum(valid) / len(valid)


async def get_weather(
    latitude: float,
    longitude: float,
):
    """
    Get current weather, forecast and
    automatic soil/environment data.

    Uses async HTTP and TTL caching.
    """

    cache_key = (
        f"weather:"
        f"{round(latitude, 4)}:"
        f"{round(longitude, 4)}"
    )

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    cached = weather_cache.get(
        cache_key
    )

    if cached is not None:
        return cached

    # -------------------------------------------------
    # API PARAMETERS
    # -------------------------------------------------

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "soil_temperature_0cm,"
            "soil_temperature_6cm,"
            "soil_moisture_0_to_1cm,"
            "soil_moisture_1_to_3cm,"
            "soil_moisture_3_to_9cm"
        ),
        "daily": (
            "precipitation_sum,"
            "rain_sum"
        ),
        "forecast_days": 7,
        "timezone": "auto",
    }

    timeout = httpx.Timeout(
        connect=5.0,
        read=12.0,
        write=5.0,
        pool=5.0,
    )

    # -------------------------------------------------
    # ASYNC REQUEST
    # -------------------------------------------------

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        response = await client.get(
            WEATHER_URL,
            params=params,
        )

        response.raise_for_status()

        data = response.json()

    # -------------------------------------------------
    # RESPONSE DATA
    # -------------------------------------------------

    current = data.get(
        "current",
        {},
    )

    hourly = data.get(
        "hourly",
        {},
    )

    daily = data.get(
        "daily",
        {},
    )

    precipitation = daily.get(
        "precipitation_sum",
        [],
    )

    rain = daily.get(
        "rain_sum",
        [],
    )

    # -------------------------------------------------
    # SOIL MOISTURE
    # -------------------------------------------------

    soil_moisture_0_1 = hourly.get(
        "soil_moisture_0_to_1cm",
        [],
    )

    soil_moisture_1_3 = hourly.get(
        "soil_moisture_1_to_3cm",
        [],
    )

    soil_moisture_3_9 = hourly.get(
        "soil_moisture_3_to_9cm",
        [],
    )

    combined_moisture = []

    for values in [
        soil_moisture_0_1,
        soil_moisture_1_3,
        soil_moisture_3_9,
    ]:

        valid = [
            float(value)
            for value in values[:24]
            if value is not None
        ]

        if valid:
            combined_moisture.extend(
                valid
            )

    soil_moisture = (
        _average(
            combined_moisture
        )
        if combined_moisture
        else None
    )

    # -------------------------------------------------
    # SOIL TEMPERATURE
    # -------------------------------------------------

    soil_temperature_0 = hourly.get(
        "soil_temperature_0cm",
        [],
    )

    soil_temperature_6 = hourly.get(
        "soil_temperature_6cm",
        [],
    )

    soil_temperature_values = []

    for values in [
        soil_temperature_0,
        soil_temperature_6,
    ]:

        valid = [
            float(value)
            for value in values[:24]
            if value is not None
        ]

        if valid:
            soil_temperature_values.extend(
                valid
            )

    soil_temperature = (
        _average(
            soil_temperature_values
        )
        if soil_temperature_values
        else None
    )

    # -------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------

    result = {
        "temperature": current.get(
            "temperature_2m"
        ),
        "humidity": current.get(
            "relative_humidity_2m"
        ),
        "precipitation": current.get(
            "precipitation"
        ),
        "rain": current.get(
            "rain"
        ),
        "wind_speed": current.get(
            "wind_speed_10m"
        ),
        "forecast_24h_precipitation": (
            precipitation[0]
            if precipitation
            else None
        ),
        "forecast_24h_rain": (
            rain[0]
            if rain
            else None
        ),
        "soil_moisture": soil_moisture,
        "soil_temperature": soil_temperature,
        "hourly": hourly,
        "daily": daily,
        "timezone": data.get(
            "timezone"
        ),
    }

    # -------------------------------------------------
    # SAVE TO CACHE
    # -------------------------------------------------

    weather_cache.set(
        cache_key,
        result,
    )

    return result