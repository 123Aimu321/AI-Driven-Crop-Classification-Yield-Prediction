import os

import joblib
import pandas as pd

from app.services.model_service import (
    model_service,
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "crop_model.joblib",
)


ALLOWED_CROPS = {
    "wheat",
    "rice",
    "ragi",
}


def load_model():

    return model_service.get_crop_model()


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


def _get_crop_probabilities(
    model,
    input_data,
):

    if not hasattr(
        model,
        "predict_proba",
    ):
        return {}

    probabilities = (
        model.predict_proba(
            input_data
        )[0]
    )

    classes = model.classes_

    result = {}

    for crop, probability in zip(
        classes,
        probabilities,
    ):

        crop_name = (
            str(crop)
            .strip()
            .lower()
        )

        if crop_name in ALLOWED_CROPS:

            result[crop_name] = round(
                float(probability) * 100,
                2,
            )

    return result


def predict_crop(
    state,
    annual_rainfall,
):

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

    # IMPORTANT:
    # Model is already loaded in memory.
    model = load_model()

    current_year = (
        pd.Timestamp.now().year
    )

    season = _get_season()

    input_data = pd.DataFrame(
        [{
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

    crop = (
        str(prediction)
        .strip()
        .lower()
    )

    if crop not in ALLOWED_CROPS:

        return {
            "success": False,
            "message": (
                "The model predicted a crop "
                "outside the supported crop list."
            ),
            "predicted_crop": crop,
            "supported_crops": [
                "Wheat",
                "Rice",
                "Ragi",
            ],
        }

    probabilities = (
        _get_crop_probabilities(
            model,
            input_data,
        )
    )

    return {
        "success": True,
        "crop": crop.title(),
        "season": season,
        "year": current_year,
        "state": str(state).strip(),
        "annual_rainfall": round(
            float(annual_rainfall),
            2,
        ),
        "probabilities": probabilities,
        "supported_crops": [
            "Wheat",
            "Rice",
            "Ragi",
        ],
        "model": "Random Forest",
    }