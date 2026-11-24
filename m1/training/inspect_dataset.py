import json
from pathlib import Path
from collections import Counter

# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Locate the JSON dataset
DATASET_PATH = PROJECT_ROOT / "m1" / "datasets" / "fakeAccountData.json"

print("=" * 45)
print("FAKE PROFILE DATASET INSPECTION")
print("=" * 45)

print("Project folder:", PROJECT_ROOT)
print("Dataset path:", DATASET_PATH)
print("File exists:", DATASET_PATH.exists())

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}\n"
        "Check the filename and folder location."
    )

# Load the dataset
with open(DATASET_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

if not isinstance(data, list):
    raise ValueError("Expected a JSON list containing profile records.")

if not data:
    raise ValueError("The dataset contains no records.")

print("\nTotal records:", len(data))

# Display available columns
columns = sorted({
    column
    for record in data
    if isinstance(record, dict)
    for column in record
})

print("\nDataset columns:")
for column in columns:
    print("-", column)

# Count labels
print("\nFake/Genuine label distribution:")

labels = Counter(
    record.get("isFake")
    for record in data
    if isinstance(record, dict)
    and record.get("isFake") in (0, 1)
)

for label, count in sorted(labels.items()):
    category = "Genuine" if label == 0 else "Fake"
    print(f"{category} (isFake={label}): {count}")

# Count missing values
print("\nMissing values:")
for column in columns:
    missing = sum(
        1 for record in data
        if not isinstance(record, dict)
        or column not in record
        or record[column] is None
    )
    print(f"{column}: {missing}")

# Show example records
print("\nFirst 3 records:")
for record in data[:3]:
    print(record)

print("\nDataset inspection completed.")

