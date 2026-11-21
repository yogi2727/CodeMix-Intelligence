# Step 33A Checksum Correction Note

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Document:** Step 33A Audit Checksum Reconciliation & Historical Trail  
**Reference Step:** Step 33A — Integrate and Verify Trained Model Artifacts Locally  
**Reconciliation Date:** 2026-11-01  
**Status:** **AUTHORITATIVE RECONCILIATION COMPLETE**  

---

## 1. Overview & Forensic Context

During the execution of **Step 33D (Freeze V1.0.0 Stable Release)**, a pre-release cryptographic audit compared the local archive files against the expected checksums documented in earlier textual reports.

The audit revealed a discrepancy between the human-readable Markdown table in [`outputs/reports/step33A_model_integration_and_audit.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33A_model_integration_and_audit.md) and the programmatic machine-readable audit report in [`outputs/reports/step33A_model_integration_and_audit.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33A_model_integration_and_audit.json).

This document serves as an official, immutable audit addendum preserving the complete historical record without altering prior reports.

---

## 2. Checksum Discrepancy & Authoritative Values

### A. Model Archive: `muril_lid_best_model.zip` (881,225,333 bytes)

* **Erroneous Textual Template Value (Markdown):**  
  `7bf407aa71bc97397b9ee9e0e56aa76d8b0ebfae5743b0c885bb24479e39433e`  
  *(Origin: Static placeholder string embedded in the string template of `scripts/generate_step33A_reports.py` at line 172).*
* **Authoritative Programmatic Value (Canonical JSON Audit):**  
  `a5439181f02fece996bf526629c70da20166a53450fb615a44f343d8cbf8a827`  
  *(Recorded dynamically in `outputs/reports/step33A_model_integration_and_audit.json` at line 12).*
* **Current Disk File SHA-256:**  
  `a5439181f02fece996bf526629c70da20166a53450fb615a44f343d8cbf8a827`  
  *(Bitwise match: 100% identical to the Step 33A programmatic audit).*

### B. Evaluation Archive: `muril_lid_evaluation_results.zip` (3,823 bytes)

* **Erroneous Textual Template Value (Markdown):**  
  `21b365e100f22f7b49cf5d064299b9cf2a53bbd35ba48a80d507b508f75ff200`  
  *(Origin: Static placeholder string embedded in the string template of `scripts/generate_step33A_reports.py` at line 173).*
* **Authoritative Programmatic Value (Canonical JSON Audit):**  
  `bbe1585281070b78baa98b0d4e6ae5e64ae9fe07c1c9ed31abb7cd08677cc876`  
  *(Recorded dynamically in `outputs/reports/step33A_model_integration_and_audit.json` at line 24).*
* **Current Disk File SHA-256:**  
  `bbe1585281070b78baa98b0d4e6ae5e64ae9fe07c1c9ed31abb7cd08677cc876`  
  *(Bitwise match: 100% identical to the Step 33A programmatic audit).*

### C. Extracted Model Weights: `model.safetensors` (947,898,192 bytes)

* **Documented & Expected SHA-256:**  
  `714defc6f90659ebc25e5e011a9101579d36cf9f3b4c57165c0614f1bc744bae`
* **Current Disk File SHA-256:**  
  `714defc6f90659ebc25e5e011a9101579d36cf9f3b4c57165c0614f1bc744bae`  
  *(Bitwise match: 100% identical across all reports and disk files).*

---

## 3. Archive Member Integrity Verification

To confirm that neither archive suffered corruption or modification:

1. **`muril_lid_best_model.zip` Contents:**
   - `model.safetensors` (947,898,192 bytes, SHA-256: `714defc6f906...`): **Bitwise Identical** to extracted file.
   - `config.json` (830 bytes, SHA-256: `357621e8db62...`): **Bitwise Identical** to extracted file.
   - `vocab.txt` (3,162,999 bytes, SHA-256: `b96cc938b400...`): **Bitwise Identical** to extracted file.
   - `tokenizer_config.json` (1,266 bytes, SHA-256: `9b05d6704f08...`): **Bitwise Identical** to extracted file.
   - `special_tokens_map.json` (125 bytes, SHA-256: `b6d346be366a...`): **Bitwise Identical** to extracted file.
   - `training_args.bin` (5,777 bytes, SHA-256: `e9225752e88d...`): **Bitwise Identical** to extracted file.

2. **`muril_lid_evaluation_results.zip` Contents:**
   - All five evaluation files (`locked_test_results.json`, `source_wise_results.json`, `source_subset_metrics_posthoc.json`, `confusion_matrix.csv`, `LOCKED_TEST_EVALUATION_COMPLETE.json`) are **100% bitwise identical** to the files residing in `artifacts/evaluation/muril_lid_baseline/`.

---

## 4. Preservation Assertions

1. Neither original archive (`muril_lid_best_model.zip`, `muril_lid_evaluation_results.zip`) was modified, overwritten, or recompressed.
2. The extracted weights (`model.safetensors`) and tokenizer assets were not altered.
3. The historical reports ([`step33A_model_integration_and_audit.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33A_model_integration_and_audit.json), [`step33A_model_integration_and_audit.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step33A_model_integration_and_audit.md), and [`scripts/generate_step33A_reports.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/generate_step33A_reports.py)) are preserved intact.
4. The canonical release checksums for V1.0.0 are formally established as `a5439181...` (model ZIP) and `bbe15852...` (evaluation ZIP).
