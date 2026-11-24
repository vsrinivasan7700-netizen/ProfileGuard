import joblib
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "m1"
    / "saved_models"
    / "fake_profile_model.joblib"
)

print("=" * 55)
print("RANDOM FOREST FEATURE IMPORTANCE ANALYSIS")
print("=" * 55)

# Check model file
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

# Load the saved model
saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]
feature_names = saved_data["feature_names"]

importance = model.feature_importances_

results = pd.DataFrame({
    "feature": feature_names,
    "importance": importance
})

results = results.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature importance ranking:\n")
print(results.to_string(index=False, formatters={
    "importance": lambda value: f"{value:.4f}"
}))

print("\nAnalysis completed.")

