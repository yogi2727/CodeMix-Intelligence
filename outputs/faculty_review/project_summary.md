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
