# Data Management Plan & Privacy Protocol

**Project Title:** CodeMix Intelligence  
**Component:** Data Management, Security, Pseudonymization, and Provenance  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  

---

## 1. Overview & Data Minimization

The CodeMix Intelligence Data Management Plan (DMP) establishes strict technical, operational, and physical safeguards governing data collection, storage, access, and lifecycle management.

The central pillar of this plan is **radical data minimization**:
- Only linguistic text essential for training and evaluating language identification models is collected.
- Zero personally identifying information (PII) is solicited, recorded, or incorporated into dataset files.

---

## 2. Separate Secure Storage for Consent Documents

A fundamental ethical safeguard is the complete physical and logical separation of contributor identity records from research dataset files:

```
[ Contributor Identity ]                 [ Research Dataset ]
  Legal Name & Signature                   Sentence Tokens & Labels
  Consent Date & Screening                 Pseudonym: contrib_01
            │                                        │
            ▼                                        ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│ Institutionally Secured │              │ Project Working Storage │
│ Encrypted Consent Store │              │ (data/custom/...)       │
│ - Restricted to Faculty │              │ - Only Pseudonyms       │
│ - Never Public          │              │ - Zero PII              │
└─────────────────────────┘              └─────────────────────────┘
```

### Institutional Storage Requirements:
1. **Designation of Storage Location:** The faculty supervisor and departmental IT coordinator must designate an institutionally approved, encrypted storage repository (e.g., departmental secure server, encrypted institutional cloud drive with two-factor authentication, or locked departmental filing cabinet for physical forms).
2. **Access Restrictions:** Access to the consent store is strictly restricted to the Faculty Principal Investigator and appointed research coordinators. Student annotators and public developers will have **zero access** to the identity store.
3. **Lookup Key Custody:** The lookup key mapping legal names to pseudonyms (`contrib_XX`) must be encrypted with AES-256 and stored separately from working dataset files.

---

## 3. Pseudonymization Architecture

- **Pseudonym Pattern:** Contributor identifiers strictly adhere to the regex `^contrib_[0-9]{2,}$` (e.g. `contrib_01`, `contrib_02`).
- **No Identity Leakage in Metadata:** Dataset records contain only:
  - `metadata.contributor_id`: `"contrib_01"`
  - `metadata.consent_status`: `"consented_academic_use"`
- **Prohibited Attributes:** Legal names, email addresses, IP addresses, student IDs, phone numbers, or demographic dossiers are never collected, stored, or referenced.

---

## 4. Data Retention & Deletion Schedule

The lifecycle of collected data requires formal faculty policy determination:

- **Pre-Freeze Deletion Protocol:** If a contributor requests withdrawal before the Dataset Freeze Date, the research coordinator will:
  1. Identify the contributor's pseudonym in the encrypted key store.
  2. Locate all matching sentences across `candidate_sentences.jsonl`, `reviewed_sentences.jsonl`, and `rejected_sentences.jsonl`.
  3. Permanently purge the records and regenerate checksums.
  4. Archive a verification log confirming deletion.
- **Post-Publication Retention Schedule:** Signed consent forms and pseudonym keys must be retained in encrypted institutional storage for a specified retention period (typically **3 to 5 years post-publication** in academic institutions) to support auditability, after which they must be securely destroyed via digital shredding or certified physical destruction.
- **Institutional Decision Required:** The exact retention period and final destruction protocol are subject to departmental approval on the Faculty Checklist.

---

## 5. Provenance Taxonomy & Sourcing Methods

Every record in the custom dataset tracks explicit provenance via `metadata.collection_method`:

| Collection Method | Permissible Context | Required Provenance Metadata | Individual Consent |
| :--- | :--- | :--- | :--- |
| **`licensed_corpus_extraction`** | Sentences extracted from public licensed corpora (e.g. BHT25 native Telugu) | `source_dataset`, `source_record_id`, `license`, `source_url`, `source_group_id` | `not_applicable_public_corpus` |
| **`naturally_occurring`** | Organic social discourse collected under verified platform terms | `source_reference`, `license`, platform compliance documentation | Verified permission / public terms |
| **`human_elicited`** | Sentences directly authored by multilingual contributors in response to scenarios | `contributor_id`, `consent_status`, contributor-agreed `license` | `consented_academic_use` |
| **`parallel_reference`** | Human-authored mixed sentences using parallel text as semantic reference | `contributor_id`, `consent_status`, `reference_source`, reference `license` | `consented_academic_use` |
| **`automatically_generated`** | **STRICTLY PROHIBITED** | Ineligible for ground-truth data in this project | N/A |

### Absolute Ban on Synthetic Data:
AI-generated synthetic text (e.g. ChatGPT, Claude, LLaMA) is strictly disqualified from inclusion as ground-truth benchmark data to prevent hallucinated grammatical patterns from corrupting evaluation.

---

## 6. Per-Record Licensing Metadata

Every sentence record includes granular licensing fields in `metadata`:
- `metadata.license`: The canonical license identifier (e.g., `"CC-BY-4.0"` or `"CC-BY-NC-4.0"`).
- `metadata.license_url`: URI link to the official legal code.
- `metadata.source_rights`: Confirms whether the record originates from human elicitation or an upstream public corpus.

This per-record tracking guarantees that downstream consumers can programmatically verify the legal rights and obligations associated with every individual utterance.

---

## 7. Treatment of Rejected Data (`rejected_sentences.jsonl`)

Sentences that fail Stage 1 screening or Stage 2 adjudication are quarantined in `rejected_sentences.jsonl`:
- **Purpose:** Tracks rejected drafts to calculate empirical acceptance rates ($A_{\text{pilot}}$) and diagnose systemic contributor difficulties.
- **Structured Rejection Codes:**
  - `REJ_NAT`: Sentence unnatural or nonsensical.
  - `REJ_SCR`: Script non-compliance (e.g. Romanized Telugu or Hindi).
  - `REJ_MIX`: Insufficient code-mixing (lacks required language tokens).
  - `REJ_LEN`: Length violation (<5 or >25 tokens).
  - `REJ_PII`: Sentence contained personal names or identifying details (redacted/rejected).
  - `REJ_TOK`: Irreconcilable tokenization or segmentation error.
  - `REJ_DIS`: Irreconcilable annotator disagreement.
- **Isolation:** Rejected records are **never** included in `reviewed_sentences.jsonl`, never split into train/val/test, and never exposed to the model.

---

## 8. Zero PII Verification in Training Pipelines

Automated validator checks in [`scripts/validate_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) enforce that:
- Any record containing unredacted PII patterns fails validation with hard errors.
- Real contributor identities cannot be committed to git or stored in public dataset partitions.
