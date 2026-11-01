# CodeMix Intelligence Artifacts Repository

This directory contains the trained model artifacts, evaluation results, and data bundles for the CodeMix Intelligence token-level Language Identification (LID) system.

---

## 1. Primary Model Specifications

* **Base Pretrained Model:** `google/muril-base-cased` (Multilingual Representations for Indian Languages)
* **Architecture:** 12-layer Transformer encoder (768 hidden dimensions, 12 attention heads) with a 4-class token classification head (`nn.Linear(768, 4)`).
* **Task:** Token-Level Trilingual Sequence Classification for Code-Mixed Social Media Text.
* **Target Label Taxonomy:**
  - `EN = 0`: English
  - `HI = 1`: Hindi (Devanagari script & Romanized transliterations)
  - `TE = 2`: Telugu (Romanized transliterations)
  - `OTHER = 3`: Universal / Symbols / Punctuation / Numbers
  - `IGNORED = -100`: Named Entities (`NE`), mixed-script morphological fusions, ambiguous tokens, null annotations, WordPiece continuation subwords (`##...`), and special tokens (`[CLS]`, `[SEP]`, `[PAD]`).
* **Selected Best Checkpoint:** `checkpoint-5000` (Restored via `load_best_model_at_end=True` monitoring validation Macro F1).
* **Training Schedule Completed:** 4 epochs (5,420 optimization steps evaluated, 5,424 total), AdamW ($3 \times 10^{-5}$), linear decay with 10% warmup (542 steps), effective batch size 32.

---

## 2. Benchmark Performance Summary

| Split / Metric | Accuracy | Macro F1 | Macro Precision | Macro Recall |
| :--- | :---: | :---: | :---: | :---: |
| **Validation Set** (`validation.jsonl`, 4,820 records) | 97.8195% | **97.4904%** | — | — |
| **Locked Test Set** (`test.jsonl`, 14,855 records) | **98.1744%** | **98.0092%** | 98.1094% | 97.9106% |

### Per-Class Performance on Locked Test Set (199,219 Supervised Tokens)

| Language Class | Precision | Recall | F1-Score | Support (Tokens) |
| :--- | :---: | :---: | :---: | :---: |
| **English (`EN: 0`)** | 97.47% | 97.63% | **97.55%** | 64,221 |
| **Hindi (`HI: 1`)** | 98.59% | 98.89% | **98.74%** | 69,130 |
| **Telugu (`TE: 2`)** | 98.81% | 98.61% | **98.71%** | 45,252 |
| **Universal / Other (`OTHER: 3`)** | 97.56% | 96.51% | **97.03%** | 20,616 |

### Confusion Matrix (Locked Test Set)

```
True \ Pred       EN       HI       TE    OTHER
EN            62,701      704      449      367
HI               678   68,362        1       89
TE               427      162   44,622       41
OTHER            523      110       86   19,897
```

### Source-Wise Evaluation Breakdown

* **COMI-LINGUA** (Hindi-English Code-Mixed): Accuracy **98.11%**, Macro F1 **97.27%** (Classes: EN, HI, OTHER).
* **Telugu-English Blog** (Romanized Telugu-English): Accuracy **98.64%**, Macro F1 **97.27%** (Classes: EN, TE, OTHER).
* **Telugu-English Twitter** (Romanized Telugu-English): Accuracy **97.94%**, Macro F1 **98.09%** (Classes: EN, TE, OTHER).

---

## 3. Directory Layout

```
artifacts/
├── README.md                                   # This reference document
├── colab/                                      # Data bundles for Google Colab GPU training/eval
│   ├── muril_lid_data_bundle.zip               # Canonical train & val data bundle (~2.84 MB)
│   └── muril_lid_test_bundle.zip               # Locked test evaluation bundle (~2.11 MB)
├── evaluation/
│   └── muril_lid_baseline/                     # Official evaluation artifacts
│       ├── LOCKED_TEST_EVALUATION_COMPLETE.json # Evaluation completion receipt
│       ├── locked_test_results.json            # Complete classification report & metrics
│       ├── source_wise_results.json            # High-level source evaluations
│       ├── source_subset_metrics_posthoc.json  # Disaggregated subset evaluations
│       └── confusion_matrix.csv                # 4x4 Confusion matrix CSV
└── models/
    └── muril_lid_baseline/
        └── best_model/                         # Fine-tuned MuRIL baseline model
            ├── config.json                     # Hugging Face model configuration
            ├── model.safetensors               # Trained model weights (947,898,192 bytes)
            ├── tokenizer_config.json           # Tokenizer settings & special token maps
            ├── special_tokens_map.json         # Special token definitions
            ├── vocab.txt                       # MuRIL WordPiece vocabulary (197,258 tokens)
            └── training_args.bin               # PyTorch training arguments binary
```

---

## 4. Critical Engineering & Research Governance Notes

1. **Frozen Trained Weights:** The model weights in `artifacts/models/muril_lid_baseline/best_model/` are fully fine-tuned and verified. The model **must not be retrained or fine-tuned** during backend application integration. All downstream serving and inference components must load these weights in read-only evaluation mode (`model.eval()`).
2. **Linguistic Scope & Script Limitations:**
   - In the current benchmark, **Telugu is strictly Romanized (Latin script transliteration)**.
   - Native-script Telugu (Telugu Unicode block `U+0C00` to `U+0C7F`) was not part of the training distribution, although MuRIL's vocabulary supports the script.
   - Trilingual mixed sentences simultaneously containing Hindi, Telugu, and English within a single clause have not been formally evaluated (the current benchmark consists of Hindi-English and Telugu-English bilingual pairs).
3. **Subword Alignment Policy:** Token-level inference must replicate the training alignment policy: each input sentence is tokenized into whitespace tokens, subwords are generated per token, and the prediction from the first subword corresponds to the token's predicted language label.
