
import ast
from collections import Counter

from datasets import load_dataset

DATASET_ID = "LingoIITGN/COMI-LINGUA"

ANNOTATOR_FIELDS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3",
]

LIMIT = 200


def parse_annotation(raw):
    return ast.literal_eval(raw)


dataset = load_dataset(
    DATASET_ID,
    "LID",
    split="train",
    streaming=True
)

unanimous = 0
majority = 0
no_majority = 0

majority_labels = Counter()
disagreement_patterns = Counter()
examples = []

aligned_rows = 0
alignment_errors = []

for row_number, row in enumerate(dataset, start=1):

    if row_number > LIMIT:
        break

    annotations = [
        parse_annotation(row[field])
        for field in ANNOTATOR_FIELDS
    ]

    lengths = [len(annotation) for annotation in annotations]

    if len(set(lengths)) != 1:

        alignment_errors.append(
            (row_number, "Different token counts")
        )
        continue

    row_aligned = True

    for position in range(lengths[0]):

        items = [
            annotation[position]
            for annotation in annotations
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

        alignment_errors.append(
            (row_number, "Token or index mismatch")
        )
        continue

    aligned_rows += 1

    for position in range(lengths[0]):

        items = [
            annotation[position]
            for annotation in annotations
        ]

        token = items[0]["key"]

        labels = [
            str(item["value"]).strip().lower()
            for item in items
        ]

        counts = Counter(labels)
        pattern = tuple(labels)

        if len(counts) == 1:
            unanimous += 1
            final_label = labels[0]

        elif counts.most_common(1)[0][1] == 2:

            majority += 1
            final_label = counts.most_common(1)[0][0]

            disagreement_patterns[pattern] += 1

        else:

            no_majority += 1
            final_label = None

        if final_label is not None:
            majority_labels[final_label] += 1

        if labels.count(labels[0]) != 3:

            if len(examples) < 15:

                examples.append({
                    "row": row_number,
                    "token": token,
                    "labels": labels,
                    "decision": final_label
                })


total = unanimous + majority + no_majority

print("\nANNOTATOR AGREEMENT ANALYSIS")
print("=" * 55)

print("Aligned rows:", aligned_rows)
print("Alignment problems:", alignment_errors)

print("\nTOKEN DECISIONS")
print("Total tokens:", total)
print("Unanimous:", unanimous)
print("Two-out-of-three majority:", majority)
print("No majority:", no_majority)

print("\nMAJORITY LABEL DISTRIBUTION")

for label, count in majority_labels.items():
    print(label, ":", count)

print("\nCOMMON DISAGREEMENT PATTERNS")

for pattern, count in disagreement_patterns.most_common(10):
    print(pattern, ":", count)

print("\nSAMPLE DISAGREEMENTS")

for example in examples:

    print(
        "\nRow:", example["row"],
        "| Token:", repr(example["token"]),
        "| Labels:", example["labels"],
        "| Decision:", example["decision"]
    )

print("\nAgreement inspection completed!")
