"""
Validation script for processed Telugu-English JSONL datasets.

Validates schema conformity, token-label alignment, text reconstruction,
label distributions, LID eligibility logic, ID uniqueness, and benchmark counts.
"""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "normalized"

REQUIRED_FIELDS = [
    "sentence_id",
    "source",
    "subset",
    "split",
    "text",
    "tokens",
    "original_labels",
    "labels",
    "text_format",
    "lid_eligible",
    "lid_eligible_tokens",
]

ALLOWED_LABELS = {"EN", "HI", "TE", "NE", "OTHER"}

FILES_TO_VALIDATE = {
    "tenglish_blog_train.jsonl": {
        "expected_source": "Telugu-English",
        "expected_subset": "Blog",
        "expected_split": "train",
        "expected_sentences": 6547,
        "expected_tokens": 92743,
    },
    "tenglish_blog_test.jsonl": {
        "expected_source": "Telugu-English",
        "expected_subset": "Blog",
        "expected_split": "test",
        "expected_sentences": 3110,
        "expected_tokens": 42898,
    },
    "tenglish_twitter_train.jsonl": {
        "expected_source": "Telugu-English",
        "expected_subset": "Twitter",
        "expected_split": "train",
        "expected_sentences": 17082,
        "expected_tokens": 148358,
    },
    "tenglish_twitter_test.jsonl": {
        "expected_source": "Telugu-English",
        "expected_subset": "Twitter",
        "expected_split": "test",
        "expected_sentences": 7322,
        "expected_tokens": 63662,
    },
}


def validate_file(filename: str, spec: dict) -> dict:
    filepath = DATA_DIR / filename
    print("\n" + "=" * 70)
    print(f"VALIDATING: {filename}")
    print("=" * 70)

    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        return {
            "status": "FAIL",
            "file": filename,
            "errors": [f"File not found: {filepath}"],
        }

    seen_ids = set()
    duplicate_ids = []
    validation_errors = []

    total_records = 0
    total_tokens = 0
    label_counts = Counter({l: 0 for l in ALLOWED_LABELS})
    ne_only_sentences = 0
    lid_eligible_sentences = 0

    expected_prefix = f"tenglish_{spec['expected_subset'].lower()}_{spec['expected_split']}_"

    with filepath.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                validation_errors.append(f"Line {line_no}: Empty line detected in JSONL.")
                continue

            # 1. Valid JSON format
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                validation_errors.append(f"Line {line_no}: JSON decode error: {e}")
                continue

            total_records += 1

            # 2. Required fields
            missing_fields = [field for field in REQUIRED_FIELDS if field not in record]
            if missing_fields:
                validation_errors.append(
                    f"Line {line_no} (ID: {record.get('sentence_id')}): Missing fields: {missing_fields}"
                )
                continue

            sentence_id = record["sentence_id"]

            # 3. Unique sentence IDs and format
            if not isinstance(sentence_id, str) or not sentence_id.startswith(expected_prefix):
                validation_errors.append(
                    f"Line {line_no}: Invalid sentence_id format: '{sentence_id}'. Expected prefix: '{expected_prefix}'"
                )

            if sentence_id in seen_ids:
                duplicate_ids.append(sentence_id)
                validation_errors.append(f"Line {line_no}: Duplicate sentence_id '{sentence_id}'")
            else:
                seen_ids.add(sentence_id)

            # 4. Metadata consistency
            if record["source"] != spec["expected_source"]:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): Invalid source '{record['source']}'. Expected '{spec['expected_source']}'"
                )
            if record["subset"] != spec["expected_subset"]:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): Invalid subset '{record['subset']}'. Expected '{spec['expected_subset']}'"
                )
            if record["split"] != spec["expected_split"]:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): Invalid split '{record['split']}'. Expected '{spec['expected_split']}'"
                )
            if record["text_format"] != "romanized_telugu_english":
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): Invalid text_format '{record['text_format']}'"
                )

            # 5. Type and length checks
            tokens = record["tokens"]
            orig_labels = record["original_labels"]
            labels = record["labels"]

            if not isinstance(tokens, list) or not isinstance(orig_labels, list) or not isinstance(labels, list):
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): 'tokens', 'original_labels', and 'labels' must be lists."
                )
                continue

            if len(tokens) == 0:
                validation_errors.append(f"Line {line_no} ({sentence_id}): Sentence has zero tokens.")
                continue

            if not (len(tokens) == len(orig_labels) == len(labels)):
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): Length mismatch: "
                    f"tokens={len(tokens)}, original_labels={len(orig_labels)}, labels={len(labels)}"
                )

            # 6. Sentence reconstruction
            expected_text = " ".join(tokens)
            if record["text"] != expected_text:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): 'text' mismatch. "
                    f"Reconstructed from tokens: '{expected_text}' != record['text']: '{record['text']}'"
                )

            # 7. Allowed normalized labels
            invalid_labels = [l for l in labels if l not in ALLOWED_LABELS]
            if invalid_labels:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): Unrecognized labels found: {invalid_labels}"
                )

            for l in labels:
                label_counts[l] += 1
            total_tokens += len(tokens)

            # 8. LID eligibility logic
            computed_eligible_tokens = sum(1 for l in labels if l != "NE")
            computed_eligible = computed_eligible_tokens > 0

            if record["lid_eligible_tokens"] != computed_eligible_tokens:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): lid_eligible_tokens mismatch: "
                    f"recorded={record['lid_eligible_tokens']}, computed={computed_eligible_tokens}"
                )

            if not isinstance(record["lid_eligible"], bool):
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): lid_eligible must be a boolean."
                )
            elif record["lid_eligible"] != computed_eligible:
                validation_errors.append(
                    f"Line {line_no} ({sentence_id}): lid_eligible boolean mismatch: "
                    f"recorded={record['lid_eligible']}, computed={computed_eligible}"
                )

            if computed_eligible:
                lid_eligible_sentences += 1
            else:
                ne_only_sentences += 1

    # Compare with expected benchmarks
    sentence_count_match = total_records == spec["expected_sentences"]
    token_count_match = total_tokens == spec["expected_tokens"]

    if not sentence_count_match:
        validation_errors.append(
            f"Benchmark mismatch: Expected {spec['expected_sentences']} sentences, got {total_records}"
        )
    if not token_count_match:
        validation_errors.append(
            f"Benchmark mismatch: Expected {spec['expected_tokens']} tokens, got {total_tokens}"
        )

    # Reporting
    print(f"File Path:                {filepath.relative_to(PROJECT_ROOT)}")
    print(f"Total Records/Sentences:  {total_records:,} (Expected: {spec['expected_sentences']:,}) -> {'MATCH' if sentence_count_match else 'MISMATCH'}")
    print(f"Total Tokens:             {total_tokens:,} (Expected: {spec['expected_tokens']:,}) -> {'MATCH' if token_count_match else 'MISMATCH'}")
    print(f"Unique Sentence IDs:      {len(seen_ids):,}")
    print(f"Duplicate Sentence IDs:   {len(duplicate_ids)}")
    print(f"LID-Eligible Sentences:   {lid_eligible_sentences:,} ({lid_eligible_sentences/total_records*100:.2f}%)")
    print(f"NE-Only Sentences:        {ne_only_sentences:,} ({ne_only_sentences/total_records*100:.2f}%)")
    print("\nToken Label Distribution:")
    for lbl in sorted(ALLOWED_LABELS):
        count = label_counts[lbl]
        pct = (count / total_tokens * 100) if total_tokens > 0 else 0
        print(f"  {lbl:<6}: {count:>8,} tokens ({pct:>5.2f}%)")

    print(f"\nValidation Errors:        {len(validation_errors)}")
    if validation_errors:
        print("Sample Errors (first 10):")
        for err in validation_errors[:10]:
            print(f"  - {err}")

    status = "PASS" if len(validation_errors) == 0 else "FAIL"
    print(f"Validation Result:        {status}")

    return {
        "status": status,
        "filename": filename,
        "total_records": total_records,
        "expected_records": spec["expected_sentences"],
        "records_match": sentence_count_match,
        "total_tokens": total_tokens,
        "expected_tokens": spec["expected_tokens"],
        "tokens_match": token_count_match,
        "unique_ids": len(seen_ids),
        "duplicate_ids": len(duplicate_ids),
        "ne_only_sentences": ne_only_sentences,
        "lid_eligible_sentences": lid_eligible_sentences,
        "label_counts": dict(label_counts),
        "validation_errors": len(validation_errors),
        "error_samples": validation_errors[:10],
    }


def main():
    print("=" * 70)
    print("TELUGU-ENGLISH PROCESSED DATASET VALIDATION")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Dir:     {DATA_DIR}")
    print("=" * 70)

    all_results = []
    grand_records = 0
    grand_tokens = 0
    grand_labels = Counter()
    grand_ne_only = 0
    grand_errors = 0

    for filename, spec in FILES_TO_VALIDATE.items():
        res = validate_file(filename, spec)
        all_results.append(res)
        if res["status"] != "FAIL" or "total_records" in res:
            grand_records += res.get("total_records", 0)
            grand_tokens += res.get("total_tokens", 0)
            grand_labels.update(res.get("label_counts", {}))
            grand_ne_only += res.get("ne_only_sentences", 0)
            grand_errors += res.get("validation_errors", 0)

    print("\n" + "=" * 70)
    print("OVERALL VALIDATION SUMMARY ACROSS ALL 4 FILES")
    print("=" * 70)
    print(f"Total Processed Sentences: {grand_records:,} (Expected: 34,061)")
    print(f"Total Processed Tokens:    {grand_tokens:,} (Expected: 347,661)")
    print(f"Total NE-Only Sentences:   {grand_ne_only:,} ({grand_ne_only/grand_records*100:.2f}%)")
    print(f"Total Validation Errors:   {grand_errors}")
    print("\nAggregated Label Counts:")
    for lbl in sorted(ALLOWED_LABELS):
        count = grand_labels[lbl]
        pct = (count / grand_tokens * 100) if grand_tokens > 0 else 0
        print(f"  {lbl:<6}: {count:>8,} tokens ({pct:>5.2f}%)")

    all_passed = all(r["status"] == "PASS" for r in all_results)

    print("\nFile-by-File Status:")
    for r in all_results:
        rec_check = "OK" if r.get("records_match") else "MISMATCH"
        tok_check = "OK" if r.get("tokens_match") else "MISMATCH"
        print(f"  [{r['status']}] {r['filename']:<30} | Records: {r.get('total_records', 0):>6} ({rec_check}) | Tokens: {r.get('total_tokens', 0):>7} ({tok_check}) | Errors: {r.get('validation_errors', 0)}")

    if all_passed:
        print("\nSUCCESS: All four Telugu-English processed files PASSED validation completely!")
        sys.exit(0)
    else:
        print("\nFAILURE: One or more files failed validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
