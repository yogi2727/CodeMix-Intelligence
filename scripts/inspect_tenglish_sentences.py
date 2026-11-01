
from pathlib import Path
from collections import Counter

# Resolve the project root automatically
PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "telugu_english"
    / "source"
)

FILES = {
    "Blog Train": SOURCE / "Blog Dataset" / "train_data.txt",
    "Blog Test": SOURCE / "Blog Dataset" / "test_data.txt",
    "Twitter Train": SOURCE / "Twitter Dataset" / "train_data.txt",
    "Twitter Test": SOURCE / "Twitter Dataset" / "test_data.txt",
}


def inspect_sentences(name, path):

    print("\n" + "=" * 65)
    print(name)
    print("=" * 65)

    if not path.exists():
        print("ERROR: File not found:", path)
        return

    samples = {
        "General": [],
        "Contains NE": None,
        "Contains UNIV": None
    }

    labels = Counter()
    sentence_count = 0
    token_count = 0
    malformed = []

    def process_sentence(tokens):

        nonlocal sentence_count

        if not tokens:
            return

        sentence_count += 1

        sentence_labels = [tag for _, tag in tokens]
        labels.update(sentence_labels)

        if len(samples["General"]) < 3:
            samples["General"].append(tokens.copy())

        if (
            "ne" in sentence_labels
            and samples["Contains NE"] is None
        ):
            samples["Contains NE"] = tokens.copy()

        if (
            "univ" in sentence_labels
            and samples["Contains UNIV"] is None
        ):
            samples["Contains UNIV"] = tokens.copy()

    current_sentence = []

    with path.open("r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            text = line.strip()

            if not text:
                process_sentence(current_sentence)
                current_sentence = []
                continue

            parts = text.rsplit(maxsplit=1)

            if len(parts) != 2:

                if len(malformed) < 5:
                    malformed.append((line_number, text))

                continue

            word, tag = parts

            current_sentence.append((word, tag))
            token_count += 1

        # Process final sentence if file has no ending blank line
        process_sentence(current_sentence)

    print("File:", path.name)
    print("Total sentences:", sentence_count)
    print("Total tokens:", token_count)
    print("Malformed lines:", len(malformed))

    print("\nLanguage label distribution:")

    for tag, count in labels.most_common():
        print(f"{tag}: {count}")

    print("\nSentence examples:")

    for index, tokens in enumerate(samples["General"], start=1):

        print(f"\nGeneral example {index}:")
        print(" ".join(f"{word}/{tag}" for word, tag in tokens))

    for category in ["Contains NE", "Contains UNIV"]:

        tokens = samples[category]

        if tokens is not None:

            print(f"\n{category} example:")
            print(" ".join(f"{word}/{tag}" for word, tag in tokens))

    if malformed:

        print("\nMalformed line examples:")

        for line_number, text in malformed:
            print(line_number, repr(text))


print("Telugu-English complete sentence inspection")
print("Project root:", PROJECT_ROOT)

for name, path in FILES.items():
    inspect_sentences(name, path)

print("\nSentence inspection completed!")
