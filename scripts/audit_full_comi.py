
import ast
from collections import Counter

from datasets import load_dataset

DATASET_ID = "LingoIITGN/COMI-LINGUA"
CONFIG = "LID"

ANNOTATORS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3"
]


def parse_annotation(raw):
    parsed = ast.literal_eval(raw)

    if not isinstance(parsed, list):
        raise ValueError("Expected a list")

    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError("Invalid token record")

        if not {"key", "value", "index"}.issubset(item):
            raise ValueError("Missing annotation fields")

    return parsed


def audit_split(split_name):

    print("\n" + "=" * 65)
    print("AUDITING:", split_name.upper())
    print("=" * 65)

    dataset = load_dataset(
        DATASET_ID,
        CONFIG,
        split=split_name,
        streaming=True
    )

    rows = 0
    annotation_valid = Counter()
    annotation_invalid = Counter()
    label_counts = {
        field: Counter() for field in ANNOTATORS
    }

    token_total = 0
    aligned_rows = 0
    alignment_errors = 0

    agreement = Counter()
    majority_labels = Counter()
    unexpected_labels = Counter()

    for row in dataset:

        rows += 1

        parsed = {}

        for field in ANNOTATORS:

            try:
                annotation = parse_annotation(row[field])

                parsed[field] = annotation
                annotation_valid[field] += 1

                for item in annotation:
                    label = str(item["value"]).strip().lower()
                    label_counts[field][label] += 1

                    if label not in {"en", "hi", "ot"}:
                        unexpected_labels[(field, label)] += 1

            except (ValueError, SyntaxError, TypeError, KeyError):
                annotation_invalid[field] += 1

        if len(parsed) != 3:
            continue

        annotations = [parsed[field] for field in ANNOTATORS]

        lengths = [len(items) for items in annotations]

        if len(set(lengths)) != 1:
            alignment_errors += 1
            continue

        aligned = True

        for position in range(lengths[0]):

            items = [
                annotation[position]
                for annotation in annotations
            ]

            tokens = [item["key"] for item in items]
            indices = [str(item["index"]) for item in items]

            if len(set(tokens)) != 1 or len(set(indices)) != 1:
                aligned = False
                break

        if not aligned:
            alignment_errors += 1
            continue

        aligned_rows += 1
        token_total += lengths[0]

        for position in range(lengths[0]):

            labels = [
                str(annotation[position]["value"]).strip().lower()
                for annotation in annotations
            ]

            counts = Counter(labels)

            if len(counts) == 1:
                agreement["unanimous"] += 1
                final_label = labels[0]

            elif max(counts.values()) == 2:
                agreement["majority"] += 1
                final_label = counts.most_common(1)[0][0]

            else:
                agreement["no_majority"] += 1
                continue

            agreement["usable"] += 1

            mapped = {
                "en": "EN",
                "hi": "HI",
                "ot": "OTHER"
            }.get(final_label)

            if mapped is not None:
                majority_labels[mapped] += 1

    print("\nRECORD COUNTS")
    print("Total records:", rows)

    print("\nANNOTATION PARSING")

    for field in ANNOTATORS:
        print(
            field,
            "| Valid:", annotation_valid[field],
            "| Invalid:", annotation_invalid[field]
        )

    print("\nANNOTATOR LABEL DISTRIBUTIONS")

    for field in ANNOTATORS:
        print(f"\n{field}:")
        print(dict(label_counts[field]))

    print("\nALIGNMENT")
    print("Fully aligned rows:", aligned_rows)
    print("Alignment problem rows:", alignment_errors)
    print("Comparable token positions:", token_total)

    print("\nANNOTATOR AGREEMENT")
    print("Unanimous:", agreement["unanimous"])
    print("Two-out-of-three majority:", agreement["majority"])
    print("No majority:", agreement["no_majority"])
    print("Usable consensus tokens:", agreement["usable"])

    total = (
        agreement["unanimous"]
        + agreement["majority"]
        + agreement["no_majority"]
    )

    if total:
        print(
            "Unanimous agreement:",
            round(agreement["unanimous"] / total * 100, 2),
            "%"
        )

    print("\nFINAL MAPPED LABEL DISTRIBUTION")
    print(dict(majority_labels))

    print("\nUNEXPECTED LABELS")
    print(dict(unexpected_labels))

    print("\nCompleted:", split_name)


print("Starting full COMI-LINGUA audit...")

audit_split("train")
audit_split("test")

print("\nFULL COMI-LINGUA AUDIT COMPLETED!")
