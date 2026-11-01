
from pathlib import Path
from collections import Counter
import os

SOURCE = Path(os.environ["TEMP"]) / "cmtet-lid-source"

FILES = {
    "Blog Train": SOURCE / "Blog Dataset" / "train_data.txt",
    "Blog Test": SOURCE / "Blog Dataset" / "test_data.txt",
    "Twitter Train": SOURCE / "Twitter Dataset" / "train_data.txt",
    "Twitter Test": SOURCE / "Twitter Dataset" / "test_data.txt",
}


def inspect_file(name, path):

    print("\n" + "=" * 65)
    print(name)
    print("=" * 65)

    if not path.exists():
        print("ERROR: File not found:", path)
        return

    tag_counts = Counter()

    total_lines = 0
    token_lines = 0
    sentence_boundaries = 0
    malformed_lines = 0

    sample_lines = []

    with path.open("r", encoding="utf-8") as file:

        for line in file:

            total_lines += 1

            clean_line = line.rstrip("\r\n")

            if not clean_line.strip():
                sentence_boundaries += 1
                continue

            token_lines += 1

            if len(sample_lines) < 25:
                sample_lines.append(repr(clean_line))

            parts = clean_line.rsplit(maxsplit=1)

            if len(parts) == 2:
                token, possible_tag = parts
                tag_counts[possible_tag] += 1
            else:
                malformed_lines += 1

    print("File:", path.name)
    print("Total lines:", total_lines)
    print("Token lines:", token_lines)
    print("Sentence boundaries:", sentence_boundaries)
    print("Malformed lines:", malformed_lines)

    print("\nFirst 25 non-empty lines:")

    for line in sample_lines:
        print(line)

    print("\nPossible language tag frequencies:")

    for tag, count in tag_counts.most_common():
        print(repr(tag), ":", count)


print("Inspecting Telugu-English dataset files...")

for name, path in FILES.items():
    inspect_file(name, path)

print("\nAll file inspections completed!")
