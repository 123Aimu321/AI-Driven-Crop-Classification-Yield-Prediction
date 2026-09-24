import os

import joblib


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


CROP_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "crop_model.joblib",
)

YIELD_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "yield_model.joblib",
)


class ModelService:

    def __init__(self):
        self.crop_model = None
        self.yield_model = None

    def load_models(self):

        if not os.path.exists(
            CROP_MODEL_PATH
        ):
            raise FileNotFoundError(
                "Crop model not found: "
                + CROP_MODEL_PATH
            )

        if not os.path.exists(
            YIELD_MODEL_PATH
        ):
            raise FileNotFoundError(
                "Yield model not found: "
                + YIELD_MODEL_PATH
            )

        print(
            "Loading crop Random Forest model..."
        )

        self.crop_model = joblib.load(
            CROP_MODEL_PATH
        )

        print(
            "Loading yield Random Forest model..."
        )

        self.yield_model = joblib.load(
            YIELD_MODEL_PATH
        )

        print(
            "ML models loaded successfully."
        )

    def get_crop_model(self):

        if self.crop_model is None:
            raise RuntimeError(
                "Crop model has not been loaded."
            )

        return self.crop_model

    def get_yield_model(self):

        if self.yield_model is None:
            raise RuntimeError(
                "Yield model has not been loaded."
            )

        return self.yield_model


model_service = ModelService()