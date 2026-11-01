# Step 25C: Source Audit Corrections & Policy Finalization Report

## Executive Summary

This report documents the corrections, policy refinements, and methodological enhancements implemented for **Step 25C** of the **CodeMix Intelligence** project. 

Following a detailed review of Step 25B outputs, all factual, licensing, provenance, and split policy items were re-examined and revised across the audit reports ([`source_inventory.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/source_audit/source_inventory.md), [`licence_review.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/source_audit/licence_review.md), [`collection_strategy.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/source_audit/collection_strategy.md)), the machine-readable inventory ([`source_inventory.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/source_audit/source_inventory.json)), and the audit execution script ([`scripts/audit_custom_lid_sources.py`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/scripts/audit_custom_lid_sources.py)).

---

## 1. Summary of Corrections Made

| Area / Component | Previous State (Step 25B) | Corrected State (Step 25C) | Rationale |
| :--- | :--- | :--- | :--- |
| **BHT25 Suitability** | Classified as `SUITABLE`. | Classified as **`SUITABLE WITH CONDITIONS`**. | 75.8% alignment accuracy is derived from a 500-sample human validation, not individual verification of all 27,149 rows. Requires 100% human review of selected sentences. |
| **BHT25 Author List** | Omitted Vineeth Kumar from the citation. | Corrected to include **Vineeth Kumar**: Sudeshna Sani, Suryakanth V. Gangashetty, Samudravijaya K, Anik Nandi, Aruna Priya, **Vineeth Kumar**, and Akhilesh Kumar Dubey. | Aligned with dataset card and paper citation (*Data in Brief* 2026, DOI: `10.1016/j.dib.2026.112775`). |
| **BHT25 Redistribution** | Termed "unrestricted". | Clarified as **permitted subject to CC BY 4.0 attribution and notice conditions**. | Redistribution requires proper attribution, DOI link, license link, and change notifications. |
| **Share-Alike Scope** | Claimed mixing NC-SA text in a file automatically forces all independent records under NC-SA ("viral"). | Refined to distinguish **Adapted Material** (Section 1(a)) vs. **Collections/Compilations** (Section 1(b)) under CC FAQ guidance. | Tokenization/annotation legal classification requires analysis under applicable law; record-level isolation recommended without broad "viral" generalizations. |
| **Non-Commercial Scope** | Claimed academic status proves non-commercial use. | Clarified that intended academic use **may qualify** under CC definition depending on context and commercialization; institutional review required. | Aligned with Creative Commons official non-commercial definition and practice. |
| **Mozilla Common Voice** | Labeled as a "settled legal contradiction". | Described as **concurrently presenting CC0 and a no-rehosting clause**. Kept as **REFERENCE ONLY**. | Awaits formal clarification from Mozilla; zero examples copied. |
| **Provenance Taxonomy** | Classified public corpus extraction under `parallel_reference`. | Added distinct **`licensed_corpus_extraction`** method alongside `naturally_occurring`, `human_elicited`, and `parallel_reference`. | Clearly separates direct licensed extraction from human-authored mixed sentences using parallel references. |
| **Schema Blueprint** | Duplicated `source_record_id`, mixed spelling `licence`/`license`. | Standardized on single canonical spelling **`license`**, top-level `source_record_id` (null for elicited), added `source_group_id`, `language_switch_count`, `language_token_counts`. | Resolves schema ambiguity and separates rights, consent, and review status. |
| **Split Grouping Policy** | Proposed contributor partitioning across train/test. | Formalized **`source_group_id`** splitting (document/chapter for corpus extraction; disjoint contributor IDs across train and test for elicited text). | Guarantees genuine out-of-contributor generalizability. |
| **Code-Mixing Rule** | Required arbitrary minimum 2 tokens per language. | Revised to **at least one unambiguous lexical token** per required language (excluding NE, punctuation, and mixed tokens). | Reflects natural single-borrowing code-switching while tracking switch density. |
| **Workload Projections** | Included speculative draft quotas (125 for B, 135 for C, 150 for D). | **Removed speculative estimates**; established a **small empirical pilot protocol** (10 sentences/category) to calculate empirical acceptance rates. | Grounded in measured pilot data rather than invented numbers. |

---

## 2. BHT25 Attribution and Quality Clarification

- **Dataset Identifier**: `sudeshna84/BHT25` (Apache Parquet on Hugging Face).
- **Research Article**: Sani et al., *BHT25: Bengali-Hindi-Telugu Parallel Corpus for Literary Machine Translation*, *Data in Brief* (2026), DOI: [`10.1016/j.dib.2026.112775`](https://doi.org/10.1016/j.dib.2026.112775).
- **Correct Full Authorship**:
  1. Sudeshna Sani (Corresponding Author, KLEF / IFHE Hyderabad)
  2. Suryakanth V. Gangashetty (KLEF)
  3. Samudravijaya K (TIFR Mumbai)
  4. Anik Nandi (IFHE Hyderabad)
  5. Aruna Priya (KLEF)
  6. **Vineeth Kumar** (KLEF)
  7. Akhilesh Kumar Dubey (KLEF)
- **Quality Metrics Clarification**:
  - Total size: **27,149 sentence triplets** across Bengali (`bn`), Hindi (`hi`), and Telugu (`te`).
  - The author-reported **75.8% alignment accuracy** and **5.8% suboptimal alignment** are derived from a **500-triplet validation sample** evaluated by expert linguists, **NOT** from individual verification of all 27,149 rows.
  - Estimated OCR error rate is below 0.5% on the evaluated sample.
  - Sourcing native Telugu sentences for Category A is viable under **SUITABLE WITH CONDITIONS**: every extracted sentence must undergo human verification for length, OCR artifacts, and semantic fluency.
  - **No Concatenation Rule**: BHT25 is a parallel corpus; concatenating Hindi and Telugu parallel sentences is strictly forbidden.

---

## 3. Licensing & Compliance Corrections

### 3.1 Creative Commons Share-Alike Analysis
- Under [Creative Commons FAQ Guidance](https://creativecommons.org/faq/#can-i-create-a-collection-that-includes-a-work-offered-under-a-cc-license) and [CC-BY-NC-SA-4.0 Legal Code](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode):
  - **Adapted Material (Section 1(a))**: Derived from or based upon the licensed material (e.g. translation, modification, transformation). Public distribution of Adapted Material must satisfy Share-Alike conditions.
  - **Collections / Compilations (Section 1(b))**: Compilations of separate and independent works in themselves. Simply including an unaltered work within a collection does not convert other independent works in the collection into adapted material.
  - Whether tokenizing and assigning token-level LID labels creates an "adaptation" or constitutes metadata tagging of compiled text is a legal question requiring analysis under applicable law.
- **Project Policy**:
  - Preserve record-level licensing in metadata (`license` field).
  - Keep NC-SA material isolated in distinct dataset files.
  - Do not redistribute adapted NC-SA content without satisfying its specific conditions.
  - Avoid blanket use of the word "viral".
  - Obtain institutional review prior to publication.

### 3.2 Non-Commercial Interpretation Analysis
- NonCommercial is defined by Creative Commons as: *"not primarily intended for or directed towards commercial advantage or monetary compensation."*
- Operating within an academic environment does not automatically guarantee non-commercial protection (e.g., commercial research grants, technology transfer, or commercial model licensing).
- CodeMix Intelligence's intended academic use may qualify depending on actual purpose and circumstances; institutional/faculty review is required prior to public model release or dataset distribution.

### 3.3 Mozilla Common Voice Telugu 27.0 Status
- The dataset page presents both **CC0-1.0** and an explicit platform statement prohibiting rehosting or resharing.
- Rather than asserting a settled legal contradiction, the project treats this as an operational ambiguity.
- Classified as **REFERENCE ONLY**. Sourcing is paused until Mozilla provides clarification. Zero examples copied.

---

## 4. Updated Provenance Taxonomy

Every record collected in CodeMix Intelligence must declare one of four mutually exclusive provenance methods:

1. **`licensed_corpus_extraction`**:
   - A sentence selected directly from an existing licensed public corpus (e.g. BHT25).
   - Preserves originating record ID, document source, and license.
   - `contributor_id` is `null`; `consent_status` is `"not_applicable_public_corpus"`.
   - Requires 100% human review for length, orthography, and token LID labeling.
2. **`naturally_occurring`**:
   - An authentic utterance collected directly from organic discourse (e.g. public forums) with appropriate permission and platform compliance.
3. **`human_elicited`**:
   - An original sentence deliberately authored by a native multilingual contributor in response to a scenario.
   - Requires pseudonymous `contributor_id` and explicit `consent_status`.
   - *Must NEVER be represented as naturally occurring.*
4. **`parallel_reference`**:
   - A human-authored code-mixed sentence composed using a parallel corpus sentence (e.g. BHT25 Hindi/Telugu pair) as a semantic reference anchor.
   - Tracks originating reference ID and attribution.
5. **`automatically_generated`**:
   - AI/machine-generated text. **Strictly ineligible as ground truth**.

---

## 5. Proposed Provenance Schema Changes (Blueprint)

The proposed schema blueprint in [`collection_strategy.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/custom/trilingual_lid/source_audit/collection_strategy.md) incorporates:
- **Canonical spelling**: Standardized to `license` and `license_url`.
- **Top-level `source_record_id`**: Retained as sole canonical identifier (`null` for direct human elicitation).
- **Separation of Concerns**:
  - *Source Rights*: `source_dataset`, `source_url`, `license`, `license_url`.
  - *Contributor Consent*: `contributor_id` (null for corpus extraction), `consent_status` (`"consented_academic_use"`, `"not_applicable_public_corpus"`).
  - *Annotation Review*: `annotator_1`, `annotator_2`, `annotation_status`, `review_date` (null until final approval).
- **Evaluation & Splitting Support**:
  - `source_group_id`: Groups records by document/chapter (for extracted text) or author session (for elicited text) to enforce disjoint group splitting.
  - `source_domain`: Communicative domain.
  - `script_combination`: Script taxonomy.
  - `language_switch_count`: Integer count of intra-sentential language switches.
  - `language_token_counts`: Counts of unambiguous lexical tokens per language class (`EN`, `HI`, `TE`, `OTHER`).

*`dataset_schema.json` remains untouched pending formal approval.*

---

## 6. Updated Split Policy & Inclusion Rules

### 6.1 Disjoint Group Splitting Across 60/20/20
- **Stratified Partition**: 60 train / 20 validation / 20 test per category (240 / 80 / 80 total).
- **Group Separation**:
  - Corpus-derived records: grouped by `source_group_id` (literary work/chapter).
  - Elicited records: grouped by `source_group_id` / `contributor_id`.
  - **Test split contributors must be disjoint from training split contributors**.
  - If recruitment volume limits contributor disjointness, this will be recorded transparently as a known limitation.
  - Near-identical sentences must never be split across train and test.

### 6.2 Revised Inclusion Rule for Code-Mixing
- **Lexical Threshold**: At least **one unambiguous lexical token** from every participating language required by the category.
- **Exclusions**: Named entities (`NE`), punctuation/symbols (`OTHER`), and ambiguous tokens (`MIXED`/-100) do not satisfy language presence checks.
- **Switch Density**: `language_switch_count` and `language_token_counts` are recorded per record to enable analyzing dense code-mixing as a separate subset without arbitrarily disqualifying valid single-switch sentences.
- **Scope Clarification**: This is a dataset engineering scope decision, not a universal definition of code-switching.

---

## 7. Pilot-Driven Collection Methodology

1. **Unsupported Estimates Removed**: Speculative collection quotas (e.g. 125 for B, 135 for C, 150 for D) have been removed.
2. **Empirical Pilot Protocol**:
   - Author **10 pilot candidate sentences per category** (40 total) across 3 independent contributors.
   - Run the full two-stage review pipeline (linguistic screening and token LID audit).
   - Compute actual empirical acceptance rates ($A_{\text{pilot}} = N_{\text{approved}} / N_{\text{drafted}}$) to calculate the final required authoring workload ($N_{\text{required}} = 100 / A_{\text{pilot}}$).
3. **Category Feasibility**:
   - Category A: Achievable from BHT25 (`licensed_corpus_extraction`), subject to human quality review and deduplication.
   - Categories B, C, D: Achievable via structured multi-contributor elicitation with empirical pilot buffers.

---

## 8. Sample Inspection Evidence & Outstanding Uncertainties

### 8.1 Inspection Evidence Verified
- **BHT25**: Exactly **20 sample triplets** were streamed via the public Hugging Face datasets-server REST API (`id`, `bn`, `hi`, `te`). Zero Parquet files were downloaded.
- **All Other Corpora**: **0 rows downloaded**. All evaluations relied on public metadata, dataset cards, and release manifests to prevent benchmark contamination or gate violations.
- **LTRC**: Gated status confirmed from public metadata. Zero gated access was attempted.

### 8.2 Outstanding Uncertainties Requiring Future Action
1. **Mozilla Common Voice Telugu 27.0**: Await formal clarification from Mozilla regarding the concurrent CC0 declaration and no-rehosting clause.
2. **AI4Bharat IndicCorp Telugu**: Await written clarification from AI4Bharat regarding data licensing for web-scraped corpora.
3. **Institutional Review**: Submit custom dataset provenance blueprint to faculty/institutional research ethics committee prior to public release.

---

## 9. Final Status & Verification

All three custom dataset JSONL files remain at **zero records (0 bytes)**. All unified LID datasets in `data/processed/language_identification/` remain untouched. Step 25C corrections are finalized and ready for pilot candidate planning.
