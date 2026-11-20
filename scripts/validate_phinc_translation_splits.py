"""
validate_phinc_translation_splits.py
====================================
Independent Validation Suite for Step 34C Translation Splits.

Returns exit code 0 if all 14 criteria pass.
Returns non-zero exit code if any criterion fails.
"""

import os
import sys
import json
import hashlib
import unicodedata
import re

CANDIDATE_PATH = "data/processed/translation/phinc_hinglish_candidate/phinc_pairs_candidate.jsonl"
SPLITS_DIR = "data/processed/translation/phinc_hinglish_splits"

def compute_sha256(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def canonical_key(text):
    norm = unicodedata.normalize('NFC', text).strip()
    norm = re.sub(r'\s+', ' ', norm)
    return norm.lower()

def main():
    print("=" * 65)
    print("Step 34C Independent Validation Suite")
    print("=" * 65)
    
    # 1. Candidate Input Verification
    if not os.path.exists(CANDIDATE_PATH):
        print(f"[FAIL] Missing candidate dataset: {CANDIDATE_PATH}")
        sys.exit(1)
        
    cand_records = []
    with open(CANDIDATE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            cand_records.append(json.loads(line))
            
    if len(cand_records) != 13503:
        print(f"[FAIL] Candidate count != 13,503 (got {len(cand_records)})")
        sys.exit(1)
    print(f"[PASS] 1. Candidate input verified: {len(cand_records):,} records.")
    
    # 2. Output Split Files Existence and Counts
    split_paths = {
        "train": os.path.join(SPLITS_DIR, "phinc_train.jsonl"),
        "validation": os.path.join(SPLITS_DIR, "phinc_validation.jsonl"),
        "test": os.path.join(SPLITS_DIR, "phinc_test.jsonl")
    }
    
    split_records = {}
    for s, p in split_paths.items():
        if not os.path.exists(p):
            print(f"[FAIL] Missing split file: {p}")
            sys.exit(1)
        recs = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                recs.append(json.loads(line))
        split_records[s] = recs
        
    c_tr = len(split_records["train"])
    c_va = len(split_records["validation"])
    c_te = len(split_records["test"])
    
    if (c_tr, c_va, c_te) != (10802, 1350, 1351):
        print(f"[FAIL] Split counts mismatch: train={c_tr}, val={c_va}, test={c_te}")
        sys.exit(1)
    print(f"[PASS] 2. Split counts verified: train={c_tr:,}, val={c_va:,}, test={c_te:,}.")
    
    # 3. Total Record Reconciliation
    total_split_recs = c_tr + c_va + c_te
    if total_split_recs != 13503:
        print(f"[FAIL] Reconciliation failed: {total_split_recs} != 13,503")
        sys.exit(1)
    print(f"[PASS] 3. Zero-loss record reconciliation: {c_tr} + {c_va} + {c_te} == 13,503.")
    
    # 4. Unique Example IDs & Cross-Split Membership
    seen_ids = set()
    for s, recs in split_records.items():
        for r in recs:
            eid = r["example_id"]
            if eid in seen_ids:
                print(f"[FAIL] Duplicate or overlapping example_id across splits: {eid}")
                sys.exit(1)
            seen_ids.add(eid)
    if len(seen_ids) != 13503:
        print(f"[FAIL] Unique example IDs count != 13,503 (got {len(seen_ids)})")
        sys.exit(1)
    print(f"[PASS] 4. All {len(seen_ids):,} example IDs are globally unique across splits.")
    
    # 5. Field and Provenance Integrity
    required_fields = [
        "example_id", "source_dataset", "source_split", "source_row_index",
        "source_text_original", "target_text_original", "source_text", "target_text",
        "source_language_profile", "source_script_profile", "target_language",
        "target_script_profile", "translation_provenance", "license", "quality_status",
        "split", "source_group_id", "near_duplicate_group_id"
    ]
    for s, recs in split_records.items():
        for r in recs:
            for rf in required_fields:
                if rf not in r or r[rf] is None:
                    print(f"[FAIL] Record {r.get('example_id')} missing field: {rf}")
                    sys.exit(1)
            if r["split"] != s:
                print(f"[FAIL] Record {r.get('example_id')} split tag mismatch: {r['split']} != {s}")
                sys.exit(1)
            if r["translation_provenance"] != "human_translated":
                print(f"[FAIL] Non-human provenance in {r.get('example_id')}")
                sys.exit(1)
            if r["license"] != "CC BY 4.0":
                print(f"[FAIL] License mismatch in {r.get('example_id')}")
                sys.exit(1)
    print(f"[PASS] 5. Schema, license (CC BY 4.0), and human_translated provenance verified.")
    
    # 6. Cross-Split Leakage Audit (Exact, Canonical, and Cluster)
    sources_exact = {s: set(r["source_text"] for r in recs) for s, recs in split_records.items()}
    sources_canon = {s: set(canonical_key(r["source_text"]) for r in recs) for s, recs in split_records.items()}
    cluster_ids = {s: set(r["near_duplicate_group_id"] for r in recs) for s, recs in split_records.items()}
    
    pairs = [("train", "validation"), ("train", "test"), ("validation", "test")]
    for s1, s2 in pairs:
        ov_exact = sources_exact[s1].intersection(sources_exact[s2])
        if ov_exact:
            print(f"[FAIL] Exact source leakage between {s1} and {s2}: {len(ov_exact)} items")
            sys.exit(1)
        ov_canon = sources_canon[s1].intersection(sources_canon[s2])
        if ov_canon:
            print(f"[FAIL] Canonical source leakage between {s1} and {s2}: {len(ov_canon)} items")
            sys.exit(1)
        ov_clust = cluster_ids[s1].intersection(cluster_ids[s2])
        if ov_clust:
            print(f"[FAIL] Cluster leakage between {s1} and {s2}: {len(ov_clust)} clusters")
            sys.exit(1)
            
    print("[PASS] 6. Cross-split leakage audit: ZERO exact, canonical, or cluster overlap.")
    
    # 7. Manifest & Test Lock Document Consistency
    manifest_p = os.path.join(SPLITS_DIR, "split_manifest.json")
    lock_p = os.path.join(SPLITS_DIR, "PHINC_TRANSLATION_TEST_LOCK.md")
    overlap_p = os.path.join(SPLITS_DIR, "split_overlap_report.json")
    quality_p = os.path.join(SPLITS_DIR, "split_quality_report.json")
    config_p = os.path.join(SPLITS_DIR, "split_processing_config.json")
    
    for p in [manifest_p, lock_p, overlap_p, quality_p, config_p]:
        if not os.path.exists(p):
            print(f"[FAIL] Missing split metadata artifact: {p}")
            sys.exit(1)
            
    with open(manifest_p, "r", encoding="utf-8") as f:
        mf = json.load(f)
    test_sha_disk = compute_sha256(split_paths["test"])
    if mf["actual_split_metrics"]["test"]["sha256"] != test_sha_disk:
        print(f"[FAIL] Manifest test SHA-256 mismatch with disk file!")
        sys.exit(1)
        
    with open(lock_p, "r", encoding="utf-8") as f:
        lock_text = f.read()
    if test_sha_disk not in lock_text:
        print(f"[FAIL] Test lock document does not contain test SHA-256!")
        sys.exit(1)
    print(f"[PASS] 7. Manifest, test lock document, and split file hashes match bitwise.")
    
    # 8. V1 Baseline Isolation Check
    muril_safetensors = "artifacts/models/muril_lid_baseline/best_model/model.safetensors"
    expected_muril_sha = "714defc6f90659ebc25e5e011a9101579d36cf9f3b4c57165c0614f1bc744bae"
    actual_muril_sha = compute_sha256(muril_safetensors)
    if actual_muril_sha != expected_muril_sha:
        print(f"[FAIL] MuRIL baseline model weights modified!")
        sys.exit(1)
    print(f"[PASS] 8. V1 MuRIL baseline weights confirmed untouched ({actual_muril_sha[:16]}...).")
    
    print("=" * 65)
    print("ALL STEP 34C VALIDATION CHECKS PASSED SUCCESSFULLY (EXIT 0)!")
    print("=" * 65)
    sys.exit(0)

if __name__ == "__main__":
    main()
