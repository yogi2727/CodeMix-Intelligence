"""
CodeMix Intelligence - Step 33D
V1.0.0 Source Code & Lightweight Documentation Snapshot Packager

Packages canonical V1 source files into:
outputs/releases/CodeMix_Intelligence_v1.0.0_source.zip

Excludes:
- .venv/
- __pycache__/
- model.safetensors (948 MB) and *.safetensors
- *.zip (avoids recursion)
- Raw datasets
- Colab bundles
"""

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "outputs" / "releases"
ZIP_PATH = OUTPUT_DIR / "CodeMix_Intelligence_v1.0.0_source.zip"
MANIFEST_PATH = OUTPUT_DIR / "v1.0.0" / "BACKUP_MANIFEST.json"

def should_include_file(file_path: Path) -> bool:
    rel_path = file_path.relative_to(REPO_ROOT).as_posix()

    # Explicit Exclusions
    if ".venv" in file_path.parts:
        return False
    if "__pycache__" in file_path.parts:
        return False
    if ".git" in file_path.parts:
        return False
    if ".pytest_cache" in file_path.parts:
        return False
    if "scratch" in file_path.parts:
        return False
    if "artifacts/colab" in rel_path:
        return False
    if "data" in file_path.parts:
        return False
    if file_path.suffix.lower() in [".safetensors", ".bin", ".zip", ".tar", ".gz", ".pyc"]:
        return False

    # Inclusions
    if rel_path.startswith("frontend/"):
        return True
    if rel_path.startswith("backend/"):
        return True
    if rel_path.startswith("src/"):
        return True
    if rel_path.startswith("tests/"):
        return True
    if rel_path.startswith("configs/"):
        return True
    if rel_path.startswith("scripts/"):
        return True
    if rel_path.startswith("artifacts/evaluation/muril_lid_baseline/"):
        return True
    if rel_path.startswith("artifacts/models/muril_lid_baseline/best_model/"):
        # Include configs and tokenizer, exclude weights
        return file_path.name in ["config.json", "tokenizer_config.json", "special_tokens_map.json", "vocab.txt"]
    if rel_path == "artifacts/README.md":
        return True
    if rel_path.startswith("outputs/reports/step33"):
        return True
    if rel_path.startswith("outputs/releases/v1.0.0/"):
        return True
    if rel_path in ["README.md", "requirements.txt", ".gitignore", ".env.example"]:
        return True

    return False

def main():
    print(f"Creating V1.0.0 source snapshot at: {ZIP_PATH}...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Remove old archive if exists to ensure clean build
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    included_files = []
    
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(REPO_ROOT):
            # Prune excluded directories for performance
            dirs[:] = [d for d in dirs if d not in [".venv", "__pycache__", ".git", ".pytest_cache", "scratch", "data"]]
            for file_name in sorted(files):
                full_path = Path(root) / file_name
                if should_include_file(full_path):
                    arcname = full_path.relative_to(REPO_ROOT).as_posix()
                    zf.write(full_path, arcname)
                    included_files.append((arcname, full_path.stat().st_size))

    size_bytes = ZIP_PATH.stat().st_size
    print(f"Archive built successfully. Total files: {len(included_files)}, Size: {size_bytes:,} bytes")

    # Compute SHA-256
    h = hashlib.sha256()
    with open(ZIP_PATH, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    zip_sha256 = h.hexdigest()
    print(f"Archive SHA-256: {zip_sha256}")

    # Verify that the ZIP opens cleanly and contains expected files
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        members = zf.namelist()
        assert len(members) == len(included_files), "Member count mismatch!"
        print(f"Verification: Zip contains {len(members)} entries and opens cleanly.")

    # Create Backup Manifest
    manifest_data = {
        "snapshot_archive": {
            "path": "outputs/releases/CodeMix_Intelligence_v1.0.0_source.zip",
            "size_bytes": size_bytes,
            "sha256": zip_sha256,
            "file_count": len(included_files),
            "description": "V1.0.0 source code, configurations, lightweight model metadata, evaluation reports, and screenshots."
        },
        "included_files_summary": {
            "frontend_files": [f for f, s in included_files if f.startswith("frontend/")],
            "backend_files": [f for f, s in included_files if f.startswith("backend/")],
            "src_files": [f for f, s in included_files if f.startswith("src/")],
            "test_files": [f for f, s in included_files if f.startswith("tests/")],
            "config_files": [f for f, s in included_files if f.startswith("configs/")],
            "script_files": [f for f, s in included_files if f.startswith("scripts/")],
            "report_files": [f for f, s in included_files if f.startswith("outputs/reports/")],
            "release_files": [f for f, s in included_files if f.startswith("outputs/releases/")]
        }
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Backup manifest saved to: {MANIFEST_PATH}")

if __name__ == "__main__":
    main()
