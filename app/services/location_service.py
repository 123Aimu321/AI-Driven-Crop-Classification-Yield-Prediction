import httpx

from app.services.cache_service import (
    location_cache,
)


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

REVERSE_URL = (
    "https://nominatim.openstreetmap.org/reverse"
)


HEADERS = {
    "User-Agent": (
        "AI-Crop-Prediction/1.0 "
        "(agricultural-research-project)"
    )
}


async def search_location(
    place: str,
):
    """
    Search location using Open-Meteo.

    Results are cached for one hour.
    """

    place = place.strip()

    if not place:
        return []

    cache_key = (
        f"location:"
        f"{place.lower()}"
    )

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    cached = location_cache.get(
        cache_key
    )

    if cached is not None:
        return cached

    # -------------------------------------------------
    # REQUEST
    # -------------------------------------------------

    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=5.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        response = await client.get(
            GEOCODING_URL,
            params={
                "name": place,
                "count": 5,
                "language": "en",
                "format": "json",
            },
        )

        response.raise_for_status()

        data = response.json()

    # -------------------------------------------------
    # NORMALIZE RESULTS
    # -------------------------------------------------

    results = []

    for item in data.get(
        "results",
        [],
    ):

        results.append(
            {
                "name": item.get(
                    "name"
                ),
                "state": item.get(
                    "admin1"
                ),
                "country": item.get(
                    "country"
                ),
                "country_code": item.get(
                    "country_code"
                ),
                "latitude": item.get(
                    "latitude"
                ),
                "longitude": item.get(
                    "longitude"
                ),
            }
        )

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    location_cache.set(
        cache_key,
        results,
    )

    return results


async def reverse_geocode(
    latitude: float,
    longitude: float,
):
    """
    Reverse geocode coordinates.

    Results are cached for one hour.
    """

    cache_key = (
        f"reverse:"
        f"{round(latitude, 4)}:"
        f"{round(longitude, 4)}"
    )

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    cached = location_cache.get(
        cache_key
    )

    if cached is not None:
        return cached

    # -------------------------------------------------
    # REQUEST
    # -------------------------------------------------

    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=5.0,
        pool=5.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:

        response = await client.get(
            REVERSE_URL,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 10,
                "addressdetails": 1,
            },
            headers=HEADERS,
        )

        response.raise_for_status()

        data = response.json()

    # -------------------------------------------------
    # ADDRESS
    # -------------------------------------------------

    address = data.get(
        "address",
        {},
    )

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or "Unknown"
    )

    result = {
        "name": city,
        "state": address.get(
            "state"
        ),
        "country": address.get(
            "country"
        ),
        "country_code": address.get(
            "country_code"
        ),
        "latitude": latitude,
        "longitude": longitude,
        "display_name": data.get(
            "display_name"
        ),
    }

    # -------------------------------------------------
    # CACHE
    # -------------------------------------------------

    location_cache.set(
        cache_key,
        result,
    )

    return result