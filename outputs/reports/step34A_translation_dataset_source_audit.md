# CODEMIX INTELLIGENCE — V2 (mT5-small)
## STEP 34A — TRANSLATION DATASET ACQUISITION & FORENSIC AUDIT REPORT
**Timestamp:** 2026-11-01T18:38:00+05:30  
**Project Workspace:** `c:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**GitHub Remote:** [https://github.com/yogi2727/CodeMix-Intelligence](https://github.com/yogi2727/CodeMix-Intelligence)  
**Active Development Branch:** `feature/mt5-translation-v2`  
**Stable Release Tag:** `v1.0.0` (commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`)  
**Audit Status:** <span style="color:green;font-weight:bold;">COMPLETED — ZERO REPO LEAKAGE</span>  

---

## EXECUTIVE SUMMARY

Step 34A initiates Model 2 (`google/mt5-small`) development for CodeMix Intelligence, targeting code-mixed sentence-to-English translation. While Version 1 (MuRIL) solved token-level Language Identification (LID), sentence translation requires parallel sentence pairs (`source_text` -> `target_text`). 

A rigorous forensic audit was conducted across candidate parallel corpora, licensing frameworks, provenance trails, and research literature.

### Key Audit Findings:
1. **Source A — PHINC Acquired & Verified (`PRIMARY_CANDIDATE_PENDING_AUDIT`):**
   - 13,738 Hinglish-English parallel pairs (100% match with published count).
   - 99.77% Latin-script Romanized Hindi input; human-annotated English references (W-NUT 2020).
   - Critical forensic discovery: **232 target rows contain only punctuation (e.g., single closing parentheses `)`)** which must be filtered in Step 34B before any training.
2. **Source B — COMI-LINGUA MT Acquired & Verified (`PENDING_PROVENANCE_REVIEW`):**
   - MT_train: 24,692 rows; MT_test: 5,000 rows.
   - Predominantly Devanagari script (87.18% mixed script, 12.82% Devanagari).
   - Critical forensic discovery: **98.52% of training translations are verbatim, unaltered outputs from Meta's Llama-3.3-70B-Instruct**. This dataset must strictly be classified as `human_corrected_machine_draft`, not independent gold human translations.
   - Zero leakage observed between `MT_train.csv` and `MT_test.csv` (100% split separation).
3. **Source C — Telugu-English Code-Mixed Translation Gap (`RESEARCH_GAP`):**
   - **ReDial-Indic:** Quarantined (`QUARANTINED_PENDING_LICENSE_REVIEW`). Repository has no license file (HTTP 404), underlying ReDial redistribution terms are unverified, and translations are synthetic MT of movie dialogue turns.
   - **Sravani & Mamidi (CoNLL 2023):** Marked `RELATED_WORK_ONLY`. Generates code-mixed from English using synthetic filtered data; no public open dataset download exists.
   - **Empirical Search Conclusion:** **No verified Telugu-English code-mixed-to-English training source established in this step.** This is documented as a legitimate research finding reflecting the genuine state of open Indic NLP resources.
4. **Disjoint Source Overlap:**
   - 0 exact or normalized source sentence overlaps between PHINC and COMI-LINGUA MT.
5. **V1 Absolute Protection:**
   - Zero modifications to MuRIL baseline model weights, evaluation metrics, FastAPI backend, Vanilla JS frontend, or Git tags. All raw translation files are stored in `data/raw/translation/`, fully ignored by `.gitignore`.

---

## 1. GIT BRANCH AND RELEASE SAFETY VERIFICATION

Before acquiring or auditing any data, read-only Git checks verified that the workspace remains in an isolated V2 state:

```powershell
git status
git branch --show-current
git branch -v
git tag --list
git rev-parse "v1.0.0^{commit}"
git merge-base v1.0.0 feature/mt5-translation-v2
```

### Verification Results:
- **Active Branch:** `feature/mt5-translation-v2` (tracking `origin/feature/mt5-translation-v2`).
- **Stable Tag:** `v1.0.0` points precisely to commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`.
- **Ancestry:** `git merge-base v1.0.0 feature/mt5-translation-v2` returned `c9509f0e9e10fe715c759edc09d1dacadb540f74`, confirming V2 directly extends V1 without diverging.
- **Tracked Working Tree:** Completely clean. No tracked files from V1 were modified.
- **Untracked Preserved Files:** Untracked release backups and verification documents from Steps 33D–33F and 34 were preserved untouched.
- **Raw Data Isolation:** `data/raw/*` is covered by `.gitignore` (with `!.gitkeep`), ensuring no raw translation data is staged or committed.

---

## 2. SOURCE A — PHINC HINGLISH-ENGLISH PARALLEL CORPUS

### 2.1 Acquisition and Integrity
- **Official Hugging Face Hub:** [LingoIITGN/PHINC](https://huggingface.co/datasets/LingoIITGN/PHINC)
- **Direct Download URL:** `https://huggingface.co/datasets/LingoIITGN/PHINC/resolve/main/PHINC.csv`
- **Research Citation:** Srivastava & Singh, *"PHINC: A Parallel Hinglish Social Media Code-Mixed Corpus for Machine Translation"*, W-NUT 2020 ([ACL Anthology: 2020.wnut-1.7](https://aclanthology.org/2020.wnut-1.7/))
- **Local Storage Path:** `data/raw/translation/phinc/PHINC.csv`
- **File Size:** 2,125,039 bytes (2.03 MB)
- **SHA-256 Checksum:** `325ba383cd6d73e0c3128885e2a79133e612ec03d18c8b55506d0b4b12ec68ed`
- **File Signature:** Verified text/csv; header begins with `Sentence,English_Translation`.

### 2.2 Schema and Field Mapping
- **Total Columns:** 2
- **Column 1:** `Sentence` -> Mapped to `source_text` (code-mixed input).
- **Column 2:** `English_Translation` -> Mapped to `target_text` (English reference translation).
- **Sentence IDs:** None provided in source CSV.
- **Official Splits:** Monolithic release (single split; no pre-existing train/dev/test partition).

### 2.3 Row Count & Data Quality Audit
| Metric | Value | Audit Finding |
| :--- | :--- | :--- |
| **Total Rows** | 13,738 | Matches published paper count exactly |
| **Missing Source Values** | 0 | None |
| **Missing Target Values** | 0 | None |
| **Empty Strings (Source)** | 0 | None |
| **Empty Strings (Target)** | 0 | None |
| **Whitespace-only Fields** | 0 | None |
| **Malformed CSV Rows** | 0 | Valid 2-column CSV parsing throughout |
| **Exact Duplicate Pairs** | 1 | Row 64 & Row 1093 are identical |
| **Unique Source Sentences** | 13,736 | 2 source duplicates detected |
| **Conflicting Target Translations**| 1 | Row 300 vs Row 341 share source with slightly different targets |
| **No-Alpha / Punctuation-Only Targets** | **232** | **Target contains only punctuation like `)` or `"'("`** |

> [!CAUTION]
> **Forensic Finding — 232 Defective Targets in PHINC:**
> A forensic check on alphabetic characters revealed that **232 target rows contain zero letters**, consisting solely of characters like `)` or `'(`. For instance, Line 39 (`@mamtan14 didi abhi apni me time hai`) has target `)`. If trained without filtering, an encoder-decoder model will learn to output punctuation artifacts. These 232 rows must be quarantined during Step 34B preprocessing.

### 2.4 Script and Length Statistics
- **Input Script Distribution (Source):**
  - **Latin Script (Romanized Hindi):** 13,707 rows (**99.77%**)
  - **Mixed Script (Latin + Devanagari):** 29 rows (**0.21%**)
  - **Devanagari Only:** 2 rows (**0.01%**)
- **Target Script Distribution:**
  - **Latin Script (English):** 13,497 rows (**98.25%**)
  - **No Alphabetic Characters (Punctuation):** 232 rows (**1.69%**)
  - **Mixed Script:** 9 rows (**0.07%**)
- **Length Analysis:**
  | Field | Min Chars | Median Chars | Mean Chars | 95th % Chars | Max Chars | Min Tokens | Median Tokens | Mean Tokens | 95th % Tokens | Max Tokens |
  | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
  | **Source** | 3 | 70.0 | 76.58 | 141.0 | 274 | 1 | 12.0 | 13.28 | 27.0 | 40 |
  | **Target** | 1 | 67.0 | 73.98 | 142.0 | 278 | 1 | 11.0 | 12.31 | 25.0 | 46 |

### 2.5 License and Provenance Review
- **Publisher:** Lingo Research Group at IIT Gandhinagar.
- **Declared License:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Translation Provenance:** `human_translated` (manually translated by 54 human annotators).
- **Redistribution & Research Fine-Tuning:** Permitted under CC BY 4.0 with attribution.
- **Inclusion Status:** `PRIMARY_CANDIDATE_PENDING_AUDIT`.

---

## 3. SOURCE B — COMI-LINGUA MT (MACHINE TRANSLATION)

### 3.1 Acquisition and Integrity
- **Official Hugging Face Hub:** [LingoIITGN/COMI-LINGUA](https://huggingface.co/datasets/LingoIITGN/COMI-LINGUA)
- **Candidate Files Downloaded:**
  - `MT_train.csv`: 60,989,602 bytes (58.16 MB) | SHA-256: `9a9bf88ced2cd94925549cce0b3f361eb4ae1f70b1d4abf9fbeec22deae1a2cc`
  - `MT_test.csv`: 11,592,610 bytes (11.06 MB) | SHA-256: `4160eb08b8db47fcc8925791c523746a73ea645b4b6c2f04f1fc0593f9e3c3e8`
- **Research Citation:** Sheth et al., *"COMI-LINGUA: Expert Annotated Large-Scale Dataset for Multitask NLP in Hindi-English Code-Mixing"*, EMNLP 2025 Findings ([ACL Anthology: 2025.findings-emnlp.422](https://aclanthology.org/2025.findings-emnlp.422/))
- **Local Storage Path:** `data/raw/translation/comi_lingua_mt/`
- **File Signatures:** Both verified genuine CSV format.

### 3.2 Schema and Multi-Annotator Architecture
Header length: 13 columns.
1. `Sentences`: Code-mixed input sentence.
2. `Predicted_en_translation`: Model prediction from `meta-llama/Llama-3.3-70B-Instruct`.
3. `Predicted_RH_translation`: Llama 3.3 Romanized Hindi prediction.
4. `Predicted_DH_translation`: Llama 3.3 Devanagari Hindi prediction.
5. `Annotator_1_en_translation`: Annotator 1 refined English translation.
6. `Annotator_1_RH_translation`: Annotator 1 refined Romanized Hindi translation.
7. `Annotator_1_DH_translation`: Annotator 1 refined Devanagari Hindi translation.
8. `Annotator_2_en_translation`: Annotator 2 refined English translation.
9. `annotator2_RH_translation`: Annotator 2 refined Romanized Hindi translation.
10. `Annotator_2_DH_translation`: Annotator 2 refined Devanagari Hindi translation.
11. `Annotator_3_en_translation`: Annotator 3 refined English translation.
12. `annotator3_RH_translation`: Annotator 3 refined Romanized Hindi translation.
13. `Annotator_3_DH_translation`: Annotator 3 refined Devanagari Hindi translation.

### 3.3 Forensic Provenance Audit (Llama 3.3 vs Annotator Agreement)
To evaluate the true provenance of COMI-LINGUA MT translations, an agreement audit was run comparing the raw LLM draft (`Predicted_en_translation`) against the three annotator columns:

| Split | Total Rows | Predicted == Annotator 1 | Predicted == Annotator 2 | Predicted == Annotator 3 | All 3 Annotators Identical | All 4 Identical (Predicted + Annotators) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MT_train.csv** | 24,692 | 24,659 (99.87%) | 24,607 (99.66%) | 24,404 (98.83%) | 24,330 (98.53%) | **24,327 (98.52%)** |
| **MT_test.csv** | 5,000 | 4,988 (99.76%) | 4,984 (99.68%) | 4,901 (98.02%) | 4,892 (97.84%) | **4,890 (97.80%)** |

> [!IMPORTANT]
> **Forensic Finding — Provenance Classification:**
> In **98.52% of training rows** and **97.80% of test rows**, all three annotators accepted the Llama 3.3 translation without altering a single character. Only ~1.5% of rows underwent active human correction. Therefore, under rigorous scientific ethics, this dataset **must be designated as `human_corrected_machine_draft`**. It must never be represented as independent human reference data.

### 3.4 Row Counts, Integrity, and Script Analysis
- **Train Row Count:** 24,692 rows (0 missing, 0 empty, 0 duplicate source sentences, 0 conflicting targets).
- **Test Row Count:** 5,000 rows (0 missing, 0 empty, 0 duplicate source sentences, 0 conflicting targets).
- **Input Script Distribution:**
  - `MT_train.csv`: Mixed script (Devanagari letters + Latin letters): **21,527 (87.18%)**; Devanagari only: **3,165 (12.82%)**; Latin only: **0 (0.00%)**.
  - `MT_test.csv`: Mixed script: **5,000 (100.00%)**.
- **Target Script Distribution:** Over 99.94% Latin script (English) in both train and test; 0 punctuation-only targets.
- **Length Statistics:**
  - Train Source: Chars (mean: 121.23, median: 119.0, max: 485); Tokens (mean: 21.91, median: 22.0, max: 71).
  - Train Target: Chars (mean: 119.18, median: 116.0, max: 475); Tokens (mean: 19.34, median: 19.0, max: 64).
  - Test Source: Chars (mean: 118.26, median: 119.0, max: 206); Tokens (mean: 21.21, median: 21.0, max: 32).
  - Test Target: Chars (mean: 110.80, median: 109.0, max: 264); Tokens (mean: 18.22, median: 18.0, max: 38).
- **Official Split Preservation:** `MT_train.csv` and `MT_test.csv` are strictly maintained in isolation.
- **Inclusion Status:** `PENDING_PROVENANCE_REVIEW`.

---

## 4. SOURCE C — TELUGU-ENGLISH CODE-MIXED TRANSLATION RESEARCH

A central objective was investigating candidate parallel corpora for Telugu-English code-mixed translation.

### 4.1 C1 — ReDial-Indic Investigation
- **Repository:** `https://github.com/darshna001/ReDial-Indic`
- **Resource Examined:** Multilingual conversational recommendation dataset for Gujarati-English, Hindi-English, and Telugu-English (derived from the English ReDial movie recommendation dataset; Li et al., NeurIPS 2018).
- **Telugu-English Statistics:** 8,464 train dialogues, 1,000 validation dialogues, 542 test dialogues (181,984 total utterances).
- **Forensic Findings:**
  1. **Licensing Blocker:** An inspection of the repository root confirmed that **no LICENSE file exists** (`HTTP 404` on `https://raw.githubusercontent.com/darshna001/ReDial-Indic/main/LICENSE`). Under copyright law, an unlicensed public GitHub repository is "All Rights Reserved" with no legal redistribution or derivation grant.
  2. **Translation Provenance:** Utterances were produced by passing English dialogues through automated translation models (**Helsinki-NLP, mBART, and NLLB**) followed by entity placeholder insertion (`placeholder replacements: 64,461`). They are synthetic MT outputs, not naturally occurring code-mixing.
  3. **Task Mismatch:** The data consists of multi-turn conversational movie recommendation dialogue turns where sentences depend on movie-mention context, not standalone general sentence translation.
- **Status:** **`QUARANTINED_PENDING_LICENSE_REVIEW` (Excluded from acquisition/training).**

### 4.2 C2 — Sravani & Mamidi (CoNLL 2023) Investigation
- **Paper:** *"Enhancing Code-mixed Text Generation Using Synthetic Data Filtering in Neural Machine Translation"*, Dama Sravani and Radhika Mamidi, CoNLL 2023 ([ACL Anthology: 2023.conll-1.15](https://aclanthology.org/2023.conll-1.15/))
- **Forensic Findings:**
  1. **Task Direction:** The paper's core task is English-to-Code-Mixed generation (the reverse of our task), training models to synthesize code-mixed text from monolingual English.
  2. **Data Generation:** It employs rule-based and linguistic matrices to synthesize code-mixed sentences from parallel English-Indic corpora, which are then passed through human-judgement-trained classifier filters to yield a "three-way silver parallel corpus".
  3. **Data Availability:** No publicly downloadable Hugging Face or GitHub repository with an open license is released.
  4. **Policy Constraint:** Project guidelines strictly forbid generating or relying on synthetic training data.
- **Status:** **`RELATED_WORK_ONLY_PENDING_DATA_AND_LICENSE_VERIFICATION` (Not acquired).**

### 4.3 C3 — Targeted Search for Additional Telugu-English Candidates
A comprehensive scan of Hugging Face datasets and NLP literature was conducted:
- Datasets tagged `telugu english translation` on Hugging Face (e.g. `Lots-of-LoRAs/pib_translation`, `AI4Bharat`, `prudhvirajdowluri`) are standard **monolingual English to standard Telugu** (e.g., formal government press releases), containing zero code-mixed sentences.
- Datasets tagged `tenglish` (e.g., `indiehackers/tenglish_dataset`, `CulturaX_tenglish_split`) are transliterated monolingual web texts without parallel English reference translations.
- DravidianLangTech (EACL) shared task datasets contain code-mixed Telugu-English social media comments, but they are annotated exclusively for classification tasks (sentiment analysis, offensive language detection) and have no parallel English translations.
- Local V1 raw data (`data/raw/telugu_english/source/Blog Dataset`, `Twitter Dataset`) contains token-level LID tags only.

### 4.4 Definitive Telugu-English Research Finding
> **Official Finding:**  
> **"No verified Telugu-English code-mixed-to-English training source established in this step."**  
> This absence is a legitimate empirical research finding. High-quality, naturally occurring Telugu-English parallel translation data with open licensing does not exist in open NLP repositories. Claiming trilingual translation in V2 would be dishonest; the project will focus its translation engine on Hindi-English (Romanized and Devanagari) while documenting the Telugu gap as an open research challenge.

---

## 5. OTHER REFERENCE RESOURCES AUDIT

### 5.1 Source D — Samanantar and MultiIndicMT
- **Samanantar (`ai4bharat/samanantar`):**
  - Largest Indic parallel corpus (49.7M pairs across 11 languages; 12.3M En-Hi, 5.3M En-Te).
  - License: `CC BY-NC 4.0` (Non-commercial clause).
  - Nature: Monolingual Indic to English parallel data (formal news/web). Does not contain natural code-mixing.
  - Classification: `AUXILIARY_REFERENCE_NOT_ACQUIRED`.
- **MultiIndicMT (WAT Indic Multilingual Shared Task):**
  - Monolingual benchmark for Indic machine translation.
  - Classification: `AUXILIARY_REFERENCE_NOT_ACQUIRED`.

### 5.2 Source E — Trilingual Hinglish Corpus
- **Repository:** [debajyotimaz/trilingual-hinglish-corpus](https://huggingface.co/datasets/debajyotimaz/trilingual-hinglish-corpus)
- **Content:** 21,139 triples (English, Hindi Devanagari, Romanized Hinglish).
- **License:** **`CC BY-NC-SA 4.0`** (Non-commercial, Share-Alike).
- **Audit Findings:**
  1. The corpus explicitly derives from PHINC as one of its base components.
  2. The `NC-SA` restriction would legally contaminate our downstream release and fine-tuned model weights.
  3. Machine-checked translations are mixed with human translations.
- **Classification:** **`CONDITIONAL_REFERENCE_NOT_ACQUIRED` (Excluded).**

---

## 6. CROSS-SOURCE DUPLICATE AND LEAKAGE AUDIT

A bidirectional duplication and leakage audit was performed across all acquired candidate splits using both exact match and conservative normalization (Unicode NFC, whitespace stripping, consecutive whitespace collapsing, and Latin lowercasing):

| Comparison Pair | Exact Source Overlap | Normalized Source Overlap | Exact Pair Overlap | Conflicting Targets | Leakage Assessment |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PHINC vs COMI MT_train** | **0** | **0** | **0** | 0 | **Clean (Disjoint)** |
| **PHINC vs COMI MT_test** | **0** | **0** | **0** | 0 | **Clean (Disjoint)** |
| **COMI MT_train vs COMI MT_test** | **0** | **0** | **0** | 0 | **Clean (Zero Test Leakage)** |

### Analysis:
- PHINC and COMI-LINGUA MT share **0 overlapping source sentences**. They represent entirely separate data collection efforts (PHINC is Twitter social media in Romanized Latin script; COMI-LINGUA is predominantly mixed Devanagari script).
- COMI-LINGUA `MT_train.csv` and `MT_test.csv` share **0 overlapping sentences**, verifying that the publisher's official split separation is strictly intact.

---

## 7. DATA STORAGE & ARTIFACT REGISTRY

All acquired data and audit reports are cataloged under the following directory hierarchy:

```
data/
└── raw/
    └── translation/
        ├── phinc/
        │   ├── PHINC.csv                 (2,125,039 B | SHA-256: 325ba383...)
        │   ├── README_source.md          (3,105 B | Source dataset card snapshot)
        │   └── source_manifest.json      (Standardized metadata manifest)
        ├── comi_lingua_mt/
        │   ├── MT_train.csv              (60,989,602 B | SHA-256: 9a9bf88c...)
        │   ├── MT_test.csv               (11,592,610 B | SHA-256: 4160eb08...)
        │   ├── README_source.md          (7,267 B | Source dataset card snapshot)
        │   └── source_manifest.json      (Standardized metadata manifest)
        └── translation_source_audit/
            ├── cross_source_overlap_report.json
            ├── source_audit_report.json
            └── source_registry.json
```

All files in `data/raw/` remain outside Git tracking pursuant to the active `.gitignore` rules.

---

## 8. CANDIDATE CLASSIFICATION & INCLUSION STATUS

| Candidate Dataset | Declared License | Provenance Classification | Split Count | Inclusion Status | Readiness Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PHINC** | CC BY 4.0 | `human_translated` | 13,738 | `PRIMARY_CANDIDATE_PENDING_AUDIT` | **Approved for Step 34B processing.** Single split requires filtering 232 invalid targets and partitioning. |
| **COMI-LINGUA MT** | CC BY 4.0 | `human_corrected_machine_draft` | 24,692 train<br>5,000 test | `PENDING_PROVENANCE_REVIEW` | **Approved for Step 34B as secondary/Devanagari corpus.** Must be clearly labeled as LLM-drafted; test split quarantined. |
| **ReDial-Indic** | Unlicensed (404) | `machine_translated` | 181,984 | `QUARANTINED_PENDING_LICENSE_REVIEW` | **Excluded.** No open license, synthetic MT dialogue turns. |
| **Sravani & Mamidi (2023)** | Unpublished | `machine_generated_human_filtered` | N/A | `RELATED_WORK_ONLY_PENDING_DATA_AND_LICENSE_VERIFICATION` | **Excluded.** Synthetic silver data, reverse task direction. |
| **Trilingual Hinglish** | CC BY-NC-SA 4.0 | `mixed` | 21,139 | `CONDITIONAL_REFERENCE_NOT_ACQUIRED` | **Excluded.** License incompatibility (`NC-SA`), PHINC overlap. |
| **Samanantar** | CC BY-NC 4.0 | `parallel_reference` | 49.7M | `AUXILIARY_REFERENCE_NOT_ACQUIRED` | **Excluded.** Monolingual parallel Indic, non-commercial license. |
| **MultiIndicMT** | Evaluation | `parallel_reference` | Benchmark | `AUXILIARY_REFERENCE_NOT_ACQUIRED` | **Excluded.** Monolingual benchmark only. |

---

## 9. TRAINING READINESS ASSESSMENT (mT5-small EXPERIMENT)

1. **Is PHINC alone sufficient for an initial Hinglish-English baseline?**
   - **Yes.** PHINC provides 13,506 usable sentence pairs (after removing the 232 punctuation-only targets). With an 80/10/10 split (~10,800 train, ~1,350 val, ~1,350 test), this offers ample density for fine-tuning `google/mt5-small` on Romanized Hinglish-to-English translation.
2. **Is COMI-LINGUA MT suitable for additional experiments?**
   - **Yes, with explicit provenance caveats.** COMI-LINGUA MT provides 24,692 train pairs that expand coverage to Devanagari script code-mixing. However, because 98.52% of its targets are verbatim Llama 3.3 outputs, it must be evaluated separately or trained with clear ablation tracking against the pure human PHINC baseline. The official 5,000-example `MT_test.csv` split must be strictly quarantined from training.
3. **Is verified Telugu-English code-mixed translation data available?**
   - **No.** Verified naturally occurring Telugu-English code-mixed translation corpora do not exist in the open research domain.
4. **Can we honestly claim trilingual Hindi-Telugu-English translation?**
   - **No.** The model can honestly be described as a **Multimodal Code-Mixed Hindi-English Translation model** (covering both Romanized Latin and Devanagari scripts). The Telugu translation component remains an open research gap.
5. **Remaining Data Gaps:**
   - Naturally occurring Telugu-English (Tenglish) sentence-level parallel translation data.
   - Gold human-authored translations for Devanagari-script code-mixing (to contrast with COMI-LINGUA's LLM drafts).

---

## 10. PROJECT INTEGRITY & V1 PROTECTION CONFIRMATION

In strict adherence to project safety rules:
- [x] **MuRIL LID baseline model files (`artifacts/models/muril_lid_baseline/`) are UNTOUCHED.**
- [x] **MuRIL locked evaluation artifacts (`artifacts/evaluation/muril_lid_baseline/`) are UNTOUCHED.**
- [x] **Existing LID processed datasets (`data/processed/language_identification/`) are UNTOUCHED.**
- [x] **FastAPI backend (`backend/`) and Vanilla JS frontend (`frontend/`) are UNTOUCHED.**
- [x] **Git tag `v1.0.0` points unchanged to commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`.**
- [x] **No model fine-tuning or inference occurred.**
- [x] **No final translation train/val/test splits were constructed.**
- [x] **No Git commits were generated.**
- [x] **No remote Git push occurred.**

---

## 11. FINAL STOP CONDITION & NEXT STEPS

Execution has halted per Step 34A instructions. No files have been committed, and no splits have been finalized.

### Next Step:
**Step 34B — Select Eligible Datasets, Normalize Sentence-Pair Schema, and Prepare Leakage-Safe Consolidation:**
1. Filter the 232 invalid punctuation targets and 1 duplicate pair from PHINC.
2. Establish a leakage-safe 80/10/10 train/validation/test split for PHINC.
3. Define the experimental policy for COMI-LINGUA MT (as a standalone Devanagari track or secondary ablation).
4. Construct consolidated, normalized JSONL translation datasets (`source_text`, `target_text`, `source_dataset`, `script_type`, `provenance`).
