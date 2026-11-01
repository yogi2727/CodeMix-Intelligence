
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "data"
    / "raw"
    / "telugu_english"
    / "source"
)

OUTPUT = ROOT / "data" / "processed" / "normalized"

LABEL_MAP = {
    "te": "TE",
    "en": "EN",
    "ne": "NE",
    "univ": "OTHER"
}

FILES = {
    "blog_train": SOURCE / "Blog Dataset" / "train_data.txt",
    "blog_test": SOURCE / "Blog Dataset" / "test_data.txt",
    "twitter_train": SOURCE / "Twitter Dataset" / "train_data.txt",
    "twitter_test": SOURCE / "Twitter Dataset" / "test_data.txt"
}


def parse_file(name, path):

    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    records = []

    current_tokens = []
    current_original_labels = []
    current_labels = []

    errors = []
    statistics = Counter()

    sentence_number = 0

    def save_sentence():

        nonlocal sentence_number

        if not current_tokens:
            return

        sentence_number += 1

        text = " ".join(current_tokens)

        # NE is preserved but is not a primary language label.
        # A sentence containing at least one non-NE token
        # can contribute to the LID task.
        eligible_count = sum(
            label != "NE"
            for label in current_labels
        )

        record = {
            "sentence_id": (
                f"tenglish_{name}_{sentence_number:06d}"
            ),
            "source": "Telugu-English",
            "subset": name.split("_")[0].capitalize(),
            "split": name.split("_")[1],
            "text": text,
            "tokens": current_tokens.copy(),
            "original_labels": current_original_labels.copy(),
            "labels": current_labels.copy(),
            "text_format": "romanized_telugu_english",
            "lid_eligible": eligible_count > 0,
            "lid_eligible_tokens": eligible_count
        }

        records.append(record)

        current_tokens.clear()
        current_original_labels.clear()
        current_labels.clear()

    print(f"\nProcessing: {name}")

    with path.open("r", encoding="utf-8") as file:

        for line_number, line in enumerate(file, start=1):

            value = line.strip()

            # An empty line marks the end of a sentence.
            if not value:

                save_sentence()
                continue

            parts = value.rsplit(maxsplit=1)

            if len(parts) != 2:

                errors.append({
                    "line": line_number,
                    "reason": "Missing token or label",
                    "content": value
                })

                continue

            token, original_label = parts

            original_label = original_label.strip().lower()

            if original_label not in LABEL_MAP:

                errors.append({
                    "line": line_number,
                    "reason": "Unknown label",
                    "content": value
                })

                continue

            normalized_label = LABEL_MAP[original_label]

            current_tokens.append(token)
            current_original_labels.append(original_label)
            current_labels.append(normalized_label)

            statistics["tokens"] += 1
            statistics[normalized_label] += 1

        # Handle the last sentence if the file has no final blank line.
        save_sentence()

    if errors:

        print("ERRORS FOUND:", len(errors))

        for error in errors[:10]:
            print(error)

        raise ValueError(
            f"Preprocessing aborted for {name}. "
            "Resolve malformed lines before saving."
        )

    OUTPUT.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT / f"tenglish_{name}.jsonl"

    with output_path.open("w", encoding="utf-8") as file:

        for record in records:

            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

    print("Input file:", path.name)
    print("Total sentences:", len(records))
    print("Token distribution:", dict(statistics))
    print(
        "NE-only sentences:",
        sum(not record["lid_eligible"] for record in records)
    )
    print("Saved:", output_path.relative_to(ROOT))

    return records


def main():

    print("=" * 65)
    print("TELUGU-ENGLISH DATA PREPROCESSING")
    print("=" * 65)

    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    results = {}

    for name, path in FILES.items():

        results[name] = parse_file(name, path)

    print("\n" + "=" * 65)
    print("PREPROCESSING SUMMARY")
    print("=" * 65)

    for name, records in results.items():

        eligible = sum(
            record["lid_eligible"]
            for record in records
        )

        print(
            name,
            "| Sentences:", len(records),
            "| LID-eligible:", eligible,
            "| NE-only:", len(records) - eligible
        )

    print("\nAll four files processed successfully!")


if __name__ == "__main__":
    main()
