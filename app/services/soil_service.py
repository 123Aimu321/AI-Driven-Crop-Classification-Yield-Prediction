import requests


SOILGRIDS_URL = (
    "https://rest.isric.org/"
    "soilgrids/v2.0/properties/query"
)


PROPERTIES = [
    "phh2o",
    "nitrogen",
    "clay",
    "sand",
    "silt",
    "soc",
]


def _convert_value(
    property_name,
    value,
):

    if value is None:
        return None

    # SoilGrids commonly stores:
    # pH as pH x 10
    # nitrogen as cg/kg
    # organic carbon as dg/kg
    # texture as g/kg

    if property_name == "phh2o":
        return value / 10

    if property_name == "nitrogen":
        return value / 100

    if property_name == "soc":
        return value / 10

    if property_name in [
        "clay",
        "sand",
        "silt",
    ]:
        return value / 10

    return value


def _soil_texture(
    sand,
    clay,
    silt,
):

    if (
        sand is None
        or clay is None
        or silt is None
    ):
        return "Unknown"


    # Simple texture classification.
    # This is only used when actual
    # texture percentages are available.

    if clay >= 40:
        return "Clay"

    if sand >= 70:
        return "Sandy"

    if silt >= 50:
        return "Silty"

    if (
        sand >= 45
        and clay < 20
    ):
        return "Sandy Loam"

    if (
        clay >= 20
        and clay < 35
        and sand < 45
    ):
        return "Loam"

    return "Loamy"


def get_soil_data(
    latitude: float,
    longitude: float,
):

    params = [
        (
            "lat",
            latitude,
        ),
        (
            "lon",
            longitude,
        ),
    ]

    for property_name in PROPERTIES:

        params.append(
            (
                "property",
                property_name,
            )
        )

    try:

        response = requests.get(
            SOILGRIDS_URL,
            params=params,
            timeout=30,
        )

        if response.status_code != 200:

            return {
                "available": False,
                "message": (
                    "Soil data provider "
                    "is currently unavailable."
                ),
                "source": "ISRIC SoilGrids",
            }

        data = response.json()

        properties = data.get(
            "properties",
            {}
        )

        layers = properties.get(
            "layers",
            []
        )

        extracted = {}

        for layer in layers:

            name = layer.get(
                "name"
            )

            depths = layer.get(
                "depths",
                []
            )

            if not depths:
                continue

            first_depth = depths[0]

            values = first_depth.get(
                "values",
                {}
            )

            median = values.get(
                "M"
            )

            extracted[name] = (
                _convert_value(
                    name,
                    median,
                )
            )

        ph = extracted.get(
            "phh2o"
        )

        nitrogen = extracted.get(
            "nitrogen"
        )

        clay = extracted.get(
            "clay"
        )

        sand = extracted.get(
            "sand"
        )

        silt = extracted.get(
            "silt"
        )

        soc = extracted.get(
            "soc"
        )

        soil_type = _soil_texture(
            sand=sand,
            clay=clay,
            silt=silt,
        )

        return {
            "available": True,
            "source": "ISRIC SoilGrids",

            "soil_type": soil_type,

            "ph": ph,

            "nitrogen": nitrogen,

            "phosphorus": None,

            "potassium": None,

            "sand": sand,

            "clay": clay,

            "silt": silt,

            "organic_carbon": soc,
        }

    except requests.RequestException as error:

        return {
            "available": False,
            "message": str(error),
            "source": "ISRIC SoilGrids",
        }

    except Exception as error:

        return {
            "available": False,
            "message": str(error),
            "source": "ISRIC SoilGrids",
        }