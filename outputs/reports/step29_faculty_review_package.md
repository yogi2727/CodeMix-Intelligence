# Step 29: Faculty Review and Research Governance Submission Package Report

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 29 — Faculty Review & Research Governance Package Preparation  
**Workspace:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**Timestamp:** `2026-11-01T04:55:52Z`  
**Status:** **SUBMISSION PACKAGE PREPARED — PENDING FACULTY REVIEW**  

---

## Executive Summary

Step 29 establishes the formal **Faculty Review and Research Governance Submission Package** in [`outputs/faculty_review/`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/). This package consolidates all research designs, ethical protocols, participant eligibility criteria, licensing analyses, data management plans, quality control pipelines, and decision checklists required for institutional oversight before any human data collection is initiated.

In strict adherence to project directives:
- **Zero sentences were authored, elicited, or fabricated.**
- **No human contributors were recruited, contacted, or invited.**
- **No consent forms were collected or signed.**
- **All custom dataset JSONL files remain strictly empty (0 records, 0 bytes).**
- **Original unified LID benchmark files remain 100% hash-identical and untouched.**
- **No machine learning model training or dataset splitting occurred.**
- **All documents are explicitly marked `DRAFT — FOR FACULTY REVIEW`.**

---

## 1. Submission Package Directory Tree

The complete submission package is organized in [`outputs/faculty_review/`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/):

```
outputs/faculty_review/
├── README.md                                      (4,780 bytes)
├── project_summary.md                             (10,272 bytes)
├── human_participant_protocol.md                  (10,668 bytes)
├── licensing_decision_sheet.md                    (5,853 bytes)
├── data_management_plan.md                        (7,917 bytes)
├── annotation_quality_control.md                  (7,905 bytes)
├── dataset_split_policy.md                        (5,672 bytes)
├── faculty_approval_checklist.md                  (5,915 bytes)
└── CodeMix_Intelligence_Faculty_Review_Package.md (61,711 bytes)
```

---

## 2. Document Summaries

| Document | Primary Focus & Governance Scope |
| :--- | :--- |
| [`README.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/README.md) | Package index, executive summary, navigation table, and overview of requested faculty actions. |
| [`project_summary.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/project_summary.md) | Technical problem statement, 4 supervised classes (`EN: 0, HI: 1, TE: 2, OTHER: 3`), MuRIL backbone, unified benchmark baseline (69,079 records), critical gaps (zero native Telugu, zero Hindi-Telugu, zero trilingual), rationale for authentic human elicitation, 40-sentence pilot scope, and 400-sentence dataset plan. |
| [`human_participant_protocol.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/human_participant_protocol.md) | Ethical safeguards, adult-only eligibility (>=18), minor protection, 4 linguistic categories, self-screening questionnaire, pseudonymous identification (`contrib_XX`), voluntary participation, 6-domain communicative scenarios, two-stage independent review, and pre/post-freeze withdrawal procedures. Explicitly clarifies that the pilot is **40 total sentences** across 3 contributors, not 40 per contributor. |
| [`licensing_decision_sheet.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/licensing_decision_sheet.md) | Contributor intellectual property analysis, CC BY 4.0 rights/obligations, commercial reuse permissibility, irrevocability, post-release realities, permissive (CC BY 4.0) vs non-commercial (CC BY-NC 4.0) comparison, and formal deferral as **PENDING FACULTY APPROVAL**. |
| [`data_management_plan.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/data_management_plan.md) | Physical/logical separation of consent forms from dataset files, encrypted key custody, access control, data retention/destruction schedules, provenance taxonomy (`licensed_corpus_extraction`, `naturally_occurring`, `human_elicited`, `parallel_reference`; banned `automatically_generated`), per-record licensing, and rejection logging. |
| [`annotation_quality_control.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/annotation_quality_control.md) | Two-stage independent review pipeline, Stage 1 screening/labeling, Stage 2 independent blind audit, adjudication, structural reviewer roles (`annotator_01`, `annotator_02`), fused-token (`MIXED` -100) and proper noun (`NE` -100) governance, 8-key closed language token statistics (Schema v1.3.0), sum parity law, and language switch calculation. |
| [`dataset_split_policy.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/dataset_split_policy.md) | Target stratified 60/20/20 split (240 train / 80 val / 80 test across 400 sentences, seed 42), dedicated custom test split (`custom_test.jsonl`) isolated from benchmark test sets, group-aware atomicity, realities of leakage prevention, group sparsity handling, and pilot non-split governance. |
| [`faculty_approval_checklist.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/faculty_approval_checklist.md) | Actionable 10-point decision checklist providing empty checkboxes `[ ]` for faculty determination on ethics review, eligibility, consent text, license type, commercial policy, secure storage, data retention, reviewer appointments, pilot launch, and release conditions. |
| [`CodeMix_Intelligence_Faculty_Review_Package.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/outputs/faculty_review/CodeMix_Intelligence_Faculty_Review_Package.md) | Consolidated single-file submission document assembling all 8 modular sections with unified table of contents for holistic review. |

---

## 3. List of Pending Faculty Decisions

The submission package presents **10 explicit decision points** requiring formal faculty determination:

1. **Institutional Ethics Review (IRB / IEC):** Determination whether formal institutional Ethics Committee clearance is required or if departmental faculty oversight is sufficient.
2. **Contributor Eligibility Criteria:** Approval of the adult-only ($\ge 18$) mandate and exclusion of minors from the pilot.
3. **Informed Consent Text:** Approval of [`draft_consent_form.md`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/custom/trilingual_lid/pilot/draft_consent_form.md) and contributor rights disclosures.
4. **Contributor Licensing Determination:** Decision whether to proceed with permissive **CC BY 4.0** or adopt a restrictive **CC BY-NC 4.0** non-commercial license.
5. **Commercial Reuse Policy:** Policy determination whether commercial developers may evaluate/fine-tune models on the dataset or if use is strictly limited to non-profit academic research.
6. **Secure Consent Storage Designation:** Designation of an institutionally managed, encrypted repository for storing signed consent forms and pseudonym lookup keys.
7. **Data Retention & Withdrawal Schedule:** Approval of data retention duration (e.g. 3–5 years post-publication) and secure digital shredding protocol.
8. **Appointment of Independent Reviewers:** Formal appointment of two qualified multilingual linguists / researchers for Stage 1 and Stage 2 review.
9. **Pilot Launch Authorization:** Permission to recruit 3 adult contributors and elicit the 40-sentence feasibility pilot.
10. **Public Release Conditions:** Definition of milestone gates and audits required before any public release of datasets or model checkpoints.

---

## 4. Full Workspace Integrity Verification

A complete audit verified that the workspace remains in a pristine, pre-collection state:

| Component / File | Verification Metric | Status |
| :--- | :--- | :---: |
| [`candidate_sentences.jsonl`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/custom/trilingual_lid/candidate_sentences.jsonl) | Exactly 0 records (0 bytes) | **VERIFIED (EMPTY)** |
| [`reviewed_sentences.jsonl`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/custom/trilingual_lid/reviewed_sentences.jsonl) | Exactly 0 records (0 bytes) | **VERIFIED (EMPTY)** |
| [`rejected_sentences.jsonl`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/custom/trilingual_lid/rejected_sentences.jsonl) | Exactly 0 records (0 bytes) | **VERIFIED (EMPTY)** |
| [`dataset_schema.json`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/custom/trilingual_lid/dataset_schema.json) | Version `1.3.0` (8 required count keys) | **VERIFIED (UNCHANGED)** |
| [`dataset_manifest.json`](file:///C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence/data/custom/trilingual_lid/dataset_manifest.json) | Version `1.3.0`, schema `1.3.0` | **VERIFIED (UNCHANGED)** |
| Model Training Execution | Zero training started or run | **VERIFIED (NONE)** |
| Split Script Execution | `split_custom_trilingual_dataset.py` not run | **VERIFIED (NONE)** |
| Draft Labels across Package | All 9 review files contain `DRAFT — FOR FACULTY REVIEW` | **VERIFIED** |
| Approval Checkboxes | All 10 checklist items remain blank `[ ]` | **VERIFIED** |

### Original Processed LID Benchmark Hash Verification:
- `train.jsonl` (52,692,357 B): `879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b` (**100% MATCH**)
- `validation.jsonl` (5,900,569 B): `3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b` (**100% MATCH**)
- `test.jsonl` (16,230,756 B): `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca` (**100% MATCH**)
- `quarantined_duplicates.jsonl` (7,951,036 B): `c3a715e737cf2775118226f2ced94e6cd20ef8eff4035fcbcda534de23f7af61` (**100% MATCH**)
- `excluded_records.jsonl` (1,115,199 B): `6f6b0ac82c9b8082e79ba94a1d98b9e0bc250b40f4ab77b8bf3884377f17a815` (**100% MATCH**)
- `dataset_manifest.json` (3,224 B): `8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d` (**100% MATCH**)

---

## 5. Confirmation Statement

The research team formally confirms:
1. **Zero human data collection has occurred.**
2. **No participant recruitment or contact has taken place.**
3. **No consent agreements have been executed.**
4. **No faculty approvals have been assumed or pre-empted.**
5. **Data collection activities remain strictly on hold awaiting formal sign-off.**
