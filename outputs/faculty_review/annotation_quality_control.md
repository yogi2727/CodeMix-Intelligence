# Annotation Guidelines & Two-Stage Review Quality Control

**Project Title:** CodeMix Intelligence  
**Component:** Linguistic Annotation Pipeline, Inter-Annotator Agreement & Statistics Schema v1.3.0  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  

---

## 1. Two-Stage Independent Review Pipeline

To ensure that the custom dataset achieves publication-grade benchmark quality, every sentence submitted by a contributor must pass an independent, double-review pipeline:

```
[ Contributor Draft ]
         │
         ▼
┌─────────────────────────────────┐
│ Stage 1: Linguistic Screening   │
│ - Naturalness & script check    │
│ - PII & length (5-25 tokens)    │
│ - Initial tokenization & labels │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Stage 2: Independent Blind Audit│
│ - Reviewer 2 receives RAW text  │
│ - Zero access to Stage 1 labels │
│ - Blind independent labeling    │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Post-Annotation Adjudication    │
│ - Automated label comparison    │
│ - Consensus conference          │
│ - Unresolved -> AMBIGUOUS (-100)│
└─────────────────────────────────┘
```

### Stage 1: Linguistic Screening & Initial Annotation (`annotator_01`)
- **Naturalness:** Verifies the utterance reflects genuine colloquial usage, rejecting robotic translations.
- **Script Conformity:** Ensures English is in Latin script (`[A-Za-z]`), Hindi is in Devanagari (`U+0900–U+097F`), and Telugu is in Telugu script (`U+0C00–U+0C7F`). Transliterations into English alphabet are rejected.
- **Length & Privacy:** Confirms sentence length is between 5 and 25 tokens and contains zero personal data.
- **Initial Label Sequence:** Generates first-pass token-level language assignments.

### Stage 2: Independent Blind Audit (`annotator_02`)
- **Strict Blind Review:** To avoid confirmation bias, Reviewer 2 receives only the raw sentence text and **must annotate all tokens without seeing Stage 1 labels**.
- **Independent Label Sequence:** Produces an independent set of token annotations.

### Stage 3: Adjudication & Disagreement Resolution
- Only after both independent annotations are committed are the sequences compared programmatically.
- **Agreement:** Tokens where Reviewer 1 and Reviewer 2 agree are finalized directly.
- **Disagreement:** Conflicting tokens are flagged for collaborative discussion.
- **Unresolved Discrepancies:** If consensus cannot be reached, the token is assigned the source label `"AMBIGUOUS"` and mapped to `model_label: -100`.

---

## 2. Reviewer Appointment Status: Placeholder Roles

In project templates, schemas, and tracking sheets:
- `annotator_01` and `annotator_02` represent **structural review roles**, not appointed individuals.
- No actual reviewers have been appointed or recruited during preparatory steps.
- Formal appointment of two qualified multilingual linguists / research assistants is submitted for faculty approval on the checklist.

---

## 3. Special Fused-Token & Named Entity Governance

Accurate token-level LID in Indian code-mixed text requires rigorous linguistic policies for complex morphological edge cases:

### A. Fused-Script Words (Latin Base + Telugu Suffix) — Policy B
In Indian texting, speakers frequently attach Telugu case markers to English words:
- Examples: `computerలో` (*in the computer*), `projectకి` (*to the project*), `collegeని` (*the college [acc]*).
- **Governance:**
  - `source_label`: `"MIXED"`
  - `model_label`: `-100` (ignored during primary supervised loss).
- **Strict Rule:** Reviewers must **NEVER** force `MIXED` tokens into `EN`, `TE`, or `OTHER` (class 3). They must not artificially split the word into two tokens during this phase.

### B. Fully Assimilated Loanwords in Telugu Script — Policy A
When an English or Hindi loanword is written entirely using the Telugu script:
- Examples: `కంప్యూటర్లో`, `డేటా`, `ఫైల్`.
- **Governance:**
  - `source_label`: `"TE"`
  - `model_label`: `2` (supervised Telugu class).
- **Linguistic Rationale:** Phonological and orthographic assimilation into Telugu script establishes syntactic function in the Telugu clause.

### C. Named Entities (`NE`)
Proper nouns designating specific persons, locations, organizations, or products:
- Examples: *Sachin*, *Virat*, *Hyderabad*, *Vijayawada*, *Delhi*, *Google*, *Microsoft*.
- **Governance:**
  - `source_label`: `"NE"`
  - `model_label`: `-100` (ignored during primary loss).
- **Linguistic Rationale:** Proper names lack intrinsic language meaning; forcing them into language classes distorts vocabulary representations.

---

## 4. Eight-Key Closed Language Token Statistics (Schema v1.3.0)

Under Schema v1.3.0, every record tracks language token counts using an **exact 8-key closed accounting dictionary**:

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

### Governing Accounting Laws:
1. **Exact Sum Parity Law:** Every token in `tokens` must contribute to exactly one count key:
   $$\sum_{k \in \text{Keys}} \text{language\_token\_counts}[k] == \text{len}(\text{tokens})$$
2. **Null Accounting:** Missing or null source labels increment `NULL`.
3. **Ambiguous Accounting:** Undecidable or unadjudicated tokens increment `AMBIGUOUS`.
4. **Provenance Isolation:** `NE`, `MIXED`, `AMBIGUOUS`, and `NULL` are never lumped into `OTHER`.
5. **No Silent Zeroes:** Missing count keys are strictly rejected by the validator.

---

## 5. Language Switch Calculation Policy

The complexity of code-mixing is tracked via `metadata.language_switch_count`:
- **Algorithm:** Traverses the token sequence sequentially, considering **only language-bearing classes (`EN`, `HI`, `TE`)**.
- **Switch Condition:** Increments when the current language-bearing token differs from the preceding language-bearing token.
- **Ignored Classes:** Tokens labeled `OTHER`, `NE`, `MIXED`, `AMBIGUOUS`, or `NULL` do **not** trigger a switch and do **not** interrupt the active language context.

```
Example:    "Today [EN] , [OTHER] Hyderabad [NE] lo [TE] meeting [EN] undi [TE] ."
Bearing:    [EN]                                [TE]     [EN]        [TE]
Switches:         (EN -> TE: switch 1)                 (TE -> EN: 2) (EN -> TE: 3)
Switch Count: 3
```

---

## 6. Supervised Model Classes vs. Ignored Annotations

The project maintains a strict boundary between supervised training targets and provenance tracking:

```
Supervised Classes (Loss Calculated):
├── EN (0)     : English in Latin script
├── HI (1)     : Hindi in Devanagari script
├── TE (2)     : Telugu in Telugu script
└── OTHER (3)  : Universal punctuation, numbers, symbols

Ignored Classes (Loss Masked with -100):
├── NE (-100)        : Named Entities
├── MIXED (-100)     : Fused Latin-Telugu tokens
├── AMBIGUOUS (-100) : Unresolved inter-annotator disagreements
└── NULL (-100)      : Missing source annotations
```

This ensures that the model learns clean language representations without being penalized on linguistically contested boundary words.
