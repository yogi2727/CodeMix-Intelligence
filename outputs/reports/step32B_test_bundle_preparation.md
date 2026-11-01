# Step 32B: MuRIL Locked Test-Evaluation Bundle Preparation Report

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 32B — Prepare the Locked MuRIL Test-Evaluation Bundle  
**Workspace:** [`C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence)  
**Timestamp:** `2026-11-01T06:13:22.750480+00:00`  
**Status:** **TEST BUNDLE CREATED, VERIFIED & ISOLATED**  

---

## 1. Executive Summary

In preparation for post-training benchmark evaluation of the fine-tuned `google/muril-base-cased` LID model, the locked evaluation dataset was audited, verified against its cryptographic baseline, and packaged into a dedicated standalone test bundle [`artifacts/colab/muril_lid_test_bundle.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/colab/muril_lid_test_bundle.zip).

Strict governance rules were maintained throughout:
- **Zero Modifications:** The original [`test.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/test.jsonl) file was read-only inspected and remains 100% bitwise identical to its baseline.
- **Strict Isolation:** `train.jsonl` and `validation.jsonl` are completely excluded from this bundle.
- **Zero Training or Evaluation:** No model training, fine-tuning, or inference was performed.

---

## 2. Original Test File Location & Integrity Verification

* **Original Location:** [`data/processed/language_identification/test.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/test.jsonl)
* **File Size:** `16,230,756 bytes` (Matches expected `16,230,756 bytes` exactly)
* **SHA-256 Checksum:** `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca` (Matches baseline hash exactly)
* **Record Count:** `14,855 records` (Matches expected `14,855` exactly)
* **Total Token Count:** `211,576 tokens` (Matches expected `211,576` exactly)

### Source-Wise Record Distribution

| Source & Subset Category | Verified Record Count | Expected Record Count | Verification Status |
| :--- | :---: | :---: | :---: |
| **`COMI-LINGUA`** (Hindi-English Code-Mixed Social Media) | 4,944 | 4,944 | **MATCH** |
| **`Telugu-English Blog`** (Telugu-English Romanized Blog Text) | 3,105 | 3,105 | **MATCH** |
| **`Telugu-English Twitter`** (Telugu-English Romanized Tweets) | 6,806 | 6,806 | **MATCH** |
| **Total Test Records** | **14,855** | **14,855** | **MATCH** |

### Metadata & Provenance Preservation
Every record in `test.jsonl` was verified to preserve:
- Unique benchmark sentence ID (`sentence_id`)
- Original source sentence ID (`original_sentence_id`)
- Source dataset name (`source`)
- Subset classification (`subset`)
- Full whitespace token sequences (`tokens`)
- Model target labels (`model_labels`) and source strings (`source_labels`)

---

## 3. Test Bundle Archive Specifications

* **ZIP File Path:** [`artifacts/colab/muril_lid_test_bundle.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/colab/muril_lid_test_bundle.zip)
* **Archive Size:** `2,213,548 bytes` (~3.68 MB)
* **SHA-256 Checksum:** `7969f24f238e57e2b3245245149820742c31f1c1d63a552811a09f61a00e4956`
* **Archive Member Count:** Exactly 2 files

### Archive Contents

1. **`test.jsonl`**
   - Size: 16,230,756 bytes
   - SHA-256: `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca`
   - Description: Complete, bitwise-identical copy of the locked benchmark test set.
2. **`test_manifest.json`**
   - Description: Formal evaluation manifest documenting purpose, governance mandates, taxonomy, and file hashes.

---

## 4. Archive Verification & Governance Assertions

The created ZIP archive was reopened and verified programmatically:
1. **Successful Reopening:** Archive opens cleanly via `zipfile.ZipFile`.
2. **Exact Member Conformance:** Archive contains strictly `('test.jsonl', 'test_manifest.json')`.
3. **No Training/Validation Leakage:** Confirmed that `train.jsonl` and `validation.jsonl` are completely absent.
4. **Extracted Checksum Verification:** Extracted `test.jsonl` computes to SHA-256 `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca`, matching the source benchmark exactly.

### Governance Mandate
> **LOCKED TEST EVALUATION MANDATE:**  
> This test dataset is strictly reserved for post-training benchmark evaluation.  
> It must NOT be used for model training, parameter optimization, learning rate tuning, early stopping, or checkpoint selection.

---

## 5. Warnings and Failures

* **Warnings:** None.
* **Failures:** None.
* **Integrity Status:** 100% Passed. Ready for locked evaluation workflow.
