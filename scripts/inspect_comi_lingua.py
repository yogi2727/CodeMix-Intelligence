
from datasets import load_dataset

DATASET_ID = "LingoIITGN/COMI-LINGUA"
CONFIG = "LID"

print("Loading COMI-LINGUA dataset metadata...")

dataset = load_dataset(
    DATASET_ID,
    CONFIG,
    split="train",
    streaming=True
)

print("\nDataset information")
print("-----------------------------")
print("Dataset:", DATASET_ID)
print("Configuration:", CONFIG)
print("Features:", dataset.features)
print("Columns:", dataset.column_names)

print("\nInspecting first 3 records")
print("=============================")

for index, row in enumerate(dataset.take(3)):

    print(f"\nRECORD {index + 1}")
    print("-----------------------------")

    for column, value in row.items():

        print(f"\nField: {column}")
        print("Data type:", type(value).__name__)

        if isinstance(value, list):
            print("Number of elements:", len(value))
            print("First 3 elements:", value[:3])

        elif isinstance(value, dict):
            print("Value:", value)

        elif isinstance(value, str):
            print("Value:", repr(value[:300]))

        else:
            print("Value:", value)

print("\nDataset inspection completed!")
