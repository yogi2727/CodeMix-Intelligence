
import ast
from collections import Counter, defaultdict

from datasets import load_dataset

DATASET_ID = "LingoIITGN/COMI-LINGUA"

ANNOTATORS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3"
]

KNOWN_LABELS = {"hi", "en", "ot"}

unexpected_counts = defaultdict(Counter)
unexpected_samples = defaultdict(list)
unusual_shapes = Counter()
shape_examples = []

parse_errors = Counter()

print("Investigating COMI-LINGUA annotation structures...")

dataset = load_dataset(
    DATASET_ID,
    "LID",
    split="train",
    streaming=True
)


def is_valid_dictionary_item(item):

    return (
        isinstance(item, dict)
        and {"key", "value", "index"}.issubset(item)
    )


for row_number, row in enumerate(dataset, start=1):

    parsed_annotations = {}

    # Parse all three human annotations
    for field in ANNOTATORS:

        try:

            annotation = ast.literal_eval(row[field])

            if isinstance(annotation, list):
                parsed_annotations[field] = annotation

        except (ValueError, SyntaxError, TypeError, KeyError):

            parse_errors[field] += 1

    # Inspect the structure and labels
    for field, annotation in parsed_annotations.items():

        for position, item in enumerate(annotation):

            if not is_valid_dictionary_item(item):

                shape = type(item).__name__
                unusual_shapes[(field, shape)] += 1

                if len(shape_examples) < 15:

                    shape_examples.append({
                        "row": row_number,
                        "field": field,
                        "position": position,
                        "item": repr(item),
                        "sentence": row.get("Sentences")
                    })

                continue

            token = str(item["key"])
            label = str(item["value"]).strip().lower()
            index = item["index"]

            if label in KNOWN_LABELS:
                continue

            unexpected_counts[field][label] += 1

            # Collect up to three examples for each unexpected label
            if len(unexpected_samples[label]) >= 3:
                continue

            comparison = {}

            for other_field, other_annotation in parsed_annotations.items():

                matches = []

                for candidate in other_annotation:

                    if not is_valid_dictionary_item(candidate):
                        continue

                    same_token = str(candidate["key"]) == token
                    same_index = str(candidate["index"]) == str(index)

                    if same_token and same_index:
                        matches.append(candidate["value"])

                comparison[other_field] = matches

            unexpected_samples[label].append({
                "row": row_number,
                "field": field,
                "token": token,
                "index": index,
                "label": label,
                "sentence": row.get("Sentences"),
                "comparison": comparison
            })


print("\n" + "=" * 65)
print("UNEXPECTED LABEL FREQUENCIES")
print("=" * 65)

for field, counts in unexpected_counts.items():

    print("\n", field)

    for label, count in counts.most_common():
        print(repr(label), ":", count)


print("\n" + "=" * 65)
print("SAMPLE UNEXPECTED LABEL RECORDS")
print("=" * 65)

for label, samples in unexpected_samples.items():

    print("\nUNEXPECTED LABEL:", repr(label))

    for sample in samples:

        print("\nRow:", sample["row"])
        print("Source field:", sample["field"])
        print("Token:", repr(sample["token"]))
        print("Index:", sample["index"])
        print("Sentence:", sample["sentence"])
        print("Other annotators:")

        for field, values in sample["comparison"].items():
            print(" ", field, ":", values)


print("\n" + "=" * 65)
print("UNUSUAL ANNOTATION STRUCTURES")
print("=" * 65)

for (field, shape), count in unusual_shapes.items():

    print(field, "| Type:", shape, "| Count:", count)


print("\nSAMPLE UNUSUAL RECORDS")
print("=" * 65)

for sample in shape_examples:

    print("\nRow:", sample["row"])
    print("Field:", sample["field"])
    print("Position:", sample["position"])
    print("Item:", sample["item"])
    print("Sentence:", sample["sentence"])


print("\nANNOTATION PARSING ERRORS")

for field, count in parse_errors.items():
    print(field, ":", count)


print("\nInvestigation completed!")
