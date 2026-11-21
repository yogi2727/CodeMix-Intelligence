# Step 33E: Read-Only V1 Git Release Content Audit

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 33E — Read-only V1 Git Release Content Audit  
**Workspace:** [`C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence)  
**Target Release Tag:** `v1.0.0`  
**Target Release Commit:** `c9509f0e9e10fe715c759edc09d1dacadb540f74`  
**Current Active Branch:** `feature/mt5-translation-v2`  
**Audit Timestamp:** `2026-11-01T12:13:00Z`  
**Audit Mode:** **READ-ONLY INSPECTION (Zero Modifications, Zero Deletions, Zero Rewrites)**  

---

## 1. Executive Summary

A comprehensive, read-only audit of Git tag `v1.0.0` and its complete tracked object tree (137 tracked files) was conducted to verify security, isolation of heavy model weights, absence of raw datasets and secrets, and repository structure.

All nine verification points passed with 100% compliance.

---

## 2. Core Security & Isolation Audit Checklist

| Item | Verification Requirement | Result | Finding Details |
| :---: | :--- | :---: | :--- |
| **1** | No `model.safetensors` files committed | **PASSED** | **0** `.safetensors` files found across the entire tree. (Local 947.9 MB weights file is properly excluded). |
| **2** | No model ZIP archives committed | **PASSED** | **0** `.zip` archives found. (Local 881.2 MB model ZIP, evaluation ZIP, Colab bundles, and source snapshot ZIP are strictly excluded). |
| **3** | No raw `train.jsonl`, `validation.jsonl`, or `test.jsonl` committed | **PASSED** | **0** raw JSONL dataset files found. Only `.gitkeep` placeholders exist in `data/raw/`, `data/processed/`, and `data/custom/`. |
| **4** | No `.venv` or cache directories committed | **PASSED** | **0** `.venv`, `__pycache__`, or `.pytest_cache` directories found. |
| **5** | No `.env` files, credentials, private keys, or secrets committed | **PASSED** | **0** secrets or `.env` files found. Only the non-sensitive configuration template [`.env.example`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/.env.example) is tracked. |
| **6** | List 20 largest tracked blobs in V1 with sizes | **PASSED** | Documented in Section 3 below. Only 1 file exceeds 1 MB (`vocab.txt` at 3.02 MB). |
| **7** | Explain the 290,327 insertions in commit `c9509f0` | **PASSED** | 89.9% of insertions come from two structured text files: `vocab.txt` (197,285 lines) and `step30_lid_training_readiness.json` (63,644 lines). |
| **8** | Verify tag `v1.0.0` points to commit `c9509f0...` | **PASSED** | `git rev-parse "v1.0.0^{commit}"` resolves strictly to `c9509f0e9e10fe715c759edc09d1dacadb540f74`. |
| **9** | Verify current active branch remains `feature/mt5-translation-v2` | **PASSED** | `git branch --show-current` confirms active branch is `feature/mt5-translation-v2`. |

---

## 3. Top 20 Largest Tracked Blobs in V1.0.0

| Rank | Object Size | Size in Bytes | Tracked File Path | Category |
| :---: | :---: | :---: | :--- | :--- |
| **1** | **3.02 MB** | 3,162,999 B | [`artifacts/models/muril_lid_baseline/best_model/vocab.txt`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/models/muril_lid_baseline/best_model/vocab.txt) | Pretrained Model Vocabulary |
| **2** | **984.27 KB** | 1,007,896 B | [`outputs/reports/step30_lid_training_readiness.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step30_lid_training_readiness.json) | Audit Report |
| **3** | **79.36 KB** | 81,262 B | [`outputs/reports/step33C_screenshots/desktop.png`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33C_screenshots/desktop.png) | UI Verification Screenshot |
| **4** | **69.24 KB** | 70,897 B | [`scripts/validate_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) | Python Validation Script |
| **5** | **64.94 KB** | 66,499 B | [`outputs/reports/step33C_screenshots/tablet.png`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33C_screenshots/tablet.png) | UI Verification Screenshot |
| **6** | **60.29 KB** | 61,732 B | [`outputs/faculty_review/CodeMix_Intelligence_Faculty_Review_Package.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/CodeMix_Intelligence_Faculty_Review_Package.md) | Governance Documentation |
| **7** | **51.00 KB** | 52,221 B | [`outputs/reports/step33C_screenshots/mobile.png`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33C_screenshots/mobile.png) | UI Verification Screenshot |
| **8** | **46.87 KB** | 47,998 B | [`outputs/reports/muril_token_alignment_audit.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/muril_token_alignment_audit.json) | Audit Report |
| **9** | **42.87 KB** | 43,897 B | [`scripts/audit_lid_training_readiness.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/audit_lid_training_readiness.py) | Python Audit Script |
| **10** | **37.32 KB** | 38,212 B | [`scripts/reconcile_quarantine_counts.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/reconcile_quarantine_counts.py) | Python Audit Script |
| **11** | **36.32 KB** | 37,194 B | [`training/colab/muril_lid_baseline.ipynb`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/training/colab/muril_lid_baseline.ipynb) | Jupyter Training Notebook |
| **12** | **35.29 KB** | 36,141 B | [`scripts/generate_muril_colab_notebook.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/generate_muril_colab_notebook.py) | Python Generator Script |
| **13** | **32.88 KB** | 33,667 B | [`scripts/reconcile_step30A_statistics.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/reconcile_step30A_statistics.py) | Python Audit Script |
| **14** | **31.12 KB** | 31,866 B | [`scripts/audit_quarantined_leakage.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/audit_quarantined_leakage.py) | Python Audit Script |
| **15** | **29.15 KB** | 29,850 B | [`scripts/audit_custom_lid_sources.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/audit_custom_lid_sources.py) | Python Audit Script |
| **16** | **26.66 KB** | 27,297 B | [`scripts/generate_step31_reports.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/generate_step31_reports.py) | Python Report Script |
| **17** | **23.80 KB** | 24,374 B | [`frontend/app.js`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/frontend/app.js) | Frontend Application Logic |
| **18** | **23.79 KB** | 24,360 B | [`outputs/reports/quarantined_leakage_audit.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/quarantined_leakage_audit.json) | Audit Report |
| **19** | **21.41 KB** | 21,928 B | [`scripts/audit_final_lid_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/audit_final_lid_dataset.py) | Python Audit Script |
| **20** | **21.00 KB** | 21,503 B | [`outputs/reports/step28_governance_and_schema.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step28_governance_and_schema.md) | Governance Report |

---

## 4. Forensic Investigation of the 290,327 Insertions

When the V1 baseline was committed in `c9509f0`, `git diff --stat` reported **290,327 insertions**. The forensic audit confirms that this high line count is entirely due to plain-text vocabulary tokens and structured JSON audit data, not binary leakage or bloated code:

### Primary Contributors

1. **`artifacts/models/muril_lid_baseline/best_model/vocab.txt`**:  
   - **197,285 lines** (**67.95%** of all insertions).  
   - *Reason:* Standard WordPiece vocabulary for `google/muril-base-cased` where each line represents exactly one token in the subword vocabulary.
2. **`outputs/reports/step30_lid_training_readiness.json`**:  
   - **63,644 lines** (**21.92%** of all insertions).  
   - *Reason:* Comprehensive pre-training readiness audit mapping token frequencies, subset distribution tallies, and schema validation receipts.
3. **`outputs/reports/muril_token_alignment_audit.json`**:  
   - **1,457 lines** (**0.50%** of all insertions).  
   - *Reason:* Detailed Subword-to-WordPiece alignment verification mapping.
4. **`scripts/validate_custom_trilingual_dataset.py`**:  
   - **1,418 lines** (**0.49%** of all insertions).  
   - *Reason:* Source validator with exhaustive rule tables.
5. **`outputs/faculty_review/CodeMix_Intelligence_Faculty_Review_Package.md`**:  
   - **981 lines** (**0.34%** of all insertions).
6. **`frontend/styles.css`**:  
   - **951 lines** (**0.33%** of all insertions).
7. **`training/colab/muril_lid_baseline.ipynb`**:  
   - **930 lines** (**0.32%** of all insertions).  
   - *Reason:* Standard formatted JSON notebook structure (36.3 KB).

**Summary:** The top two files (`vocab.txt` + `step30_lid_training_readiness.json`) alone account for **260,929 lines (89.87%)** of the entire commit. No bloated or runaway binary blobs exist.

---

## 5. Git Reference Integrity

```text
Tag:                  v1.0.0
Dereferenced Commit:  c9509f0e9e10fe715c759edc09d1dacadb540f74
Tag Target Match:     EXACT MATCH
Current Branch:       feature/mt5-translation-v2
Branch Starting Point:c9509f0e9e10fe715c759edc09d1dacadb540f74 (v1.0.0)
Working Tree Status:  Clean
```

---

## 6. Conclusion & Stop

All 9 requirements for Step 33E have been verified and documented. No application or repository changes were made. Execution is stopped.
