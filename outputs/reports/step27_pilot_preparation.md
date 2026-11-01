# Step 27: Human Contributor Pilot Preparation Kit & Calibration Protocol

**Project:** CodeMix Intelligence  
**Directory:** [C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence)  
**Target Path:** [`data/custom/trilingual_lid/pilot/`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/)  
**Status:** **FACULTY-REVIEWABLE DRAFT PREPARATION KIT — ZERO HUMAN RECORDS CREATED**  
**Schema Compatibility:** `v1.2.0` (Step 26 Provenance-Aware Architecture)  

---

## Executive Summary

Step 27 developed a complete, faculty-reviewable **Human Contributor Pilot Preparation Kit** to establish empirical feasibility, calibration, and workload metrics for the CodeMix Intelligence custom trilingual LID dataset.

To ensure that the upcoming 400-sentence custom collection (100 sentences per category) is grounded in measured human authoring and review performance rather than speculative estimates, a **40-sentence empirical pilot** (10 sentences per category across 3 independent adult contributors) has been specified.

All documents created in this step are **blank instruction guides, plain-language consent drafts, scenario prompts without priming examples, and tabular tracking templates**. No participant has been recruited, no personal identifying information (PII) has been collected, and the custom dataset files remain strictly at 0 records (0 bytes).

---

## 1. Pilot Directory Tree

The complete preparation kit is located in [`data/custom/trilingual_lid/pilot/`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/):

```
data/custom/trilingual_lid/pilot/
├── README.md                      # Overview of the pilot kit, objectives, and operational safeguards
├── contributor_guide.md           # Plain-language instructions for native multilingual authors
├── draft_consent_form.md          # Faculty-reviewable informed consent draft & contributor rights notice
├── contributor_eligibility.md     # Linguistic proficiency criteria, PII exclusion rules, minor protection
├── elicitation_scenarios.md       # 40 communicative scenario prompts across 4 categories and 6 domains
├── pilot_protocol.md              # 7-phase operational protocol from faculty sign-off to workload projection
├── pilot_record_template.csv      # Blank tabular template for contributor submissions and annotations
├── reviewer_instruction_sheet.md  # Detailed criteria, checklists, and rejection codes for Stage 1 & 2 reviewers
├── pilot_acceptance_tracker.csv   # Tabular tracker for recording category submissions, approvals, and error types
└── ethics_and_privacy_notes.md    # Ethical safeguards, PII exclusion, CC non-commercial boundaries, IRB checklist
```

---

## 2. Contributor Eligibility Requirements

As specified in [`contributor_eligibility.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/contributor_eligibility.md), eligibility is defined per category:

1. **Category A (`Native_Telugu`):** Fluent native or heritage Telugu speaker capable of writing natural, contemporary Telugu in Telugu Unicode script (`U+0C00–U+0C7F`).
2. **Category B (`English_Telugu`):** Conversational bilingual speaker comfortable mixing English (Latin script) and Telugu (Telugu script) within the same communicative turn.
3. **Category C (`Hindi_Telugu`):** Bilingual speaker proficient in reading and writing both Hindi (Devanagari script `U+0900–U+097F`) and Telugu (Telugu script).
4. **Category D (`English_Hindi_Telugu`):** Trilingual speaker proficient in English, Hindi, and Telugu across all three scripts (Latin, Devanagari, Telugu).

### Privacy & Safeguards:
- **Self-Reported Assessment:** Qualification is evaluated through a non-intrusive self-assessment questionnaire; no intrusive testing or personal dossiers are collected.
- **Pseudonymous Identifiers:** Contributors are assigned random pseudonymous codes (`contrib_01`, `contrib_02`, `contrib_03`).
- **Strict PII Exclusion:** No legal names, phone numbers, email addresses, student roll numbers, or government IDs are entered into dataset files.
- **Minor Protection Policy:** The pilot strictly requires adult participants ($\ge 18$ years old). No minors will be recruited without formal institutional IRB approval and parental/guardian consent.

---

## 3. Draft Consent Document Summary

[`draft_consent_form.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/draft_consent_form.md) establishes a transparent, plain-language framework for institutional review:

- **Project Purpose:** Explains academic research into token-level language identification in mixed Indian discourse.
- **Nature of Tasks:** Writing 5–15 short sentences (5–25 words each) responding to everyday hypothetical scenarios. No audio recording, chat log extraction, or software installation.
- **Token-Level Annotation:** Explains that sentences will be segmented into individual words and tagged with language classes.
- **Voluntary Participation & Withdrawal:** Participation is entirely voluntary. Contributors may withdraw their submissions at any time prior to the designated **Dataset Freeze Date** using their pseudonym (`contrib_XX`).
- **Anonymization:** Zero PII collected; records identified solely by pseudonyms.
- **Proposed License:** Contributions provided under **Creative Commons Attribution 4.0 International (CC BY 4.0)** for open academic research.
- **Non-Commercial Legal Notice:** Explicitly notes that operating in an academic university setting does not automatically prove non-commercial status under CC terms; institutional review is required prior to external distribution.
- **Institutional Contact:** Channel provided for departmental faculty supervisor and research coordinator.

---

## 4. Four-Category Elicitation Strategy

[`elicitation_scenarios.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/elicitation_scenarios.md) provides **40 structured situational prompts (10 per category)** across 6 core domains:
1. College & Higher Education
2. Technology & Software Programming
3. Everyday Conversational & Family Life
4. Food, Cooking & Dining
5. Entertainment, Cinema & Sports
6. Workplace & Professional Collaboration

### Key Methodological Decisions:
- **Zero Example Sentences:** To prevent semantic priming and template copying, scenarios provide situational contexts and communication goals only. Contributors compose original utterances in their own voice.
- **Script Enforcement:**
  - English words $\rightarrow$ Latin script (`[A-Za-z]`)
  - Hindi words $\rightarrow$ Devanagari script (`U+0900–U+097F`)
  - Telugu words $\rightarrow$ Telugu Unicode script (`U+0C00–U+0C7F`)
  - Romanized transliterations of Hindi or Telugu are prohibited.
- **Lexical Presence:** Each participating language must be represented by at least one unambiguous lexical token (proper nouns and punctuation do not fulfill this requirement).
- **Prohibitions:** LLM generation alone is strictly barred from ground truth. Parallel corpus sentences must never be automatically concatenated.

---

## 5. Reviewer Process & Two-Stage Quality Control

[`reviewer_instruction_sheet.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/reviewer_instruction_sheet.md) establishes the verification workflow:

1. **Stage 1 (Linguistic Reviewer — `annotator_01`):**
   - Screens sentence naturalness and idiomatic fluency.
   - Verifies script conformity and language presence.
   - Verifies whitespace tokenization and punctuation detachment.
   - Provides initial token-by-token source labels (`EN`, `HI`, `TE`, `OTHER`, `NE`, `MIXED`).
2. **Stage 2 (Independent Auditor — `annotator_02`):**
   - Conducts a blind token-by-token audit without viewing Stage 1 labels.
   - Enforces special governance:
     - Fused tokens (Latin root + Telugu suffix like `computerలో`) $\rightarrow$ `MIXED` (`model_label: -100`).
     - Named entities (proper nouns) $\rightarrow$ `NE` (`model_label: -100`).
   - Independently recalculates `language_token_counts` and `language_switch_count`.
   - Reconciles label discrepancies or quarantines flawed sentences with explicit rejection codes (`REJ_NAT`, `REJ_SCR`, `REJ_MIX`, `REJ_LEN`, `REJ_PII`, `REJ_TOK`, `REJ_DIS`).

---

## 6. Acceptance-Rate Methodology & Workload Projection

[`pilot_protocol.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_protocol.md) and [`pilot_acceptance_tracker.csv`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/pilot_acceptance_tracker.csv) establish the empirical measurement protocol:

### 6.1 Formula
$$\text{Acceptance Rate } (A_{\text{pilot}}) = \frac{N_{\text{stage2\_approved}}}{N_{\text{submitted}}}$$
- Computed independently for each of the four categories.
- No speculative acceptance rates are assumed or invented.

### 6.2 Workload Projection for Step 28
Using the empirical acceptance rate measured during the pilot, the required drafting volume to reach the target of 100 reviewed sentences per category is calculated scientifically:
$$N_{\text{drafts\_needed}} = \left\lceil \frac{100}{A_{\text{pilot}}} \right\rceil$$

### 6.3 Quarantine Rule
Pilot records remain in `data/custom/trilingual_lid/pilot/`. They are **not** automatically transferred to `reviewed_sentences.jsonl` or partitioned into final splits.

---

## 7. BHT25 Source-Group Decision Note

An audit of the public BHT25 repository (`sudeshna84/BHT25`) confirmed that individual dataset rows expose only `id`, `bn`, `hi`, `te`, leaving literary document boundaries unresolved in the raw corpus.

### Comparison of Category A Sourcing Routes:

| Consideration | Route A: Manual BHT25 Work-Level Mapping | Route B: Direct Human Elicitation (Recommended) |
| :--- | :--- | :--- |
| **Operational Effort** | High: requires locating original Bengali/Hindi novels and manually mapping 100 rows to specific chapters or stories. | Moderate: contributors author 10 pilot / 100 final sentences responding to contemporary prompts. |
| **Leakage Risk** | High: unresolved story boundaries risk cross-split narrative leakage if mapping contains errors. | **Zero:** `source_group_id` maps unambiguously to `contributor_id`, guaranteeing clean train/val/test contributor disjointness. |
| **Linguistic Domain** | 19th-century literary translation bias; archaic syntax, formal classical vocabulary. | **Contemporary, natural spoken/written Telugu** across everyday, campus, technical, and culinary domains. |
| **Licensing / Provenance** | Sourced under CC BY 4.0; requires attribution notice. | Governed cleanly by contributor agreement under CC BY 4.0. |

### Operational Recommendation:
**Route B (Direct Human Elicitation) is the safer, cleaner, and higher-fidelity operational route** for the custom dataset. It ensures complete source-group isolation, eliminates literary translation artifacts, and provides natural contemporary Telugu. BHT25 should be preserved as an out-of-domain evaluation benchmark rather than primary candidate material.

---

## 8. Statistics Accounting Issue & Proposed Backward-Compatible Correction

### Issue Identified:
In `dataset_schema.json` (v1.2.0), `language_token_counts` defines non-negative integer fields for `EN`, `HI`, `TE`, `OTHER`, `NE`, `MIXED` with `additionalProperties: false`.  
However, `source_labels` also allows `"AMBIGUOUS"` and `null`.  
If an annotator tags a contested token as `"AMBIGUOUS"` or unresolved `null`, the token is silently omitted from `language_token_counts`. Consequently, the sum of `language_token_counts` does not equal the total number of tokens ($\sum \text{counts} < \text{len}(\text{tokens})$), and adding `"AMBIGUOUS"` to the object causes a schema validation failure.

### Proposed Backward-Compatible Schema Correction (for Schema v1.3.0):
In the next approved schema update, extend `language_token_counts` to include `AMBIGUOUS` and `NULL` as optional non-negative integer fields:
```json
"language_token_counts": {
  "type": "object",
  "required": ["EN", "HI", "TE", "OTHER", "NE", "MIXED"],
  "properties": {
    "EN": { "type": "integer", "minimum": 0 },
    "HI": { "type": "integer", "minimum": 0 },
    "TE": { "type": "integer", "minimum": 0 },
    "OTHER": { "type": "integer", "minimum": 0 },
    "NE": { "type": "integer", "minimum": 0 },
    "MIXED": { "type": "integer", "minimum": 0 },
    "AMBIGUOUS": { "type": "integer", "minimum": 0 },
    "NULL": { "type": "integer", "minimum": 0 }
  },
  "additionalProperties": false
}
```
This preserves backward compatibility with all existing records (where `AMBIGUOUS` and `NULL` are absent or zero) while guaranteeing complete token-count parity ($\sum \text{counts} == \text{len}(\text{tokens})$) when ambiguous tokens are encountered.

*Per instructions, `dataset_schema.json` remains strictly unchanged in this step.*

---

## 9. Verification & Workspace Integrity Results (PASS)

The workspace was verified using `.venv\Scripts\python.exe scripts/validate_custom_trilingual_dataset.py`:

```text
===========================================================================
RUNNING VALIDATOR SELF-TEST SUITE (STEP 26 SPECIFICATION - 22 TESTS)
===========================================================================
  [PASS] All 22/22 unit tests executed and passed.
===========================================================================

===========================================================================
VALIDATING CUSTOM TRILINGUAL DATASET INFRASTRUCTURE (STEP 26)
Target Directory: C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence\data\custom\trilingual_lid
===========================================================================
[PASS] candidate_sentences.jsonl: 0 records | Errors: 0 | Warnings: 0
[PASS] reviewed_sentences.jsonl:  0 records | Errors: 0 | Warnings: 0
[PASS] rejected_sentences.jsonl:  0 records | Errors: 0 | Warnings: 0
Validating illustrative dummy schema example (examples/schema_example.json)... PASS
Validating dataset_manifest.json... PASS
Checking presence of documentation & infrastructure files... ALL FOUND
===========================================================================
OVERALL VALIDATION STATUS: PASS (Hard Errors: 0 | Warnings: 0)
===========================================================================
```

### Cryptographic Isolation Summary:
- `candidate_sentences.jsonl`: **0 bytes (0 records)** | SHA256: `e3b0c44298fc1c14...`
- `reviewed_sentences.jsonl`: **0 bytes (0 records)** | SHA256: `e3b0c44298fc1c14...`
- `rejected_sentences.jsonl`: **0 bytes (0 records)** | SHA256: `e3b0c44298fc1c14...`
- `splits/` directory: **Does not exist** (split script was not executed).
- Original unified LID benchmark splits in `data/processed/language_identification/`: **100% untouched**.
- Zero participants recruited; zero synthetic sentences created.

---

## 10. Required Approvals Prior to Collection

Before participant recruitment or pilot authoring can begin:
1. **Departmental / Faculty Supervisor Review:** Review and sign-off on [`draft_consent_form.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/draft_consent_form.md) and [`ethics_and_privacy_notes.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/pilot/ethics_and_privacy_notes.md).
2. **Institutional Ethics Clearance:** Confirmation from the institutional ethics coordinator regarding whether formal IRB review is required.
3. **Secure Consent Archive:** Dedicated encrypted storage configured for signed consent records.
4. **Reviewer Appointment:** Confirmation of two independent, qualified reviewers for Stage 1 and Stage 2 verification.
