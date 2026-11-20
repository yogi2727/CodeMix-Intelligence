# CodeMix Intelligence — mT5-small Hinglish-to-English Baseline
## Google Colab Training Guide & Operational Runbook

**Document Version:** 1.0.0  
**Phase:** Step 34D — Colab Training Preparation  
**Model Target:** `google/mt5-small` (~300M parameters, Multilingual T5)  
**Task:** Romanized Hinglish Code-Mixed Sentence $\rightarrow$ Natural English Translation  
**Corpus:** PHINC (Parallel Hinglish Social Media Corpus, W-NUT 2020)  
**License:** CC BY 4.0  
**Target Execution Environment:** Google Colab GPU (NVIDIA T4 16GB VRAM)  
**Parent Branch:** `feature/mt5-translation-v2`  
**Protected Baseline:** `v1.0.0` (MuRIL LID Engine)  

---

## 1. Overview & Objective

This package provides a completely reproducible, self-contained, and leakage-controlled training pipeline for fine-tuning `google/mt5-small` to translate Romanized Hinglish sentences into natural English.

The training notebook (`training/colab/mt5_phinc_hinglish_baseline.ipynb`) is designed to run in a standard Google Colab GPU environment (such as an NVIDIA T4 instance). All checkpoints, validation metrics, and model exports are automatically synced to Google Drive.

```
+-------------------------------------------------------------------------+
|                  Local Workstation (CodeMix Intelligence)               |
|                                                                         |
|  phinc_train.jsonl (10,802) + phinc_val.jsonl (1,350) + Manifest        |
|                                |                                        |
|                                v                                        |
|              artifacts/colab/mt5_phinc_training_bundle.zip              |
|              (Size: 1.38 MB | SHA-256: d2af7d5a193b6418...)             |
+--------------------------------+----------------------------------------+
                                 |
                                 | Upload to Google Drive
                                 v
+-------------------------------------------------------------------------+
|                    Google Drive Persistent Storage                      |
|                                                                         |
|  MyDrive/CodeMix_Intelligence/mt5_phinc_training_bundle.zip             |
|  MyDrive/CodeMix_Intelligence/mt5_phinc_baseline/                       |
|    |-- checkpoints/      (Epoch checkpoints, max 2)                     |
|    |-- best_model/       (Best validation BLEU checkpoint)              |
|    |-- metrics/          (validation_metrics.json, training_history)    |
|    |-- metadata/         (environment.json, training_config, model card)|
|    +-- mt5_phinc_baseline_best_model.zip                                |
+--------------------------------+----------------------------------------+
                                 ^
                                 | Bi-directional Mount & Run
                                 v
+-------------------------------------------------------------------------+
|                    Google Colab Runtime (NVIDIA T4)                     |
|                                                                         |
|  mt5_phinc_hinglish_baseline.ipynb                                      |
|  - Cryptographic verification of bundle SHA-256                         |
|  - Model & tokenizer loading (google/mt5-small)                         |
|  - Tokenization preflight audit (Zero silent truncation)                |
|  - Seq2Seq fine-tuning (Effective Batch Size 16, lr=1e-4, 3 epochs)     |
|  - Generation-based validation (SacreBLEU + chrF++)                     |
|  - Automatic export of best model                                       |
+-------------------------------------------------------------------------+
```

---

## 2. Why the Test Dataset is Excluded (Anti-Leakage Safeguard)

In standard machine learning practice, evaluating on the test set during training or using test set metrics to tune hyperparameters, pick learning rates, select epochs, or trigger early stopping leads to **data snooping and contaminated evaluation**.

To maintain strict scientific integrity:
1. **Physical Isolation:** The project test split (`phinc_test.jsonl`, 1,351 records) is **completely omitted** from `mt5_phinc_training_bundle.zip`. It resides exclusively on the local workstation.
2. **Zero Test Code in Colab:** The Colab notebook does not contain any code cells that load, parse, or evaluate on test data.
3. **Validation-Only Selection:** All checkpoint comparisons, early stopping decisions, and hyperparameter evaluations use `phinc_validation.jsonl` (1,350 records) exclusively.
4. **Final Locked Evaluation:** Once the model is trained and imported back to the local repository, final evaluation will be conducted against the locked test set in an isolated, one-pass benchmark step (Step 34F).

---

## 3. Step-by-Step Colab Execution Runbook

### Step 1: Upload the Training Bundle to Google Drive
Before launching Colab, place the training bundle in your Google Drive:

1. Locate the local bundle:  
   `artifacts/colab/mt5_phinc_training_bundle.zip`
2. Open [Google Drive](https://drive.google.com).
3. Create a folder named: `CodeMix_Intelligence` in `MyDrive`.
4. Upload `mt5_phinc_training_bundle.zip` to:  
   `MyDrive/CodeMix_Intelligence/mt5_phinc_training_bundle.zip`

*(Note: If you omit this step, Cell C2 of the notebook will offer an interactive file upload widget).*

### Step 2: Open and Configure the Notebook in Colab
1. Navigate to [Google Colab](https://colab.research.google.com).
2. Click **Upload** and select `training/colab/mt5_phinc_hinglish_baseline.ipynb`.
3. Configure the GPU accelerator:
   - Click **Runtime** in the top menu $\rightarrow$ **Change runtime type**.
   - Under **Hardware accelerator**, select **T4 GPU** (Standard free tier GPU).
   - Click **Save**.

### Step 3: Run the Notebook Sequentially
Execute the notebook cells top-to-bottom (`Shift + Enter` on each cell, or **Runtime $\rightarrow$ Run all**):

| Section | Cell / Step | Description | Expected Output / Checks |
| :--- | :--- | :--- | :--- |
| **Section B** | Cell B1 | GPU Hardware Inspection | Checks CUDA availability, GPU device name (`Tesla T4`), total VRAM ($\approx 15.0$ GB). Raises `RuntimeError` if GPU is missing. |
| | Cell B2 | Package Installation | Installs `transformers`, `accelerate`, `sentencepiece`, `sacrebleu`, `safetensors`. |
| | Cell B3 | Reproducibility Seeds | Sets random seed to `42` across Python, NumPy, PyTorch, and CUDA. |
| **Section C** | Cell C1 | Mount Google Drive | Prompts Google authentication. Mounts `/content/drive`. Creates output directory tree. |
| | Cell C2 | Ingest & Verify Bundle | Copies bundle from Drive and computes SHA-256. Validates against expected hash: `d2af7d5a193b641878f34b19f1a0dab5dd1ff65cc7c78c87f76884e31b87ff60`. |
| **Section D** | Cell D1 | Extract Bundle | Verifies archive has exactly 3 members. Asserts zero test data files. Unpacks to `/content/CodeMix_Intelligence_mt5_phinc_data`. |
| | Cell D2 | Split Data Validation | Validates Train SHA-256 (`f9b9b4e5...`), Val SHA-256 (`b63971bb...`), row counts (10,802 / 1,350), and zero ID overlap. |
| **Section E** | Cell E1 | Load Pretrained mT5 | Loads `google/mt5-small` and SentencePiece tokenizer. Reports ~300M parameters, 250,100 vocabulary tokens. |
| **Section F** | Cell F1 | Task Prefix Formatting | Enforces canonical prefix: `translate Hinglish to English: ` on source inputs only. |
| **Section G** | Cell G1 | Tokenization Preflight | Audits token lengths across all 12,152 examples. Chooses safe sequence lengths (`MAX_SOURCE_LENGTH=128`, `MAX_TARGET_LENGTH=128`) ensuring **zero silent truncation**. |
| **Section H** | Cell H1 | PyTorch Datasets | Creates `train_dataset` and `val_dataset`. Configures `DataCollatorForSeq2Seq` with dynamic padding and `-100` target padding masking. |
| **Section I** | Cell I1 | Generation Metrics | Configures generation-based evaluation using `sacrebleu.corpus_bleu` and `sacrebleu.corpus_chrf`. Decodes tokens and strips `-100`. |
| **Section J** | Cell J1 | Training Arguments | Sets effective batch size 16 (4 batch $\times$ 4 grad accum), lr 1e-4, 3 epochs, evaluation/saving per epoch, best model via validation BLEU, FP16 enabled. |
| **Section K/L** | Cell L1/L2 | Training Execution | Runs `Seq2SeqTrainer.train()`. Evaluates at epoch boundaries. Restores best validation checkpoint automatically. |
| **Section M** | Cell M1 | Save Best Model | Exports model weights, tokenizer, and `task_config.json` to Google Drive `best_model/`. Verifies reloadability. |
| **Section N** | Cell N1 | Save Metrics & Cards | Writes `validation_metrics.json`, `training_history.json`, `environment.json`, and `model_card.md` to Drive. |
| **Section P** | Cell P1 | Export Model ZIP | Compresses `best_model/` to `mt5_phinc_baseline_best_model.zip`. Computes archive size and SHA-256. |
| **Section Q** | Cell Q1 | Sample Inference | Runs live Hinglish-to-English translation on sample sentences. |

---

## 4. Output Artifacts in Google Drive

When training completes, the following files will be stored in your Google Drive under:  
`/content/drive/MyDrive/CodeMix_Intelligence/mt5_phinc_baseline/`

```
mt5_phinc_baseline/
├── best_model/
│   ├── config.json
│   ├── generation_config.json
│   ├── model.safetensors (or pytorch_model.bin)
│   ├── spiece.model
│   ├── special_tokens_map.json
│   ├── task_config.json
│   ├── tokenizer_config.json
│   └── tokenizer.json
├── checkpoints/
│   ├── checkpoint-<step_A>/
│   └── checkpoint-<step_B>/
├── metrics/
│   ├── best_checkpoint_info.json
│   ├── training_history.json
│   └── validation_metrics.json
├── metadata/
│   ├── environment.json
│   ├── model_card.md
│   └── training_config.json
└── mt5_phinc_baseline_best_model.zip  <-- Download this archive!
```

---

## 5. How to Download and Bring Model Back to Local Repository

1. In Google Drive, navigate to `MyDrive/CodeMix_Intelligence/mt5_phinc_baseline/`.
2. Locate `mt5_phinc_baseline_best_model.zip` (and optionally the `metrics/` folder).
3. Download the ZIP file to your local computer.
4. In Step 34F (Evaluation and Deployment), the ZIP file will be placed into:  
   `artifacts/models/mt5_phinc_baseline/`  
   and verified with its SHA-256 checksum before running the local locked test evaluation.

---

## 6. How to Avoid Accidental Test Set Contamination

To ensure full compliance with scientific evaluation standards:
1. **Never upload `phinc_test.jsonl` to Google Drive or Colab.**
2. **Never attempt to concatenate the test set with validation or training splits.**
3. **Do not use final test BLEU scores to decide whether to change learning rates or training epochs.** Any hyperparameter search must be evaluated solely on validation BLEU (`phinc_validation.jsonl`).
4. **The test set is a locked benchmark:** It is evaluated only once on the final selected model checkpoint.

---

## 7. Scope and Language Limitations

- **Script:** Primarily Romanized Hinglish (Hindi written in Latin script, mixed with English vocabulary).
- **Telugu Support:** `PHINC` is a Hindi-English dataset; this model has **not** been fine-tuned on Telugu-English translation. Do not make claims regarding Telugu translation capability for this baseline.
- **Devanagari Coverage:** Only two Devanagari sentences were present in the cleaned candidate dataset; do not claim native Devanagari translation capability.
- **Baseline Nature:** This is a controlled experimental baseline. It establishes the benchmark against which subsequent architectural and data enhancements will be evaluated.
