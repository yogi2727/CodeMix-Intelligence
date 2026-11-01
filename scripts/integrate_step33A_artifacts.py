"""
CodeMix Intelligence - Step 33A
Model and Evaluation Artifact Integration Script

Extracts and verifies:
1. Model files from muril_lid_best_model.zip into artifacts/models/muril_lid_baseline/best_model/
2. Evaluation files from muril_lid_evaluation_results.zip into artifacts/evaluation/muril_lid_baseline/
3. Validates file presence, hashes, and evaluation metrics.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parent.parent
MODEL_DIR = WORKSPACE / "artifacts" / "models" / "muril_lid_baseline" / "best_model"
EVAL_DIR = WORKSPACE / "artifacts" / "evaluation" / "muril_lid_baseline"

MODEL_ZIP = WORKSPACE / "muril_lid_best_model.zip"
EVAL_ZIP = WORKSPACE / "muril_lid_evaluation_results.zip"

REQUIRED_MODEL_FILES = [
    "config.json",
    "model.safetensors",
    "vocab.txt",
    "tokenizer_config.json",
    "special_tokens_map.json"
]

REQUIRED_EVAL_FILES = [
    "locked_test_results.json",
    "source_wise_results.json",
    "source_subset_metrics_posthoc.json",
    "confusion_matrix.csv",
    "LOCKED_TEST_EVALUATION_COMPLETE.json"
]


def extract_and_verify_model():
    print("[1/3] Extracting and verifying trained model artifacts...")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    assert MODEL_ZIP.exists(), f"Model ZIP archive not found: {MODEL_ZIP}"
    
    with zipfile.ZipFile(MODEL_ZIP, "r") as zf:
        for member in zf.infolist():
            if member.filename.endswith("/"):
                continue
            # Strip top-level folder prefix (e.g. best_model/)
            rel_name = Path(member.filename).name
            target_path = MODEL_DIR / rel_name
            print(f"  Extracting {member.filename} -> {target_path.relative_to(WORKSPACE)}")
            with zf.open(member) as src, open(target_path, "wb") as dst:
                dst.write(src.read())
                
    # Verify presence of all required model files
    extracted_model_files = {}
    for rmf in REQUIRED_MODEL_FILES:
        p = MODEL_DIR / rmf
        assert p.exists(), f"Missing required model file: {rmf}"
        size = p.stat().st_size
        extracted_model_files[rmf] = size
        print(f"  Verified {rmf}: {size:,} bytes")
        
    # Also verify training_args.bin if present
    extra_files = ["training_args.bin"]
    for ef in extra_files:
        p = MODEL_DIR / ef
        if p.exists():
            extracted_model_files[ef] = p.stat().st_size
            print(f"  Verified {ef}: {p.stat().st_size:,} bytes")

    # Compute SHA-256 and size of model.safetensors
    safetensors_path = MODEL_DIR / "model.safetensors"
    safetensors_size = safetensors_path.stat().st_size
    print(f"  Computing SHA-256 for model.safetensors ({safetensors_size:,} bytes)...")
    h = hashlib.sha256()
    with open(safetensors_path, "rb") as f:
        while chunk := f.read(1024 * 1024 * 8):
            h.update(chunk)
    safetensors_sha256 = h.hexdigest()
    print(f"  model.safetensors SHA-256: {safetensors_sha256}")
    print(f"  model.safetensors Size:   {safetensors_size:,} bytes")

    return {
        "model_dir": str(MODEL_DIR),
        "files": extracted_model_files,
        "safetensors_size": safetensors_size,
        "safetensors_sha256": safetensors_sha256
    }


def extract_and_verify_evaluation():
    print("\n[2/3] Extracting and verifying evaluation artifacts...")
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    
    assert EVAL_ZIP.exists(), f"Evaluation ZIP archive not found: {EVAL_ZIP}"
    
    with zipfile.ZipFile(EVAL_ZIP, "r") as zf:
        for member in zf.infolist():
            if member.filename.endswith("/"):
                continue
            rel_name = Path(member.filename).name
            target_path = EVAL_DIR / rel_name
            print(f"  Extracting {member.filename} -> {target_path.relative_to(WORKSPACE)}")
            with zf.open(member) as src, open(target_path, "wb") as dst:
                dst.write(src.read())

    # Verify presence of all required evaluation files
    extracted_eval_files = {}
    for ref in REQUIRED_EVAL_FILES:
        p = EVAL_DIR / ref
        assert p.exists(), f"Missing required evaluation file: {ref}"
        size = p.stat().st_size
        extracted_eval_files[ref] = size
        print(f"  Verified {ref}: {size:,} bytes")

    # Read and validate JSON contents
    print("  Validating evaluation JSON structures...")
    
    # 1. locked_test_results.json
    with open(EVAL_DIR / "locked_test_results.json", "r", encoding="utf-8") as f:
        locked_test_res = json.load(f)
    print("    - locked_test_results.json keys:", list(locked_test_res.keys()))
    
    # 2. source_wise_results.json
    with open(EVAL_DIR / "source_wise_results.json", "r", encoding="utf-8") as f:
        source_wise_res = json.load(f)
    print("    - source_wise_results.json keys:", list(source_wise_res.keys()))

    # 3. source_subset_metrics_posthoc.json
    with open(EVAL_DIR / "source_subset_metrics_posthoc.json", "r", encoding="utf-8") as f:
        posthoc_res = json.load(f)
    print("    - source_subset_metrics_posthoc.json keys:", list(posthoc_res.keys()))

    # 4. LOCKED_TEST_EVALUATION_COMPLETE.json
    with open(EVAL_DIR / "LOCKED_TEST_EVALUATION_COMPLETE.json", "r", encoding="utf-8") as f:
        complete_res = json.load(f)
    print("    - LOCKED_TEST_EVALUATION_COMPLETE.json keys:", list(complete_res.keys()))

    # 5. confusion_matrix.csv
    with open(EVAL_DIR / "confusion_matrix.csv", "r", encoding="utf-8") as f:
        cm_lines = [line.strip() for line in f if line.strip()]
    print(f"    - confusion_matrix.csv lines ({len(cm_lines)} lines):")
    for l in cm_lines:
        print(f"        {l}")

    return {
        "eval_dir": str(EVAL_DIR),
        "files": extracted_eval_files,
        "locked_test_results": locked_test_res,
        "source_wise_results": source_wise_res,
        "source_subset_metrics_posthoc": posthoc_res,
        "completion_info": complete_res,
        "confusion_matrix_lines": cm_lines
    }


def main():
    print("=" * 70)
    print("CodeMix Intelligence - Step 33A: Integrate and Verify Trained Model")
    print("=" * 70)

    model_info = extract_and_verify_model()
    eval_info = extract_and_verify_evaluation()

    print("\n[3/3] Integration and validation summary:")
    print(f"  Model directory: {model_info['model_dir']}")
    print(f"  model.safetensors Size:   {model_info['safetensors_size']:,} bytes")
    print(f"  model.safetensors SHA256: {model_info['safetensors_sha256']}")
    print(f"  Evaluation directory: {eval_info['eval_dir']}")
    print(f"  Evaluation files count: {len(eval_info['files'])}")
    print("=" * 70)


if __name__ == "__main__":
    main()
