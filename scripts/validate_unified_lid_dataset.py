"""
Comprehensive validation script for the Unified Language Identification Dataset.

Checks:
- JSONL syntax across all 8 output files.
- Manifest existence and count consistency.
- Required fields in common schema.
- Length parity: len(tokens) == len(source_labels) == len(model_labels).
- Model label values in {0, 1, 2, 3, -100}.
- sentence_id uniqueness across all files.
- Zero normalized sentence overlap between train, validation, and test.
- Zero test-to-training leakage.
- Test split subset partition equality: test == test_comi + test_blog + test_twitter.
- Complete accounting: primary splits + excluded + quarantined == 69,079.
- Label distribution breakdown per split and subset.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "language_identification"

REQUIRED_FIELDS = [
    "sentence_id",
    "original_sentence_id",
    "source",
    "subset",
    "original_split",
    "split",
    "text",
    "tokens",
    "original_labels",
    "source_labels",
    "model_labels",
    "text_format",
    "lid_eligible",
    "lid_eligible_tokens",
    "source_record_id",
]

ALLOWED_MODEL_LABELS = {0, 1, 2, 3, -100}
TOTAL_RAW_EXPECTED = 69079


def normalize_comparison_key(tokens: list) -> str:
    return " ".join(t.strip().casefold() for t in tokens)


def validate_file(filepath: Path, expected_split: str) -> dict:
    print(f"\nValidating {filepath.name}...", flush=True)
    if not filepath.exists():
        return {"status": "FAIL", "errors": [f"File not found: {filepath}"]}

    records = []
    errors = []
    seen_ids = set()
    label_counts = Counter()
    subset_counts = Counter()
    total_tokens = 0
    norm_keys = set()

    with filepath.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                errors.append(f"Line {line_no}: Empty line")
                continue

            try:
                rec = json.loads(line_str)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_no}: JSON decode error: {e}")
                continue

            records.append(rec)
            sid = rec.get("sentence_id")

            # Check ID uniqueness
            if sid in seen_ids:
                errors.append(f"Line {line_no}: Duplicate sentence_id '{sid}'")
            else:
                seen_ids.add(sid)

            # Check required fields
            missing = [f for f in REQUIRED_FIELDS if f not in rec]
            if missing:
                errors.append(f"Line {line_no} ({sid}): Missing fields: {missing}")
                continue

            # Check split field
            if rec["split"] != expected_split:
                errors.append(f"Line {line_no} ({sid}): Split '{rec['split']}' != expected '{expected_split}'")

            # Check lengths
            tokens = rec["tokens"]
            src_labels = rec["source_labels"]
            model_labels = rec["model_labels"]

            if not (len(tokens) == len(src_labels) == len(model_labels)):
                errors.append(
                    f"Line {line_no} ({sid}): Length mismatch: tokens={len(tokens)}, "
                    f"source_labels={len(src_labels)}, model_labels={len(model_labels)}"
                )

            # Check allowed model labels
            for l in model_labels:
                if l not in ALLOWED_MODEL_LABELS:
                    errors.append(f"Line {line_no} ({sid}): Invalid model label '{l}'")
                label_counts[l] += 1

            total_tokens += len(tokens)
            subset_counts[rec["subset"]] += 1

            # Check lid eligibility counts
            comp_eligible_tokens = sum(1 for m in model_labels if m != -100)
            if rec["lid_eligible_tokens"] != comp_eligible_tokens:
                errors.append(f"Line {line_no} ({sid}): lid_eligible_tokens mismatch")
            if rec["lid_eligible"] != (comp_eligible_tokens > 0):
                errors.append(f"Line {line_no} ({sid}): lid_eligible boolean mismatch")

            norm_keys.add(normalize_comparison_key(tokens))

    print(f"  Records: {len(records):,} | Tokens: {total_tokens:,} | Errors: {len(errors)}")
    print(f"  Subsets: {dict(subset_counts)}")
    print(f"  Model Labels: EN(0)={label_counts[0]:,}, HI(1)={label_counts[1]:,}, TE(2)={label_counts[2]:,}, OTHER(3)={label_counts[3]:,}, IGNORED(-100)={label_counts[-100]:,}")

    return {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "file": filepath.name,
        "record_count": len(records),
        "total_tokens": total_tokens,
        "seen_ids": seen_ids,
        "norm_keys": norm_keys,
        "label_counts": dict(label_counts),
        "subset_counts": dict(subset_counts),
        "errors": errors,
        "records": records,
    }


def main():
    print("=" * 70)
    print("VALIDATING UNIFIED LANGUAGE IDENTIFICATION DATASET")
    print(f"Directory: {OUTPUT_DIR}")
    print("=" * 70)

    # 1. Validate Individual Files
    files_to_check = [
        ("train.jsonl", "train"),
        ("validation.jsonl", "validation"),
        ("test.jsonl", "test"),
        ("test_comi_lingua.jsonl", "test"),
        ("test_tenglish_blog.jsonl", "test"),
        ("test_tenglish_twitter.jsonl", "test"),
        ("excluded_records.jsonl", "excluded"),
        ("quarantined_duplicates.jsonl", "quarantined"),
    ]

    results = {}
    for filename, split in files_to_check:
        res = validate_file(OUTPUT_DIR / filename, split)
        results[filename] = res

    # 2. Check Global ID Uniqueness across primary splits, excluded and quarantined
    print("\n" + "=" * 70)
    print("CHECKING GLOBAL SENTENCE ID UNIQUENESS ACROSS ALL FILES")
    print("=" * 70)

    global_ids = Counter()
    for fname in ["train.jsonl", "validation.jsonl", "test.jsonl", "excluded_records.jsonl", "quarantined_duplicates.jsonl"]:
        for sid in results[fname]["seen_ids"]:
            global_ids[sid] += 1

    dup_global_ids = [sid for sid, c in global_ids.items() if c > 1]
    print(f"Total Unique Global IDs: {len(global_ids):,}")
    print(f"Global ID Duplicates:    {len(dup_global_ids)}")

    # 3. Check Zero Overlap Across Train, Validation, and Test
    print("\n" + "=" * 70)
    print("CHECKING SPLIT OVERLAPS & LEAKAGE")
    print("=" * 70)

    train_keys = results["train.jsonl"]["norm_keys"]
    val_keys = results["validation.jsonl"]["norm_keys"]
    test_keys = results["test.jsonl"]["norm_keys"]

    train_val_overlap = train_keys & val_keys
    train_test_overlap = train_keys & test_keys
    val_test_overlap = val_keys & test_keys

    print(f"Train vs. Validation Overlap: {len(train_val_overlap)} (Expected: 0)")
    print(f"Train vs. Test Overlap:       {len(train_test_overlap)} (Expected: 0)")
    print(f"Validation vs. Test Overlap:  {len(val_test_overlap)} (Expected: 0)")

    # 4. Check Test Subset Partition Integrity
    print("\n" + "=" * 70)
    print("CHECKING TEST SUBSET PARTITION INTEGRITY")
    print("=" * 70)

    unified_test_ids = results["test.jsonl"]["seen_ids"]
    sub_test_ids = (
        results["test_comi_lingua.jsonl"]["seen_ids"]
        | results["test_tenglish_blog.jsonl"]["seen_ids"]
        | results["test_tenglish_twitter.jsonl"]["seen_ids"]
    )

    test_partition_match = (unified_test_ids == sub_test_ids)
    print(f"Unified Test IDs ({len(unified_test_ids):,}) == Combined Domain Test IDs ({len(sub_test_ids):,}): {test_partition_match}")

    # 5. Check Overall Record Accounting
    print("\n" + "=" * 70)
    print("CHECKING OVERALL DATASET RECORD ACCOUNTING")
    print("=" * 70)

    n_train = results["train.jsonl"]["record_count"]
    n_val = results["validation.jsonl"]["record_count"]
    n_test = results["test.jsonl"]["record_count"]
    n_excl = results["excluded_records.jsonl"]["record_count"]
    n_quar = results["quarantined_duplicates.jsonl"]["record_count"]

    total_accounted = n_train + n_val + n_test + n_excl + n_quar

    print(f"Train:        {n_train:,}")
    print(f"Validation:   {n_val:,}")
    print(f"Test:         {n_test:,}")
    print(f"Excluded:     {n_excl:,}")
    print(f"Quarantined:  {n_quar:,}")
    print(f"Total:        {total_accounted:,} (Expected: {TOTAL_RAW_EXPECTED:,}) -> {'EXACT MATCH' if total_accounted == TOTAL_RAW_EXPECTED else 'MISMATCH'}")

    # 6. Check Manifest Consistency
    manifest_path = OUTPUT_DIR / "dataset_manifest.json"
    manifest_errors = []
    if not manifest_path.exists():
        manifest_errors.append("dataset_manifest.json missing")
    else:
        with manifest_path.open("r", encoding="utf-8") as f:
            man = json.load(f)
        if man["splits_summary"]["train"]["records"] != n_train:
            manifest_errors.append("Manifest train count mismatch")
        if man["splits_summary"]["validation"]["records"] != n_val:
            manifest_errors.append("Manifest validation count mismatch")
        if man["splits_summary"]["test"]["records"] != n_test:
            manifest_errors.append("Manifest test count mismatch")
        if man["total_raw_records_accounted"] != TOTAL_RAW_EXPECTED:
            manifest_errors.append("Manifest total raw records mismatch")

    print(f"\nManifest Validation Errors: {len(manifest_errors)}")

    # Overall Status
    all_files_pass = all(r["status"] == "PASS" for r in results.values())
    no_leakage = (len(train_val_overlap) == 0 and len(train_test_overlap) == 0 and len(val_test_overlap) == 0)
    accounting_pass = (total_accounted == TOTAL_RAW_EXPECTED)
    manifest_pass = (len(manifest_errors) == 0)

    if all_files_pass and no_leakage and accounting_pass and manifest_pass and len(dup_global_ids) == 0:
        print("\n" + "=" * 70)
        print("SUCCESS: All Unified Dataset Files and Manifest PASSED Validation Completely!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("FAILURE: Validation failed with issues detected above.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
