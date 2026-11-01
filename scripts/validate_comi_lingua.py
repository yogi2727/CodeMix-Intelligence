"""
Validation script for processed COMI-LINGUA JSONL files and audit reports.

Validates schema conformity, consensus label integrity, length alignment,
ID uniqueness, complete record accounting (no loss), and audit consistency.
"""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "normalized" / "comi_lingua"

REQUIRED_ALIGNED_FIELDS = [
    "sentence_id",
    "source",
    "subset",
    "split",
    "text",
    "tokens",
    "original_labels_by_annotator",
    "labels",
    "consensus_method",
    "ignored_token_count",
    "lid_eligible",
    "lid_eligible_tokens",
    "alignment_method",
]

REQUIRED_REJECTED_FIELDS = [
    "original_index",
    "split",
    "text",
    "rejection_reason",
    "rejection_details",
]

ALLOWED_CONSENSUS_LABELS = {"EN", "HI", "OTHER", None}

EXPECTED_COUNTS = {
    "train": 30487,
    "test": 5000,
}


def validate_split(split_name: str) -> dict:
    aligned_path = DATA_DIR / f"comi_lid_{split_name}.jsonl"
    rejected_path = DATA_DIR / f"comi_lid_{split_name}_rejected.jsonl"

    print("\n" + "=" * 70)
    print(f"VALIDATING SPLIT: {split_name.upper()}")
    print("=" * 70)

    errors = []

    if not aligned_path.exists():
        errors.append(f"Missing aligned file: {aligned_path}")
    if not rejected_path.exists():
        errors.append(f"Missing rejected file: {rejected_path}")

    if errors:
        return {"status": "FAIL", "errors": errors}

    # Validate Aligned file
    seen_ids = set()
    aligned_count = 0
    total_tokens = 0
    label_counts = Counter()
    total_ignored = 0
    lid_eligible_sentences = 0
    lid_ineligible_sentences = 0
    expected_prefix = f"comi_lid_{split_name}_"

    with aligned_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                errors.append(f"Aligned line {line_no}: Empty line")
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Aligned line {line_no}: JSON decode error: {e}")
                continue

            aligned_count += 1

            # Required fields
            missing = [fld for fld in REQUIRED_ALIGNED_FIELDS if fld not in record]
            if missing:
                errors.append(f"Aligned line {line_no} (ID: {record.get('sentence_id')}): Missing fields: {missing}")
                continue

            sid = record["sentence_id"]
            if sid in seen_ids:
                errors.append(f"Aligned line {line_no}: Duplicate sentence_id '{sid}'")
            else:
                seen_ids.add(sid)

            if not sid.startswith(expected_prefix):
                errors.append(f"Aligned line {line_no}: ID '{sid}' does not start with '{expected_prefix}'")

            if record["source"] != "COMI-LINGUA":
                errors.append(f"Aligned line {line_no} ({sid}): Invalid source '{record['source']}'")
            if record["split"] != split_name:
                errors.append(f"Aligned line {line_no} ({sid}): Split '{record['split']}' != expected '{split_name}'")

            tokens = record["tokens"]
            labels = record["labels"]
            orig_annotators = record["original_labels_by_annotator"]

            if not isinstance(tokens, list) or not isinstance(labels, list):
                errors.append(f"Aligned line {line_no} ({sid}): tokens and labels must be lists")
                continue

            if len(tokens) == 0:
                errors.append(f"Aligned line {line_no} ({sid}): Empty tokens list")

            if len(tokens) != len(labels):
                errors.append(f"Aligned line {line_no} ({sid}): Length mismatch tokens={len(tokens)}, labels={len(labels)}")

            # Check original labels by annotator
            if not isinstance(orig_annotators, dict) or not {"annotator_1", "annotator_2", "annotator_3"}.issubset(orig_annotators):
                errors.append(f"Aligned line {line_no} ({sid}): Invalid original_labels_by_annotator format")
            else:
                for a_key in ["annotator_1", "annotator_2", "annotator_3"]:
                    if len(orig_annotators[a_key]) != len(tokens):
                        errors.append(f"Aligned line {line_no} ({sid}): Length mismatch in {a_key}: {len(orig_annotators[a_key])} vs {len(tokens)}")

            # Allowed labels and counts
            for l in labels:
                if l not in ALLOWED_CONSENSUS_LABELS:
                    errors.append(f"Aligned line {line_no} ({sid}): Illegal label '{l}'")
                label_counts["null" if l is None else l] += 1

            total_tokens += len(tokens)

            # Ignored and LID eligibility checks
            comp_ignored = sum(1 for l in labels if l is None)
            comp_eligible = sum(1 for l in labels if l is not None)

            if record["ignored_token_count"] != comp_ignored:
                errors.append(f"Aligned line {line_no} ({sid}): ignored_token_count mismatch: {record['ignored_token_count']} != {comp_ignored}")
            if record["lid_eligible_tokens"] != comp_eligible:
                errors.append(f"Aligned line {line_no} ({sid}): lid_eligible_tokens mismatch: {record['lid_eligible_tokens']} != {comp_eligible}")
            if record["lid_eligible"] != (comp_eligible > 0):
                errors.append(f"Aligned line {line_no} ({sid}): lid_eligible boolean mismatch")

            total_ignored += comp_ignored
            if comp_eligible > 0:
                lid_eligible_sentences += 1
            else:
                lid_ineligible_sentences += 1

    # Validate Rejected file
    rejected_count = 0
    rejection_reasons = Counter()

    with rejected_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                errors.append(f"Rejected line {line_no}: Empty line")
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Rejected line {line_no}: JSON decode error: {e}")
                continue

            rejected_count += 1
            missing = [fld for fld in REQUIRED_REJECTED_FIELDS if fld not in record]
            if missing:
                errors.append(f"Rejected line {line_no}: Missing fields: {missing}")
                continue

            if record["split"] != split_name:
                errors.append(f"Rejected line {line_no}: Split '{record['split']}' != expected '{split_name}'")

            rejection_reasons[record["rejection_reason"]] += 1

    # Total accounting check (zero loss of records)
    total_processed = aligned_count + rejected_count
    expected_total = EXPECTED_COUNTS[split_name]
    accounting_match = (total_processed == expected_total)

    if not accounting_match:
        errors.append(
            f"Record accounting mismatch: Aligned ({aligned_count}) + Rejected ({rejected_count}) = {total_processed} != Expected ({expected_total})"
        )

    print(f"Total Raw Records Accounted: {total_processed:,} / {expected_total:,} -> {'MATCH' if accounting_match else 'MISMATCH'}")
    print(f"  Successfully Aligned:      {aligned_count:,} ({aligned_count/total_processed*100:.2f}%)")
    print(f"  Quarantined / Rejected:    {rejected_count:,} ({rejected_count/total_processed*100:.2f}%)")
    print(f"  Rejection Reasons:         {dict(rejection_reasons)}")
    print(f"Total Tokens in Aligned:     {total_tokens:,}")
    print(f"  Usable Consensus Tokens:   {total_tokens - total_ignored:,}")
    print(f"  Ignored (No-Majority) Tok: {total_ignored:,} ({total_ignored/total_tokens*100:.2f}%)")
    print(f"  Label Counts:              {dict(label_counts)}")
    print(f"Validation Errors:           {len(errors)}")

    if errors:
        print("Sample Errors (first 10):")
        for err in errors[:10]:
            print(f"  - {err}")

    status = "PASS" if len(errors) == 0 else "FAIL"
    print(f"Split Result:                {status}")

    return {
        "status": status,
        "split": split_name,
        "total_records": total_processed,
        "aligned_records": aligned_count,
        "rejected_records": rejected_count,
        "rejection_reasons": dict(rejection_reasons),
        "total_tokens": total_tokens,
        "ignored_tokens": total_ignored,
        "usable_tokens": total_tokens - total_ignored,
        "label_counts": dict(label_counts),
        "lid_eligible_sentences": lid_eligible_sentences,
        "lid_ineligible_sentences": lid_ineligible_sentences,
        "errors": errors,
    }


def main():
    print("=" * 70)
    print("COMI-LINGUA PROCESSED DATASET VALIDATION")
    print("=" * 70)

    train_res = validate_split("train")
    test_res = validate_split("test")

    # Validate audit json
    audit_path = DATA_DIR / "comi_lid_audit.json"
    audit_errors = []
    print("\n" + "=" * 70)
    print("VALIDATING AUDIT REPORT: comi_lid_audit.json")
    print("=" * 70)

    if not audit_path.exists():
        audit_errors.append("comi_lid_audit.json does not exist")
    else:
        with audit_path.open("r", encoding="utf-8") as f:
            audit = json.load(f)

        if audit["splits"]["train"]["aligned_records"] != train_res.get("aligned_records"):
            audit_errors.append("Audit train aligned count mismatch")
        if audit["splits"]["test"]["aligned_records"] != test_res.get("aligned_records"):
            audit_errors.append("Audit test aligned count mismatch")
        if audit["overall_summary"]["total_records"] != (train_res.get("total_records", 0) + test_res.get("total_records", 0)):
            audit_errors.append("Audit overall total records mismatch")

    print(f"Audit File Errors: {len(audit_errors)}")
    if audit_errors:
        for err in audit_errors:
            print(f"  - {err}")

    all_passed = (
        train_res["status"] == "PASS"
        and test_res["status"] == "PASS"
        and len(audit_errors) == 0
    )

    print("\n" + "=" * 70)
    if all_passed:
        print("SUCCESS: All COMI-LINGUA files PASSED validation completely!")
        sys.exit(0)
    else:
        print("FAILURE: Validation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
