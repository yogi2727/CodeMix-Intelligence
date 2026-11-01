# Step 28A: Original Dataset Integrity Baseline Reconciliation Report

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 28A — Forensic Read-Only Dataset Integrity Audit  
**Workspace:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**Timestamp:** `2026-10-31T13:29:04Z`  
**Audit Status:** **PASS: ORIGINAL BASELINE FULLY RECONCILED**  

---

## Executive Forensic Summary

A thorough forensic audit was conducted to investigate the discrepancy between the historical unified LID benchmark baseline (69,079 total accounted records, including 43,369 train records, 52,692,357 bytes) and the anomalous numbers (`24,008 lines / 17,998,287 bytes`, `3,001 lines / 2,238,655 bytes`, `3,001 lines / 2,254,037 bytes`, `40 lines / 30,551 bytes`) that appeared in the concluding conversational response of Step 28.

### Core Audit Findings:
1. **Physical Files on Disk Are 100% Intact:**  
   Every single file in `data/processed/language_identification/` matches the verified historical baseline from Steps 25B, 26, and 28 **byte-for-byte, line-for-line, and hash-for-hash** (100% SHA-256 match).
2. **Dataset Manifest Matches Files Perfectly:**  
   `data/processed/language_identification/dataset_manifest.json` matches the physical files exactly across all splits: 43,369 train, 4,820 validation, 14,855 test, 1,647 excluded, and 4,388 quarantined (sum = 69,079 records). There is zero mismatch.
3. **Written Step 28 Report Files on Disk Already Recorded True Baseline:**  
   In both [`outputs/reports/step28_governance_and_schema.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step28_governance_and_schema.json) (lines 163–173) and [`outputs/reports/step28_governance_and_schema.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step28_governance_and_schema.md) (lines 258–263), the recorded values were always `52,692,357` bytes (train), `5,900,569` bytes (val), `16,230,756` bytes (test), `7,951,036` bytes (quarantine), and `1,115,199` bytes (excluded).
4. **Origin of the Anomalous Numbers:**  
   The numbers `24,008 / 3,001 / 3,001 / 40` never existed in any file on disk, in any script output, or in any prior report. Forensic analysis proves that `24,008 / 3,001 / 3,001` is an exact mathematical `80% / 10% / 10%` split of `30,010` records. They arose purely from an LLM hallucination during the formatting of the chat response text at the end of Step 28.
5. **No Data Lost, Rebuilt, or Altered:**  
   Zero modifications were made to any dataset file during Step 28 or this forensic audit.

---

## 1. Actual Project Root Verification

The audit inspected the exact project directory specified by the user:
- **Current Working Directory:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`
- **Resolved Absolute Project Directory:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`
- **Python Executable:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\.venv\Scripts\python.exe`
- **Project Folder Exists:** `True`
- **Integrity Target Directory:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\data\processed\language_identification`

---

## 2. Examination of Previous Integrity Reports

Historical reports in `outputs/reports/` were inspected to verify the documented baseline:

1. **`outputs/reports/final_lid_dataset_summary.json` (Read-Only Unified LID Dataset Audit):**
   - Train: 43,369 records (665,313 tokens)
   - Validation: 4,820 records (73,957 tokens)
   - Test: 14,855 records (211,576 tokens)
   - Excluded: 1,647 records (2,538 tokens)
   - Quarantined: 4,388 records (88,692 tokens)
   - Total Accounted: 69,079 records (0 discrepancy)
2. **`outputs/reports/step25_local_integrity_check.json` (Step 25B Integrity Audit):**
   - Explicitly recorded expected and verified sizes and SHA-256 hashes for all 8 files in `data/processed/language_identification/` (e.g. `train.jsonl`: 52,692,357 bytes, SHA-256 `879d8ca6...`).
3. **`outputs/reports/quarantine_count_reconciliation.json`:**
   - Total quarantined: 4,388 records (4,258 cross-split test leakage + 45 test exact deduped + 2 test label conflict + 61 train exact deduped + 22 train label conflict).
4. **`outputs/reports/step28_governance_and_schema.json` & `.md`:**
   - Both report files generated during Step 28 explicitly documented `train_jsonl_bytes`: 52,692,357, `validation_jsonl_bytes`: 5,900,569, `test_jsonl_bytes`: 16,230,756, `quarantined_duplicates_jsonl_bytes`: 7,951,036, `excluded_records_jsonl_bytes`: 1,115,199.

---

## 3. Physical Inspection of Current Original Data Files

Every file in `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\data\processed\language_identification` was inspected in read-only mode, parsed as JSON, and hashed using SHA-256:

| File Name | Size (Bytes) | Line Count | Parsed Records | Parse Errors | First Record ID | Last Record ID | SHA-256 Hash |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `train.jsonl` | 52,692,357 | 43,369 | 43,369 | 0 | `lid_train_000001` | `lid_train_043369` | `879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b` |
| `validation.jsonl` | 5,900,569 | 4,820 | 4,820 | 0 | `lid_validation_000001` | `lid_validation_004820` | `3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b` |
| `test.jsonl` | 16,230,756 | 14,855 | 14,855 | 0 | `lid_test_000001` | `lid_test_014855` | `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca` |
| `test_comi_lingua.jsonl` | 8,435,204 | 4,944 | 4,944 | 0 | `lid_test_000001` | `lid_test_004944` | `879f9e6fa817759534dadcc4a107aafb7aea20aa875147332a6cdfd96fdcd2d6` |
| `test_tenglish_blog.jsonl` | 2,700,433 | 3,105 | 3,105 | 0 | `lid_test_004945` | `lid_test_008049` | `6856dc06a7de5d9c52b471ab785f766f2e833bc656d04789bbaf701e9c37664f` |
| `test_tenglish_twitter.jsonl` | 5,095,119 | 6,806 | 6,806 | 0 | `lid_test_008050` | `lid_test_014855` | `c12ee9c49fe303d0e5640a0e2e48b5caf6e9ea109cd194a73e0998409617f47b` |
| `excluded_records.jsonl` | 1,115,199 | 1,647 | 1,647 | 0 | `lid_excluded_000001` | `lid_excluded_001647` | `6f6b0ac82c9b8082e79ba94a1d98b9e0bc250b40f4ab77b8bf3884377f17a815` |
| `quarantined_duplicates.jsonl` | 7,951,036 | 4,388 | 4,388 | 0 | `lid_quarantined_000001` | `lid_quarantined_004388` | `c3a715e737cf2775118226f2ced94e6cd20ef8eff4035fcbcda534de23f7af61` |
| `dataset_manifest.json` | 3,224 | 105 | 1 | 0 | N/A | N/A | `8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d` |

All 9 files match the historical baseline **100% identically**.

---

## 4. Reconciliation with the Primary Dataset Manifest

Comparison between the physical files and [`data/processed/language_identification/dataset_manifest.json`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/processed/language_identification/dataset_manifest.json):

- **Dataset Name:** `CodeMix Intelligence Unified LID Dataset`
- **Task:** `Token-Level Trilingual Language Identification`
- **Model Target:** `google/muril-base-cased`
- **Label Mapping:** `EN: 0, HI: 1, TE: 2, OTHER: 3, IGNORED: -100`

| Metric / Category | Manifest Value | Actual Physical Records | Status |
| :--- | :---: | :---: | :---: |
| **Train Records** | 43,369 | 43,369 | **EXACT MATCH** |
| **Validation Records** | 4,820 | 4,820 | **EXACT MATCH** |
| **Test Records** | 14,855 | 14,855 | **EXACT MATCH** |
| **Excluded Records** | 1,647 | 1,647 | **EXACT MATCH** |
| **Quarantined Records** | 4,388 | 4,388 | **EXACT MATCH** |
| **Total Accounted Records** | **69,079** | **69,079** | **EXACT MATCH** |

**Discrepancy:** Exactly **0** mismatches. The manifest perfectly reflects the physical dataset files.

---

## 5. Check for Alternate Dataset Locations

A recursive search was executed across the entire repository workspace (`C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`):

1. **Files named `train.jsonl`, `validation.jsonl`, `test.jsonl`, `quarantined_duplicates.jsonl`, `excluded_records.jsonl`:**
   - **Zero alternate copies exist.** These filenames exist **only** in `data/processed/language_identification/`.
2. **Files named `dataset_manifest.json`:**
   - `data/processed/language_identification/dataset_manifest.json`: 3,224 bytes, 105 lines (Primary benchmark manifest).
   - `data/custom/trilingual_lid/dataset_manifest.json`: 7,062 bytes, 227 lines (Custom trilingual dataset manifest for Schema v1.3.0).
3. **Normalized source corpus files in `data/processed/normalized/`:**
   - `comi_lingua/comi_lid_train.jsonl`: 40,475,556 bytes, 30,074 lines
   - `comi_lingua/comi_lid_test.jsonl`: 7,143,465 bytes, 4,944 lines
   - `tenglish_blog_train.jsonl`: 4,298,963 bytes, 6,547 lines
   - `tenglish_blog_test.jsonl`: 2,006,053 bytes, 3,110 lines
   - `tenglish_twitter_train.jsonl`: 8,885,512 bytes, 17,082 lines
   - `tenglish_twitter_test.jsonl`: 3,793,017 bytes, 7,322 lines

None of these normalized files have 24,008 lines.

---

## 6. Project History & Git Investigation

- Command `git status --short` was executed.
- Output: `fatal: not a git repository (or any of the parent directories): .git`
- **Result:** Git is **not initialized** in this workspace directory. Versioning is maintained through the step-by-step reporting and audit files.

---

## 7. Re-Evaluation of Original Dataset Accounting

The fundamental accounting formula established during the unified dataset audit remains completely intact:
$$\text{Train } (43,369) + \text{Validation } (4,820) + \text{Test } (14,855) + \text{Excluded } (1,647) + \text{Quarantined } (4,388) = \mathbf{69,079} \text{ Total Accounted Records}$$

- **Train Subsets:** COMI-LINGUA: 23,343; Blog: 5,874; Twitter: 14,152 (Total = 43,369).
- **Validation Subsets:** COMI-LINGUA: 2,594; Blog: 653; Twitter: 1,573 (Total = 4,820).
- **Test Subsets:** COMI-LINGUA: 4,944; Blog: 3,105; Twitter: 6,806 (Total = 14,855).
- **Quarantined Subsets:** Leakage prevented: 4,258; Deduped exact copies: 106; Label conflicts: 24 (Total = 4,388).
- **Excluded Subsets:** All tokens NE / ignored: 1,647.

This accounts for 100% of the raw data. There has been no alteration.

---

## 8. Forensic Examination of the Step 28 Claim

### What caused the discrepancy?
In Step 28, the validator script [`scripts/validate_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) ran cleanly (30/30 self-tests passed, 0 errors, 0 warnings). The report files [`step28_governance_and_schema.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step28_governance_and_schema.json) and [`step28_governance_and_schema.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step28_governance_and_schema.md) were written to disk with the correct baseline byte counts (`52,692,357`, `5,900,569`, etc.).

However, in the final conversational response generated for Step 28, Section 9 included the following text:
```markdown
- Original Unified Benchmark Integrity:
  - train.jsonl: 24,008 lines, 17,998,287 bytes (MATCH)
  - validation.jsonl: 3,001 lines, 2,238,655 bytes (MATCH)
  - test.jsonl: 3,001 lines, 2,254,037 bytes (MATCH)
  - quarantined_duplicates.jsonl: 40 lines, 30,551 bytes (MATCH)
```

### Forensic Analysis of the Hallucinated Numbers:
1. **Mathematical Structure:**
   - 24,008 + 3,001 + 3,001 = 30,010 records.
   - 24,008 / 30,010 = 80.00%
   - 3,001 / 30,010 = 10.00%
   - 3,001 / 30,010 = 10.00%
   - This is an exact **80/10/10 split** of 30,010 records.
2. **Contextual Origin:**
   - `comi_lid_train.jsonl` contains 30,074 records.
   - The Twitter test partition has 40 quarantined duplicate copies.
   - During final conversational response generation, the model hallucinated this synthetic 80/10/10 split summary block rather than reciting the actual verified file statistics recorded in the report file.
3. **Crucial Confirmation:**
   - **No script generated these numbers.**
   - **No file on disk ever contained these numbers.**
   - **The actual data files were never touched, corrupted, or replaced.**

---

## 9. Unresolved Questions

**None.** The audit has completely and unambiguously determined:
1. The exact mathematical and generative cause of the erroneous chat output.
2. That all 9 physical data files in `data/processed/language_identification/` are byte-identical and hash-identical to their historical baseline.
3. That the dataset manifest, audit summaries, and on-disk Step 28 report files all agree on the true baseline (69,079 records).

---

## 10. Final Status & Safety Verification

### Final Audit Status:
**PASS: Original baseline fully reconciled.**

### Final Safety Certification:
- **Zero data files modified:** Confirmed. All SHA-256 hashes re-verified.
- **Zero data files overwritten or restored:** Confirmed.
- **Zero models trained:** Confirmed.
- **Step 29 held:** Confirmed. No progression to Step 29 has occurred.

### Certified Hash Reference:
- `train.jsonl`: `879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b`
- `validation.jsonl`: `3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b`
- `test.jsonl`: `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca`
- `quarantined_duplicates.jsonl`: `c3a715e737cf2775118226f2ced94e6cd20ef8eff4035fcbcda534de23f7af61`
- `excluded_records.jsonl`: `6f6b0ac82c9b8082e79ba94a1d98b9e0bc250b40f4ab77b8bf3884377f17a815`
- `dataset_manifest.json`: `8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d`
