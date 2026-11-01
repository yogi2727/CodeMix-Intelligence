
import ast
import json
from pathlib import Path
from collections import Counter

from datasets import load_dataset

ROOT = Path(__file__).resolve().parents[1]

CONFIG_PATH = ROOT / "configs" / "label_mapping.json"

with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config = json.load(f)

LABEL_MAP = config["source_mappings"]["COMI-LINGUA"]

ANNOTATORS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3"
]

DATASET_ID = "LingoIITGN/COMI-LINGUA"


def parse_annotation(raw):

    parsed = ast.literal_eval(raw)

    if not isinstance(parsed, list):
        raise ValueError("Expected a list")

    result = []

    for position, item in enumerate(parsed):

        if isinstance(item, dict):

            token = item["key"]
            original_label = item["value"]
            original_index = item.get("index")

        elif isinstance(item, (list, tuple)) and len(item) == 2:

            token, original_label = item
            original_index = None

        else:
            raise ValueError("Unsupported annotation item")

        original_label = str(original_label).strip().lower()

        if original_label not in LABEL_MAP:
            raise ValueError(f"Unexpected label: {original_label}")

        result.append({
            "token": str(token),
            "label": LABEL_MAP[original_label],
            "position": position,
            "original_index": original_index
        })

    return result


def audit_split(split_name):

    print("\n" + "=" * 60)
    print("SPLIT:", split_name.upper())
    print("=" * 60)

    dataset = load_dataset(
        DATASET_ID,
        "LID",
        split=split_name,
        streaming=True
    )

    total_rows = 0
    aligned_rows = 0
    invalid_rows = 0
    alignment_errors = 0

    final_counts = Counter()

    unanimous_tokens = 0
    majority_tokens = 0
    no_majority_tokens = 0

    original_votes = Counter()

    for row in dataset:

        total_rows += 1

        try:

            annotations = [
                parse_annotation(row[field])
                for field in ANNOTATORS
            ]

        except (ValueError, SyntaxError, TypeError, KeyError):
            invalid_rows += 1
            continue

        lengths = [len(annotation) for annotation in annotations]

        if len(set(lengths)) != 1:
            alignment_errors += 1
            continue

        row_aligned = True

        for position in range(lengths[0]):

            items = [
                annotation[position]
                for annotation in annotations
            ]

            tokens = [item["token"] for item in items]

            indices = [
                str(item["original_index"])
                for item in items
                if item["original_index"] is not None
            ]

            if len(set(tokens)) != 1:
                row_aligned = False
                break

            if len(set(indices)) > 1:
                row_aligned = False
                break

        if not row_aligned:
            alignment_errors += 1
            continue

        aligned_rows += 1

        for position in range(lengths[0]):

            items = [
                annotation[position]
                for annotation in annotations
            ]

            labels = [item["label"] for item in items]

            original_votes.update(labels)

            counts = Counter(labels)

            if len(counts) == 1:

                unanimous_tokens += 1
                final_label = labels[0]

            elif max(counts.values()) == 2:

                majority_tokens += 1
                final_label = counts.most_common(1)[0][0]

            else:

                no_majority_tokens += 1
                continue

            final_counts[final_label] += 1

    consensus_tokens = sum(final_counts.values())

    print("Total records:", total_rows)
    print("Invalid records:", invalid_rows)
    print("Aligned records:", aligned_rows)
    print("Alignment errors:", alignment_errors)

    print("\nConsensus decisions")
    print("Unanimous:", unanimous_tokens)
    print("Majority:", majority_tokens)
    print("No majority:", no_majority_tokens)

    print("\nFINAL MAJORITY-VOTE LABEL COUNTS")

    for label in ["EN", "HI", "OTHER"]:
        print(label, ":", final_counts[label])

    print("\nTotal usable consensus tokens:", consensus_tokens)

    print("\nFinal label percentages:")

    if consensus_tokens:

        for label in ["EN", "HI", "OTHER"]:

            percentage = (
                final_counts[label] / consensus_tokens * 100
            )

            print(label, ":", round(percentage, 2), "%")

    print("\nOriginal normalized annotation votes:")
    print(dict(original_votes))


audit_split("train")
audit_split("test")

print("\nConsensus calculation completed!")
