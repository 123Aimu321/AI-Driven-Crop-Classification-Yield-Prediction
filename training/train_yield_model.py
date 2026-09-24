import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "crop_yield.csv",
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models",
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "yield_model.joblib",
)


ALLOWED_CROPS = [
    "wheat",
    "rice",
    "ragi",
]


def main():

    print("Loading crop yield dataset...")

    df = pd.read_csv(DATA_PATH)

    print(
        "Original dataset shape:",
        df.shape,
    )

    df["Crop"] = (
        df["Crop"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["Season"] = (
        df["Season"]
        .astype(str)
        .str.strip()
    )

    df["State"] = (
        df["State"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["Crop"].isin(
            ALLOWED_CROPS
        )
    ].copy()

    print(
        "Filtered dataset shape:",
        df.shape,
    )

    print("\nCrop distribution:")

    print(
        df["Crop"].value_counts()
    )

    required_columns = [
        "Crop",
        "Crop_Year",
        "Season",
        "State",
        "Annual_Rainfall",
        "Yield",
    ]

    df = df[
        required_columns
    ].copy()

    df = df.dropna()

    df["Crop_Year"] = pd.to_numeric(
        df["Crop_Year"],
        errors="coerce",
    )

    df["Annual_Rainfall"] = pd.to_numeric(
        df["Annual_Rainfall"],
        errors="coerce",
    )

    df["Yield"] = pd.to_numeric(
        df["Yield"],
        errors="coerce",
    )

    df = df.dropna()

    print(
        "\nDataset after cleaning:",
        df.shape,
    )

    X = df[
        [
            "Crop",
            "Crop_Year",
            "Season",
            "State",
            "Annual_Rainfall",
        ]
    ]

    y = df["Yield"]

    categorical_features = [
        "Crop",
        "Season",
        "State",
    ]

    numerical_features = [
        "Crop_Year",
        "Annual_Rainfall",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
            (
                "numerical",
                "passthrough",
                numerical_features,
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_features="sqrt",
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
        )
    )

    print(
        "\nTraining yield prediction model..."
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    predictions = pipeline.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    print(
        "\nYield model evaluation:"
    )

    print(
        f"MAE: {mae:.4f}"
    )

    print(
        f"R2 Score: {r2:.4f}"
    )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True,
    )

    joblib.dump(
        pipeline,
        MODEL_PATH,
    )

    print(
        "\nYield model saved successfully:"
    )

    print(MODEL_PATH)


if __name__ == "__main__":
    main()