
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "raw" / "telugu_english" / "source"

FILES = {
    "Blog": {
        "train": SOURCE / "Blog Dataset" / "train_data.txt",
        "test": SOURCE / "Blog Dataset" / "test_data.txt"
    },
    "Twitter": {
        "train": SOURCE / "Twitter Dataset" / "train_data.txt",
        "test": SOURCE / "Twitter Dataset" / "test_data.txt"
    }
}

LABEL_MAP = {
    "te": "TE",
    "en": "EN",
    "ne": "NE",
    "univ": "OTHER"
}


def read_sentences(path, source_name, split_name):

    records = []
    current = []

    def save_sentence(tokens):

        if not tokens:
            return

        text_key = " ".join(
            word.casefold().strip()
            for word, _ in tokens
        )

        labels = [
            LABEL_MAP[tag]
            for _, tag in tokens
        ]

        records.append({
            "source": source_name,
            "split": split_name,
            "text": text_key,
            "tokens": [word for word, _ in tokens],
            "labels": labels
        })

    with path.open("r", encoding="utf-8") as file:

        for line in file:

            value = line.strip()

            if not value:

                save_sentence(current)
                current = []
                continue

            parts = value.rsplit(maxsplit=1)

            if len(parts) != 2:
                continue

            word, tag = parts

            current.append((word, tag.lower()))

    save_sentence(current)

    return records


train_index = defaultdict(list)
test_index = defaultdict(list)

print("Loading Telugu-English sentence records...")

for source_name, splits in FILES.items():

    for split_name, path in splits.items():

        records = read_sentences(
            path,
            source_name,
            split_name
        )

        target = train_index if split_name == "train" else test_index

        for record in records:
            target[record["text"]].append(record)


overlapping = set(train_index) & set(test_index)

status_counts = Counter()
source_pair_counts = defaultdict(set)

examples = []
short_duplicates = 0

for text in sorted(overlapping):

    train_records = train_index[text]
    test_records = test_index[text]

    comparisons = []

    for train_record in train_records:

        for test_record in test_records:

            comparisons.append(
                train_record["labels"] == test_record["labels"]
            )

            source_pair_counts[
                (
                    train_record["source"],
                    test_record["source"]
                )
            ].add(text)

    if all(comparisons):
        status = "ALL_LABELS_AGREE"

    elif not any(comparisons):
        status = "ALL_LABELS_CONFLICT"

    else:
        status = "MIXED_LABEL_AGREEMENT"

    status_counts[status] += 1

    token_count = len(train_records[0]["tokens"])

    if token_count <= 2:
        short_duplicates += 1

    if len(examples) < 15:

        examples.append({
            "text": text,
            "train": train_records[:2],
            "test": test_records[:2],
            "status": status
        })


print("\n" + "=" * 65)
print("DUPLICATE ANNOTATION ANALYSIS")
print("=" * 65)

print("Unique overlapping sentences:", len(overlapping))

print("\nLabel agreement categories:")

for category, count in status_counts.items():
    print(category, ":", count)

print("\nOverlapping sentences with 1 or 2 tokens:")
print(short_duplicates)

print("\nSource pair breakdown:")

for pair, sentences in source_pair_counts.items():

    print(
        pair[0], "TRAIN ->", pair[1], "TEST:",
        len(sentences), "unique sentences"
    )


print("\n" + "=" * 65)
print("DUPLICATE EXAMPLES")
print("=" * 65)

for index, example in enumerate(examples, start=1):

    print("\nExample:", index)
    print("Sentence:", example["text"])
    print("Annotation status:", example["status"])

    for record in example["train"]:

        print(
            "TRAIN:",
            record["source"],
            record["labels"]
        )

    for record in example["test"]:

        print(
            "TEST:",
            record["source"],
            record["labels"]
        )


print("\nDuplicate analysis completed!")
