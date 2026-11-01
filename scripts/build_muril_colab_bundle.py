"""
CodeMix Intelligence - Step 31
Colab Training Bundle Builder

Creates artifacts/colab/muril_lid_data_bundle.zip containing strictly:
- train.jsonl
- validation.jsonl
- bundle_manifest.json
- README.md

Strict Constraints:
- Zero modifications to original processed datasets or manifests.
- Zero test set inclusion (test_data_included = false).
- Verified canonical schema: {"id": str, "tokens": list[str], "labels": list[int]}.
- Cryptographic hash verification before and after bundling.
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

# Ensure UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parent.parent
DATA_DIR = WORKSPACE / "data" / "processed" / "language_identification"
ARTIFACTS_DIR = WORKSPACE / "artifacts" / "colab"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
BUNDLE_ZIP = ARTIFACTS_DIR / "muril_lid_data_bundle.zip"

BASELINE_HASHES = {
    "train.jsonl": {
        "size": 52692357,
        "sha256": "879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b"
    },
    "validation.jsonl": {
        "size": 5900569,
        "sha256": "3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b"
    },
    "test.jsonl": {
        "size": 16230756,
        "sha256": "58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca"
    },
    "dataset_manifest.json": {
        "size": 3224,
        "sha256": "8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d"
    }
}


def verify_source_integrity():
    print("[1/5] Verifying source dataset integrity against baselines...")
    for fname, meta in BASELINE_HASHES.items():
        p = DATA_DIR / fname
        if not p.exists():
            raise FileNotFoundError(f"Missing source file: {p}")
        size = p.stat().st_size
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert size == meta["size"], f"Size mismatch for {fname}: expected {meta['size']}, got {size}"
        assert h == meta["sha256"], f"SHA256 mismatch for {fname}: expected {meta['sha256']}, got {h}"
    print("  Source integrity verified: 100% match with baseline SHA-256 hashes.")


def build_canonical_records(split_name: str, src_path: Path, dest_path: Path):
    print(f"  Extracting canonical records for {split_name}...")
    records_count = 0
    total_tokens = 0
    label_counts = Counter()
    
    with open(src_path, "r", encoding="utf-8") as f_in, open(dest_path, "w", encoding="utf-8") as f_out:
        for line in f_in:
            rec = json.loads(line)
            sid = rec["sentence_id"]
            tokens = rec["tokens"]
            model_labels = rec["model_labels"]
            
            assert len(tokens) == len(model_labels), f"Length mismatch in record {sid}"
            for ml in model_labels:
                assert ml in {0, 1, 2, 3, -100}, f"Invalid label {ml} in record {sid}"
                label_counts[ml] += 1
                
            canonical = {
                "id": sid,
                "tokens": tokens,
                "labels": model_labels
            }
            f_out.write(json.dumps(canonical, ensure_ascii=False) + "\n")
            records_count += 1
            total_tokens += len(tokens)
            
    supervised_tokens = label_counts[0] + label_counts[1] + label_counts[2] + label_counts[3]
    ignored_tokens = label_counts[-100]
    assert supervised_tokens + ignored_tokens == total_tokens
    
    return {
        "records": records_count,
        "total_tokens": total_tokens,
        "supervised_tokens": supervised_tokens,
        "ignored_tokens": ignored_tokens,
        "label_counts": {
            "EN_0": label_counts[0],
            "HI_1": label_counts[1],
            "TE_2": label_counts[2],
            "OTHER_3": label_counts[3],
            "IGNORED_minus100": label_counts[-100]
        }
    }


def create_readme(dest_path: Path):
    content = """# CodeMix Intelligence: MuRIL Baseline Training Data Bundle

This data bundle contains the preprocessed, canonical training and validation datasets for fine-tuning `google/muril-base-cased` on token-level Language Identification (LID).

## Bundle Contents

- `train.jsonl`: 43,369 canonical training sentences.
- `validation.jsonl`: 4,820 canonical validation sentences.
- `bundle_manifest.json`: Verification manifest with dataset statistics and SHA-256 hashes.
- `README.md`: This reference documentation.

## Record Schema

Each line in `train.jsonl` and `validation.jsonl` is a valid JSON object with the following fields:
- `id` (string): Unique sentence identifier (e.g., `lid_train_000001`).
- `tokens` (list of strings): Original whitespace tokens preserving exact text sequence.
- `labels` (list of integers): Token-level model labels matching `tokens` 1-to-1.

## Label Taxonomy

- `0`: English (`EN`)
- `1`: Hindi (`HI`)
- `2`: Telugu (`TE`)
- `3`: Universal / Punctuation / Symbols (`OTHER`)
- `-100`: Ignored token position (Named Entities, mixed-script, ambiguous, null, continuation subwords, and special tokens)

## Strict Test Set Isolation

In accordance with empirical governance standards:
- **Zero test records** are included in this bundle.
- Model checkpoint selection, learning rate scheduling, and early stopping must be performed strictly using `validation.jsonl`.
- The locked benchmark test set (`test.jsonl`) remains reserved exclusively for final post-training evaluation.
"""
    dest_path.write_text(content, encoding="utf-8")


def main():
    print("=" * 70)
    print("CodeMix Intelligence - Step 31: Colab Training Bundle Builder")
    print("=" * 70)

    # 1. Verify source dataset integrity
    verify_source_integrity()

    # 2. Prepare staging directory
    staging_dir = WORKSPACE / "scratch" / "bundle_staging"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    print("[2/5] Generating canonical training and validation datasets...")
    train_stats = build_canonical_records(
        "train",
        DATA_DIR / "train.jsonl",
        staging_dir / "train.jsonl"
    )
    val_stats = build_canonical_records(
        "validation",
        DATA_DIR / "validation.jsonl",
        staging_dir / "validation.jsonl"
    )

    # Assert expected counts
    assert train_stats["records"] == 43369
    assert train_stats["total_tokens"] == 665313
    assert train_stats["supervised_tokens"] == 638926
    assert train_stats["ignored_tokens"] == 26387

    assert val_stats["records"] == 4820
    assert val_stats["total_tokens"] == 73957
    assert val_stats["supervised_tokens"] == 70992
    assert val_stats["ignored_tokens"] == 2965

    # 3. Create README
    print("[3/5] Creating README and bundle manifest...")
    create_readme(staging_dir / "README.md")

    # Compute checksums of files in staging
    train_dest = staging_dir / "train.jsonl"
    val_dest = staging_dir / "validation.jsonl"
    readme_dest = staging_dir / "README.md"

    manifest = {
        "bundle_name": "MuRIL Baseline LID Colab Training Bundle",
        "version": "1.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_dataset_directory": "data/processed/language_identification",
        "original_source_checksums": {
            "train_jsonl_sha256": BASELINE_HASHES["train.jsonl"]["sha256"],
            "validation_jsonl_sha256": BASELINE_HASHES["validation.jsonl"]["sha256"]
        },
        "governance": {
            "test_data_included": False,
            "custom_pilot_data_included": False,
            "isolation_status": "STRICT_EVALUATION_ISOLATION"
        },
        "taxonomy": {
            "model_id": "google/muril-base-cased",
            "classes": {
                "EN": 0,
                "HI": 1,
                "TE": 2,
                "OTHER": 3
            },
            "ignore_label_id": -100,
            "recommended_max_length": 256
        },
        "splits": {
            "train": {
                "records": train_stats["records"],
                "total_tokens": train_stats["total_tokens"],
                "supervised_tokens": train_stats["supervised_tokens"],
                "ignored_tokens": train_stats["ignored_tokens"],
                "label_counts": train_stats["label_counts"],
                "file_size_bytes": train_dest.stat().st_size,
                "sha256": hashlib.sha256(train_dest.read_bytes()).hexdigest()
            },
            "validation": {
                "records": val_stats["records"],
                "total_tokens": val_stats["total_tokens"],
                "supervised_tokens": val_stats["supervised_tokens"],
                "ignored_tokens": val_stats["ignored_tokens"],
                "label_counts": val_stats["label_counts"],
                "file_size_bytes": val_dest.stat().st_size,
                "sha256": hashlib.sha256(val_dest.read_bytes()).hexdigest()
            }
        },
        "archive_members": [
            "train.jsonl",
            "validation.jsonl",
            "bundle_manifest.json",
            "README.md"
        ]
    }

    manifest_dest = staging_dir / "bundle_manifest.json"
    with open(manifest_dest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 4. Create ZIP archive
    print(f"[4/5] Packaging zip archive: {BUNDLE_ZIP}...")
    if BUNDLE_ZIP.exists():
        BUNDLE_ZIP.unlink()

    with zipfile.ZipFile(BUNDLE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(train_dest, arcname="train.jsonl")
        zf.write(val_dest, arcname="validation.jsonl")
        zf.write(manifest_dest, arcname="bundle_manifest.json")
        zf.write(readme_dest, arcname="README.md")

    zip_size = BUNDLE_ZIP.stat().st_size
    zip_sha256 = hashlib.sha256(BUNDLE_ZIP.read_bytes()).hexdigest()
    print(f"  Archive created: {zip_size:,} bytes, SHA-256: {zip_sha256}")

    # 5. Programmatically verify archive contents
    print("[5/5] Programmatically verifying archive contents...")
    with zipfile.ZipFile(BUNDLE_ZIP, "r") as zf:
        members = zf.namelist()
        assert set(members) == {"train.jsonl", "validation.jsonl", "bundle_manifest.json", "README.md"}, f"Unexpected members: {members}"
        
        # Verify train line count in zip
        with zf.open("train.jsonl") as f:
            train_lines = sum(1 for _ in f)
        assert train_lines == 43369, f"Expected 43369 train lines in zip, found {train_lines}"
        
        # Verify val line count in zip
        with zf.open("validation.jsonl") as f:
            val_lines = sum(1 for _ in f)
        assert val_lines == 4820, f"Expected 4820 val lines in zip, found {val_lines}"

    # Re-verify source files unchanged
    verify_source_integrity()

    # Clean up staging directory
    shutil.rmtree(staging_dir)
    print("=" * 70)
    print("Data bundle generation and verification successful!")
    print(f"Archive: {BUNDLE_ZIP}")
    print("=" * 70)


if __name__ == "__main__":
    main()
