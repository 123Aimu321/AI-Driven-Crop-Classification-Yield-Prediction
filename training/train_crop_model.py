import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# PATHS
# --------------------------------------------------

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
    "crop_model.joblib",
)


# --------------------------------------------------
# SUPPORTED CROPS
# --------------------------------------------------

SUPPORTED_CROPS = {
    "wheat",
    "rice",
    "ragi",
}


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("Loading crop yield dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Original dataset shape: {df.shape}")


# --------------------------------------------------
# CLEAN COLUMN VALUES
# --------------------------------------------------

df["Crop"] = (
    df["Crop"]
    .astype(str)
    .str.strip()
    .str.lower()
)

df["State"] = (
    df["State"]
    .astype(str)
    .str.strip()
)

df["Season"] = (
    df["Season"]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# KEEP ONLY WHEAT, RICE AND RAGI
# --------------------------------------------------

df = df[
    df["Crop"].isin(SUPPORTED_CROPS)
].copy()

print(
    "Filtered dataset shape:",
    df.shape,
)

print("\nCrop distribution:")
print(df["Crop"].value_counts())


# --------------------------------------------------
# REMOVE INVALID ROWS
# --------------------------------------------------

FEATURES = [
    "Crop_Year",
    "Season",
    "State",
    "Annual_Rainfall",
]

TARGET = "Crop"

df = df.dropna(
    subset=FEATURES + [TARGET]
)

print(
    "\nDataset after cleaning:",
    df.shape,
)


# --------------------------------------------------
# FEATURES / TARGET
# --------------------------------------------------

X = df[FEATURES]
y = df[TARGET]


# --------------------------------------------------
# CATEGORICAL + NUMERICAL FEATURES
# --------------------------------------------------

categorical_features = [
    "Season",
    "State",
]

numeric_features = [
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
            "numeric",
            "passthrough",
            numeric_features,
        ),
    ]
)


# --------------------------------------------------
# MODEL
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1,
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


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


print("\nTraining crop classification model...")


# --------------------------------------------------
# TRAIN
# --------------------------------------------------

pipeline.fit(
    X_train,
    y_train,
)


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

predictions = pipeline.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions,
)

print(
    f"\nValidation accuracy: "
    f"{accuracy:.4f}"
)

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0,
    )
)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

os.makedirs(
    MODEL_DIR,
    exist_ok=True,
)

joblib.dump(
    pipeline,
    MODEL_PATH,
)


print(
    "\nCrop model saved successfully:"
)

print(MODEL_PATH)