# Step 28: Statistics Schema v1.3 and Pilot Governance Finalization Report

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 28 — Infrastructure & Documentation Governance Finalization  
**Workspace:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**Timestamp:** `2026-10-31T18:45:00+05:30`  
**Schema Version:** `1.3.0`  
**Manifest Version:** `1.3.0`  
**Status:** **INFRASTRUCTURE & GOVERNANCE CORRECTIONS COMPLETE (READY FOR FACULTY REVIEW)**  

---

## Executive Summary

Step 28 successfully resolves the statistics accounting, contributor consent, participant distribution, reviewer independence, and split grouping issues identified during the Step 27 pilot review. 

All modifications in this step are **infrastructure, validation code, and documentation corrections only**. In strict adherence to project directives:
- Zero sentences were generated or fabricated.
- No contributors were recruited, invited, or contacted.
- No consent forms were collected.
- All custom dataset JSONL files ([`candidate_sentences.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/candidate_sentences.jsonl), [`reviewed_sentences.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/reviewed_sentences.jsonl), [`rejected_sentences.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/rejected_sentences.jsonl)) remain strictly empty ($0$ records, $0$ bytes).
- All pilot tracking templates remain completely blank.
- The original unified benchmark datasets in `data/processed/language_identification/` remain 100% byte-identical and untouched.
- No machine learning model training or final splitting script execution occurred.

---

## 1. Schema Version Upgrade (v1.2.0 $\rightarrow$ v1.3.0)

The custom trilingual dataset schema has been upgraded from `v1.2.0` to **`v1.3.0`** across all specifications and manifests:
- **Schema Definition:** [`dataset_schema.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/dataset_schema.json) reflects schema version `1.3.0` with explicit 8-key required object properties.
- **Dataset Manifest:** [`dataset_manifest.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/dataset_manifest.json) reflects version `1.3.0` and schema version `1.3.0`.
- **Schema Example:** [`examples/schema_example.json`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/examples/schema_example.json) has been updated to include all 8 required count keys and validates cleanly in isolation.
- **Documentation Alignment:** [`README.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/README.md), [`annotation_guidelines.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/annotation_guidelines.md), [`label_reference.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/label_reference.md), and [`pilot/README.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/README.md) consistently reflect `v1.3.0`.

---

## 2. Eight-Key Language Statistics Design

In schema `v1.2.0`, `metadata.language_token_counts` tracked only 6 keys (`EN`, `HI`, `TE`, `OTHER`, `NE`, `MIXED`), which caused records containing `AMBIGUOUS` or JSON `null` source annotations to have $\sum \text{counts} < \text{len}(\text{tokens})$.

Schema `v1.3.0` establishes a mathematically complete, closed **8-key language token accounting structure**:

```json
"language_token_counts": {
  "EN": 0,
  "HI": 0,
  "TE": 0,
  "OTHER": 0,
  "NE": 0,
  "MIXED": 0,
  "AMBIGUOUS": 0,
  "NULL": 0
}
```

### Governing Rules & Accounting Principles:
1. **Exact One-to-One Accounting:** Every token in `tokens` must contribute to exactly one count key in `language_token_counts`.
2. **JSON Null Accounting:** Tokens with JSON `null` source labels strictly increment `NULL`.
3. **Ambiguous Accounting:** Tokens with `"AMBIGUOUS"` source labels strictly increment `AMBIGUOUS`.
4. **Provenance Isolation:**
   - `MIXED` and `NE` must never be classified or counted as `OTHER`.
   - `AMBIGUOUS` and `NULL` must never be classified or counted as `OTHER`.
5. **Total Count Parity:** The sum of all 8 count keys must strictly equal the exact token count:
   $$\sum_{k \in \{\text{EN, HI, TE, OTHER, NE, MIXED, AMBIGUOUS, NULL}\}} \text{language\_token\_counts}[k] \equiv \text{len}(\text{tokens})$$
6. **No Silent Zero Defaulting:** Missing count keys are strictly rejected; the validator and schema do not allow keys to be omitted or silently assumed zero.
7. **Strict Model Class Boundaries:** No new supervised model classes are introduced.
   - **Supervised Classes (4):** `EN = 0`, `HI = 1`, `TE = 2`, `OTHER = 3`.
   - **Provenance Ignored Annotations (-100):** `NE = -100`, `MIXED = -100`, `AMBIGUOUS = -100`, `null = -100`.
   - `AMBIGUOUS` and `NULL` cannot receive a supervised class ID (`0, 1, 2, 3`).
8. **Language-Switch Count Policy:** `language_switch_count` strictly evaluates intra-sentential transitions between language-bearing tokens (`EN`, `HI`, `TE`), completely ignoring `OTHER`, `NE`, `MIXED`, `AMBIGUOUS`, and `null`.

---

## 3. Validator Test Suite Results (30 / 30 Tests Passed)

The custom validator [`scripts/validate_custom_trilingual_dataset.py`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) was upgraded from 22 unit tests to **30 comprehensive synthetic tests**.

Execution command:
```powershell
.venv\Scripts\python.exe scripts/validate_custom_trilingual_dataset.py --self-test
```

### Self-Test Results Summary:
```text
===========================================================================
RUNNING VALIDATOR SELF-TEST SUITE (STEP 28 SPECIFICATION - 30 TESTS)
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
  [PASS] Test 23: AMBIGUOUS token counted correctly under AMBIGUOUS key.
  [PASS] Test 24: JSON null token counted under NULL key.
  [PASS] Test 25: Eight count keys sum exactly to token count.
  [PASS] Test 26: Incorrect total count rejected.
  [PASS] Test 27: Missing count keys strictly rejected for schema v1.3.0.
  [PASS] Test 28: AMBIGUOUS strictly cannot receive any supervised class ID (0, 1, 2, 3).
  [PASS] Test 29: NULL strictly cannot receive any supervised class ID (0, 1, 2, 3).
  [PASS] Test 30: Language-switch count ignores AMBIGUOUS and NULL tokens.

===========================================================================
SELF-TEST SUITE RESULT: ALL 30/30 SPECIFIED CASES PASSED!
===========================================================================
```

### Production Validation Execution:
```powershell
.venv\Scripts\python.exe scripts/validate_custom_trilingual_dataset.py
```
Output:
```text
===========================================================================
VALIDATING CUSTOM TRILINGUAL DATASET INFRASTRUCTURE (STEP 28)
Target Directory: C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\data\custom\trilingual_lid
===========================================================================

[PASS] candidate_sentences.jsonl: 0 records | Errors: 0 | Warnings: 0
[PASS] reviewed_sentences.jsonl: 0 records | Errors: 0 | Warnings: 0
[PASS] rejected_sentences.jsonl: 0 records | Errors: 0 | Warnings: 0

Validating illustrative dummy schema example (examples/schema_example.json)...
  Schema Example Status: PASS | Errors: 0 | Warnings: 0

Validating dataset_manifest.json...
  Manifest Status: PASS | Errors: 0

Checking presence of documentation & infrastructure files...
  [FOUND] README.md                  (13,287 bytes)
  [FOUND] split_policy.md            (8,173 bytes)
  [FOUND] annotation_guidelines.md   (24,081 bytes)
  [FOUND] label_reference.md         (12,812 bytes)
  [FOUND] dataset_schema.json        (9,709 bytes)
  [FOUND] annotation_template.csv    (1,174 bytes)
  [FOUND] dataset_manifest.json      (7,062 bytes)

===========================================================================
OVERALL VALIDATION STATUS: PASS
  Hard Errors: 0
  Warnings:    0
  Candidate Records: 0
  Reviewed Records:  0
  Rejected Records:  0
===========================================================================
```

---

## 4. Contributor Consent Document Corrections

In [`draft_consent_form.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/draft_consent_form.md), the legal explanation of Creative Commons licensing was thoroughly revised in alignment with official CC BY 4.0 terms:

1. **Accurate Legal Scope of CC BY 4.0:**
   - CC BY 4.0 grants recipients permission to copy, redistribute, remix, transform, and build upon the material in any medium, **including for commercial purposes**.
   - Mandatory conditions: proper attribution, a link to the license, and notice of changes.
   - The license is **legally irrevocable** for compliant recipients.
   - CC BY 4.0 is **never described as an "academic-only" or "non-commercial-only" license**.
2. **Commercial Reuse Marked PENDING FACULTY REVIEW:**
   - Because the research project is an academic initiative, if the institution intends to restrict commercial reuse (e.g. via CC BY-NC 4.0), that decision is explicitly designated as **`STATUS: PENDING FACULTY REVIEW`**.
   - No alternative license was substituted automatically; faculty and legal counsel sign-off is required.
3. **Withdrawal Boundaries & Practical Realities:**
   - Contributors may withdraw their sentences at any time **prior to dataset freeze**; upon request quoting their pseudonymous contributor ID, submissions are permanently purged from drafts.
   - **Post-Distribution Reality:** After public release under an open license, existing recipients may continue using previously distributed material under license terms. Maintainers will remove records from future official releases upon request, but the project cannot promise complete removal of copies already downloaded across the Internet.
4. **Draft Status Notice:**
   - The document explicitly states it is a preliminary exploratory research draft, not formal legal advice or institutional approval.

---

## 5. Corrected 40-Sentence Participant Distribution

The participant distribution for the empirical pilot has been clarified across [`pilot_protocol.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_protocol.md), [`contributor_guide.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/contributor_guide.md), [`elicitation_scenarios.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/elicitation_scenarios.md), and [`pilot_acceptance_tracker.csv`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_acceptance_tracker.csv):

| Category Key | Category Name | Total Pilot Sentences | Contributor Distribution Model |
| :--- | :--- | :---: | :--- |
| **`Native_Telugu`** | Monolingual Telugu | **10** | Distributed across 3 qualified adult contributors (~3–4 per contributor) |
| **`English_Telugu`** | English + Telugu | **10** | Distributed across 3 qualified adult contributors (~3–4 per contributor) |
| **`Hindi_Telugu`** | Hindi + Telugu | **10** | Distributed across 3 qualified adult contributors (~3–4 per contributor) |
| **`English_Hindi_Telugu`** | English + Hindi + Telugu | **10** | Distributed across 3 qualified adult contributors (~3–4 per contributor) |
| **TOTAL** | — | **40** | **40 sentences total across the entire pilot** |

### Critical Directives:
- **No Multiplicative Misinterpretation:** This must **NOT** be interpreted as 10 examples per contributor per category (which would erroneously generate 120 sentences). The total volume is strictly 40 sentences.
- **Proficiency Gate:** A contributor may author sentences for a category only if they satisfy its specific linguistic proficiency standards (as defined in [`contributor_eligibility.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/contributor_eligibility.md)).
- **No Fabricated Identities:** All contributor IDs (`contrib_01`, `contrib_02`, `contrib_03`) are pseudonyms assigned upon official onboarding; zero real or fabricated identities exist in records.

---

## 6. Group-Separation Policy & Realistic Limitations

In [`split_policy.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/split_policy.md) and [`pilot_protocol.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_protocol.md), claims that assigning `source_group_id` automatically guarantees zero leakage were removed and replaced with sound methodological principles:

1. **Group Identifiers:**
   - Contributor IDs identify human authoring groups (idiolects, stylistic habits).
   - Document/work identifiers identify corpus source groups (passages, chapters).
2. **Leakage Realities:**
   - Merely assigning `source_group_id` does **not** automatically guarantee zero leakage if the collection pool has an insufficient number of independent groups.
   - The split algorithm enforces that groups remain strictly disjoint across Train, Validation, and Test partitions.
   - To achieve disjoint partitions, sufficient independent groups ($\ge 3$ per category) must exist.
3. **Limitation Reporting:**
   - If a category has insufficient independent groups, this structural limitation must be formally reported in documentation.
   - **Never split a single group across partitions** merely to force exact 60/20/20 numerical counts.
4. **Pilot Isolation:**
   - The 40-sentence pilot is exclusively for contributor workflow calibration and review protocol testing—**not for final model evaluation**.
   - Pilot records are **never assigned final train/val/test splits** automatically.
   - The approved 60/20/20 target (240 train / 80 validation / 80 test across 400 sentences, seed 42) remains unchanged for the final dataset release.

---

## 7. Adult Participant and Privacy Safeguards

The following safeguards are codified across all pilot documentation:
- **Adults-Only Mandate:** The pilot and subsequent collections are strictly restricted to adults ($\ge 18$ years of age). Minors are excluded.
- **Pre-Collection Approval:** Written faculty/institutional sign-off is strictly required prior to any recruitment or collection.
- **Separate Secure Consent Storage:** Signed physical or electronic consent forms, if later collected, must be stored in institutionally approved, encrypted, access-controlled storage **completely separate from pseudonymous dataset files**. They must never be colocated with or cross-referenced in public repository files.
- **Data Minimization:** No unnecessary personal information (legal names, phone numbers, email addresses, student roll numbers, or government IDs) is collected.
- **Zero Participant Records:** No participant records were collected or created in this step.

---

## 8. Reviewer Independence Protocol

To prevent confirmation bias, Stage 2 review governance was updated in [`reviewer_instruction_sheet.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/reviewer_instruction_sheet.md) and [`pilot_protocol.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_protocol.md):
- **Strict Blind Initial Annotation:** The Stage 2 reviewer receives the raw tokenized sentence **completely blinded to Stage 1 labels**. Reviewer 2 must produce an initial annotation sequence independently.
- **Post-Annotation Adjudication:** Disagreements between Reviewer 1 and Reviewer 2 are compared and adjudicated only after independent annotation is completed. Unresolved discrepancies are assigned `"AMBIGUOUS"` (`-100`).
- **No Placeholder Pretenses:** Placeholder strings (`annotator_01`, `annotator_02`) represent structural review roles in templates, not real appointed individuals. No real reviewer appointments have been made prior to faculty sign-off.

---

## 9. Comprehensive Integrity Verification

A full workspace audit verified absolute dataset isolation and immutability:

| Component / File | Verification Metric | Status |
| :--- | :--- | :---: |
| [`data/custom/trilingual_lid/candidate_sentences.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/candidate_sentences.jsonl) | Exactly 0 records (0 bytes) | **VERIFIED** |
| [`data/custom/trilingual_lid/reviewed_sentences.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/reviewed_sentences.jsonl) | Exactly 0 records (0 bytes) | **VERIFIED** |
| [`data/custom/trilingual_lid/rejected_sentences.jsonl`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/rejected_sentences.jsonl) | Exactly 0 records (0 bytes) | **VERIFIED** |
| [`data/custom/trilingual_lid/pilot/pilot_acceptance_tracker.csv`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_acceptance_tracker.csv) | Blank tracking template (target notes only) | **VERIFIED** |
| [`data/custom/trilingual_lid/pilot/pilot_record_template.csv`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_record_template.csv) | Blank submission template (header only) | **VERIFIED** |
| Original unified `train.jsonl` | Exactly 52,692,357 bytes (unchanged) | **VERIFIED** |
| Original unified `validation.jsonl` | Exactly 5,900,569 bytes (unchanged) | **VERIFIED** |
| Original unified `test.jsonl` | Exactly 16,230,756 bytes (unchanged) | **VERIFIED** |
| Original benchmark `test_comi_lingua.jsonl` | Exactly 8,435,204 bytes (unchanged) | **VERIFIED** |
| Original benchmark `test_tenglish_blog.jsonl` | Exactly 2,700,433 bytes (unchanged) | **VERIFIED** |
| Original benchmark `test_tenglish_twitter.jsonl` | Exactly 5,095,119 bytes (unchanged) | **VERIFIED** |
| Machine learning model training | Zero training started or run | **VERIFIED** |
| Final split execution | `split_custom_trilingual_dataset.py` not executed | **VERIFIED** |

---

## 10. Remaining Faculty Approvals Required Prior to Data Collection

Before initiating any participant recruitment, contributor onboarding, or sentence collection, the following institutional approvals must be secured:

1. **Review and Sign-off on Informed Consent:** Faculty supervisor review and formal approval of [`draft_consent_form.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/draft_consent_form.md).
2. **Formal Commercial Reuse Decision:** Institutional decision whether to permit downstream commercial adaptation under CC BY 4.0 or require a non-commercial restriction (CC BY-NC 4.0).
3. **Ethics / IRB Clearance:** Departmental confirmation whether formal institutional Ethics Committee / IRB approval is required for adult linguistic elicitation.
4. **Approval of Contributor Eligibility Guidelines:** Sign-off on [`contributor_eligibility.md`](file:///c:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/contributor_eligibility.md) and adult-only enforcement.
5. **Secure Storage Designation:** Institutional designation and access configuration of secure storage for physical/electronic signed consent forms.
6. **Appointment of Qualified Reviewers:** Official appointment of qualified multilingual reviewers for Stage 1 and Stage 2 independent review.

---
*Report certified complete for Step 28.*
