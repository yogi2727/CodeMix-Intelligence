
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = (
    PROJECT_ROOT / "configs" / "label_mapping.json"
)

with CONFIG_PATH.open("r", encoding="utf-8") as file:
    config = json.load(file)

labels = config["labels"]
label2id = config["label2id"]
id2label = config["id2label"]

assert len(labels) == len(set(labels)), "Duplicate labels"

assert set(labels) == set(label2id), "label2id mismatch"

assert len(labels) == len(id2label), "id2label length mismatch"

for label in labels:

    label_id = label2id[label]

    assert id2label[str(label_id)] == label

for dataset, mapping in config["source_mappings"].items():

    for source_label, target_label in mapping.items():

        assert target_label in labels, (
            f"Invalid mapping: {dataset}: "
            f"{source_label} -> {target_label}"
        )

print("Label configuration validated successfully!")

print("\nUnified labels:")

for label, label_id in label2id.items():
    print(f"{label}: {label_id}")

print("\nSource mappings:")

for dataset, mapping in config["source_mappings"].items():
    print(f"\n{dataset}:")
    for source, target in mapping.items():
        print(f"  {source} -> {target}")

print("\nAll validation checks passed!")
