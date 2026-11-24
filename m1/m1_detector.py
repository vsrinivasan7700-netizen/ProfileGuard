import joblib
from pathlib import Path
import pandas as pd

# Find the main project directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "m1"
    / "saved_models"
    / "fake_profile_model.joblib"
)

# Load the trained model
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

saved_model = joblib.load(MODEL_PATH)

model = saved_model["model"]
feature_names = saved_model["feature_names"]


def predict_profile(profile_features: dict) -> dict:
    """Predict the dataset label for a profile."""

    missing_features = [
        name for name in feature_names
        if name not in profile_features
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    input_data = pd.DataFrame(
        [[profile_features[name] for name in feature_names]],
        columns=feature_names
    )

    prediction = int(model.predict(input_data)[0])
    probabilities = model.predict_proba(input_data)[0]
    classes = list(model.classes_)

    return {
        "predicted_label": prediction,
        "prediction": (
            "fake_labelled" if prediction == 1
            else "genuine_labelled"
        ),
        "fake_label_probability": round(
            float(probabilities[classes.index(1)]), 4
        ),
        "notice": (
            "This prediction reflects patterns in the training "
            "dataset and does not prove that an account is fake."
        )
    }
