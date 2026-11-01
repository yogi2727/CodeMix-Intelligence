# Faculty Review & Research Governance Approval Checklist

**Project Title:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Target Reviewer:** Departmental Faculty Supervisor / Ethics Review Committee  
**Document Status:** **DRAFT — FOR FACULTY REVIEW (ACTIONABLE APPROVAL CHECKLIST)**  
**Date:** November 2026  

---

## Instructions for Reviewing Faculty

Please review the accompanying governance and protocol documents in `outputs/faculty_review/` and record your determinations across the following ten governance decisions.

No human data collection, participant recruitment, or pilot sentence authoring will begin until this checklist is formally signed and dated.

---

## The 10 Faculty Decision Points

### Decision 1: Institutional Ethics Review (IRB / IEC) Determination
*Reference: `human_participant_protocol.md` §1–2, `ethics_and_privacy_notes.md`*
- [ ] **EXEMPT:** Protocol involves non-invasive, adult linguistic text elicitation with zero PII; departmental faculty approval is sufficient.
- [ ] **FORMAL IRB REQUIRED:** Protocol must be submitted for formal institutional Institutional Review Board / Ethics Committee clearance before recruitment.

### Decision 2: Contributor Eligibility & Adult-Only Mandate
*Reference: `human_participant_protocol.md` §2–3, `contributor_eligibility.md`*
- [ ] **APPROVED:** Contributor recruitment is strictly restricted to competent adults (aged >= 18). Minors are completely excluded from the pilot.
- [ ] **MODIFICATIONS REQUIRED:** (Specify below)

### Decision 3: Informed Consent Document Approval
*Reference: `draft_consent_form.md`, `licensing_decision_sheet.md`*
- [ ] **APPROVED AS DRAFT:** The text of `draft_consent_form.md` accurately describes the project, tasks, pseudonymous identification, and withdrawal terms.
- [ ] **REVISIONS REQUIRED:** (Specify required amendments below)

### Decision 4: Contributor Licensing Determination
*Reference: `licensing_decision_sheet.md` §2–5*
- [ ] **APPROVE CC BY 4.0 (Permissive):** Contributors grant Creative Commons Attribution 4.0 International, permitting broad academic and commercial research reuse with attribution.
- [ ] **MANDATE CC BY-NC 4.0 (Non-Commercial):** Restrict dataset redistribution strictly to non-commercial entities to protect contributor inputs.
- [ ] **ALTERNATIVE LICENSE MANDATED:** (Specify alternative legal instrument below)

### Decision 5: Commercial Reuse Policy Determination
*Reference: `licensing_decision_sheet.md` §4–5*
- [ ] **PERMIT COMMERCIAL REUSE:** Downstream academic and industrial developers may evaluate and fine-tune models on the dataset for commercial applications.
- [ ] **PROHIBIT COMMERCIAL REUSE:** Dataset and fine-tuned model artifacts are restricted strictly to non-profit academic research.

### Decision 6: Secure Consent Storage Designation & Access Authorization
*Reference: `data_management_plan.md` §2–3*
- [ ] **DESIGNATED & APPROVED:** The following institutionally approved, encrypted storage repository is authorized for storing signed consent records and lookup keys:
  *Designated Repository:* ____________________________________________________________________
- [ ] **ACCESS RESTRICTIONS CONFIRMED:** Access is strictly restricted to the Faculty Supervisor and authorized Principal Investigator.

### Decision 7: Data Retention & Contributor Withdrawal Schedule
*Reference: `data_management_plan.md` §4*
- [ ] **APPROVED:** Signed consent forms and pseudonym keys will be retained in encrypted storage for _____ years post-publication, then destroyed securely.
- [ ] **WITHDRAWAL PROTOCOL APPROVED:** Pre-freeze deletion requests will permanently purge records from repositories; post-release limitations are acknowledged.

### Decision 8: Appointment of Independent Multilingual Reviewers
*Reference: `annotation_quality_control.md` §1–2, `reviewer_instruction_sheet.md`*
- [ ] **REVIEWERS APPOINTED:** The following qualified multilingual individuals are officially appointed:
  - *Stage 1 Reviewer (`annotator_01`):* _____________________________________________________
  - *Stage 2 Independent Auditor (`annotator_02`):* __________________________________________
- [ ] **BLIND AUDIT PROTOCOL CONFIRMED:** Reviewer 2 will annotate raw tokens without access to Stage 1 labels.

### Decision 9: Authorization to Commence 40-Sentence Pilot
*Reference: `human_participant_protocol.md` §8, `pilot_protocol.md`*
- [ ] **AUTHORIZED TO PROCEED:** The research team is permitted to onboard 3 qualified adult contributors and elicit the 40-sentence feasibility pilot.
- [ ] **HOLD PENDING CONDITIONS:** (Specify conditions below)

### Decision 10: Release Conditions for Future Public Dataset / Model
*Reference: `dataset_split_policy.md` §2, `split_policy.md`*
- [ ] **CONDITIONS DEFINED:** Prior to any public upload (e.g. to Hugging Face or GitHub), the research team must present:
  1. Complete pilot acceptance report.
  2. Final 400-sentence validation report (0 errors, 0 warnings).
  3. Final verification that no PII exists in dataset records.
  4. Final faculty sign-off on release repository.

---

## Faculty Supervisor Sign-Off

**Faculty Supervisor Name:** ____________________________________________________  
**Academic Title & Department:** ________________________________________________  
**Institutional Affiliation:** __________________________________________________  

**Signature:** _________________________________________  
**Date:** ______________________________________________  

**Reviewer Notes / Mandatory Conditions:**  
_________________________________________________________________________________  
_________________________________________________________________________________  
_________________________________________________________________________________  
