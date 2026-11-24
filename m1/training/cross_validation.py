import pandas as pd

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "m1"
    / "datasets"
    / "Instagram_fake_profile_dataset.csv"
)

print("=" * 55)
print("RANDOM FOREST FIVE-FOLD CROSS-VALIDATION")
print("=" * 55)

# --------------------------------------------------
# LOAD AND PREPARE DATA
# --------------------------------------------------

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)
df = df.drop_duplicates().copy()

X = df.drop(columns=["fake"])
y = df["fake"]

if X.select_dtypes(exclude="number").shape[1] > 0:
    raise ValueError(
        "Non-numeric features require preprocessing."
    )

print("\nRecords:", len(df))
print("Features:", X.shape[1])

print("\nClass distribution:")
print(y.value_counts().sort_index())

# --------------------------------------------------
# BUILD MODEL
# --------------------------------------------------

model = make_pipeline(
    SimpleImputer(strategy="median"),
    RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )
)

# --------------------------------------------------
# FIVE-FOLD CROSS-VALIDATION
# --------------------------------------------------

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scoring = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1"
}

print("\nRunning five-fold cross-validation...")

results = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=scoring,
    n_jobs=1
)

print("\nCROSS-VALIDATION RESULTS")
print("-" * 35)

for metric in scoring:
    scores = results[f"test_{metric}"]

    print(
        f"{metric.capitalize()}: "
        f"{scores.mean():.4f} "
        f"+/- {scores.std():.4f}"
    )

print("\nIndividual fold accuracies:")
for index, score in enumerate(
    results["test_accuracy"], start=1
):
    print(f"Fold {index}: {score:.4f}")

print("\nCross-validation completed.")

