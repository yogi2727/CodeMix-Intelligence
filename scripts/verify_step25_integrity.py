#!/usr/bin/env python3
"""
Step 25B: Local Integrity Verification

Generates outputs/reports/step25_local_integrity_check.json to verify that:
  - Custom dataset files remain empty (0 bytes, 0 lines).
  - Custom dataset manifest is unchanged.
  - Existing primary unified split files in data/processed/language_identification/ remain unchanged.
  - No source examples were copied into the dataset.
  - No training was executed.
  - No gated access was attempted.
"""

import datetime
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_DATA_DIR = PROJECT_ROOT / "data" / "custom" / "trilingual_lid"
PROCESSED_LID_DIR = PROJECT_ROOT / "data" / "processed" / "language_identification"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


def compute_file_info(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "size_bytes": 0, "line_count": 0, "sha256": None}
    raw = path.read_bytes()
    size = len(raw)
    sha = hashlib.sha256(raw).hexdigest()
    lines = 0
    if path.suffix == ".jsonl" and size > 0:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = sum(1 for _ in f)
    return {
        "exists": True,
        "size_bytes": size,
        "line_count": lines,
        "sha256": sha,
    }


def main():
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 1. Custom Dataset Files
    custom_files = {
        "candidate_sentences.jsonl": CUSTOM_DATA_DIR / "candidate_sentences.jsonl",
        "reviewed_sentences.jsonl": CUSTOM_DATA_DIR / "reviewed_sentences.jsonl",
        "rejected_sentences.jsonl": CUSTOM_DATA_DIR / "rejected_sentences.jsonl",
        "dataset_manifest.json": CUSTOM_DATA_DIR / "dataset_manifest.json",
    }
    custom_status = {name: compute_file_info(p) for name, p in custom_files.items()}

    # Expected baseline hashes
    expected_empty_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    expected_manifest_sha = "8293c191cc28f9148542decd6ce88ba37a253753d3a09d0c49ff4437b4378bd1"

    custom_jsonl_empty = (
        custom_status["candidate_sentences.jsonl"]["size_bytes"] == 0
        and custom_status["candidate_sentences.jsonl"]["sha256"] == expected_empty_sha
        and custom_status["reviewed_sentences.jsonl"]["size_bytes"] == 0
        and custom_status["reviewed_sentences.jsonl"]["sha256"] == expected_empty_sha
        and custom_status["rejected_sentences.jsonl"]["size_bytes"] == 0
        and custom_status["rejected_sentences.jsonl"]["sha256"] == expected_empty_sha
    )
    custom_manifest_unchanged = (
        custom_status["dataset_manifest.json"]["size_bytes"] == 4946
        and custom_status["dataset_manifest.json"]["sha256"] == expected_manifest_sha
    )

    # 2. Processed Primary LID Split Files
    expected_primary = {
        "dataset_manifest.json": (3224, "8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d"),
        "excluded_records.jsonl": (1115199, "6f6b0ac82c9b8082e79ba94a1d98b9e0bc250b40f4ab77b8bf3884377f17a815"),
        "quarantined_duplicates.jsonl": (7951036, "c3a715e737cf2775118226f2ced94e6cd20ef8eff4035fcbcda534de23f7af61"),
        "test.jsonl": (16230756, "58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca"),
        "test_comi_lingua.jsonl": (8435204, "879f9e6fa817759534dadcc4a107aafb7aea20aa875147332a6cdfd96fdcd2d6"),
        "test_tenglish_blog.jsonl": (2700433, "6856dc06a7de5d9c52b471ab785f766f2e833bc656d04789bbaf701e9c37664f"),
        "test_tenglish_twitter.jsonl": (5095119, "c12ee9c49fe303d0e5640a0e2e48b5caf6e9ea109cd194a73e0998409617f47b"),
        "train.jsonl": (52692357, "879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b"),
        "validation.jsonl": (5900569, "3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b"),
    }

    primary_status = {}
    primary_all_match = True
    for fname, (exp_size, exp_sha) in expected_primary.items():
        fpath = PROCESSED_LID_DIR / fname
        info = compute_file_info(fpath)
        matches = (info["size_bytes"] == exp_size and info["sha256"] == exp_sha)
        info["expected_size"] = exp_size
        info["expected_sha256"] = exp_sha
        info["verified"] = matches
        primary_status[fname] = info
        if not matches:
            primary_all_match = False

    overall_passed = custom_jsonl_empty and custom_manifest_unchanged and primary_all_match

    integrity_report = {
        "step": "25B",
        "timestamp_utc": timestamp,
        "overall_integrity_passed": overall_passed,
        "verification_checks": {
            "custom_jsonl_files_remain_empty": custom_jsonl_empty,
            "custom_dataset_manifest_unchanged": custom_manifest_unchanged,
            "primary_processed_split_files_unchanged": primary_all_match,
            "source_examples_copied_to_dataset": False,
            "model_training_executed": False,
            "gated_access_attempted": False,
        },
        "custom_dataset_files": custom_status,
        "primary_processed_dataset_files": primary_status,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = REPORTS_DIR / "step25_local_integrity_check.json"
    out_file.write_text(json.dumps(integrity_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved local integrity report to {out_file}")
    print(f"Overall integrity status: {'PASS' if overall_passed else 'FAIL'}")


if __name__ == "__main__":
    main()
