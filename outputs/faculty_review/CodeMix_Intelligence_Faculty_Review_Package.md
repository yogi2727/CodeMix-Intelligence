# CodeMix Intelligence: Faculty Review & Research Governance Submission Package (Consolidated)

**Project Title:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Target Reviewer:** Departmental Faculty Supervisor & Institutional Ethics Review Committee  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  
**Repository Working Directory:** `C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence`  

> [!IMPORTANT]
> **GOVERNANCE & INTEGRITY NOTICE:**  
> This consolidated dossier contains the preliminary technical specifications, participant protection protocols, licensing options, data management plans, quality control procedures, and decision checklists for the proposed CodeMix Intelligence Custom Trilingual Dataset.  
> 
> In accordance with strict institutional research ethics:
> - **Zero human data collection has been initiated.**
> - **No human contributors have been contacted, invited, or recruited.**
> - **No consent agreements have been executed.**
> - **All custom dataset repositories remain strictly empty (0 records, 0 bytes).**
> - **Data collection will begin only after formal written faculty sign-off on the included checklist.**

---

## Consolidated Table of Contents

1. [Executive Overview & Package Structure](#part-1-executive-overview--package-structure)
2. [Project Summary & Technical Problem Definition](#part-2-project-summary--technical-problem-definition)
3. [Human Participant Protocol & Contributor Governance](#part-3-human-participant-protocol--contributor-governance)
4. [Contributor Rights, Licensing & Commercial Reuse Decision Sheet](#part-4-contributor-rights-licensing--commercial-reuse-decision-sheet)
5. [Data Management Plan & Privacy Protocol](#part-5-data-management-plan--privacy-protocol)
6. [Annotation Guidelines & Quality Control Protocol](#part-6-annotation-guidelines--quality-control-protocol)
7. [Dataset Split Policy & Leakage Prevention Governance](#part-7-dataset-split-policy--leakage-prevention-governance)
8. [Actionable Faculty Approval Checklist](#part-8-actionable-faculty-approval-checklist)

---

# Part 1: Executive Overview & Package Structure

# Faculty Review & Research Governance Submission Package

**Project Title:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Target Submission:** Departmental Faculty Supervisor & Institutional Ethics Review Committee  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  
**Directory:** `outputs/faculty_review/`  

---

## Executive Overview

This submission package provides a comprehensive, structured presentation of the research governance, human participant protocols, licensing frameworks, data management plans, quality control pipelines, and dataset partitioning strategies for the **CodeMix Intelligence Custom Trilingual Language Identification Dataset**.

All documents in this package represent **preliminary research designs and policy proposals**. In accordance with strict project governance rules:
- **No human contributors have been recruited or contacted.**
- **No participant consent has been collected.**
- **No sentences have been authored, elicited, or fabricated.**
- **All custom dataset repositories remain strictly empty (0 records, 0 bytes).**
- **No data collection or pilot authoring will begin prior to written faculty approval.**

---

## Document Index & Navigation

This review package is organized into modular governance documents, accompanied by a consolidated reference manual:

| Document | File Name | Primary Focus |
| :--- | :--- | :--- |
| **1. Project Summary** | [`project_summary.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/project_summary.md) | Technical problem statement, 4 supervised classes, MuRIL backbone, benchmark gaps, and research objectives. |
| **2. Human Participant Protocol** | [`human_participant_protocol.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/human_participant_protocol.md) | Adult-only eligibility (>=18), 4 linguistic categories, self-screening, scenario elicitation, 40-sentence pilot scope, and participant rights. |
| **3. Licensing Decision Sheet** | [`licensing_decision_sheet.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/licensing_decision_sheet.md) | CC BY 4.0 analysis, commercial reuse permissions, attribution terms, irrevocability, post-release realities, and pending decisions. |
| **4. Data Management Plan** | [`data_management_plan.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/data_management_plan.md) | Consent storage separation, encrypted key-custody, pseudonymization, data retention/destruction, provenance taxonomy, and rejection logging. |
| **5. Annotation Quality Control** | [`annotation_quality_control.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/annotation_quality_control.md) | Stage 1 screening, Stage 2 independent blind audit, adjudication, 8-key language token statistics, and 4 supervised classes. |
| **6. Dataset Split Policy** | [`dataset_split_policy.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/dataset_split_policy.md) | Stratified 60/20/20 split (240/80/80), dedicated custom test split, disjoint group isolation, group sparsity realities, and pilot isolation. |
| **7. Faculty Approval Checklist** | [`faculty_approval_checklist.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/faculty_approval_checklist.md) | 10-point actionable decision checklist for formal departmental and faculty sign-off. |
| **Consolidated Manual** | [`CodeMix_Intelligence_Faculty_Review_Package.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/CodeMix_Intelligence_Faculty_Review_Package.md) | Unified complete submission document containing all sections for single-file review. |

---

## Action Requested from Faculty Reviewers

Faculty supervisors and ethics committee members are invited to review this package and complete the **[Faculty Approval Checklist](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/faculty_review/faculty_approval_checklist.md)**, specifically determining:
1. Whether institutional IRB/IEC review is formally mandated for this adult linguistic elicitation protocol.
2. Whether the proposed CC BY 4.0 license is approved, or if a non-commercial restriction (CC BY-NC 4.0) should be applied.
3. Formal approval of the informed consent text and designated secure storage repository for physical/digital consent archives.
4. Appointment of two independent qualified multilingual reviewers for Stage 1 and Stage 2 verification.
5. Authorization to initiate the 40-sentence feasibility pilot.


---

# Part 2: Project Summary & Technical Problem Definition

# Project Summary: Multilingual Token-Level Language Identification

**Project Title:** CodeMix Intelligence  
**Component:** System Architecture, Benchmark Audit, and Research Scope  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  

---

## 1. What CodeMix Intelligence Does

**CodeMix Intelligence** is an applied Natural Language Processing (NLP) research and engineering initiative dedicated to solving the challenge of **token-level language identification (LID)** in multilingual Indian communication.

In linguistically diverse societies like India, individuals routinely interleave multiple languages and scripts within a single communicative turn, social media post, or messaging thread—a sociolinguistic phenomenon known as **code-mixing** and **code-switching**. Standard NLP pipelines (such as tokenizers, part-of-speech taggers, syntactic parsers, and machine translation systems) fail catastrophically when presented with code-mixed input because they implicitly assume monolingual text.

CodeMix Intelligence processes text at the sub-sentential level: it segments an input sequence into discrete lexical units (tokens) and predicts the language affiliation of **every individual word** in real-time.

```
Example Input:   "ఈ ప్రాజెక్ట్ report ని kal submit చేద్దాం."
Token Sequence:  ["ఈ", "ప్రాజెక్ట్", "report", "ని", "kal", "submit", "చేద్దాం", "."]
Language Labels: [TE,   TE,          EN,       MIXED, HI,   EN,       TE,        OTHER]
Model Classes:   [2,    2,           0,        -100,  1,    0,        2,         3]
```

---

## 2. Four Supervised Classes & Labeling Architecture

The underlying Transformer classification head is structured around **four primary supervised language classes**:

| Class Name | Label Code | Integer Class ID | Linguistic Scope | Unicode Script Requirement |
| :--- | :---: | :---: | :--- | :--- |
| **English** | `EN` | `0` | English lexical items | Latin script (`[A-Za-z]`) |
| **Hindi** | `HI` | `1` | Hindi words and morphemes | Devanagari script (`U+0900–U+097F`) |
| **Telugu** | `TE` | `2` | Telugu words and morphemes | Telugu script (`U+0C00–U+0C7F`) |
| **Universal / Other** | `OTHER` | `3` | Punctuation, symbols, numerals, emojis | Universal punctuation, digits (`0-9`) |

### Non-Supervised Provenance Annotations (Ignored Loss: `-100`)
To prevent corrupting the primary supervised loss while retaining complete linguistic provenance, ambiguous or boundary-crossing tokens are assigned non-loss labels:
- **Named Entities (`NE` $ightarrow$ `-100`):** Proper nouns (people, cities, organizations like *Hyderabad*, *Google*, *Virat*) that lack an intrinsic language identity.
- **Fused Fused-Script Words (`MIXED` $ightarrow$ `-100`):** Morphological hybrids combining a Latin base with a Telugu inflectional suffix (e.g. `computerలో`, `projectకి`).
- **Ambiguous Words (`AMBIGUOUS` $ightarrow$ `-100`):** Homographs or unresolved consensus words where even human reviewers cannot establish definitive single-language provenance.
- **Null / Untagged Words (`NULL` $ightarrow$ `-100`):** Missing source annotations.

No fifth model class is introduced; all non-supervised tokens are ignored during cross-entropy loss computation using PyTorch's `ignore_index = -100`.

---

## 3. Model Architecture & Pre-trained Backbone

The project fine-tunes **MuRIL (`google/muril-base-cased`)** (Multilingual Representations for Indian Languages):
- **Architecture:** BERT-base encoder architecture (12 transformer layers, 768 hidden dimension, 12 attention heads, 110 million parameters).
- **Subword Vocabulary:** 197,285 subword tokens trained on 17 Indian languages and English, including native Devanagari, native Telugu, and transliterated scripts.
- **Subword Alignment:** Token-level predictions utilize first-subword pooling with label alignment and subword-level mask propagation.
- **Sequence Profiling:** p99 sequence length in the benchmark is 73 subwords; `max_length = 128` comfortably covers >99% of sequences without truncation.

---

## 4. Unified Benchmark Baseline & Critical Limitations

The project previously constructed and verified a primary processed benchmark dataset comprising **69,079 total accounted records** across three public corpora:
1. **COMI-LINGUA:** Hindi-English code-mixed dialogue from entertainment and web sources.
2. **Telugu-English Blog Corpus:** Code-mixed blog articles.
3. **Telugu-English Twitter Corpus:** Social media micro-posts.

### The Verified Baseline Accounting:
- **Training Set:** 43,369 records (665,313 tokens)
- **Validation Set:** 4,820 records (73,957 tokens)
- **Test Set (Unified):** 14,855 records (211,576 tokens)
  - Dedicated Subsets: COMI-LINGUA (4,944), Blog (3,105), Twitter (6,806)
- **Excluded Records:** 1,647 records (all tokens ignored NE)
- **Quarantined Records:** 4,388 records (4,258 cross-split test leakage + 130 duplicate/conflict records)
- **Total Accounted:** **69,079 records**

### Critical Gaps in Existing Datasets:
A systematic audit revealed three severe vulnerabilities that prevent the current model from serving real-world Indian multilingual communities:
1. **Zero Native-Script Telugu:** In all existing Telugu-English corpora, Telugu words are **100% Romanized** (written phonetically in Latin script). There are **0 tokens of native Telugu script** (`U+0C00–U+0C7F`) across the entire 69,079-sentence benchmark.
2. **Complete Absence of Hindi + Telugu Mixing:** South India (particularly Telangana, Andhra Pradesh, and border areas) exhibits extensive conversational code-mixing between Hindi and Telugu. Existing corpora contain **0 sentences** of Hindi-Telugu mixing.
3. **Complete Absence of Trilingual Mixing:** In metropolitan hubs (e.g. Hyderabad, Bengaluru), speakers seamlessly mix English, Hindi, and Telugu in the same sentence. Existing corpora contain **0 trilingual sentences**.

---

## 5. Why Custom Human Data is Essential (Why Not LLMs?)

A common question is whether modern Large Language Models (LLMs) can simply generate synthetic code-mixed training examples. The project conducted a forensic evaluation of LLM generation and established strict policies **prohibiting synthetic/automatically generated data as ground truth**:
- **Grammatical Inauthenticity:** LLMs generate mechanical, translated word-for-word calques that do not reflect organic colloquial discourse.
- **Script Hallucination & Leakage:** LLMs frequently default to Romanized transliteration or introduce erroneous Hindi matras into Telugu script.
- **Sociolinguistic Bias:** Models trained on synthetic data overfit to LLM tokenization artifacts rather than real human communication.
- **Scientific Integrity:** An evaluation benchmark must evaluate how models perform on human language, not how well models predict other models' synthetic text.

Consequently, authentic human elicitation is scientifically indispensable.

---

## 6. Proposed 40-Sentence Human Contributor Pilot

Before committing resources to full-scale dataset curation, the project has designed an empirical **40-sentence human contributor pilot**:
- **Total Volume:** Exactly 40 sentences total (10 per category).
- **Target Categories:**
  - *Category A (Native Telugu):* 10 sentences
  - *Category B (English + Telugu):* 10 sentences
  - *Category C (Hindi + Telugu):* 10 sentences
  - *Category D (English + Hindi + Telugu):* 10 sentences
- **Participant Allocation:** Distributed across **three qualified adult contributors** where feasible (~3–4 sentences per contributor per category).
- **Primary Objectives:**
  1. Measure empirical contributor acceptance and rejection rates ($A_{\text{pilot}} = N_{\text{approved}} / N_{\text{submitted}}$).
  2. Test and refine the 40 communicative scenario prompts.
  3. Calibrate inter-annotator agreement between Stage 1 and Stage 2 reviewers.
  4. Project required drafting volume for full dataset collection ($N_{\text{drafts}} = \lceil 100 / A_{\text{pilot}} \rceil$).

---

## 7. Planned 400-Sentence Custom Dataset

Following pilot review and calibration, the full custom dataset will target **400 gold-standard human-reviewed sentences**:
- **100 sentences per category** across the four categories.
- Stratified **60/20/20 partitioning**:
  - **Train:** 240 sentences (60 per category)
  - **Validation:** 80 sentences (20 per category)
  - **Test:** 80 sentences (20 per category)
- Preserved in dedicated files (`custom_test.jsonl`), completely isolated from the baseline benchmark test sets.

---

## 8. Completed Infrastructure vs. Proposed Future Work

It is critical to distinguish what has already been built from what is proposed for future execution:

### Completed Technical Infrastructure (Steps 23–28A):
- **Schema v1.3.0 Specification:** Complete JSON Schema ([`dataset_schema.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/dataset_schema.json)) with 8-key closed accounting, provenance metadata, and strict typing.
- **Validator Test Suite:** 30 comprehensive self-tests in [`scripts/validate_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/validate_custom_trilingual_dataset.py) verifying script validation, duplicate detection, loss isolation, and parity.
- **Operational Pilot Kit:** Scenario prompts, contributor guides, reviewer instruction sheets, and tracking templates in `data/custom/trilingual_lid/pilot/`.
- **Baseline Verification:** Read-only audits confirming that original unified datasets and custom dataset files are 100% verified, clean, and empty.

### Proposed Future Work (Awaiting Faculty Approval):
- Recruitment and onboarding of 3 qualified adult human contributors.
- Collection and submission of 40 pilot sentences.
- Execution of independent Stage 1 and Stage 2 human annotation.
- Calculation of empirical acceptance rates.
- Full 400-sentence collection, splitting, and MuRIL fine-tuning.

**No human data collection will occur without prior written faculty sign-off.**


---

# Part 3: Human Participant Protocol & Contributor Governance

# Human Participant Protocol & Contributor Governance

**Project Title:** CodeMix Intelligence  
**Component:** Human Subject Safeguards, Elicitation Scenarios, and Contributor Onboarding  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  

---

## 1. Ethical Principles & Research Intent

The collection of human linguistic data for CodeMix Intelligence is guided by fundamental ethical principles established in academic research codes (including the Declaration of Helsinki, Belmont Report, and Indian Council of Medical Research Ethical Guidelines for Social and Behavioural Research):

1. **Autonomy & Respect for Persons:** Contributors are autonomous individuals who make free, informed choices to contribute without coercion.
2. **Beneficence & Non-Maleficence:** The research carries minimal risk; contributors author non-sensitive sentences about hypothetical everyday scenarios.
3. **Data Minimization:** No personal identifying information (PII) is collected or preserved.
4. **Transparency:** Contributors are fully informed of how their text will be annotated, licensed, and distributed.

---

## 2. Contributor Eligibility (Adult-Only Mandate)

To guarantee legal capacity to provide informed consent and eliminate risks to vulnerable populations:

- **Adult Requirement:** **All contributors in the pilot must be adults aged 18 years or older.**
- **Minor Protection Policy:** Minors (under age 18) are **strictly barred** from participating in this pilot. If younger individuals are ever considered for future expansions:
  1. Formal Institutional Review Board (IRB) / Ethics Committee clearance must be granted.
  2. Dual written parental consent and minor assent must be obtained.
  3. Additional child privacy safeguards must be enforced.
- **Pilot Population:** The 40-sentence pilot will invite qualified, adult university students, researchers, and multilingual staff members within the institution.

---

## 3. Four Linguistic Categories & Proficiency Profiles

Contributors author sentences within one or more of four distinct linguistic categories based on their verified proficiency:

### Category A: Native Telugu (`Native_Telugu`)
- **Linguistic Profile:** Fluent native or heritage Telugu speaker.
- **Script Competency:** Able to read and type natively in Telugu script (`U+0C00–U+0C7F`).
- **Linguistic Focus:** Contemporary, idiomatic spoken Telugu syntax (excluding English borrowings unless fully assimilated into Telugu script).

### Category B: English + Telugu (`English_Telugu`)
- **Linguistic Profile:** Conversational bilingual speaker of English and Telugu.
- **Script Competency:** Able to type English in Latin script (`[A-Za-z]`) and Telugu in Telugu script (`U+0C00–U+0C7F`) within the same sentence boundary.
- **Linguistic Focus:** Natural intra-sentential switching common in campus, software workplace, and social media messaging.

### Category C: Hindi + Telugu (`Hindi_Telugu`)
- **Linguistic Profile:** Bilingual speaker proficient in Hindi and Telugu.
- **Script Competency:** Able to read and write in both Devanagari script (`U+0900–U+097F`) and Telugu script (`U+0C00–U+0C7F`).
- **Linguistic Focus:** Multi-state transit, trade, cinema commentary, and cross-family Indian code-mixing.

### Category D: English + Hindi + Telugu (`English_Hindi_Telugu`)
- **Linguistic Profile:** Trilingual speaker proficient in English, Hindi, and Telugu.
- **Script Competency:** Fully comfortable typing across all three scripts: Latin, Devanagari, and Telugu.
- **Linguistic Focus:** Metropolitan multi-script code-mixing (such as in Hyderabad or Bengaluru) where three languages naturally intermingle.

---

## 4. Self-Reported Proficiency Screening Framework

To assess linguistic capability without administering high-stress tests or creating intrusive dossiers, contributors complete a lightweight self-assessment screening questionnaire prior to assignment:

```
CONTRIBUTOR SELF-ASSESSMENT CHECKLIST (CONFIDENTIAL)

Assigned Pseudonym: contrib_XX [Assigned by Research Coordinator]

1. Native / Primary Spoken Language(s):
   [ ] Telugu    [ ] Hindi    [ ] English    [ ] Other: __________________

2. Telugu Script Typing Competency:
   [ ] Fluent: I can easily read and type Telugu script on phone/computer.
   [ ] Moderate: I can type with some assistance.
   [ ] Romanized Only: (Ineligible for native Telugu text)

3. Hindi (Devanagari) Script Typing Competency:
   [ ] Fluent: I can easily read and type Hindi in Devanagari script.
   [ ] Moderate: I can type basic Hindi words in Devanagari.
   [ ] Romanized Only: (Ineligible for Categories C and D)

4. Code-Mixing Frequency:
   - How often do you mix English with Telugu in daily conversations?
     [ ] Daily    [ ] Frequently    [ ] Rarely    [ ] Never
   - How often do you mix Hindi with Telugu or English?
     [ ] Daily    [ ] Frequently    [ ] Rarely    [ ] Never

5. Eligibility Assignment (Determined by Reviewer):
   Eligible for Category A (Native Telugu):            [ ] Yes   [ ] No
   Eligible for Category B (English + Telugu):          [ ] Yes   [ ] No
   Eligible for Category C (Hindi + Telugu):            [ ] Yes   [ ] No
   Eligible for Category D (English + Hindi + Telugu):  [ ] Yes   [ ] No
```

---

## 5. Pseudonymous Identification & Privacy Guardrails

- **Pseudonymous Identifiers:** Every participant is assigned a unique alphanumeric code (`contrib_01`, `contrib_02`, `contrib_03`).
- **Zero Extraneous PII:** The dataset records, annotations, and public files contain **zero personally identifying information (PII)**.
- **Strictly Barred Data Elements:** Legal names, student registration numbers, employee roll numbers, email addresses, phone numbers, home addresses, government IDs, and payment details are strictly barred from dataset files.
- **Separate Consent Custody:** Physical signed consent sheets or digital signatures linking a legal name to a contributor ID are stored in institutionally approved, encrypted storage accessible exclusively to the faculty supervisor.

---

## 6. Voluntary Participation & Academic Freedom

- **Completely Voluntary:** Participation is entirely optional. Refusal to participate carries zero academic, financial, or institutional penalty.
- **No Coercion:** Faculty supervisors and project leads must ensure that student participation is never tied to course grades, laboratory standing, or academic evaluations.
- **Right to Pause or Stop:** Contributors may discontinue participation at any point without providing a justification.

---

## 7. Communicative Scenario Elicitation Methodology

Rather than providing example sentences (which induces cognitive anchoring and unnatural template imitation), contributors are presented with **communicative situational scenarios** across six domains:

1. **College & Higher Education:** Group projects, lab schedules, exam preparation, library visits, campus canteen chats.
2. **Technology & Software Programming:** Debugging code, git branches, server outages, laptop repair, hackathons.
3. **Everyday Conversational & Family Life:** Family travel, festival plans, neighborhood events, weekend chores.
4. **Food, Cooking & Dining:** Ordering food, street food debates, grocery shopping, restaurant reviews.
5. **Entertainment, Cinema & Sports:** Cricket match discussions, movie trailers, OTT shows, actor performances.
6. **Workplace & Professional Collaboration:** Meeting minutes, client deadlines, email follow-ups, remote work coordination.

### Elicitation Rules:
- **Sentence Length:** 5 to 25 words per sentence.
- **Lexical Threshold:** Each sentence must contain at least one unambiguous lexical token from each required language for the category.
- **Naturalness:** Sentences must reflect natural, conversational syntax, avoiding artificial translationese.
- **No Private Disclosures:** Contributors must not disclose real living persons' private names, phone numbers, or confidential information.

---

## 8. Contributor Workload & 40-Sentence Pilot Allocation

A critical clarification was codified during Step 28 governance finalization:

> [!IMPORTANT]
> **PILOT VOLUME CLARIFICATION:**  
> The pilot consists of **40 total sentences** across all four categories:
> - Category A: 10 sentences total
> - Category B: 10 sentences total
> - Category C: 10 sentences total
> - Category D: 10 sentences total
> 
> **It is strictly NOT 40 sentences per contributor, and NOT 10 sentences per contributor per category.**

### Allocation Across Three Contributors:
Where feasible, the 10 sentences per category are distributed across **three independent qualified adult contributors**:
- Contributor 1 (`contrib_01`): 3–4 sentences per eligible category.
- Contributor 2 (`contrib_02`): 3–4 sentences per eligible category.
- Contributor 3 (`contrib_03`): 3–4 sentences per eligible category.

This design ensures:
1. Low contributor burden (a contributor authors only 10–15 sentences total across their eligible categories, requiring ~20–30 minutes).
2. Author diversity across every category (preventing single-contributor stylistic bias).
3. Empirical baseline calibration across multiple human writing styles.

---

## 9. Two-Stage Independent Review Pipeline

Every submitted sentence undergoes rigorous two-stage review:
1. **Stage 1 Reviewer (`annotator_01`):** Screens for naturalness, script conformity, length, and PII; tokenizes the sentence; and assigns initial token labels.
2. **Stage 2 Reviewer (`annotator_02`):** Independently and **blindly** annotates raw tokens without seeing Stage 1 labels.
3. **Adjudication:** Disagreements are compared only after both reviewers have completed independent labeling. Unresolvable disagreements are marked `AMBIGUOUS` (`-100`).

---

## 10. Participant Withdrawal Procedure

- **Pre-Freeze Withdrawal:** Contributors may withdraw submitted sentences at any time prior to the official **Dataset Freeze Date**. Upon receiving notification with their pseudonymous contributor ID, the project team will permanently purge their sentences from candidate pools, drafts, and review logs.
- **Post-Distribution Open License Realities:** Once the dataset is published under an open license (such as CC BY 4.0), that grant is legally irrevocable for recipients who comply with its terms. The project team can remove contributions from future release versions, but cannot guarantee the recall or deletion of copies previously downloaded across the public Internet.


---

# Part 4: Contributor Rights, Licensing & Commercial Reuse Decision Sheet

# Contributor Rights, Licensing & Commercial Reuse Decision Sheet

**Project Title:** CodeMix Intelligence  
**Component:** Contributor Licensing, Intellectual Property & Faculty Determination  
**Document Status:** **DRAFT — FOR FACULTY REVIEW & DECISION**  
**Date:** November 2026  

---

## 1. Purpose of this Decision Sheet

This document outlines the intellectual property, copyright, and licensing considerations for human-authored sentences in the custom trilingual dataset.

Because open-source machine learning datasets often have long lifecycles and broad international circulation, selecting an appropriate contributor license requires a careful balance between:
1. **Academic Openness & Reproducibility:** Enabling global researchers to evaluate and advance token-level multilingual models.
2. **Contributor Expectations & Rights:** Protecting contributors from unauthorized misattribution or exploitative reuse.
3. **Institutional Policy Alignment:** Adhering to university intellectual property frameworks and research ethics standards.

---

## 2. Proposed Contributor License: Creative Commons Attribution 4.0 (CC BY 4.0)

The research team has prepared draft materials assuming the **Creative Commons Attribution 4.0 International License (CC BY 4.0)** (official legal code: https://creativecommons.org/licenses/by/4.0/).

### Core Grants Under CC BY 4.0:
- **Share:** Copy and redistribute the material in any medium or format.
- **Adapt:** Remix, transform, and build upon the material for any purpose.
- **Commercial Permissibility:** The licensor permits reuse **for any purpose, including commercially**.

### Mandatory Licensee Obligations:
- **Attribution:** Downstream users must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **No Additional Restrictions:** Users may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

---

## 3. Key Legal Realities of CC BY 4.0

To ensure informed consent and institutional transparency, three crucial legal realities must be recognized:

### A. Commercial Exploitation is Explicitly Permitted
CC BY 4.0 is **not** an academic-only or non-commercial license. Anyone—including commercial tech corporations, proprietary software vendors, and private cloud providers—may legally use, incorporate, and monetize data licensed under CC BY 4.0 without paying royalties, provided they maintain attribution notices.

### B. The License is Irrevocable
Under Section 2(a)(1) of the CC BY 4.0 legal code:
> *"The licensor cannot revoke these freedoms as long as you follow the license terms."*

Once a recipient acquires a copy of the dataset under CC BY 4.0, their rights to use that copy cannot be revoked by the contributor or the institution, even if the contributor later decides to withdraw from the study.

### C. Post-Distribution Withdrawal Realities
While the project team can honor pre-freeze withdrawal requests by deleting sentences from draft repositories, **complete Internet-wide deletion cannot be guaranteed once public distribution occurs**:
- The project team can delete the contributor's sentences from future official releases.
- However, third-party mirrors, research papers, cached downloads, and commercial copies already distributed under CC BY 4.0 cannot be recalled.
- Consent forms must explicitly disclose this limitation to contributors prior to onboarding.

---

## 4. The Critical Institutional Decision: CC BY 4.0 vs. CC BY-NC 4.0

The faculty supervisor and departmental ethics committee must formally decide between two licensing routes:

| Feature / Consideration | Option A: CC BY 4.0 (Permissive) | Option B: CC BY-NC 4.0 (Non-Commercial) |
| :--- | :--- | :--- |
| **Commercial Reuse** | Permitted (commercial AI labs can use it) | Prohibited (strictly non-commercial entities) |
| **Research Adoption** | Maximum (adopted by major benchmark repositories) | Moderate (some industry research labs cannot touch NC data) |
| **Contributor Protection** | Standard (attribution required) | Enhanced (prevents direct commercial monetisation) |
| **Industry Collaboration** | Seamless | Requires bespoke commercial licensing agreements |
| **Upstream Compatibility** | Fully compatible with public Hugging Face models | Compatible with academic research use only |
| **Risk of Student Pushback** | Low if fully disclosed; potential concern if commercialized | Lowest (students assured work remains non-commercial) |

### Important Distinction on "Academic Context":
Operating within an academic university does **not** automatically render downstream use non-commercial under Creative Commons definitions. Under official Creative Commons guidelines, "non-commercial" depends on the nature of the use and user, not the setting of the initial creation. If the institution wishes to prevent commercial monetization of student-authored sentences, an explicit non-commercial license (CC BY-NC 4.0) must be mandated.

---

## 5. Formal Policy Decision: PENDING FACULTY APPROVAL

> [!IMPORTANT]
> **STATUS: PENDING FACULTY REVIEW.**  
> The project team has **NOT** made a final decision on licensing and has **NOT** substituted an alternative license.  
> 
> The decision whether to proceed with **CC BY 4.0** or adopt a **CC BY-NC 4.0** restriction is formally submitted to the faculty supervisor and departmental committee for written determination.

---

## 6. Legal Disclaimer

This document and associated draft consent forms represent preliminary research proposals drafted for departmental evaluation. They **do not constitute legal advice**, have not been reviewed by institutional legal counsel, and cannot be executed prior to official departmental sign-off.


---

# Part 5: Data Management Plan & Privacy Protocol

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


---

# Part 6: Annotation Guidelines & Quality Control Protocol

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


---

# Part 7: Dataset Split Policy & Leakage Prevention Governance

# Dataset Split Policy & Data Leakage Prevention Governance

**Project Title:** CodeMix Intelligence  
**Component:** Custom Dataset Partitioning, Group Isolation, and Evaluation Safeguards  
**Document Status:** **DRAFT — FOR FACULTY REVIEW**  
**Date:** November 2026  

---

## 1. Target 60/20/20 Stratified Partitioning

Upon successful completion of the full 400-sentence two-stage human review in `reviewed_sentences.jsonl`, the dataset is scheduled to be partitioned using a **stratified 60% train / 20% validation / 20% test split within each category**:

| Category Name | Category Key | Collection Target | Train (60%) | Validation (20%) | Test (20%) | Primary Purpose |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Native Telugu** | `Native_Telugu` | **100** | 60 | 20 | 20 | Calibrate model on native Telugu script syntax |
| **English + Telugu** | `English_Telugu` | **100** | 60 | 20 | 20 | Benchmark intra-sentential English-Telugu mixing |
| **Hindi + Telugu** | `Hindi_Telugu` | **100** | 60 | 20 | 20 | Benchmark cross-family Indian code-mixing |
| **English + Hindi + Telugu** | `English_Hindi_Telugu` | **100** | 60 | 20 | 20 | True trilingual code-mixed evaluation |
| **TOTAL** | — | **400** | **240** | **80** | **80** | **Balanced evaluation & calibration corpus** |

Partitioning will utilize a fixed random seed (`seed = 42`) to ensure 100% scientific reproducibility.

---

## 2. Dedicated Test Split & Complete Benchmark Isolation

A core architectural principle of CodeMix Intelligence is that **the custom test split (80 sentences) will be preserved in a dedicated file (`custom_test.jsonl`)**:
- It will **never be merged into or overwrite** the established baseline test files:
  - `test_comi_lingua.jsonl` (4,944 records)
  - `test_tenglish_blog.jsonl` (3,105 records)
  - `test_tenglish_twitter.jsonl` (6,806 records)
  - `test.jsonl` (14,855 records)
- **Scientific Rationale:** Baseline test sets remain completely frozen and comparable with published literature, while `custom_test.jsonl` provides an independent benchmark measuring zero-shot and fine-tuned generalization on previously absent language pairs.

### Evaluation Lock-In Rules:
- The 80 custom test sentences are **strictly locked**:
  - Never used for gradient descent or model updates.
  - Never used for hyperparameter selection or early stopping.
  - Evaluated **exactly once** per finalized model release.

---

## 3. Group-Aware Splitting & Disjointness Principles

Naively shuffling individual sentences creates severe risks of subtle data leakage if multiple sentences originate from the same human author (sharing vocabulary habits, sentence structures, or colloquial quirks) or the same literary document.

### Technical Group Identification:
- **Human-Authored Elicited Data:** `metadata.source_group_id = metadata.contributor_id` (identifying individual authoring styles).
- **Corpus-Derived Data:** `metadata.source_group_id = metadata.source_document_id` (identifying individual articles, books, or conversational dialogues).

### The Atomicity Principle:
The split algorithm enforces that **all sentences sharing the same `source_group_id` must be assigned atomically to exactly one partition** (either Train, Validation, or Test). Under no circumstances will sentences from a single contributor be divided across training and test sets.

---

## 4. Realities of Leakage Prevention & Group Sparsity

A critical governance correction made in Step 28 eliminated false claims regarding automatic zero leakage:

> [!WARNING]
> **LEAKAGE REALITIES & PREREQUISITES:**  
> Simply tagging a record with `source_group_id` does **NOT** magically eliminate data leakage.  
> 
> True group disjointness mathematically requires that the collection pool contains a **sufficient number of independent groups** ($\ge 3$ independent groups per category to populate train, validation, and test partitions).

### Policy on Group Sparsity:
If a category contains fewer than three independent groups (e.g. only two contributors authored all sentences for a category):
1. **Never Violate Group Atomicity:** A single contributor's sentences must **never** be split across train and test partitions merely to satisfy exact 60/20/20 numerical counts.
2. **Document the Structural Limitation:** The dataset documentation must formally state that group-disjoint partitioning could not be achieved without omitting a partition.
3. **Accept Numerical Count Variations:** Group integrity always takes precedence over exact numerical counts (e.g., a 58/21/21 split preserving disjoint groups is far superior to a 60/20/20 split that leaks a contributor).

---

## 5. Pilot Non-Split Governance

- **Feasibility Calibration Only:** The 40-sentence human contributor pilot is designed solely for operational feasibility, contributor instruction calibration, and review protocol validation.
- **Excluded from Model Splitting:** Pilot records are **never assigned train/val/test splits** and are **never processed** by the split script.
- **Isolation:** Pilot data is quarantined in `data/custom/trilingual_lid/pilot/` and will not be used to train or evaluate model candidates.

---

## 6. Execution Status: Proposal Only

The split policy is a **governance design proposal**. The split script ([`scripts/split_custom_trilingual_dataset.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/split_custom_trilingual_dataset.py)) has **NOT been executed**, and will not be run until all 400 sentences have been collected, reviewed, and approved under faculty oversight.


---

# Part 8: Actionable Faculty Approval Checklist

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

