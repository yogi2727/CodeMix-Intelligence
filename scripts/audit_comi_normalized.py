
import ast
from collections import Counter

from datasets import load_dataset

DATASET_ID = "LingoIITGN/COMI-LINGUA"

ANNOTATORS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3"
]

LABEL_MAP = {
    "hi": "HI",
    "h": "HI",
    "en": "EN",
    "e": "EN",
    "ot": "OTHER",
    "u": "OTHER"
}


def normalize_annotation(raw):

    parsed = ast.literal_eval(raw)

    if not isinstance(parsed, list):
        raise ValueError("Expected annotation list")

    result = []
    format_counts = Counter()
    alias_counts = Counter()

    for position, item in enumerate(parsed):

        if isinstance(item, dict):

            if not {"key", "value"}.issubset(item):
                raise ValueError("Missing key or value")

            token = item["key"]
            original_label = str(item["value"]).strip().lower()

            original_index = item.get("index")

            if original_index is None:
                index_source = "position_fallback"
            else:
                index_source = "original_index"

            format_counts["dictionary"] += 1

        elif isinstance(item, (list, tuple)) and len(item) == 2:

            token, original_label = item

            original_label = str(original_label).strip().lower()

            original_index = None
            index_source = "position_fallback"

            format_counts["pair_list"] += 1

        else:
            raise ValueError(
                f"Unsupported record at position {position}: {item!r}"
            )

        token = str(token)

        if original_label not in LABEL_MAP:
            raise ValueError(
                f"Unknown label {original_label!r} at position {position}"
            )

        normalized_label = LABEL_MAP[original_label]

        alias_counts[original_label] += 1

        result.append({
            "token": token,
            "label": normalized_label,
            "original_label": original_label,
            "position": position,
            "original_index": original_index,
            "index_source": index_source
        })

    return result, format_counts, alias_counts


def audit_split(split_name):

    print("\n" + "=" * 65)
    print("SPLIT:", split_name.upper())
    print("=" * 65)

    dataset = load_dataset(
        DATASET_ID,
        "LID",
        split=split_name,
        streaming=True
    )

    rows = 0
    valid_rows = 0
    invalid_rows = 0
    alignment_errors = 0

    label_counts = Counter()
    alias_counts = Counter()
    format_counts = Counter()
    agreement = Counter()
    errors = []

    for row_number, row in enumerate(dataset, start=1):

        rows += 1

        annotations = []

        try:

            for field in ANNOTATORS:

                normalized, formats, aliases = normalize_annotation(
                    row[field]
                )

                annotations.append(normalized)

                format_counts.update(formats)
                alias_counts.update(aliases)

        except (ValueError, SyntaxError, TypeError, KeyError) as error:

            invalid_rows += 1

            if len(errors) < 5:
                errors.append((row_number, str(error)))

            continue

        for annotation in annotations:

            for item in annotation:
                label_counts[item["label"]] += 1

        # Verify token alignment across annotators
        lengths = [len(annotation) for annotation in annotations]

        if len(set(lengths)) != 1:
            alignment_errors += 1
            continue

        aligned = True

        for position in range(lengths[0]):

            items = [
                annotation[position]
                for annotation in annotations
            ]

            tokens = [item["token"] for item in items]

            if len(set(tokens)) != 1:
                aligned = False
                break

            supplied_indices = [
                item["original_index"]
                for item in items
                if item["original_index"] is not None
            ]

            if len(set(map(str, supplied_indices))) > 1:
                aligned = False
                break

        if not aligned:
            alignment_errors += 1
            continue

        valid_rows += 1

        for position in range(lengths[0]):

            labels = [
                annotation[position]["label"]
                for annotation in annotations
            ]

            counts = Counter(labels)

            if len(counts) == 1:
                agreement["unanimous"] += 1

            elif max(counts.values()) == 2:
                agreement["majority"] += 1

            else:
                agreement["no_majority"] += 1

    print("Total rows:", rows)
    print("Valid parsed rows:", rows - invalid_rows)
    print("Invalid rows:", invalid_rows)
    print("Aligned rows:", valid_rows)
    print("Alignment errors:", alignment_errors)

    print("\nUnified label counts:")
    print(dict(label_counts))

    print("\nOriginal label counts:")
    print(dict(alias_counts))

    print("\nAnnotation formats:")
    print(dict(format_counts))

    print("\nAgreement:")
    print(dict(agreement))

    total = sum(agreement.values())

    if total:
        print(
            "Unanimous agreement:",
            round(agreement["unanimous"] / total * 100, 2),
            "%"
        )

    if errors:
        print("\nSample errors:")

        for error in errors:
            print(error)

    print("\nSplit audit complete!")


audit_split("train")
audit_split("test")

print("\nNormalized COMI-LINGUA audit completed!")
