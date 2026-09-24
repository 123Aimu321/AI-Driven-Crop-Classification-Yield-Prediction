import pandas as pd

from app.services.model_service import (
    model_service,
)


ALLOWED_CROPS = {
    "wheat",
    "rice",
    "ragi",
}


def load_model():

    return model_service.get_yield_model()


def _get_season():

    month = pd.Timestamp.now().month

    if month in [
        6,
        7,
        8,
        9,
        10,
    ]:
        return "Kharif"

    if month in [
        11,
        12,
        1,
        2,
        3,
    ]:
        return "Rabi"

    return "Summer"


def predict_yield(
    crop,
    state,
    annual_rainfall,
):

    crop = (
        str(crop)
        .strip()
        .lower()
    )

    if crop not in ALLOWED_CROPS:
        raise ValueError(
            "Unsupported crop. "
            "Only Wheat, Rice and Ragi "
            "are supported."
        )

    if not state:
        return {
            "success": False,
            "message": (
                "State could not be detected "
                "from the selected location."
            ),
        }

    if annual_rainfall is None:
        return {
            "success": False,
            "message": (
                "Annual rainfall data is "
                "currently unavailable."
            ),
        }

    # Already loaded into memory.
    model = load_model()

    current_year = (
        pd.Timestamp.now().year
    )

    season = _get_season()

    input_data = pd.DataFrame(
        [{
            "Crop": crop,
            "Crop_Year": current_year,
            "Season": season,
            "State": str(state).strip(),
            "Annual_Rainfall": float(
                annual_rainfall
            ),
        }]
    )

    prediction = model.predict(
        input_data
    )[0]

    return {
        "success": True,
        "crop": crop.title(),
        "state": str(state).strip(),
        "year": current_year,
        "season": season,
        "annual_rainfall": round(
            float(annual_rainfall),
            2,
        ),
        "predicted_yield": round(
            float(prediction),
            2,
        ),
        "unit": "dataset yield units",
        "model": "Random Forest",
    }