# Step 26: Implement Provenance-Aware Custom Dataset Schema

**Project:** CodeMix Intelligence  
**Directory:** [C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence)  
**Schema Version:** `1.2.0`  
**Manifest Version:** `1.2.0`  
**Validation Status:** **PASS (All 22/22 Self-Tests Passed | Zero Hard Errors | Integrity Verified)**  

---

## Executive Summary

Step 26 implemented the Step 25C approved provenance architecture across the CodeMix Intelligence custom dataset infrastructure. This infrastructure upgrade establishes:
1. A **Draft-07 JSON Schema** ([`data/custom/trilingual_lid/dataset_schema.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/dataset_schema.json)) with canonical top-level `source_record_id`, standardized `license` spelling, explicit source rights, contributor consent, review audit trail, and language statistics.
2. A **Provenance Taxonomy** defining four eligible collection methods (`licensed_corpus_extraction`, `naturally_occurring`, `human_elicited`, `parallel_reference`), and strictly prohibiting `automatically_generated` AI text from ground-truth data.
3. **Conditional Validation Logic** in [`scripts/validate_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) enforcing method-specific constraints, review barriers, and independent recalculation of evaluation statistics.
4. An expanded **22-test automated self-test suite** covering all Step 26 specification requirements with 100% pass rate.
5. Verification that all custom dataset JSONL files remain strictly empty (0 records / 0 bytes), the split script was not executed, and the original unified LID benchmark remains completely untouched.

---

## 1. Updated Schema Structure (v1.2.0)

The updated schema ([`dataset_schema.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/dataset_schema.json)) standardizes canonical fields and embeds comprehensive provenance:

### 1.1 Canonical Top-Level Field
- **`source_record_id`**:
  - Maintained as the sole canonical identifier.
  - Allows `string` or `null`.
  - `null` is canonical for direct human elicitation (`human_elicited`).
  - Required and non-null for public corpus extraction (`licensed_corpus_extraction`) and parallel reference anchoring (`parallel_reference`).
  - Not duplicated inside `metadata`.

### 1.2 Standardized Metadata Fields
- **Source Rights**:
  - `metadata.source_dataset`: Originating corpus or reference dataset name (`string` or `null`).
  - `metadata.source_url`: Public URI link to dataset card or repository (`string` or `null`).
  - `metadata.license`: Canonical spelling `license` tracking SPDX identifier or agreement (`string` or `null`).
  - `metadata.license_url`: Canonical URL to legal license terms (`string` or `null`).
- **Collection Context**:
  - `metadata.collection_method`: Enum `["licensed_corpus_extraction", "naturally_occurring", "human_elicited", "parallel_reference"]`.
  - `metadata.source_group_id`: Identifier for literary work, document, or author session to enforce group-aware splitting.
  - `metadata.source_domain`: Communicative domain (`string` or `null`).
  - `metadata.script_combination`: Script taxonomy combination (`string` or `null`).
- **Contributor and Consent**:
  - `metadata.contributor_id`: Pseudonymous author identifier matching regex `^contrib_[0-9]{2,}$` (`null` for public corpus extraction).
  - `metadata.consent_status`: Enum `["consented_academic_use", "not_applicable_public_corpus", "platform_terms_compliant", "pending_consent", null]`.
- **Annotation Review**:
  - `metadata.annotator_1`: Pseudonymous identifier for primary reviewer (`string` or `null`).
  - `metadata.annotator_2`: Pseudonymous identifier for secondary reviewer (`string` or `null`).
  - `metadata.annotation_status`: Lifecycle status enum `["candidate", "stage1_approved", "stage2_approved", "adjudicated", "rejected"]`.
  - `metadata.review_date`: ISO-8601 review approval date (`YYYY-MM-DD` or `null`).
- **LID and Evaluation Statistics**:
  - `metadata.language_switch_count`: Non-negative integer count of intra-sentential transitions between language-bearing tokens.
  - `metadata.language_token_counts`: Object with exact non-negative integer counts for `EN`, `HI`, `TE`, `OTHER`, `NE`, `MIXED`.

### 1.3 Supervised Model Labels Preserved
The model strictly maintains **four supervised classes**:
$$\text{EN} = 0, \quad \text{HI} = 1, \quad \text{TE} = 2, \quad \text{OTHER} = 3$$
`MIXED` and `NE` are provenance annotations only and always map to `-100`:
$$\text{MIXED} = -100, \quad \text{NE} = -100, \quad \text{AMBIGUOUS} = -100, \quad \text{null} = -100$$
No fifth model class has been introduced.

---

## 2. Provenance Taxonomy & Method Definitions

Every record submitted to CodeMix Intelligence must declare one of four mutually exclusive collection methods:

| Method Code | Definition | `source_record_id` | `contributor_id` | `consent_status` | `source_dataset` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`licensed_corpus_extraction`** | Sentence selected directly from an existing licensed corpus (e.g., BHT25 native Telugu). Originating record ID, document source, and license preserved. Requires 100% human review. | Non-null string | **Must be `null`** | `"not_applicable_public_corpus"` | Required (e.g. `"BHT25"`) |
| **`naturally_occurring`** | Authentic utterance collected from organic discourse with documented permission and platform compliance. | Optional | Pseudonymous or null | `"platform_terms_compliant"` | Required |
| **`human_elicited`** | Original sentence intentionally authored by a multilingual contributor in response to a communication scenario. | **Must be `null`** | **Required** (pseudonym) | `"consented_academic_use"` | `null` |
| **`parallel_reference`** | Human-authored code-mixed sentence composed by a contributor using parallel text as a semantic reference. Preserves reference source and attribution. | Required (ref ID) | **Required** (author pseudonym) | `"consented_academic_use"` | Required (ref dataset) |
| **`automatically_generated`** | Synthetic text generated by AI/LLMs. **Strictly prohibited from ground truth.** | — | — | — | — |

> [!IMPORTANT]
> **Distinction:** Raw public corpus extraction (`licensed_corpus_extraction`) must never be confused with or classified as human elicitation. Parallel text must never be automatically concatenated.

---

## 3. Conditional Validation Rules

[`scripts/validate_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) implements the following conditional rules:

1. **For `licensed_corpus_extraction`**:
   - `metadata.source_dataset` is required (non-empty string).
   - Top-level `source_record_id` is required and non-null.
   - `metadata.license` is required (non-empty string).
   - `metadata.source_url` is required (non-empty string).
   - `metadata.contributor_id` must be `null` (public corpus records do not have individual contributor consent).
   - `metadata.consent_status` must be `"not_applicable_public_corpus"`.
   - Missing `source_group_id` records a split-readiness warning.
2. **For `naturally_occurring`**:
   - `metadata.source_url` or documented `metadata.source_dataset` required.
   - Verified permission/platform-compliance evidence required in `consent_status`.
   - Contributor ID may be pseudonymous or null.
3. **For `human_elicited`**:
   - `metadata.contributor_id` is required and must match pseudonymous regex (`^contrib_[0-9]{2,}$`).
   - Top-level `source_record_id` must be `null`.
   - Contributor consent must be recorded (`consent_status: "consented_academic_use"`).
   - Contributor agreed rights must be recorded in `metadata.license`.
4. **For `parallel_reference`**:
   - Human contributor author required (`metadata.contributor_id` non-null pseudonym).
   - Contributor consent required (`consent_status`).
   - Reference dataset and reference record ID required (`source_dataset`, `source_record_id`).
   - Reference source license and attribution preserved in `metadata.license`.
5. **Reviewed Data Barriers (`reviewed_sentences.jsonl` or status `stage2_approved`/`adjudicated`)**:
   - Both reviewer IDs required (`metadata.annotator_1`, `metadata.annotator_2`).
   - Review date required (`metadata.review_date` matching `YYYY-MM-DD`).
   - Unverified or pending rights (`license: "pending"` or `"unclear"`) strictly rejected.
   - Pending consent (`consent_status: "pending"` or `"pending_consent"`) strictly rejected.
   - Unreviewed candidate records strictly blocked from entering reviewed data.
6. **Non-Commercial Legal Notice**:
   - Documentation and validator confirm that academic status does not automatically prove non-commercial use under CC licenses; institutional review is required prior to external distribution.

---

## 4. BHT25 Source Grouping Investigation Finding

As required by Task 4, an investigation of the 27,149-row BHT25 corpus ([`sudeshna84/BHT25`](https://huggingface.co/datasets/sudeshna84/BHT25)) was conducted:

| Investigation Aspect | Finding |
| :--- | :--- |
| **Exposed Fields in Parquet Files** | Only `id`, `bn`, `hi`, `te`. |
| **Work / Book Identifiers in Records** | **Absent.** Individual rows do not carry book title, author, or literary work identifiers. |
| **Chapter / Boundary Delimiters** | **Absent.** Rows are indexed sequentially from 1 to 27,149 without document boundaries. |
| **Literature Identified in Research Paper** | Sani et al. (*Data in Brief* 2026) state the corpus draws from literary works of Rabindranath Tagore and Sarat Chandra Chattopadhyay translated into Hindi and Telugu. |
| **Record-Level Traceability** | Individual sentences cannot be traced reliably to specific works from the public dataset fields alone without manual full-text alignment against the source novels. |
| **Investigation Result** | **BHT25 document-level grouping remains UNRESOLVED in the raw corpus.** Claiming a leakage-free document-group split without source information is barred. |
| **Split Script Enforcement** | [`scripts/split_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/split_custom_trilingual_dataset.py) has been updated to **refuse to assign final splits to records without a valid `source_group_id`** unless an explicit approved grouping exception is documented. |

---

## 5. Language Statistics Calculation Rules

`metadata.language_token_counts` and `metadata.language_switch_count` are defined and independently verified as follows:

### 5.1 `language_token_counts`
- An exact dictionary tallying source annotation labels across all six permitted tags:
  ```json
  {
    "EN": 0,
    "HI": 0,
    "TE": 0,
    "OTHER": 0,
    "NE": 0,
    "MIXED": 0
  }
  ```
- Non-supervised classes (`MIXED`, `NE`) are counted for linguistic tracking without affecting model labels.

### 5.2 `language_switch_count`
- **Algorithm**:
  1. Traverse the sentence tokens in their original sequential order.
  2. Filter for language-bearing classes: only tokens tagged with `{"EN", "HI", "TE"}` participate.
  3. Tokens tagged with `OTHER`, `NE`, `MIXED`, `AMBIGUOUS`, or `null` are **strictly ignored**.
  4. Compare each language-bearing token to the immediately preceding language-bearing token.
  5. Increment `language_switch_count` by 1 whenever `current_lang != previous_lang`.
- **Validation**:
  - The dataset validator independently recomputes both statistics from `source_labels` and errors on any discrepancy.

---

## 6. Validator Self-Test Suite Results (22/22 Tests Passed)

Running `.venv\Scripts\python.exe scripts/validate_custom_trilingual_dataset.py --self-test` executed all 22 specified tests on isolated synthetic fixtures:

```text
===========================================================================
RUNNING VALIDATOR SELF-TEST SUITE (STEP 26 SPECIFICATION - 22 TESTS)
===========================================================================
  [PASS] Test 1: Valid licensed_corpus_extraction record accepted.
  [PASS] Test 2: Missing license rejected for corpus extraction.
  [PASS] Test 3: Missing source_record_id rejected for corpus extraction.
  [PASS] Test 4: Missing source_group_id flags split readiness warning.
  [PASS] Test 5: Valid human_elicited record accepted.
  [PASS] Test 6: Missing contributor ID rejected for human elicitation.
  [PASS] Test 7: Missing consent rejected for human elicitation.
  [PASS] Test 8: Valid parallel_reference record accepted.
  [PASS] Test 9: Missing reference record ID rejected for parallel reference.
  [PASS] Test 10: Automatically generated record strictly rejected.
  [PASS] Test 11: Duplicate source_record_id detection validated.
  [PASS] Test 12: Null source_record_id accepted for direct human elicitation.
  [PASS] Test 13: Supervised EN/HI/TE/OTHER mapping confirmed unchanged.
  [PASS] Test 14: MIXED strictly cannot receive any supervised class ID (0, 1, 2, 3).
  [PASS] Test 15: NE confirmed ignored (-100).
  [PASS] Test 16: Language token counts independently recalculated & verified.
  [PASS] Test 17: Language switch count independently recalculated & verified.
  [PASS] Test 18: Both reviewers strictly required for stage2_approved.
  [PASS] Test 19: Reviewers and review_date strictly required for adjudicated records.
  [PASS] Test 20: Existing Telugu and Devanagari script validation confirmed active.
  [PASS] Test 21: Duplicate normalized sentence detection confirmed active.
  [PASS] Test 22: 60/20/20 target allocation (240/80/80, seed=42) confirmed unchanged.

===========================================================================
SELF-TEST SUITE RESULT: ALL 22/22 SPECIFIED CASES PASSED!
===========================================================================
```

---

## 7. Dataset Manifest Update (v1.2.0)

[`data/custom/trilingual_lid/dataset_manifest.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/dataset_manifest.json) has been updated to version `1.2.0`:
- **Schema Version**: `1.2.0`.
- **Provenance Architecture**: Records eligible collection methods, canonical field conventions, metadata categories, and language statistics policies.
- **Split Policy**: Reaffirms group-aware stratified 60/20/20 allocation across 400 target sentences with seed 42.
- **Current Counts Preserved**:
  - `candidate_sentences`: 0
  - `reviewed_sentences`: 0
  - `rejected_sentences`: 0
  - `total_tokens_reviewed`: 0

---

## 8. Explicit File Integrity Verification (PASS)

The workspace was verified for strict isolation and integrity:

| Target File / Resource | Verification Status | Details |
| :--- | :---: | :--- |
| `candidate_sentences.jsonl` | **PASS (0 bytes)** | Exactly 0 records; SHA256: `e3b0c44298fc1c14...` |
| `reviewed_sentences.jsonl` | **PASS (0 bytes)** | Exactly 0 records; SHA256: `e3b0c44298fc1c14...` |
| `rejected_sentences.jsonl` | **PASS (0 bytes)** | Exactly 0 records; SHA256: `e3b0c44298fc1c14...` |
| `dataset_schema.json` | **PASS (Valid)** | Updated to Draft-07 v1.2.0 with provenance fields |
| `dataset_manifest.json` | **PASS (Valid)** | Updated to v1.2.0 with provenance architecture |
| `examples/schema_example.json` | **PASS (Valid)** | Updated with Step 26 fields; strictly isolated from datasets |
| `data/custom/trilingual_lid/splits/` | **PASS (Not executed)** | Directory does not exist; split script was not executed |
| `data/processed/language_identification/*` | **PASS (Untouched)** | All 9 original unified LID files untouched |
| Model Training Processes | **PASS (None)** | Zero training runs initiated |

---

## 9. Remaining Blockers for Data Collection

With Step 26 complete, the schema, validator, split script, and documentation are fully aligned. Before beginning full data collection in Step 27:

1. **Empirical Pilot Execution**: Author a 10-sentence pilot per category (40 sentences total) across 3 contributors to calculate empirical acceptance rates ($A_{\text{pilot}} = N_{\text{approved}} / N_{\text{drafted}}$) before setting drafting quotas.
2. **BHT25 Category A Grouping Resolution**: Sourcing Category A native Telugu sentences from BHT25 requires manually attributing the selected sentences to specific literary works (Tagore / Chattopadhyay) so that a valid `source_group_id` can be assigned prior to splitting.
3. **Institutional Review**: Submit the contributor consent form and provenance metadata blueprint to faculty/institutional research review prior to public release.
