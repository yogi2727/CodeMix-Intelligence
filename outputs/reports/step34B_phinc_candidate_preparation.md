# CODEMIX INTELLIGENCE — V2 (mT5-small)
## STEP 34B — PHINC DATASET CLEANING, NORMALIZATION AND CANDIDATE PREPARATION REPORT

**Document Version:** 1.0.0  
**Timestamp:** 2026-11-01T18:51:49.914269  
**Project Workspace:** `c:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**GitHub Remote:** [https://github.com/yogi2727/CodeMix-Intelligence](https://github.com/yogi2727/CodeMix-Intelligence)  
**Active Development Branch:** `feature/mt5-translation-v2`  
**Stable Tag:** `v1.0.0` (commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`)  
**Processing Status:** <span style="color:green;font-weight:bold;">COMPLETED & VALIDATED (ZERO REPO LEAKAGE)</span>  

---

## EXECUTIVE SUMMARY

Step 34B executes the deterministic cleaning, conservative normalization, and candidate dataset preparation for the primary translation corpus: **PHINC (Parallel Hinglish Social Media Code-Mixed Corpus)**. 

Following the forensic findings of Step 34A, this step resolves all defective targets, source conflicts, and duplicate pairs using an auditable, reproducible pipeline without altering original raw files, without merging unverified secondary datasets, and without creating final train/val/test splits (reserved for Step 34C).

### Key Results Summary:
1. **Raw Input Verified:** 13,738 raw records in `data/raw/translation/phinc/PHINC.csv` verified bitwise (SHA-256: `325ba383cd6d73e0c3128885e2a79133e612ec03d18c8b55506d0b4b12ec68ed`).
2. **Defective Targets Quarantined:** **232 target rows containing zero Unicode letters** (e.g., `)`, `"'("`) were quarantined under code `target_no_unicode_letters`.
3. **Conflicting Translations Quarantined:** **2 rows across 1 conflicting source group** (Row 299 vs Row 340) were quarantined under code `conflicting_targets_for_same_source`.
4. **Duplicate Pair Copies Quarantined:** **1 subsequent copy** of an exact duplicate pair (Row 1092, duplicate of Row 63) was quarantined under code `exact_duplicate_pair`.
5. **Exact Zero-Loss Accounting:**
   $$\text{Raw Records (13,738)} = \text{Retained Candidates (13,503)} + \text{Quarantined Records (235)}$$
6. **Candidate Pool Prepared:** 13,503 clean, normalized, non-conflicting sentence pairs saved to `phinc_pairs_candidate.jsonl` (SHA-256: `aa4fdf0c72183d3a3e3ca100798bdfe396cecd18c7515a7adac2396c0d6e4b5b`).
7. **COMI-LINGUA Isolation:** COMI-LINGUA MT remains completely excluded from the primary supervised pool per [`outputs/reports/step34B_comi_lingua_track_decision.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step34B_comi_lingua_track_decision.md).
8. **V1 Absolute Protection:** MuRIL baseline model files, evaluation artifacts, frontend/backend code, and Git tags remain 100% untouched.

---

## 1. GIT AND V1 SAFETY VERIFICATION

Before executing any data transformation, read-only Git checks verified the workspace state:
- **Active Branch:** `feature/mt5-translation-v2` (up to date with remote).
- **V1 Commit:** `c9509f0e9e10fe715c759edc09d1dacadb540f74`.
- **Merge Base:** Confirmed `v1.0.0` is an ancestor of `feature/mt5-translation-v2`.
- **Tracked Working Tree:** Completely clean.
- **Data Protection:** `data/raw/` and `data/processed/` are completely excluded from Git via `.gitignore`.

---

## 2. ORIGINAL DATA VERIFICATION & SOURCE SCHEMA

### 2.1 Raw File Verification
- **Input File:** `data/raw/translation/phinc/PHINC.csv`
- **File Size:** 2,125,039 bytes (exact match with Step 34A).
- **SHA-256:** `325ba383cd6d73e0c3128885e2a79133e612ec03d18c8b55506d0b4b12ec68ed` (bitwise match).
- **Total Data Rows:** 13,738.
- **Parsing Mode:** Read-only CSV stream with UTF-8 encoding and quoted multiline field support.
- **Original Row Ordering:** Preserved as authoritative provenance (`source_row_index` 1 to 13,738).

### 2.2 Source Schema
Header: `Sentence,English_Translation`
- `Sentence` -> `source_text_original` (informal Romanized Hinglish social media text).
- `English_Translation` -> `target_text_original` (English reference translation).
- **Native IDs:** None provided in raw CSV. Every record receives a deterministic unique identifier: `PHINC:row:{source_row_index:06d}`.

---

## 3. CLEANING DECISIONS AND FILTERING POLICIES

The cleaning pipeline applies non-destructive, auditable, deterministic policies:

```
Raw PHINC Records (13,738)
          │
          ├── [1] Syntax & Validation Pass ────────────► 0 Malformed / Empty
          │
          ├── [2] Unicode Letter Filter (Target) ──────► 232 Quarantined (target_no_unicode_letters)
          │
          ├── [3] Canonical Conflict Check ────────────► 2 Quarantined (conflicting_targets_for_same_source)
          │
          ├── [4] Duplicate Pair Deduplication ────────► 1 Quarantined (exact_duplicate_pair)
          │
          ▼
Final Retained Candidates: 13,503 Records
```

### 3.1 Input Validation (Section 5.1)
Each row was checked for missing fields, empty strings, whitespace-only content, and malformed CSV structure. All 13,738 rows contained two non-empty, syntactically valid fields.

### 3.2 Target Alphabetic Filter (Section 5.2)
- **Rule:** A target translation must contain at least one character belonging to Unicode general category `L` (Letter: `Lu`, `Ll`, `Lt`, `Lm`, `Lo`).
- **Audit Result:** **232 rows** were identified where targets consisted exclusively of punctuation symbols (predominantly single closing parentheses `)` or punctuation combinations like `"'("`).
- **Action:** Quarantined under `reason_code: "target_no_unicode_letters"`.
- **Impact:** Eliminates degenerative training examples that would cause `mT5-small` to emit single punctuation characters on code-mixed inputs.

### 3.3 Conflicting Translation Resolution (Section 5.3)
- **Canonical Key:** Unicode NFC normalization, trimmed leading/trailing whitespace, collapsed internal whitespace to single spaces (casing preserved).
- **Rule:** If the same canonical source sentence maps to multiple distinct canonical target translations among letter-containing records, **the entire source group is quarantined**. No arbitrary winner is selected.
- **Audit Result:** Exactly **1 conflict group** was identified:
  - **Source Sentence:** `'When Sagarika was born doctor said "Mubarak ho aur Shubhkamnayen bhi"'`
  - **Variant A (Row 299):** `'When Sagarika was brn doctor said "Congratulations and good wishes!!"'`
  - **Variant B (Row 340):** `'When Sagarika was born doctor said "congratulations and good wishes too"'`
- **Action:** Both Row 299 and Row 340 quarantined under `reason_code: "conflicting_targets_for_same_source"`.

### 3.4 Exact Duplicate Pair Deduplication (Section 5.4)
- **Rule:** If multiple records share identical canonical source and canonical target strings, retain the first occurrence (lowest `source_row_index`) and quarantine subsequent copies.
- **Audit Result:** Exactly **1 duplicate copy** was identified:
  - **Pair:** `'Brilliant Answer By Boy Friend on Break Up … . Girl '` -> `' Tumhe Mere Jaisi Ladki Nahi Milegi . . . . . Boy '`
  - **First Occurrence (Row 63):** Retained in candidate pool.
  - **Subsequent Occurrence (Row 1092):** Quarantined under `reason_code: "exact_duplicate_pair"`.

---

## 4. RECORD ACCOUNTING AND RECONCILIATION

The record accounting reconciles with zero loss and zero double-counting:

| Processing Category | Record Count | % of Raw Data | Action Taken |
| :--- | :---: | :---: | :--- |
| **Raw Input Rows** | **13,738** | 100.00% | Source verification passed |
| ↳ Targets with No Unicode Letters | **232** | 1.69% | Quarantined to `phinc_excluded_records.jsonl` |
| ↳ Conflicting Source Group Members | **2** | 0.01% | Quarantined to `phinc_excluded_records.jsonl` |
| ↳ Subsequent Duplicate Pair Copies | **1** | 0.01% | Quarantined to `phinc_excluded_records.jsonl` |
| **Total Quarantined Records** | **235** | **1.71%** | Fully auditable in excluded records file |
| **Total Retained Candidate Records** | **13,503** | **98.29%** | Prepared in `phinc_pairs_candidate.jsonl` |

$$\text{Reconciliation Check: } 13,503 + 235 = 13,738 \quad \text{[100% RECONCILED]}$$

---

## 5. NORMALIZATION POLICY AND REPRODUCIBILITY

### 5.1 Normalization Applied
To produce `source_text` and `target_text`:
1. **Unicode NFC Normalization:** Standardizes multi-byte composite characters.
2. **Whitespace Trimming:** Strips leading and trailing whitespace.
3. **Internal Whitespace Collapsing:** Replaces multi-space gaps, tabs, and newline sequences with single ASCII spaces.
4. **Preservation:** Original strings are preserved verbatim in `source_text_original` and `target_text_original`. No text was lowercased, paraphrased, grammatically edited, or transliterated.

### 5.2 Reusable Script
The entire cleaning and normalization process is implemented in:  
[`scripts/prepare_phinc_translation_candidate.py`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/prepare_phinc_translation_candidate.py)  
The script is documented, deterministic, and idempotent. Re-running the script against `PHINC.csv` regenerates identical output files with identical checksums.

---

## 6. SCRIPT AND LANGUAGE CHARACTERISTICS

Unicode-aware script categorization on the **13,503 retained candidate records**:

| Linguistic Profile | Script Profile | Source Records | Source % | Target Records | Target % |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Romanized Hinglish** | Latin Script | 13,472 | **99.77%** | 13,494 | **99.93%** |
| **Mixed Script** | Latin + Devanagari | 29 | **0.21%** | 9 | **0.07%** |
| **Devanagari Only** | Devanagari Script | 2 | **0.01%** | 0 | **0.00%** |
| **No Letters** | Punctuation / Numbers | 0 | **0.00%** | 0 | **0.00%** |

### Linguistic Takeaway:
- The candidate dataset is overwhelmingly (**99.77%**) **Romanized Hinglish** in Latin script.
- The 29 mixed-script and 2 Devanagari sentences are preserved with accurate metadata tags (`Hinglish_Mixed_Script`, `Hinglish_Devanagari`), but they do NOT constitute sufficient density to claim robust Devanagari translation support.

---

## 7. LENGTH STATISTICS (RETAINED CANDIDATE POOL)

| Dimension | Min | Median | Mean | 95th Percentile | Max |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Source Characters (Normalized)** | 3 | 70.0 | 76.16 | 140.0 | 273 |
| **Source Whitespace Tokens** | 1 | 12.0 | 13.28 | 27.0 | 40 |
| **Target Characters (Normalized)** | 1 | 68.0 | 75.06 | 142.0 | 277 |
| **Target Whitespace Tokens** | 1 | 11.0 | 12.50 | 25.0 | 46 |

Length distribution is well-behaved: 95% of examples have $\le 27$ source tokens and $\le 25$ target tokens, fitting comfortably within the standard maximum sequence length (128 or 256 tokens) for `google/mt5-small`.

---

## 8. PREPARED CANDIDATE ARTIFACTS AND REGISTRY

All output files are saved under:  
`data/processed/translation/phinc_hinglish_candidate/`

| Artifact Filename | File Size | SHA-256 Checksum | Record Count | Description |
| :--- | :---: | :--- | :---: | :--- |
| [`phinc_pairs_candidate.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_candidate/phinc_pairs_candidate.jsonl) | 10,465,060 B | `aa4fdf0c72183d3a3e3ca100798bdfe396cecd18c7515a7adac2396c0d6e4b5b` | 13,503 | Retained, clean candidate parallel pairs |
| [`phinc_excluded_records.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_candidate/phinc_excluded_records.jsonl) | 84,708 B | `88a99af16fe0ef5062dae746bb6348b68bdb62f7a55f1bb18c97bd282e2f489a` | 235 | Quarantined records with reason codes & details |
| [`phinc_dataset_manifest.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_candidate/phinc_dataset_manifest.json) | 3,361 B | Dynamic | N/A | Full dataset provenance, policy & artifact manifest |
| [`phinc_quality_summary.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_candidate/phinc_quality_summary.json) | 3,115 B | Dynamic | N/A | Accounting reconciliation, lengths & integrity |
| [`phinc_processing_config.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/translation/phinc_hinglish_candidate/phinc_processing_config.json) | 1,289 B | Dynamic | N/A | Environment, rules & reproducibility config |

---

## 9. COMI-LINGUA MT SEPARATE TRACK RECORD

Pursuant to Section 13, COMI-LINGUA MT was strictly quarantined and NOT merged into the PHINC candidate pool:
- **Decision Record:** [`outputs/reports/step34B_comi_lingua_track_decision.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step34B_comi_lingua_track_decision.md)
- **Empirical Rationale:** COMI-LINGUA MT English targets reproduce `Llama-3.3-70B-Instruct` drafts verbatim in **98.52% of training rows** (24,327 / 24,692) and **97.80% of test rows** (4,890 / 5,000).
- **Policy Enforcement:** Merging it would corrupt the gold human translation baseline (`PHINC`). Official test split (`MT_test.csv`, 5,000 rows) is isolated to prevent test leakage.

---

## 10. PROJECT INTEGRITY & V1 PROTECTION CONFIRMATION

- [x] **MuRIL LID baseline model weights (`artifacts/models/muril_lid_baseline/best_model/model.safetensors`):** Bitwise identical (`714defc6f90659eb...`).
- [x] **MuRIL locked evaluation artifacts (`artifacts/evaluation/muril_lid_baseline/`):** Untouched.
- [x] **Existing LID processed datasets (`data/processed/language_identification/`):** Untouched.
- [x] **FastAPI backend (`backend/`) and Vanilla JS frontend (`frontend/`):** Untouched.
- [x] **Git tag `v1.0.0`:** Points unchanged to commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`.
- [x] **No train/validation/test splits were created.** (Reserved for Step 34C).
- [x] **No model training or inference occurred.**
- [x] **No Git commits were generated; no remote push occurred.**

---

## 11. READINESS FOR STEP 34C & FINAL STOP CONDITION

The candidate dataset is verified, deterministic, and ready for train/validation/test splitting.

### Readiness Status: <span style="color:green;font-weight:bold;">APPROVED FOR STEP 34C</span>

### Next Step Preview:
**Step 34C — Leakage-Safe Train/Validation/Test Split Preparation:**
1. Ingest `phinc_pairs_candidate.jsonl` (13,503 records).
2. Apply an 80/10/10 split policy (~10,802 train, ~1,350 val, ~1,351 test).
3. Ensure source-level grouping so near-duplicate source sentences do not leak across splits.
4. Fix a deterministic random seed for strict reproducibility.
5. Generate `train.jsonl`, `validation.jsonl`, and `test.jsonl` under `data/processed/translation/phinc_hinglish_splits/`.

---
*Execution has halted per Step 34B Final Stop Condition. Awaiting user instruction.*
