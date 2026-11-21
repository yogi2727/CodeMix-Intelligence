# CodeMix Intelligence V2.0.0 — Model Cards

This document provides formal Model Cards for both production models integrated within CodeMix Intelligence V2.0.0.

---

# Model Card 1: MuRIL Token-Level Language Identification Baseline

## 1. Model Details
- **Model Name:** CodeMix Intelligence MuRIL LID Baseline
- **Base Architecture:** `google/muril-base-cased` (Multilingual Representations for Indian Languages)
- **Model Type:** Transformer Encoder with Linear Sequence Classification Head
- **Parameter Count:** ~237 Million parameters (199 weight tensors in safetensors format)
- **Vocabulary Size:** 197,285 WordPiece tokens
- **Output Classes (4):**
  - `EN (0)`: English
  - `HI (1)`: Hindi (Devanagari script and Romanized Hinglish)
  - `TE (2)`: Telugu (Telugu script and Romanized Tenglish)
  - `OTHER (3)`: Numbers, punctuation, symbols, universal tokens
- **Release Version:** 1.0.0 (Preserved in V2.0.0)
- **License:** Apache 2.0 (Pretrained backbone) / Research Artifact

## 2. Intended Use
- **Primary Use Case:** Token-level and word-level language identification in multilingual, code-mixed, and transliterated sentences common in Indian digital media.
- **Target Applications:** Social media text normalization, multilingual customer support triage, acoustic model routing, linguistic analysis.
- **Supported Scripts:** Latin script (transliterated / Romanized), Devanagari script, Telugu script.

## 3. Out-of-Scope Uses & Limitations
- **Not a Translation Engine:** This model performs token sequence classification only; it cannot translate, rephrase, or generate text.
- **Language Boundaries:** Specifically trained for English, Hindi, and Telugu. Other Indic languages (e.g., Tamil, Bengali, Marathi) will be categorized as `OTHER` or misclassified.
- **WordPiece Aggregation:** Predictions are aggregated across WordPiece subword tokens via first-subword token mapping; edge cases with unconventional typographical splittings may experience reduced precision.

## 4. Training Data & Preprocessing
- **Source Corpora:**
  - COMI-LINGUA (Hindi-English code-mixed)
  - Telugu-English Blog Corpus
  - Telugu-English Twitter Corpus
- **Dataset Partitioning:**
  - Training Set: 4 Epochs, 5,420 steps (NVIDIA A100 GPU FP16)
  - Supervised Validation Tokens: 24,902 tokens
  - Locked Test Set: 14,855 records / 199,219 supervised evaluation tokens

## 5. Evaluation & Performance Metrics

### Locked Test Set Results (199,219 Tokens)
| Metric | Value |
| :--- | :---: |
| **Overall Accuracy** | **98.1744%** |
| **Macro F1-Score** | **98.0092%** |

### Per-Class Performance
| Class | Label | Precision | Recall | F1-Score | Support (Tokens) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **English (`EN`)** | 0 | 97.47% | 97.63% | **97.5511%** | 64,221 |
| **Hindi (`HI`)** | 1 | 98.59% | 98.89% | **98.7405%** | 69,130 |
| **Telugu (`TE`)** | 2 | 98.81% | 98.61% | **98.7103%** | 45,252 |
| **Other (`OTHER`)** | 3 | 97.56% | 96.51% | **97.0349%** | 20,616 |

---

# Model Card 2: mT5-Small Romanized Hinglish-to-English Translation

## 1. Model Details
- **Model Name:** CodeMix Intelligence mT5 Hinglish-to-English Translation Baseline
- **Base Architecture:** `google/mt5-small` (multilingual Text-to-Text Transfer Transformer)
- **Model Type:** Encoder-Decoder Sequence-to-Sequence Transformer
- **Parameter Count:** ~300 Million parameters (190 weight tensors in safetensors format, ~1.14 GB FP32)
- **Vocabulary Size:** 250,100 SentencePiece tokens
- **Task Prefix:** `"translate Hinglish to English: "`
- **Release Version:** 1.0.0 (Integrated into CodeMix Intelligence V2.0.0)
- **Fine-Tuning Framework:** Hugging Face `transformers` 5.22.0, PyTorch 2.11.0+cu130 (Training) / PyTorch 2.15.0+cpu (Inference)
- **License:** Apache 2.0 (Pretrained backbone) / CC BY 4.0 (Fine-tuning dataset)

## 2. Intended Use
- **Primary Use Case:** Translating informal, Romanized Hinglish sentences (Hindi written using Latin script, often mixed with English vocabulary) into standardized, grammatically coherent English sentences.
- **Target Applications:** Cross-lingual chat comprehension, content moderation preprocessing, machine translation aid for conversational agents.

## 3. Out-of-Scope Uses & Explicit Scope Boundary

> [!WARNING]
> **Strict Domain Boundary:**
> Model 2 is trained and evaluated solely on **Romanized Hinglish-to-English** translation.
> - **NOT a Telugu Translation Model:** Model 2 has **not** been trained or evaluated on Telugu-to-English or Tenglish-to-English translation. Passing Romanized Telugu or Telugu script to this model will produce hallucinated or inaccurate translations. Telugu inputs must be analyzed using Model 1 for language tagging.
> - **NOT Bidirectional:** The model only translates Hinglish $\rightarrow$ English, not English $\rightarrow$ Hinglish.

## 4. Training Data & Preprocessing
- **Dataset:** PHINC (Parallel Hinglish Dataset)
- **Data License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Dataset Partitions:**
  - **Train:** 10,802 parallel pairs
  - **Validation:** 1,350 parallel pairs
  - **Test (Held-out):** 1,351 parallel pairs (SHA-256: `7cd192e2d65b1cd7c3b8b725690cf9e0f0e948e3ace3650235f832ae8ca8bf20`)
- **Preprocessing:** Strip leading/trailing whitespace, enforce minimum token length, normalize non-standard punctuation.

## 5. Evaluation Metrics & Benchmark Performance

### Held-Out Test Evaluation (1,351 Records)
| Metric | Benchmark Score | Interpretation |
| :--- | :---: | :--- |
| **BLEU** | **25.3784** | Standard corpus n-gram precision metric ($0-100$ scale). |
| **chrF** | **43.2323** | Character n-gram F-score ($0-100$ scale), robust to transliteration variance. |

> [!IMPORTANT]
> **Metric Clarification:**
> BLEU and chrF scores represent geometric and harmonic corpus overlaps against reference translations. They are **not** percentage accuracy rates. A BLEU of 25+ on informal code-mixed user text represents strong translation utility.

### Validation Set Comparison
- **Validation Loss:** 2.3983
- **Validation BLEU:** 45.50
- **Validation chrF:** 37.71

## 6. Technical Specifications & Generation Hyperparameters

```python
{
    "prefix": "translate Hinglish to English: ",
    "precision": "FP32 (torch.float32)",
    "num_beams": 4,
    "max_source_length": 128,  # Limits encoder input sequence
    "max_length": 128,  # Caps generated decoder sequence (including decoder-start token)
    "do_sample": False,
    "early_stopping": False,  # Default in generation_config.json
    "no_repeat_ngram_size": 0,  # Default in generation_config.json
    "length_penalty": 1.0  # Default in generation_config.json
}
```

> [!NOTE]
> **Sequence Length Semantics:** `max_source_length=128` limits the encoder input, while `max_length=128` caps the generated decoder sequence (including the decoder-start token). It does not represent a combined encoder-input-plus-decoder-output length.

## 7. Known Limitations & Failure Modes
- **Colloquial Slang & Transliteration Noise:** Romanized Hindi lacks standardized spelling rules (e.g., *"kya"* vs *"kyaa"*, *"bahut"* vs *"bhot"*). Highly divergent or heavily misspelled slang may lead to omitted clauses.
- **Ambiguous Code-Switching:** Sentences with dense, alternating English/Hindi clauses may sometimes retain untranslated Hindi words if the subwords were not well-represented in the vocabulary.
- **Named Entities:** Indian proper names or localized brand names might occasionally be transliterated incorrectly or translated phonetically.

