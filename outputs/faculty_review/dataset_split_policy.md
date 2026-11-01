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
