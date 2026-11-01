
from datasets import load_dataset_builder

DATASET_ID = "LingoIITGN/COMI-LINGUA"
CONFIG = "LID"

print("Inspecting COMI-LINGUA metadata...")

builder = load_dataset_builder(
    DATASET_ID,
    CONFIG
)

info = builder.info

print("\n" + "=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print("Dataset:", DATASET_ID)
print("Configuration:", CONFIG)
print("Builder:", builder.__class__.__name__)

print("\nDESCRIPTION")
print(info.description[:1500] if info.description else "Not available")

print("\nFEATURES")
print(info.features)

print("\nAVAILABLE SPLITS")

if info.splits:

    for split_name, split_info in info.splits.items():

        print(f"\nSplit: {split_name}")
        print("Number of examples:", split_info.num_examples)
        print("Number of bytes:", split_info.num_bytes)

else:
    print("Split metadata is not available.")

print("\nMETADATA INSPECTION COMPLETED!")
