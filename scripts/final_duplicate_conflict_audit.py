
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "raw" / "telugu_english" / "source"

FILES = {
    "Blog Train": ("Blog", "train",
        SOURCE / "Blog Dataset" / "train_data.txt"),

    "Blog Test": ("Blog", "test",
        SOURCE / "Blog Dataset" / "test_data.txt"),

    "Twitter Train": ("Twitter", "train",
        SOURCE / "Twitter Dataset" / "train_data.txt"),

    "Twitter Test": ("Twitter", "test",
        SOURCE / "Twitter Dataset" / "test_data.txt")
}

LABEL_MAP = {
    "te": "TE",
    "en": "EN",
    "ne": "NE",
    "univ": "OTHER"
}

groups = defaultdict(list)


def read_file(source_name, split_name, path):

    records = []

    current_tokens = []
    current_labels = []

    def save_sentence():

        if not current_tokens:
            return

        key = " ".join(
            token.casefold().strip()
            for token in current_tokens
        )

        records.append({
            "key": key,
            "tokens": current_tokens.copy(),
            "labels": current_labels.copy(),
            "source": source_name,
            "split": split_name
        })

        current_tokens.clear()
        current_labels.clear()

    with path.open("r", encoding="utf-8") as file:

        for line in file:

            text = line.strip()

            if not text:
                save_sentence()
                continue

            parts = text.rsplit(maxsplit=1)

            if len(parts) != 2:
                continue

            token, original_label = parts
            original_label = original_label.lower()

            if original_label not in LABEL_MAP:
                continue

            current_tokens.append(token)
            current_labels.append(
                LABEL_MAP[original_label]
            )

    save_sentence()

    return records


print("Building complete duplicate groups...")

for name, (source_name, split_name, path) in FILES.items():

    records = read_file(source_name, split_name, path)

    for record in records:
        groups[record["key"]].append(record)

    print(name, "records:", len(records))


train_test_overlaps = 0
cross_source_overlaps = 0
internal_duplicate_groups = 0

conflicting_groups = []
all_entity_only_groups = 0

source_pair_counts = Counter()

for key, records in groups.items():

    if len(records) < 2:
        continue

    sources = {record["source"] for record in records}
    splits = {record["split"] for record in records}

    sequences = {
        tuple(record["labels"])
        for record in records
    }

    if len({record["source"] + record["split"]
            for record in records}) < len(records):
        internal_duplicate_groups += 1

    if "train" in splits and "test" in splits:

        train_test_overlaps += 1

    if len(sources) > 1:

        cross_source_overlaps += 1

    if "train" in splits and "test" in splits:

        for train_record in records:

            if train_record["split"] != "train":
                continue

            for test_record in records:

                if test_record["split"] != "test":
                    continue

                source_pair_counts[
                    (train_record["source"], test_record["source"])
                ] += 1

    if all(
        all(label == "NE" for label in record["labels"])
        for record in records
    ):
        all_entity_only_groups += 1

    if len(sequences) > 1:

        conflicting_groups.append({
            "key": key,
            "records": records
        })


print("\n" + "=" * 65)
print("FINAL DUPLICATE AUDIT")
print("=" * 65)

print("Unique sentence groups:", len(groups))

print("Internal duplicate groups:", internal_duplicate_groups)

print("Unique train/test overlapping sentences:",
      train_test_overlaps)

print("Cross-source duplicate groups:",
      cross_source_overlaps)

print("Entity-only duplicate groups:",
      all_entity_only_groups)

print("\nTRAIN/TEST SOURCE PAIRS")

for pair, count in source_pair_counts.items():
    print(pair, ":", count)

print("\nCONFLICTING ANNOTATION GROUPS:",
      len(conflicting_groups))

for index, group in enumerate(conflicting_groups, start=1):

    print("\nCONFLICT:", index)
    print("Sentence:", group["key"])

    for record in group["records"]:

        print(
            record["source"],
            record["split"],
            "| Tokens:", record["tokens"],
            "| Labels:", record["labels"]
        )

print("\nFinal duplicate audit completed!")
