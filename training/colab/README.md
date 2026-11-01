# Google Colab MuRIL Baseline Training Guide

This directory contains the standalone Google Colab training notebook and documentation for fine-tuning `google/muril-base-cased` on token-level Language Identification (LID) for Code-Mixed English, Hindi, and Telugu.

---

## Directory Structure

```
training/colab/
├── muril_lid_baseline.ipynb    # Main Google Colab fine-tuning notebook (37 cells, nbformat v4)
└── README.md                   # This instruction and execution guide
```

Companion Data Bundle (in repository artifacts):
```
artifacts/colab/
└── muril_lid_data_bundle.zip   # Canonical training and validation data bundle (~2.98 MB)
```

---

## Step-by-Step Execution Guide in Google Colab

### 1. Launch Google Colab
1. Open your web browser and navigate to [Google Colab](https://colab.research.google.com/).
2. Click **Upload** in the dialog box and upload [`training/colab/muril_lid_baseline.ipynb`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/training/colab/muril_lid_baseline.ipynb).

### 2. Configure Hardware Accelerator
1. In Colab, click **Runtime** in the top navigation bar.
2. Select **Change runtime type**.
3. Under **Hardware accelerator**, select **T4 GPU** (Standard tier) or **A100 GPU** (Colab Pro).
4. Click **Save**.

### 3. Mount Google Drive (Stage B)
- Execute Stage B to mount Google Drive. This enables persistent checkpoint and metric archiving under:
  `/content/drive/MyDrive/CodeMix_Intelligence/muril_lid_baseline/`
- Alternatively, you can upload `muril_lid_data_bundle.zip` directly to your Google Drive root or `/content/`.

### 4. Upload the Training Data Bundle (Stage E)
- When executing Stage E, the notebook will check for `muril_lid_data_bundle.zip`.
- If not already in Google Drive or `/content/`, a file picker will appear. Select [`artifacts/colab/muril_lid_data_bundle.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/colab/muril_lid_data_bundle.zip) from your local computer.
- The bundle extracts automatically into `/content/codemix_intelligence/data/`.

### 5. Automated Pre-Training Verifications (Stages F – L)
The notebook will automatically perform:
- **Manifest & Integrity Check (Stage F):** Verifies 43,369 train records, 4,820 validation records, and asserts **zero test set presence**.
- **Dataset Parsing (Stage G):** Loads records into Hugging Face `Dataset` format.
- **Tokenizer Setup (Stage H):** Loads `google/muril-base-cased` with vocabulary of 197,258 tokens.
- **WordPiece Subword Alignment (Stage I):** Assigns target labels to first subwords and masks continuation subwords (`##...`), special tokens (`[CLS]`, `[SEP]`, `[PAD]`), and ignored tags (`NE`, `null`) with `-100`.
- **Bijection Assertions (Stage J):** Verifies that for every sentence, the count of supervised whitespace words exactly equals the count of supervised subword prediction positions.
- **Model Instantiation (Stage K):** Attaches a 4-class linear head (`0: EN`, `1: HI`, `2: TE`, `3: OTHER`).
- **GPU Smoke Test (Stage L):** Runs 1 forward pass and 1 backward pass on a 16-sample batch to verify finite cross-entropy loss and VRAM headroom without Out-Of-Memory (OOM) errors.

### 6. Execute Fine-Tuning (Stage P)
- Execute the dedicated training cell in Stage P (`trainer.train()`).
- **Expected Duration:** ~35 to 45 minutes on Google Colab NVIDIA T4 GPU (4 epochs, 5,424 optimization steps).
- Training logs loss and validation metrics every 500 steps.
- Early stopping automatically halts training if validation Macro F1 fails to improve for 3 consecutive evaluation cycles.

### 7. Review Final Metrics & Save Weights (Stages Q – R)
- Stage Q runs a final evaluation over `validation.jsonl` using the best checkpoint.
- Stage R saves the best model weights, tokenizer, and metrics to Google Drive:
  - `best_model/model.safetensors`
  - `best_model/config.json`
  - `best_model/vocab.txt`
  - `final_validation_metrics.json`

---

## Technical Specifications Summary

| Hyperparameter | Value | Description |
| :--- | :--- | :--- |
| **Model Backbone** | `google/muril-base-cased` | 12-layer Transformer, 768 hidden dimension |
| **Output Classes** | `4` | `EN: 0`, `HI: 1`, `TE: 2`, `OTHER: 3` |
| **Masked Label** | `-100` | Ignored by `CrossEntropyLoss` |
| **Max Sequence Length** | `256` | 100% sentence preservation (max observed length: 217) |
| **Per-Device Batch Size** | `16` | Micro-batch size per forward-backward pass |
| **Gradient Accumulation** | `2` | 2 micro-batches per optimization step |
| **Effective Batch Size** | `32` | Standard effective batch size |
| **Learning Rate** | `3e-5` | AdamW optimizer with weight decay 0.01 |
| **LR Scheduler** | `linear` | Linear decay with 10% warmup (542 steps) |
| **Epochs** | `4` | 1,356 steps/epoch $\rightarrow$ 5,424 total steps |
| **Evaluation Strategy** | Every `500` steps | 11 evaluation checkpoints total |
| **Early Stopping** | Patience `3` | Monitors validation Macro F1 |
| **Primary Metric** | `eval_macro_f1` | Unweighted macro average over EN, HI, TE, OTHER |

---

## Research Governance & Test Set Isolation

In accordance with empirical machine learning methodology:
1. **Zero Test Data:** `test.jsonl` is excluded from the data bundle and the Colab notebook.
2. **Model Selection Integrity:** The best model checkpoint is chosen exclusively based on `validation.jsonl` Macro F1.
3. **Locked Test Benchmark:** Test set evaluation is strictly reserved for Step 32 after the fine-tuned model weights are locked.
