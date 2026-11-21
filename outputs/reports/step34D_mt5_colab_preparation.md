# CodeMix Intelligence — Step 34D Completion Report
## Reproducible mT5-small Google Colab Training Package Preparation
### Romanized Hinglish-to-English Translation Baseline (V2)

**Document Version:** 1.0.0  
**Generated At (UTC):** 2026-11-02T13:02:19.063239+00:00  
**Workspace:** `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`  
**Active Development Branch:** `feature/mt5-translation-v2`  
**Stable Release Tag:** `v1.0.0` (at commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`)  
**GitHub Remote:** `https://github.com/yogi2727/CodeMix-Intelligence.git`  
**Model Target:** `google/mt5-small` (~300M parameters, Seq2Seq Transformer)  
**Task:** Romanized Hinglish sentence $\rightarrow$ Natural English translation  
**Corpus:** PHINC (Parallel Hinglish Social Media Corpus, W-NUT 2020)  
**Status:** **PASSED & VERIFIED (TRAINING NOT EXECUTED LOCALLY)**  

---

## 1. Executive Summary

In Step 34D, we prepared a complete, reproducible, and strictly leakage-isolated training package for fine-tuning `google/mt5-small` on Google Colab.

All deliverables were prepared and programmatically validated:
1. **Clean Branch & Protected V1:** Branch is `feature/mt5-translation-v2`, `v1.0.0` ancestry is intact, and MuRIL model weights (`model.safetensors`, SHA-256 `714defc6...`) are completely untouched.
2. **Bitwise Dataset Split Verification:** Training (`phinc_train.jsonl`, 10,802 records) and Validation (`phinc_validation.jsonl`, 1,350 records) splits match their authoritative hashes. The locked test split (`phinc_test.jsonl`, 1,351 records) was verified by hash only and remains immutably locked on the local workstation.
3. **Hermetic Training Bundle:** Created `artifacts/colab/mt5_phinc_training_bundle.zip` (1,387,072 bytes, SHA-256: `d2af7d5a193b641878f34b19f1a0dab5dd1ff65cc7c78c87f76884e31b87ff60`). It contains **strictly three files**: `phinc_train.jsonl`, `phinc_validation.jsonl`, and `training_bundle_manifest.json`. Zero test records are included.
4. **Colab Jupyter Notebook:** Created `training/colab/mt5_phinc_hinglish_baseline.ipynb` (37 cells, 19 code cells, 18 markdown cells) with complete end-to-end instructions from Sections A through Q. All code cells pass Python AST parsing.
5. **Colab README & Config:** Created comprehensive runbook `training/colab/mt5_phinc_hinglish_baseline_README.md` and training configuration `training/colab/mt5_phinc_training_config.json`.
6. **Strict Anti-Leakage Safeguard:** No test loading, no test evaluation, and no test metrics are present in the Colab notebook. Model checkpoint selection is strictly driven by validation SacreBLEU.

---

## 2. Section A: Branch and V1 Integrity

| Property | Value | Verification Status |
| :--- | :--- | :--- |
| **Current Branch** | `feature/mt5-translation-v2` | Matches requirement |
| **Head Commit** | `e2902aac5ba1` | Verified |
| **Stable Tag** | `v1.0.0` | Verified |
| **V1 Tag Commit** | `c9509f0e9e10fe715c759edc09d1dacadb540f74` | Matches authoritative commit |
| **V1 Merge Base** | `c9509f0e9e10fe715c759edc09d1dacadb540f74` | `v1.0.0` is direct ancestor |
| **Working Tree (Tracked Files)** | Clean (0 modified tracked files) | Clean |
| **MuRIL Model Weights** | `artifacts/models/muril_lid_baseline/best_model/model.safetensors` | Untouched |
| **MuRIL Weights SHA-256** | `714defc6f90659ebc25e5e011a9101579d36cf9f3b4c57165c0614f1bc744bae` | Exact match to Step 33A/33D |
| **MuRIL Weights Size** | `947,898,192` bytes (903.99 MB) | Exact match |

---

## 3. Section B: Dataset Splits Verification

Each split file in `data/processed/translation/phinc_hinglish_splits/` was inspected:

| Split | Records | Byte Size | Expected SHA-256 | Actual SHA-256 | Status |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **TRAIN** | 10,802 | 9,563,198 | `f9b9b4e5678c5ce628891d0fa9e53224d4723a8015828a95206ce2a3c34f7f41` | `f9b9b4e5678c5ce628891d0fa9e53224d4723a8015828a95206ce2a3c34f7f41` | **MATCH** |
| **VALIDATION** | 1,350 | 1,199,187 | `b63971bbc05c692279f092c682d6c2bd1e184fe759009a3a52576c5e54500007` | `b63971bbc05c692279f092c682d6c2bd1e184fe759009a3a52576c5e54500007` | **MATCH** |
| **LOCKED TEST** | 1,351 | 1,193,404 | `7cd192e2d65b1cd7c3b8b725690cf9e0f0e948e3ace3650235f832ae8ca8bf20` | `7cd192e2d65b1cd7c3b8b725690cf9e0f0e948e3ace3650235f832ae8ca8bf20` | **MATCH** |

*Note: The locked test file's integrity was verified strictly against its recorded hash without reading, parsing, or copying its sentence records.*

---

## 4. Section C & D: Training Bundle Contents and Checksums

### Bundle File: `artifacts/colab/mt5_phinc_training_bundle.zip`
- **File Size:** 1,387,072 bytes (1.32 MB)
- **SHA-256:** `d2af7d5a193b641878f34b19f1a0dab5dd1ff65cc7c78c87f76884e31b87ff60`
- **Git Ignore Status:** Ignored by `.gitignore` under `artifacts/colab/` (Zero data committed)

### Archive Contents (Exact namelist):
```
1. phinc_train.jsonl                (Size: 9,563,198 bytes | SHA-256: f9b9b4e5...)
2. phinc_validation.jsonl           (Size: 1,199,187 bytes | SHA-256: b63971bb...)
3. training_bundle_manifest.json    (Size: 1,791 bytes | SHA-256: acc45125...)
```

### Verification Findings:
- Total members in archive: **exactly 3**.
- Nested directories: **0** (flat archive structure).
- Test set records present: **0** (`phinc_test.jsonl` is completely absent).
- Candidate / raw / LID datasets present: **0**.
- Split ID overlap between train and validation: **0**.
- Sidecar manifest: `artifacts/colab/mt5_phinc_training_bundle_manifest.json` matches archive SHA-256 bitwise.

---

## 5. Section E & F: Notebook Path, Cell Count, and Structure

### Notebook File: `training/colab/mt5_phinc_hinglish_baseline.ipynb`
- **Total Cells:** 37
- **Code Cells:** 19 (All pass Python AST syntax parsing)
- **Markdown Cells:** 18
- **File Size:** 57,853 bytes
- **SHA-256:** `58fc3d183283d12d9ebd56207acc99447f381d3e9f3c2828764f44c86782d905`

### Section Breakdown:
- **Header & Cover:** Title, project summary, metadata, anti-leakage safeguards.
- **SECTION A — Introduction and safeguards:** Problem context, model architecture (`google/mt5-small`), PHINC corpus, split statistics (10,802 train / 1,350 val / 1,351 locked test), script scope (Romanized Hinglish only; no Telugu translation claims).
- **SECTION B — Runtime setup and hardware verification:** GPU hardware detection (NVIDIA T4, 16GB VRAM, CUDA check, abort if CPU), package installations with version constraints (`transformers>=5.0.0,<6.0.0`, `accelerate>=1.0.0,<2.0.0`, `sentencepiece>=0.2.0,<1.0.0`, `sacrebleu>=2.4.0,<3.0.0`, `safetensors>=0.4.0`), and global seed setting (`42`).
- **SECTION C — Google Drive integration:** Mounts Google Drive (`/content/drive`), establishes persistent directory tree (`checkpoints/`, `best_model/`, `metrics/`, `logs/`, `metadata/`), ingests training bundle and verifies SHA-256 (`d2af7d5a193b641878f34b19f1a0dab5dd1ff65cc7c78c87f76884e31b87ff60`).
- **SECTION D — Bundle extraction and verification:** Unpacks bundle into `/content/CodeMix_Intelligence_mt5_phinc_data/`, verifies 3 files, checks train/validation SHA-256, verifies non-empty text fields, verifies zero ID overlap.
- **SECTION E — Load pretrained google/mt5-small and tokenizer:** Loads `AutoTokenizer` (SentencePiece) and `AutoModelForSeq2SeqLM`, records model parameter count (~300M) and vocabulary size (250,100).
- **SECTION F — Translation task prefix and prompt formatting:** Demonstrates canonical prefix `translate Hinglish to English: ` on source inputs only.
- **SECTION G — Tokenization preflight audit and truncation safeguard:** Audits token lengths across all 12,152 train + val records, establishes `MAX_SOURCE_LENGTH=128`, `MAX_TARGET_LENGTH=128` (multiple of 8, capped at 256), guarantees **zero silent truncation**.
- **SECTION H — Dataset objects and data collator:** Custom PyTorch `Dataset`, `DataCollatorForSeq2Seq` with dynamic padding and `-100` label masking.
- **SECTION I — Generation-based evaluation metrics (SacreBLEU & chrF):** Evaluates decoded text with `sacrebleu.corpus_bleu` and `sacrebleu.corpus_chrf`, decodes with `-100` stripped, records SacreBLEU signature. No classification accuracy.
- **SECTION J — Training configuration and hyperparameters:** Configures `Seq2SeqTrainingArguments` with version-proof parameter inspection (`eval_strategy` vs `evaluation_strategy`), effective batch size 16, FP16/BF16 detection.
- **SECTION K — Checkpointing and Drive storage hierarchy:** Checkpoint directory in Drive, maximum 2 checkpoints (`save_total_limit=2`), model-only saving documentation.
- **SECTION L — Seq2SeqTrainer initialization and execution:** Instantiates `Seq2SeqTrainer` with `EarlyStoppingCallback` (patience = 2), generation-based validation.
- **SECTION M — Save final best model to Google Drive:** Exports best model, tokenizer, and `task_config.json` to Drive `best_model/`, verifies disk reloadability.
- **SECTION N — Training metrics, environment metadata, and model card:** Saves all 7 required metric/metadata files to Drive.
- **SECTION O — Test set protection notice:** Explicit warning stating why test evaluation is omitted.
- **SECTION P — Best model archive export:** Creates `mt5_phinc_baseline_best_model.zip` in Drive, computes SHA-256.
- **SECTION Q — Interactive inference demonstration:** Tests sample Hinglish translations interactively.

---

## 6. Section G: Training Configuration

The configuration is saved to `training/colab/mt5_phinc_training_config.json`:

```json
{
  "model_name": "google/mt5-small",
  "task": "Romanized Hinglish-to-English Translation",
  "task_prefix": "translate Hinglish to English: ",
  "hyperparameters": {
    "seed": 42,
    "num_train_epochs": 3,
    "learning_rate": 0.0001,
    "weight_decay": 0.01,
    "warmup_ratio": 0.06,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "effective_batch_size": 16,
    "per_device_eval_batch_size": 4,
    "lr_scheduler_type": "linear",
    "max_grad_norm": 1.0,
    "logging_strategy": "steps",
    "logging_steps": 50,
    "evaluation_strategy": "epoch",
    "save_strategy": "epoch",
    "load_best_model_at_end": true,
    "metric_for_best_model": "bleu",
    "greater_is_better": true,
    "save_total_limit": 2,
    "early_stopping_patience": 2,
    "generation_num_beams": 4,
    "generation_max_length": 128,
    "max_source_length": 128,
    "max_target_length": 128,
    "fp16": true,
    "bf16": false
  }
}
```

---

## 7. Section H: Tokenization Preflight Design

To prevent silent information loss during tokenization:
1. In Section G, every sample in `train_records` and `val_records` is tokenized without truncation.
2. The notebook computes:
   - Maximum source and target token lengths
   - Median source and target token lengths
   - 95th and 99th percentile token lengths
3. Dynamic Length Selection:
   - Baseline candidate: 128 tokens.
   - If maximum measured length exceeds 128, length is dynamically rounded up to the next multiple of 8, with a hard ceiling at 256 for T4 memory safety.
   - If any sample exceeds the cap, the notebook explicitly warns and counts affected examples.
4. Dynamic batch padding is handled by `DataCollatorForSeq2Seq`, avoiding wasted padding computation.

---

## 8. Section I & J: Validation Metrics & Checkpoint Selection Strategy

- **Evaluation Mode:** Generation-based (`predict_with_generate = True`).
- **Metrics:**
  - **SacreBLEU:** `sacrebleu.corpus_bleu(decoded_predictions, [decoded_references]).score`
  - **chrF++:** `sacrebleu.corpus_chrf(decoded_predictions, [decoded_references]).score`
  - **Validation Loss:** Model cross-entropy on validation tokens with `-100` label masking.
- **Reference Normalization:** Special tokens are stripped, `-100` labels are replaced with `tokenizer.pad_token_id` prior to decoding.
- **Checkpoint Selection:** `metric_for_best_model = "bleu"` with `greater_is_better = True`.
- **Early Stopping:** `EarlyStoppingCallback(early_stopping_patience = 2)`.

---

## 9. Section K: Google Drive Output Structure

When executed on Google Colab, outputs will be written to:
`/content/drive/MyDrive/CodeMix_Intelligence/mt5_phinc_baseline/`

```
mt5_phinc_baseline/
├── best_model/                        <-- Selected best validation model
│   ├── config.json
│   ├── generation_config.json
│   ├── model.safetensors
│   ├── spiece.model
│   ├── special_tokens_map.json
│   ├── task_config.json
│   ├── tokenizer_config.json
│   └── tokenizer.json
├── checkpoints/                       <-- Epoch checkpoints (max 2)
├── metrics/
│   ├── best_checkpoint_info.json
│   ├── training_history.json
│   └── validation_metrics.json
├── metadata/
│   ├── environment.json
│   ├── model_card.md
│   └── training_config.json
└── mt5_phinc_baseline_best_model.zip  <-- Final downloadable model package
```

---

## 10. Section L: Test Set Isolation Verification

| Check | Requirement | Result |
| :--- | :--- | :---: |
| Test file in training bundle | Excluded | **PASS (0 test files in ZIP)** |
| Test file in Colab extraction | Excluded | **PASS** |
| Test file loading code in notebook | Zero occurrences | **PASS (`phinc_test.jsonl` absent from code)** |
| `trainer.predict` on test data | Zero occurrences | **PASS** |
| Test metrics in model selection | Forbidden | **PASS (Validation BLEU only)** |
| Test metrics in training report | Forbidden | **PASS (Test unaccessed)** |

---

## 11. Section M: File Integrity and Verification Summary

All deliverables were programmatically verified via `scratch/validate_step34d.py`:
- [x] Notebook JSON is valid.
- [x] All 19 code cells have syntactically valid Python.
- [x] Notebook contains all expected sections (SECTION A through Q).
- [x] Bundle contains exactly 3 permitted files.
- [x] Training row count is 10,802.
- [x] Validation row count is 1,350.
- [x] Training file SHA-256 matches: `f9b9b4e5678c5ce628891d0fa9e53224d4723a8015828a95206ce2a3c34f7f41`.
- [x] Validation file SHA-256 matches: `b63971bbc05c692279f092c682d6c2bd1e184fe759009a3a52576c5e54500007`.
- [x] Bundle SHA-256 matches sidecar manifest: `d2af7d5a193b641878f34b19f1a0dab5dd1ff65cc7c78c87f76884e31b87ff60`.
- [x] Test data is absent from bundle and notebook.
- [x] Task prefix is consistent: `translate Hinglish to English: `.
- [x] Tokenization preflight prevents silent truncation.
- [x] Validation metrics use generated English translations.
- [x] Best model selection is based on validation BLEU.
- [x] V1 MuRIL model weights strictly untouched (`714defc6f90659ebc25e5e011a9101579d36cf9f3b4c57165c0614f1bc744bae`).

---

## 12. Section N: Dependencies and Runtime Assumptions

| Component | Assumption / Specification |
| :--- | :--- |
| **Execution Platform** | Google Colab (Standard Free or Pro GPU tier) |
| **GPU Target** | NVIDIA Tesla T4 (15.0 - 16.0 GB VRAM) |
| **PyTorch** | Pre-installed Colab PyTorch 2.x with CUDA 12.x |
| **Transformers** | `transformers >= 5.0.0, < 6.0.0` (with dynamic API signature handling) |
| **Accelerate** | `accelerate >= 1.0.0, < 2.0.0` |
| **SentencePiece** | `sentencepiece >= 0.2.0, < 1.0.0` |
| **SacreBLEU** | `sacrebleu >= 2.4.0, < 3.0.0` |
| **Safetensors** | `safetensors >= 0.4.0` |

---

## 13. Section O: Files Created

| File Path | Size | Description |
| :--- | :---: | :--- |
| `artifacts/colab/mt5_phinc_training_bundle.zip` | 1,387,072 B | Self-contained train/val bundle (Git-ignored) |
| `artifacts/colab/mt5_phinc_training_bundle_manifest.json` | 1,169 B | Sidecar manifest with archive size and SHA-256 |
| `training/colab/mt5_phinc_training_config.json` | 2,773 B | Machine-readable training configuration |
| `training/colab/mt5_phinc_hinglish_baseline.ipynb` | 57,853 B | Complete 37-cell Google Colab notebook |
| `training/colab/mt5_phinc_hinglish_baseline_README.md` | 11,799 B | Colab execution runbook and student guide |
| `outputs/reports/step34D_mt5_colab_preparation.md` | (This file) | Comprehensive Step 34D completion report |
| `outputs/reports/step34D_mt5_colab_preparation.json` | (Generated) | Structured JSON verification report |

---

## 14. Section P: Explicit Boundary Commitments & Warnings

1. **NO mT5 TRAINING WAS PERFORMED:** Model fine-tuning was NOT executed in this step.
2. **NO MODEL WEIGHTS DOWNLOADED LOCALLY:** `google/mt5-small` weights were not downloaded to the local repository.
3. **COLAB NOTEBOOK PREPARED BUT NOT EXECUTED:** The notebook has been generated, formatted, and validated for syntax, but has not been run. Execution will occur in Step 34E.
4. **LOCKED TEST DATA UNTOUCHED & UNACCESSED:** `phinc_test.jsonl` was not included in the bundle, opened in the notebook, or read.
5. **STABLE V1.0.0 UNCHANGED:** Version 1 of CodeMix Intelligence (MuRIL LID engine, FastAPI backend, Vanilla frontend) remains 100% untouched and functional.
6. **NO GIT COMMIT CREATED:** In accordance with instructions, no files were staged or committed in Step 34D.
7. **LANGUAGE SCOPE WARNING:** PHINC is Romanized Hinglish. Do not claim Telugu-English translation or native Devanagari translation capability.

---

## 15. Next Step

**STEP 34E — Upload the train/validation bundle to Google Drive and execute mT5-small fine-tuning on a Google Colab GPU.**
