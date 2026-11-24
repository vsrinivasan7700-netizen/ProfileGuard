import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "m1"
    / "datasets"
    / "Instagram_fake_profile_dataset.csv"
)

MODEL_DIR = PROJECT_ROOT / "m1" / "saved_models"
MODEL_PATH = MODEL_DIR / "fake_profile_model.joblib"

print("=" * 55)
print("BLOCKCHAIN-BASED FAKE PROFILE DETECTION")
print("RANDOM FOREST MODEL TRAINING")
print("=" * 55)

# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

print("\nOriginal dataset shape:", df.shape)

# Check target column
if "fake" not in df.columns:
    raise ValueError("The target column 'fake' is missing.")

# Remove exact duplicate rows
duplicate_count = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

print("Exact duplicate rows removed:", duplicate_count)
print("Dataset shape after cleaning:", df.shape)

# --------------------------------------------------
# 3. PREPARE FEATURES AND TARGET
# --------------------------------------------------

X = df.drop(columns=["fake"])
y = df["fake"]

# Require numeric input features
non_numeric = X.select_dtypes(exclude="number").columns.tolist()

if non_numeric:
    raise ValueError(
        f"Non-numeric features need preprocessing: {non_numeric}"
    )

# Check labels
if y.isnull().any():
    raise ValueError("The target column contains missing labels.")

if set(y.unique()) != {0, 1}:
    raise ValueError(
        f"Expected binary labels 0 and 1; found {sorted(y.unique())}"
    )

print("\nFeature count:", X.shape[1])
print("\nClass distribution:")
print(y.value_counts().sort_index())

# --------------------------------------------------
# 4. SPLIT DATA
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# --------------------------------------------------
# 5. TRAIN MODEL
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

print("\nTraining model...")
model.fit(X_train, y_train)

print("Training completed!")

# --------------------------------------------------
# 6. EVALUATE MODEL
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n" + "=" * 55)
print("MODEL EVALUATION")
print("=" * 55)

print(f"\nAccuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Genuine-labelled", "Fake-labelled"],
        zero_division=0
    )
)

print("Confusion matrix:")
print("Rows = actual classes; columns = predicted classes")
print("Class order: 0 (genuine-labelled), 1 (fake-labelled)")
print(confusion_matrix(y_test, predictions, labels=[0, 1]))

# --------------------------------------------------
# 7. SAVE MODEL
# --------------------------------------------------

MODEL_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(
    {
        "model": model,
        "feature_names": X.columns.tolist(),
        "target_name": "fake"
    },
    MODEL_PATH
)

print("\nModel saved to:")
print(MODEL_PATH)

print("\nTraining and evaluation completed.")

