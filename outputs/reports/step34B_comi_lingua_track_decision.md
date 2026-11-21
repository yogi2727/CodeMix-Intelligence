# CODEMIX INTELLIGENCE — V2 (mT5-small)
## STEP 34B — COMI-LINGUA MT SEPARATE TRACK DECISION RECORD
**Document Version:** 1.0.0  
**Date:** 2026-11-01  
**Project Workspace:** `c:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**Active Branch:** `feature/mt5-translation-v2`  
**Decision Classification:** **`EXCLUDED_FROM_PRIMARY_SUPERVISED_BASELINE`** (Quarantined to Secondary Exploratory Track)  

---

## 1. PURPOSE AND CONTEXT

In Step 34A, two candidate code-mixed Hindi-English machine translation corpora were acquired and forensically audited:
1. **PHINC** (`data/raw/translation/phinc/PHINC.csv`): 13,738 rows, Romanized Hinglish, human-translated English targets.
2. **COMI-LINGUA MT** (`data/raw/translation/comi_lingua_mt/`): 24,692 train rows, 5,000 test rows, Devanagari/mixed script, Llama 3.3 drafts with three human annotator review columns.

This decision document formally records the architectural, legal, scientific, and ethical rationale for **excluding COMI-LINGUA MT from the primary supervised translation candidate pool in Step 34B**, maintaining it strictly in an isolated exploratory track.

---

## 2. FORENSIC AUDIT EVIDENCE (STEP 34A FINDINGS)

The programmatic provenance audit in Step 34A revealed the following empirical characteristics of COMI-LINGUA MT:

### A. Dataset Scale and Schema
- **`MT_train.csv`:** 24,692 rows (60,989,602 bytes | SHA-256: `9a9bf88ced2cd94925549cce0b3f361eb4ae1f70b1d4abf9fbeec22deae1a2cc`)
- **`MT_test.csv`:** 5,000 rows (11,592,610 bytes | SHA-256: `4160eb08b8db47fcc8925791c523746a73ea645b4b6c2f04f1fc0593f9e3c3e8`)
- **Schema:** 13 columns containing:
  - `Sentences`: Code-mixed input.
  - `Predicted_en_translation`: Raw model output from `meta-llama/Llama-3.3-70B-Instruct`.
  - `Annotator_1_en_translation`, `Annotator_2_en_translation`, `Annotator_3_en_translation`: English translation review columns.

### B. Provenance Reality: 98.52% LLM Verbatim Overlap
An exact bitwise and string-level comparison between the raw Llama 3.3 prediction column and the human annotator columns demonstrated:

| Split | Total Records | Predicted == Annotator 1 | Predicted == Annotator 2 | Predicted == Annotator 3 | All 3 Annotators Identical | All 4 Identical (Predicted + 3 Annotators) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MT_train.csv** | 24,692 | 24,659 (99.87%) | 24,607 (99.66%) | 24,404 (98.83%) | 24,330 (98.53%) | **24,327 (98.52%)** |
| **MT_test.csv** | 5,000 | 4,988 (99.76%) | 4,984 (99.68%) | 4,901 (98.02%) | 4,892 (97.84%) | **4,890 (97.80%)** |

- In **98.52% of training rows** (24,327 / 24,692), not a single annotator altered the Llama 3.3 machine-generated English translation.
- In **97.80% of test rows** (4,890 / 5,000), all three annotators left the Llama 3.3 output completely unchanged.
- Only **365 rows in train (1.48%)** and **110 rows in test (2.20%)** underwent active human editing by any annotator.

---

## 3. CORE EXCLUSION RATIONALE

### 3.1 Scientific Integrity & Circular Evaluation Risk
If COMI-LINGUA MT were combined into the primary candidate pool alongside PHINC, the resulting sequence-to-sequence model (`mT5-small`) would effectively be fine-tuned to distill and mimic `Llama-3.3-70B-Instruct` outputs, rather than learning authentic human-authored translations. Representing model evaluation scores on this data as "human translation quality" would constitute scientific misrepresentation.

### 3.2 Provenance Incompatibility with PHINC
PHINC consists of 100% human-annotated English translations created by 54 independent annotators from scratch (provenance: `human_translated`). Mixing it with COMI-LINGUA (provenance: `human_corrected_machine_draft`) would pollute the provenance boundary of the primary benchmark, making it impossible to establish an authentic baseline.

### 3.3 Selective Filtering Fallacy
Project rules explicitly forbid filtering down to only the ~1.5% of rows where human edits occurred and claiming that subset is "gold human translation":
1. The small minority of edited sentences is not representative of the broader distribution.
2. There is no external inter-annotator consensus validation proving the quality of those 365 edits.
3. Artificially cherry-picking 365 rows would introduce severe sample bias.

### 3.4 Script Modality Divergence
PHINC is **99.77% Romanized Hindi (Latin script)**. COMI-LINGUA MT is **87.18% Devanagari/Latin mixed script and 12.82% Devanagari-only**. Conflating these two distinct linguistic modalities into a single unstratified training pool in Step 34B would confound hyperparameter tuning, tokenizer behavior, and error analysis.

### 3.5 Test Split Protection & Benchmark Isolation
COMI-LINGUA provides an official test split (`MT_test.csv`, 5,000 rows). Under no circumstances may official test references be used for training or merged into training pools. Keeping the entire COMI-LINGUA MT corpus quarantined prevents accidental test leakage into training workflows.

---

## 4. FUTURE EXPERIMENTAL POLICY (SECONDARY TRACK ONLY)

COMI-LINGUA MT will not be deleted or discarded. It remains safely archived in `data/raw/translation/comi_lingua_mt/` under the following conditions:

1. **Exploratory Pseudo-Reference Track Only:**
   If utilized in future V2 experiments, it will be treated as an exploratory, explicitly disclosed *silver/pseudo-reference augmentation track*, never mixed silently with gold human data.
2. **Mandatory Provenance Disclosure:**
   Any publication, dashboard report, or model card referencing COMI-LINGUA must state:
   > *"Translations originated as Llama-3.3-70B-Instruct drafts and were accepted verbatim by annotators in 98.52% of cases. The dataset represents human-verified LLM drafts, not independent human references."*
3. **Quarantine of `MT_test.csv`:**
   `MT_test.csv` will remain strictly quarantined from any training, validation, or prompt tuning to preserve benchmark integrity.
4. **No Premature Devanagari Claims:**
   Until dedicated gold human translation benchmarks are established for Devanagari code-mixed text, CodeMix Intelligence will make no claims of verified Devanagari translation capability based on COMI-LINGUA alone.

---

## 5. SUMMARY OF DECISION

| Action | Decision | Justification |
| :--- | :---: | :--- |
| **Merge COMI-LINGUA into PHINC Candidate Pool** | **REJECTED** | 98.52% LLM draft overlap; corrupts gold human baseline. |
| **Filter and Keep Only Edited Rows (1.5%)** | **REJECTED** | Severe selection bias; unvalidated edit quality. |
| **Use `MT_test.csv` for Training** | **STRICTLY PROHIBITED** | Violation of test set isolation; test leakage risk. |
| **Retain in Isolated Raw Directory** | **APPROVED** | Preserved for secondary, fully disclosed exploratory tracks. |
| **Claim Devanagari Translation Parity** | **REJECTED** | Unsubstantiated by independent gold human ground truth. |

---
*Signed by V2 Architecture Lead — CodeMix Intelligence*
