import requests


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


def search_location(place: str):

    place = place.strip()

    if not place:
        return []

    response = requests.get(
        GEOCODING_URL,
        params={
            "name": place,
            "count": 5,
            "language": "en",
            "format": "json",
        },
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for item in data.get("results", []):

        results.append(
            {
                "name": item.get("name"),
                "state": item.get("admin1"),
                "country": item.get("country"),
                "country_code": item.get(
                    "country_code"
                ),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
            }
        )

    return results


def reverse_geocode(
    latitude: float,
    longitude: float,
):

    response = requests.get(
        REVERSE_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "zoom": 10,
            "addressdetails": 1,
        },
        headers=HEADERS,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

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

    return {
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