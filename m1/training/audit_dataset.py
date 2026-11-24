
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

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
print("FAKE PROFILE DATASET AUDIT")
print("=" * 55)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

if not DATASET_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

df = pd.read_csv(DATASET_PATH)

print("\nOriginal records:", len(df))
print("Number of columns:", len(df.columns))

if "fake" not in df.columns:
    raise ValueError("Target column 'fake' was not found.")

# Remove exact duplicate rows for this audit
df = df.drop_duplicates().copy()

print("Records after removing exact duplicates:", len(df))

# --------------------------------------------------
# CHECK LABELS
# --------------------------------------------------

print("\nLabel distribution:")
print(df["fake"].value_counts(dropna=False).sort_index())

print("\nLabel proportions:")
print(df["fake"].value_counts(normalize=True).sort_index().round(4))

# --------------------------------------------------
# CHECK DUPLICATES
# --------------------------------------------------

print("\nRemaining exact duplicate rows:", df.duplicated().sum())

# Check whether identical feature vectors have conflicting labels
feature_columns = [c for c in df.columns if c != "fake"]

label_counts_per_feature_vector = (
    df.groupby(feature_columns, dropna=False)["fake"]
    .nunique()
)

conflicting_vectors = int((label_counts_per_feature_vector > 1).sum())

print(
    "Identical feature vectors with conflicting labels:",
    conflicting_vectors
)

# --------------------------------------------------
# CHECK MISSING VALUES AND DATA TYPES
# --------------------------------------------------

print("\nMissing values:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)

# --------------------------------------------------
# CHECK FEATURE RELATIONSHIPS
# --------------------------------------------------

print("\nMean feature values by label:")
print(df.groupby("fake")[feature_columns].mean().round(3).T)

# --------------------------------------------------
# CHECK TRAIN/TEST OVERLAP
# --------------------------------------------------

X = df.drop(columns=["fake"])
y = df["fake"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

train_rows = set(map(tuple, X_train.to_numpy()))
test_rows = set(map(tuple, X_test.to_numpy()))

overlap = train_rows.intersection(test_rows)

print("\nTrain/test audit:")
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))
print("Identical feature vectors shared between splits:", len(overlap))

print("\nAudit completed.")

