
from pathlib import Path
from collections import Counter

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

ALLOWED_LABELS = {"te", "en", "ne", "univ"}


def read_sentences(path):

    sentences = []
    current = []
    counts = Counter()
    invalid = []

    with path.open("r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            text = line.strip()

            if not text:
                if current:
                    sentences.append(current)
                    current = []
                continue

            parts = text.rsplit(maxsplit=1)

            if len(parts) != 2:
                invalid.append(line_number)
                continue

            token, label = parts
            label = label.lower()

            if label not in ALLOWED_LABELS:
                invalid.append(line_number)
                continue

            current.append((token, label))
            counts[label] += 1

        if current:
            sentences.append(current)

    return sentences, counts, invalid


def normalize_sentence(sentence):
    return " ".join(
        token.strip().casefold()
        for token, _ in sentence
    )


all_splits = {}

print("TELUGU-ENGLISH SPLIT AUDIT")
print("=" * 65)

for source_name, split_paths in FILES.items():

    all_splits[source_name] = {}

    for split_name, path in split_paths.items():

        sentences, counts, invalid = read_sentences(path)

        normalized = {
            normalize_sentence(sentence)
            for sentence in sentences
        }

        all_splits[source_name][split_name] = {
            "sentences": sentences,
            "normalized": normalized,
            "counts": counts
        }

        print(f"\n{source_name} — {split_name.upper()}")
        print("Sentences:", len(sentences))
        print("Tokens:", sum(counts.values()))
        print("Labels:", dict(counts))
        print("Invalid lines:", len(invalid))
        print("Unique normalized sentences:", len(normalized))

    # Check within each source
    train = all_splits[source_name]["train"]["normalized"]
    test = all_splits[source_name]["test"]["normalized"]

    duplicates = train & test

    print(f"\n{source_name} TRAIN/TEST DUPLICATES")
    print("Exact normalized duplicates:", len(duplicates))

    for sentence in list(duplicates)[:5]:
        print("Example:", sentence)


# Combined cross-source split audit
combined_train = set()
combined_test = set()

for source_name in FILES:

    combined_train.update(
        all_splits[source_name]["train"]["normalized"]
    )

    combined_test.update(
        all_splits[source_name]["test"]["normalized"]
    )

cross_source_duplicates = combined_train & combined_test

print("\n" + "=" * 65)
print("COMBINED TRAIN/TEST DUPLICATE AUDIT")
print("=" * 65)

print("Unique training sentences:", len(combined_train))
print("Unique testing sentences:", len(combined_test))
print("Train/test exact duplicates:", len(cross_source_duplicates))

for sentence in list(cross_source_duplicates)[:10]:
    print("Duplicate:", sentence)

print("\nAudit completed!")
