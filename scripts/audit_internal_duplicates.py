
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "raw" / "telugu_english" / "source"

FILES = {
    "Blog Train": SOURCE / "Blog Dataset" / "train_data.txt",
    "Blog Test": SOURCE / "Blog Dataset" / "test_data.txt",
    "Twitter Train": SOURCE / "Twitter Dataset" / "train_data.txt",
    "Twitter Test": SOURCE / "Twitter Dataset" / "test_data.txt",
}

LABEL_MAP = {
    "te": "TE",
    "en": "EN",
    "ne": "NE",
    "univ": "OTHER",
}


def read_sentences(path):

    records = []
    current = []

    def save_sentence(tokens):

        if not tokens:
            return

        words = [word for word, _ in tokens]

        labels = [
            LABEL_MAP[tag]
            for _, tag in tokens
        ]

        key = " ".join(
            word.casefold().strip()
            for word in words
        )

        records.append({
            "text": key,
            "tokens": words,
            "labels": labels
        })

    with path.open("r", encoding="utf-8") as file:

        for line in file:

            text = line.strip()

            if not text:

                save_sentence(current)
                current = []
                continue

            parts = text.rsplit(maxsplit=1)

            if len(parts) != 2:
                continue

            word, tag = parts
            tag = tag.lower()

            if tag not in LABEL_MAP:
                continue

            current.append((word, tag))

    save_sentence(current)

    return records


def inspect_duplicates(name, path):

    print("\n" + "=" * 65)
    print(name)
    print("=" * 65)

    records = read_sentences(path)

    groups = defaultdict(list)

    for record in records:
        groups[record["text"]].append(record)

    duplicate_groups = {
        text: items
        for text, items in groups.items()
        if len(items) > 1
    }

    extra_rows = sum(
        len(items) - 1
        for items in duplicate_groups.values()
    )

    consistent = 0
    conflicting = 0
    entity_only = 0

    conflict_examples = []

    for text, items in duplicate_groups.items():

        label_sequences = {
            tuple(item["labels"])
            for item in items
        }

        if len(label_sequences) == 1:
            consistent += 1

        else:
            conflicting += 1

            if len(conflict_examples) < 8:
                conflict_examples.append((text, items))

        if all(
            all(label == "NE" for label in item["labels"])
            for item in items
        ):
            entity_only += 1

    print("Total sentences:", len(records))
    print("Unique normalized sentences:", len(groups))
    print("Duplicate groups:", len(duplicate_groups))
    print("Extra repeated rows:", extra_rows)

    print("\nAnnotation consistency")
    print("Consistent duplicate groups:", consistent)
    print("Conflicting duplicate groups:", conflicting)
    print("Named-entity-only duplicate groups:", entity_only)

    if conflict_examples:

        print("\nConflicting examples")

        for text, items in conflict_examples:

            print("\nSentence:", text)

            for item in items:
                print("Tokens:", item["tokens"])
                print("Labels:", item["labels"])


all_records = {}

for name, path in FILES.items():

    all_records[name] = read_sentences(path)

    inspect_duplicates(name, path)


print("\n" + "=" * 65)
print("INTERNAL DUPLICATE AUDIT COMPLETED")
print("=" * 65)
