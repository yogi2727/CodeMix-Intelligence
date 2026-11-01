
import ast
from collections import Counter, defaultdict

from datasets import load_dataset

DATASET_ID = "LingoIITGN/COMI-LINGUA"
CONFIG = "LID"
LIMIT = 200

ANNOTATOR_FIELDS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3",
]

TAG_FIELDS = [
    "Predicted tags",
    *ANNOTATOR_FIELDS,
]


def parse_annotation(raw):
    """Safely parse an annotation string."""

    if not isinstance(raw, str):
        raise ValueError("Annotation is not a string")

    parsed = ast.literal_eval(raw)

    if not isinstance(parsed, list):
        raise ValueError("Annotation is not a list")

    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError("Invalid token record")

        required = {"key", "value", "index"}

        if not required.issubset(item):
            raise ValueError("Missing annotation fields")

    return parsed


print("Loading COMI-LINGUA in streaming mode...")

dataset = load_dataset(
    DATASET_ID,
    CONFIG,
    split="train",
    streaming=True
)

parse_stats = Counter()
label_counts = defaultdict(Counter)
errors = []
agreement = Counter()

rows_processed = 0
valid_annotation_rows = 0
alignment_problems = 0

for row_number, row in enumerate(dataset, start=1):

    if row_number > LIMIT:
        break

    rows_processed += 1

    parsed_annotations = {}

    # Inspect all four annotation columns
    for field in TAG_FIELDS:

        raw = row.get(field)

        try:
            annotation = parse_annotation(raw)

            parse_stats[field + "_valid"] += 1
            parsed_annotations[field] = annotation

            for item in annotation:
                label_counts[field][str(item["value"])] += 1

        except (ValueError, SyntaxError, TypeError) as error:

            parse_stats[field + "_invalid"] += 1

            if len(errors) < 8:
                errors.append({
                    "row": row_number,
                    "field": field,
                    "error": str(error),
                    "raw": repr(raw[:300]) if isinstance(raw, str)
                    else repr(raw)
                })

    # Compare three human annotations
    available = [
        parsed_annotations[field]
        for field in ANNOTATOR_FIELDS
        if field in parsed_annotations
    ]

    if len(available) == 3:

        if not (
            len(available[0]) ==
            len(available[1]) ==
            len(available[2])
        ):
            alignment_problems += 1
            continue

        row_aligned = True

        for position in range(len(available[0])):

            items = [
                annotation[position]
                for annotation in available
            ]

            indices = [item["index"] for item in items]
            tokens = [item["key"] for item in items]

            if len(set(map(str, indices))) != 1:
                row_aligned = False
                break

            if len(set(tokens)) != 1:
                row_aligned = False
                break

        if not row_aligned:
            alignment_problems += 1
            continue

        valid_annotation_rows += 1

        for position in range(len(available[0])):

            labels = [
                annotation[position]["value"]
                for annotation in available
            ]

            agreement["total_tokens"] += 1

            if len(set(labels)) == 1:
                agreement["unanimous"] += 1
            else:
                agreement["disagreements"] += 1


print("\n" + "=" * 60)
print("COMI-LINGUA DATA QUALITY AUDIT")
print("=" * 60)

print("Rows inspected:", rows_processed)

print("\n1. PARSING RESULTS")

for field in TAG_FIELDS:

    valid = parse_stats[field + "_valid"]
    invalid = parse_stats[field + "_invalid"]

    print(f"\n{field}")
    print("Valid:", valid)
    print("Invalid:", invalid)

print("\n2. LANGUAGE LABEL COUNTS")

for field, counts in label_counts.items():

    print(f"\n{field}")

    for label, count in counts.items():
        print(f"  {label}: {count}")

print("\n3. ANNOTATOR AGREEMENT")

print("Rows with aligned annotations:", valid_annotation_rows)
print("Rows with alignment problems:", alignment_problems)
print("Comparable tokens:", agreement["total_tokens"])
print("Unanimous tokens:", agreement["unanimous"])
print("Disagreement tokens:", agreement["disagreements"])

total = agreement["total_tokens"]

if total > 0:
    percentage = agreement["unanimous"] / total * 100

    print("Unanimous agreement percentage:",
          round(percentage, 2), "%")

print("\n4. SAMPLE PARSING ERRORS")

if errors:

    for error in errors:

        print("\nRow:", error["row"])
        print("Field:", error["field"])
        print("Error:", error["error"])
        print("Raw:", error["raw"])

else:
    print("No parsing errors in inspected records.")

print("\nAudit completed!")
