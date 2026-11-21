# CODEMIX INTELLIGENCE — V2 (mT5-small)
## STEP 34C — LEAKAGE-SAFE TRAIN / VALIDATION / TEST SPLIT REPORT

**Document Version:** 1.0.0  
**Timestamp:** 2026-11-01T19:02:50.931767  
**Project Workspace:** `c:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**GitHub Remote:** [https://github.com/yogi2727/CodeMix-Intelligence](https://github.com/yogi2727/CodeMix-Intelligence)  
**Active Development Branch:** `feature/mt5-translation-v2`  
**Stable Tag:** `v1.0.0` (commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`)  
**Partitioning Status:** <span style="color:green;font-weight:bold;">COMPLETED, VERIFIED & TEST SET LOCKED (ZERO LEAKAGE)</span>  

---

## EXECUTIVE SUMMARY

Step 34C establishes the official, reproducible, leakage-controlled **Train (80%) / Validation (10%) / Test (10%) splits** for Model 2 (`google/mt5-small`), targeting Romanized Hinglish sentence to English translation.

The original PHINC dataset (Srivastava & Singh, W-NUT 2020) was released as a single monolithic flat file. Therefore, the splits created in this step represent **new project-specific partitions** constructed under rigorous leakage-prevention controls.

### Key Results Summary:
1. **Source Candidate Verified:** 13,503 clean, normalized candidate pairs ingested from `phinc_pairs_candidate.jsonl` (SHA-256: `aa4fdf0c72183d3a3e3ca100798bdfe396cecd18c7515a7adac2396c0d6e4b5b`).
2. **Deterministic Source Clustering:** Inverted index token blocking and sequence matching identified **114 high-confidence near-duplicate sentence pairs** (similarity ratio $\ge 0.88$). Connected components formed **13,403 disjoint source clusters**.
3. **Source-Grouped Leakage Prevention:** All exact canonical source matches and near-duplicate cluster members were assigned as whole atomic units. No cluster was divided across splits.
4. **Exact Target Allocation:**
   - **Train:** **10,802 records** (**80.00%**) [target: 10,802, diff: 0]
   - **Validation:** **1,350 records** (**10.00%**) [target: 1,350, diff: 0]
   - **Test:** **1,351 records** (**10.01%**) [target: 1,351, diff: 0]
   - **Total:** **13,503 records** [100% zero-loss reconciliation]
5. **Zero Cross-Split Leakage Confirmed:**
   - Exact source overlap: **0** across all split pairs.
   - Canonical normalized source overlap: **0** across all split pairs.
   - Near-duplicate cluster overlap: **0** across all split pairs.
   - Example ID collision: **0** across all split pairs.
6. **Test Set Cryptographically Locked:** Test set (`phinc_test.jsonl`, 1,351 records | SHA-256: `7cd192e2d65b1cd7c3b8b725690cf9e0f0e948e3ace3650235f832ae8ca8bf20`) is immutably locked under [`PHINC_TRANSLATION_TEST_LOCK.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/PHINC_TRANSLATION_TEST_LOCK.md), reserved exclusively for final post-training evaluation.
7. **V1 Absolute Protection:** MuRIL baseline model files, evaluation artifacts, FastAPI backend, Vanilla JS frontend, and Git tags remain 100% untouched.

---

## 1. GIT AND V1 SAFETY VERIFICATION

Before executing the splitting pipeline, read-only Git checks confirmed:
- **Active Branch:** `feature/mt5-translation-v2` (confirmed tracking `origin/feature/mt5-translation-v2`).
- **Stable Tag:** `v1.0.0` points unchanged to commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`.
- **Merge Base:** `git merge-base v1.0.0 feature/mt5-translation-v2` confirmed V1 ancestry.
- **Tracked Working Tree:** Clean. All untracked report and backup files preserved.
- **Data Protection:** `data/processed/translation/` is covered by `.gitignore`.

---

## 2. CANDIDATE SOURCE INTEGRITY & PRE-SPLIT VERIFICATION

The input dataset was validated against the Step 34B manifest prior to partitioning:
- **Input File:** [`data/processed/translation/phinc_hinglish_candidate/phinc_pairs_candidate.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_candidate/phinc_pairs_candidate.jsonl)
- **Record Count:** **13,503 records** (exact match).
- **Bitwise SHA-256:** `aa4fdf0c72183d3a3e3ca100798bdfe396cecd18c7515a7adac2396c0d6e4b5b` (exact match).
- **Integrity Invariants Passed:**
  - 100% of records have unique `example_id` values (`PHINC:row:000001` to `PHINC:row:013738`).
  - 100% contain valid `source_text_original`, `target_text_original`, `source_text`, `target_text`.
  - 100% of targets contain at least one Unicode letter.
  - Zero empty source or target fields.
  - Provenance is verified `human_translated`; License is verified `CC BY 4.0`.
  - None of the 235 quarantined rows from Step 34B entered the candidate pool.

---

## 3. SOURCE GROUPING AND NEAR-DUPLICATE DETECTION

A naive random split risks severe evaluation leakage because social media corpora frequently contain repeated templates, retweets, and minor orthographic variants. Step 34C implements a two-stage source-grouping architecture:

### 3.1 Canonical Source Grouping
- **Normalization:** Unicode NFC, trimmed whitespace, collapsed internal whitespace, Latin case-folding.
- **Result:** The 13,503 candidate records collapse into **13,497 canonical source keys** (6 multi-record groups where sentences differed only in capitalization).

### 3.2 High-Confidence Near-Duplicate Detection
To prevent lexical leakages between splits (e.g. sentences differing only by punctuation, URLs, or minor spelling variations):
- **Candidate Blocking:** An inverted token index on content words ($\ge 3$ characters) flagged sentence pairs sharing token Jaccard similarity $\ge 0.70$ and length ratio $\ge 0.75$. This generated **165 candidate pairs** out of 91 million possible pairs.
- **Similarity Computation:** `difflib.SequenceMatcher` evaluated exact character sequence similarity.
- **High-Confidence Threshold:** Pairs with similarity ratio $\ge \mathbf0.88$ were designated as near-duplicates (**114 pairs** detected).
- **Connected Components (Union-Find):** Disjoint-set clustering merged connected near-duplicate pairs into atomic source clusters.

### 3.3 Clustering Summary
- **Total Source Clusters:** **13,403** (atomic units of split assignment).
- **Singleton Clusters:** **13,322** (99.40% of clusters contain exactly 1 record).
- **Multi-Record Clusters:** **81** (covering 181 records).
- **Maximum Cluster Size:** **6 records** (small enough to allow exact 80/10/10 proportional allocation).

---

## 4. DETERMINISTIC GROUP-AWARE PARTITIONING

### 4.1 Split Algorithm & Seed 42
1. Each cluster was assigned a deterministic identifier: `cluster_{sha256(min_key)[:12]}`.
2. Clusters were sorted deterministically by `cluster_id`.
3. A local pseudo-random number generator initialized with `seed = 42` shuffled the clusters.
4. Clusters were assigned via greedy relative deficit balancing targeting 80% train, 10% validation, and 10% test.
5. All records within each cluster were assigned to the selected split without splitting any cluster.
6. Records within output JSONL files were restored to original CSV row order (`source_row_index` ascending).

### 4.2 Split Counts and Percentages

| Split Name | Target Fraction | Target Records | Actual Records | Actual % | Deviation | Clusters Assigned |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train** | 0.80 | 10,802 | **10,802** | **80.00%** | **0** | 10,724 |
| **Validation** | 0.10 | 1,350 | **1,350** | **10.00%** | **0** | 1,339 |
| **Test** | 0.10 | 1,351 | **1,351** | **10.01%** | **0** | 1,340 |
| **Total** | **1.00** | **13,503** | **13,503** | **100.00%** | **0** | **13,403** |

$$\text{Reconciliation Check: } 10,802 + 1,350 + 1,351 = 13,503 \quad [100.00\% \text{ EXACT MATCH}]$$

---

## 5. SCRIPT AND LANGUAGE REPRESENTATION PER SPLIT

Script distributions across splits demonstrate natural representation:

| Linguistic & Script Profile | Train Count (%) | Validation Count (%) | Test Count (%) | Total Candidates |
| :--- | :---: | :---: | :---: | :---: |
| **Latin (Romanized Hinglish)** | 10,779 (99.79%) | 1,345 (99.63%) | 1,348 (99.78%) | 13,472 (99.77%) |
| **Mixed Script (Latin + Devanagari)** | 21 (0.19%) | 5 (0.37%) | 3 (0.22%) | 29 (0.21%) |
| **Devanagari Only** | 2 (0.02%) | 0 (0.00%) | 0 (0.00%) | 2 (0.01%) |
| **Total Records** | **10,802** | **1,350** | **1,351** | **13,503** |

### Rare Script Note:
- The 2 Devanagari-only records naturally landed in the training split. As mandated by project policy, rare examples were not artificially duplicated or oversampled across splits.
- The project is accurately documented as primarily Romanized Hinglish-to-English translation.

---

## 6. SOURCE AND TARGET LENGTH STATISTICS

Sequence length profiles remain consistent across all three partitions:

| Split | Source Chars (Mean / Median / P95) | Source Tokens (Mean / Median / P95) | Target Chars (Mean / Median / P95) | Target Tokens (Mean / Median / P95) |
| :--- | :---: | :---: | :---: | :---: |
| **Train** | 76.12 / 70.0 / 140.0 | 13.27 / 12.0 / 27.0 | 75.02 / 68.0 / 142.0 | 12.49 / 11.0 / 25.0 |
| **Validation** | 76.19 / 69.5 / 141.0 | 13.30 / 12.0 / 27.0 | 74.90 / 68.0 / 142.0 | 12.48 / 11.0 / 25.0 |
| **Test** | 76.43 / 70.0 / 140.0 | 13.31 / 12.0 / 27.0 | 75.52 / 69.0 / 142.0 | 12.57 / 11.0 / 25.0 |

Length metrics show virtually identical distributions across train, validation, and test sets.

---

## 7. CROSS-SPLIT LEAKAGE AUDIT

An independent, exhaustive pairwise audit checked for leakage across all split boundaries:

| Pairwise Comparison | Exact Source Overlap | Canonical Source Overlap | Near-Duplicate Cluster Overlap | Example ID Overlap | Leakage Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Train vs Validation** | **0** | **0** | **0** | **0** | <span style="color:green;font-weight:bold;">ZERO LEAKAGE</span> |
| **Train vs Test** | **0** | **0** | **0** | **0** | <span style="color:green;font-weight:bold;">ZERO LEAKAGE</span> |
| **Validation vs Test** | **0** | **0** | **0** | **0** | <span style="color:green;font-weight:bold;">ZERO LEAKAGE</span> |

All 13,403 source clusters are 100% mutually exclusive across splits.

---

## 8. TEST SET LOCKING & EVALUATION FREEZE

To protect scientific integrity, the test split is immutably frozen under:  
[`data/processed/translation/phinc_hinglish_splits/PHINC_TRANSLATION_TEST_LOCK.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/PHINC_TRANSLATION_TEST_LOCK.md)

### Locked Test Asset Identity:
- **File Path:** `data/processed/translation/phinc_hinglish_splits/phinc_test.jsonl`
- **Record Count:** **1,351** sentence pairs
- **File Size:** **1,193,404** bytes
- **SHA-256 Checksum:** `7cd192e2d65b1cd7c3b8b725690cf9e0f0e948e3ace3650235f832ae8ca8bf20`
- **Split Manifest SHA-256:** `f44fa1fa3f282052c933b918b958cfae4f849202dd3e6e8ebaa0a66d0ef09159`

### Lock Agreement Rules:
1. **Zero Fine-Tuning:** Test data shall never be passed to `mt5-small` for gradient updates.
2. **Zero Checkpoint Selection:** Best checkpoints will be chosen strictly by validation loss and BLEU on `phinc_validation.jsonl`.
3. **Zero Hyperparameter Tuning:** Learning rates, warmup steps, and beam search parameters will be tuned only on validation data.
4. **Zero Reference Inspection:** No prompt crafting or heuristic regex rules based on test references.
5. **Single Final Evaluation:** Test set will only be evaluated once model training is complete and frozen.

---

## 9. SPLIT DATASET ARTIFACTS AND REGISTRY

Saved in: `data/processed/translation/phinc_hinglish_splits/` (Git-ignored):

| Artifact Filename | Size | SHA-256 Checksum | Records | Description |
| :--- | :---: | :--- | :---: | :--- |
| [`phinc_train.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/phinc_train.jsonl) | 9,563,198 B | `f9b9b4e5678c5ce628891d0fa9e53224d4723a8015828a95206ce2a3c34f7f41` | 10,802 | Training split (80.00%) |
| [`phinc_validation.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/phinc_validation.jsonl) | 1,199,187 B | `b63971bbc05c692279f092c682d6c2bd1e184fe759009a3a52576c5e54500007` | 1,350 | Validation split (10.00%) |
| [`phinc_test.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/phinc_test.jsonl) | 1,193,404 B | `7cd192e2d65b1cd7c3b8b725690cf9e0f0e948e3ace3650235f832ae8ca8bf20` | 1,351 | Locked test split (10.01%) |
| [`split_manifest.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/split_manifest.json) | 2,752 B | Dynamic | N/A | Dataset manifest with split parameters & hashes |
| [`split_quality_report.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/split_quality_report.json) | 4,218 B | Dynamic | N/A | Quality report, lengths & clustering metrics |
| [`split_processing_config.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/split_processing_config.json) | 1,198 B | Dynamic | N/A | Seed 42 configuration & algorithms |
| [`split_overlap_report.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/split_overlap_report.json) | 935 B | Dynamic | N/A | Pairwise leakage audit results |
| [`PHINC_TRANSLATION_TEST_LOCK.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_splits/PHINC_TRANSLATION_TEST_LOCK.md) | 2,140 B | Dynamic | N/A | Immutable test lock agreement |

**Production Scripts:**
- Splitting Pipeline: [`scripts/split_phinc_translation_dataset.py`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/split_phinc_translation_dataset.py)
- Independent Validation Suite: [`scripts/validate_phinc_translation_splits.py`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_phinc_translation_splits.py)

---

## 10. PROJECT INTEGRITY & V1 PROTECTION CONFIRMATION

- [x] **MuRIL LID model weights (`artifacts/models/muril_lid_baseline/best_model/model.safetensors`):** Bitwise verified (`714defc6f90659eb...`).
- [x] **MuRIL locked evaluation artifacts (`artifacts/evaluation/muril_lid_baseline/`):** Untouched.
- [x] **Existing LID processed datasets (`data/processed/language_identification/`):** Untouched.
- [x] **FastAPI backend (`backend/`) and Vanilla JS frontend (`frontend/`):** Untouched.
- [x] **Git tag `v1.0.0`:** Points unchanged to commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`.
- [x] **COMI-LINGUA MT:** Excluded from baseline and kept in separate raw directory.
- [x] **No model training or inference occurred.**
- [x] **Zero Git commits created; zero files pushed.**

---

## 11. READINESS FOR STEP 34D & FINAL STOP CONDITION

The three splits have been created, independently validated, and cryptographically locked.

### Readiness Status: <span style="color:green;font-weight:bold;">APPROVED FOR STEP 34D</span>

### Next Step Preview:
**Step 34D — Prepare Reproducible Google Colab GPU Training Notebook for mT5-small:**
1. Package `phinc_train.jsonl` (10,802 pairs) and `phinc_validation.jsonl` (1,350 pairs) for Colab ingestion.
2. Structure Seq2Seq fine-tuning notebook for `google/mt5-small` with Hugging Face `Seq2SeqTrainer`.
3. Configure evaluation on validation set only using SacreBLEU and chrF++.
4. Ensure the locked test set (`phinc_test.jsonl`) remains excluded from training environments until final model release.

---
*Execution has halted per Step 34C Final Stop Condition. Awaiting user instruction.*
