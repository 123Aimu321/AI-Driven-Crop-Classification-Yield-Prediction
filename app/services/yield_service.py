import os

import joblib
import pandas as pd


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
    "yield_model.joblib",
)


ALLOWED_CROPS = {
    "wheat",
    "rice",
    "ragi",
}


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Yield model not found. "
            "Run training/train_yield_model.py first."
        )

    return joblib.load(MODEL_PATH)


def _get_season():
    """
    Automatically determine agricultural season
    from the current month.
    """

    month = pd.Timestamp.now().month

    if month in [6, 7, 8, 9, 10]:
        return "Kharif"

    if month in [11, 12, 1, 2, 3]:
        return "Rabi"

    return "Summer"


def predict_yield(
    crop,
    state,
    annual_rainfall,
):
    """
    Predict crop yield automatically.

    Inputs:
    - Predicted crop
    - Automatically detected state
    - Automatically obtained annual rainfall
    - Automatically determined year
    - Automatically determined season
    """

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

    model = load_model()

    current_year = pd.Timestamp.now().year

    season = _get_season()

    input_data = pd.DataFrame(
        [
            {
                "Crop": crop,
                "Crop_Year": current_year,
                "Season": season,
                "State": str(state).strip(),
                "Annual_Rainfall": float(
                    annual_rainfall
                ),
            }
        ]
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