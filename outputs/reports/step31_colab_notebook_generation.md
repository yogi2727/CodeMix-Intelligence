# Step 31: Google Colab MuRIL Baseline Training Notebook Generation Report

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 31 — Generate Google Colab MuRIL Baseline Training Notebook  
**Workspace:** [`C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence)  
**Timestamp:** `2026-11-01T05:26:21.169743+00:00`  
**Status:** **NOTEBOOK GENERATED, BUNDLED & STATICALLY VALIDATED**  

---

## 1. Executive Summary

This engineering step establishes the complete, reproducible training infrastructure for fine-tuning `google/muril-base-cased` on Google Colab GPU. All assets have been constructed, validated, and verified under strict research governance constraints:
1. **Canonical Colab Data Bundle:** Created [`artifacts/colab/muril_lid_data_bundle.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/colab/muril_lid_data_bundle.zip) (2,978,074 bytes, SHA-256: `5000c1e70d642d470b61bcd10bfb58fd63d26477a7745b127e55e694da723b09`), packaging strictly `train.jsonl` (43,369 records), `validation.jsonl` (4,820 records), `bundle_manifest.json`, and `README.md`. **Zero test records** are present.
2. **Jupyter Notebook for Google Colab:** Generated [`training/colab/muril_lid_baseline.ipynb`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/training/colab/muril_lid_baseline.ipynb) (38,124 bytes, 37 cells conforming to `nbformat` v4), structured into 19 pedagogical stages (Sections A through S) tailored for third-year B.Tech students.
3. **Static Validation Passed:** Programmatically verified via `nbformat.validate()`. Confirmed all code cells are clean and unexecuted (`execution_count=None`, zero outputs), model checkpoint name is verified, classes are mapped to 4 active classes, ignore label `-100` is enforced, and zero hardcoded credentials or hub push commands exist.
4. **Execution Documentation:** Created [`training/colab/README.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/training/colab/README.md) detailing exact Google Colab setup, T4/A100 GPU selection, Google Drive mounting, and execution workflows.
5. **Zero Training & Zero Local Weights:** Local system remained CPU-only. Zero model weights were downloaded locally (`local_files_only=True` preserved), zero local training was executed, and all original processed datasets match baseline cryptographic hashes.

---

## 2. Dataset Record Schema & Taxonomy Inspection (Task 1)

Forensic inspection of [`data/processed/language_identification/train.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/train.jsonl) and [`data/processed/language_identification/validation.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/validation.jsonl) established the exact record schema:

* **Primary Unique ID:** `sentence_id` (e.g. `lid_train_000001`, `lid_validation_000001`).
* **Original Whitespace Tokens:** `tokens` (list of strings).
* **Source Annotation Field:** `source_labels` (list of strings: `EN`, `HI`, `TE`, `OTHER`, `NE`, `NULL`).
* **Model Label Field:** `model_labels` (list of integers). **Crucial Finding:** The processed records store integer target labels under `model_labels`, NOT `labels`.
* **Canonical Colab Bundle Schema:** To ensure seamless compatibility with Hugging Face token classification pipelines without redundant preprocessing, the bundle extracts compact canonical records formatted as:
  ```json
  {"id": "lid_train_000001", "tokens": ["0", "lanti", "theatrical", ...], "labels": [3, 2, 0, ...]}
  ```
  where `labels` contains the verified integer target IDs.

### Target Label Taxonomy & Model Mapping

| Language / Class | Target Code | Integer Label ID | Supervised Status | Loss Contribution |
| :--- | :---: | :---: | :---: | :---: |
| **English** | `EN` | `0` | Supervised | Active Cross-Entropy |
| **Hindi** | `HI` | `1` | Supervised | Active Cross-Entropy |
| **Telugu** | `TE` | `2` | Supervised | Active Cross-Entropy |
| **Universal / Symbols / Punctuation** | `OTHER` | `3` | Supervised | Active Cross-Entropy |
| **Named Entities** | `NE` | `-100` | Ignored | Skipped (`ignore_index=-100`) |
| **Mixed-Script Words** | `MIXED` | `-100` | Ignored | Skipped (`ignore_index=-100`) |
| **Ambiguous Words** | `AMBIGUOUS` | `-100` | Ignored | Skipped (`ignore_index=-100`) |
| **Null Annotations** | `NULL` | `-100` | Ignored | Skipped (`ignore_index=-100`) |

---

## 3. Training Data Bundle Audit (Task 2)

* **Bundle File Path:** [`artifacts/colab/muril_lid_data_bundle.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/colab/muril_lid_data_bundle.zip)
* **Archive Size:** 2,978,074 bytes (~2.84 MB)
* **SHA-256 Checksum:** `5000c1e70d642d470b61bcd10bfb58fd63d26477a7745b127e55e694da723b09`
* **Bundle Contents (Strictly 4 Members):**
  1. `train.jsonl`: 43,369 records, 665,313 tokens (638,926 supervised, 26,387 ignored)
  2. `validation.jsonl`: 4,820 records, 73,957 tokens (70,992 supervised, 2,965 ignored)
  3. `bundle_manifest.json`: Verification manifest with source hashes and class distributions
  4. `README.md`: Documentation on schema and usage
* **Test Isolation:** **0 test records** included ($test\_data\_included = false$).

---

## 4. Google Colab Notebook Structure (Task 3)

The notebook [`training/colab/muril_lid_baseline.ipynb`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/training/colab/muril_lid_baseline.ipynb) is organized into 19 sequential stages with detailed pedagogical markdown explanations:

| Section | Stage Title | Cell Type | Purpose / Pedagogical Explanation |
| :---: | :--- | :---: | :--- |
| **A** | Project Introduction & Training Objective | Markdown | Explains Code-Mixing, MuRIL Transformer architecture, and Token-Level LID |
| **B** | Colab Runtime Setup & Drive Mount | Code | Mounts Google Drive (`/content/drive/MyDrive/CodeMix_Intelligence/`) for outputs |
| **C** | Hardware & CUDA Inspection | Code | Inspects GPU model, VRAM (GB), CUDA availability, and stops if CPU-only |
| **D** | Dependency Setup | Code | Installs `transformers`, `datasets`, `accelerate`, `evaluate`, `scikit-learn` |
| **E** | Upload Training Data Bundle | Code | Uploads/extracts `muril_lid_data_bundle.zip` into `/content/codemix_intelligence/data/` |
| **F** | Verify Bundle Manifest & Test Isolation | Code | Programmatic assertion verifying 43,369 train, 4,820 val, and zero test files |
| **G** | Load Train & Validation Records | Code | Parses JSONL files into Hugging Face `Dataset` objects |
| **H** | Load MuRIL Tokenizer | Code | Loads `google/muril-base-cased` with slow `BertTokenizer` (`use_fast=False`) |
| **I** | WordPiece Token Alignment | Code | Implements word-to-subword alignment mapping target labels to first subwords |
| **J** | Alignment & Length Verification | Code | Asserts 1-to-1 bijection between supervised words and prediction positions |
| **K** | Load Token Classification Model | Code | Attaches 4-class linear head (`nn.Linear(768, 4)`) to MuRIL backbone |
| **L** | GPU Memory & Smoke Test | Code | Runs 1 forward and 1 backward pass on a 16-sample batch; checks VRAM |
| **M** | Training Configuration & Math | Code | Calculates 5,424 total steps and sets up `TrainingArguments` with dynamic padding |
| **N** | Macro F1 Metrics Implementation | Code | Defines `compute_metrics` filtering `-100` positions to evaluate true tokens |
| **O** | Fine-Tuning Setup | Code | Configures `Trainer` with `EarlyStoppingCallback(early_stopping_patience=3)` |
| **P** | Model Training Execution | Code | Dedicated cell executing `trainer.train()` (~35-45 min on Colab T4) |
| **Q** | Post-Training Final Validation | Code | Runs final `trainer.evaluate()` over `validation.jsonl` using best checkpoint |
| **R** | Save Best Model & Tokenizer | Code | Saves weights (`model.safetensors`), tokenizer, and metrics to Google Drive |
| **S** | Reproducibility & Next Steps | Code | Final summary and handover notes for Step 32 test set evaluation |

---

## 5. Subword Alignment Policy (Task 6)

Because MuRIL tokenizes words into subword pieces (e.g., `"namaskaram"` $\rightarrow$ `['nama', '##ska', '##ram']`), the notebook implements deterministic label projection:
1. **First Subword:** Assigned the target label $y_j \in \{0, 1, 2, 3\}$.
2. **Continuation Subwords (`##...`):** Assigned label `-100`.
3. **Special Tokens (`[CLS]`, `[SEP]`, `[PAD]`):** Assigned label `-100`.
4. **Ignored Annotations (`NE`, `null`):** Assigned label `-100` across all subwords.
5. **Fallback:** Tokens producing empty tokenizations are mapped to `[UNK]` with the original label to guarantee zero token drops.
6. **Mathematical Equivalence:** Because `nn.CrossEntropyLoss(ignore_index=-100)` ignores all `-100` positions, only the first subword generates loss and gradients. During evaluation, filtering out `-100` positions evaluates the exact original whitespace words with zero subword inflation.

---

## 6. Training Configuration & Mathematical Step Schedule (Tasks 10 & 11)

```
========================================================================
Training Step Schedule:
  Training Records (N):             43,369 sentences
  Per-Device Batch Size (Bm):       16
  Gradient Accumulation Steps (A):  2
  Effective Batch Size (Beff):      32
  Micro-Batches per Epoch:          ceil(43,369 / 16) = 2,711 passes
  Optimization Steps per Epoch:     ceil(43,369 / 32) = 1,356 steps
  Total Epochs:                     4
  Total Optimization Steps:         1,356 * 4 = 5,424 steps
  Warmup Steps (10%):               round(5,424 * 0.10) = 542 steps
  Evaluation Cadence:               Every 500 steps (11 checkpoints total)
  Early Stopping:                   Patience = 3 evaluations
========================================================================
```

* **Dynamic Batch Padding:** The notebook uses `DataCollatorForTokenClassification(tokenizer, pad_to_multiple_of=8, label_pad_token_id=-100)`, padding each micro-batch dynamically to its local maximum length (median length is 25-35 tokens). This reduces memory consumption by over 60% compared to static 256 padding.
* **Precision:** `fp16 = True` on Colab T4 Tensor Cores; `bf16 = True` on Ampere/A100 instances.
* **Fallback Strategy:** If GPU memory fragmentation occurs on a shared T4, users can adjust to `per_device_train_batch_size = 8` with `gradient_accumulation_steps = 4`, preserving the exact 32 effective batch size.

---

## 7. GPU Smoke Test Design (Task 9)

Stage L of the notebook runs a non-destructive GPU smoke test:
1. Samples 16 training examples.
2. Performs 1 forward pass: checks logits shape (`[16, seq_len, 4]`) and verifies finite cross-entropy loss.
3. Performs 1 backward pass (`loss.backward()`): checks gradient computation on Tensor Cores.
4. Measures peak VRAM memory footprint.
5. Clears gradients with `model.zero_grad()`, deletes temporary tensors, and calls `torch.cuda.empty_cache()`.
6. **Zero optimizer step** is executed and **zero weights** are modified, ensuring a clean initial model state.

---

## 8. Test Set Isolation Verification (Task 14)

* **Bundle Integrity:** `muril_lid_data_bundle.zip` contains strictly `train.jsonl` and `validation.jsonl`.
* **Runtime Assertion:** Stage F of the notebook executes:
  ```python
  assert manifest['governance']['test_data_included'] is False
  assert not (DATA_DIR / 'test.jsonl').exists()
  ```
* **Empirical Integrity:** No test set loader, prediction generator, or metric evaluation exists in the training notebook. Test set evaluation remains strictly locked until Step 32.

---

## 9. Notebook Static Validation Results (Task 18)

| Validation Check | Tool / Method | Result | Details |
| :--- | :---: | :---: | :--- |
| **JSON & Schema Syntax** | `nbformat.validate()` | **PASSED** | Valid Jupyter notebook conforming to nbformat v4.5 |
| **Cell Execution State** | Static AST inspection | **PASSED** | All 18 code cells have `execution_count=None` and empty `outputs=[]` |
| **Model Checkpoint** | Code search | **PASSED** | Explicitly set to `"google/muril-base-cased"` |
| **Label Classes** | Code search | **PASSED** | Exactly 4 classes: `EN: 0, HI: 1, TE: 2, OTHER: 3` |
| **Ignore Index** | Code search | **PASSED** | Enforced as `-100` across all alignment and loss functions |
| **Training Cell** | Code search | **PASSED** | Dedicated `trainer.train()` cell in Stage P |
| **Security & Privacy** | Code search | **PASSED** | Zero hardcoded API keys, tokens, or credentials |
| **Hub Publishing** | Code search | **PASSED** | Zero `push_to_hub` or publication commands |

---

## 10. Repository Integrity Baseline Verification (Task 19)

All original benchmark files and manifests were verified to be 100% bitwise identical to their Step 28A baseline hashes:

| File Path | Verified Size (Bytes) | SHA-256 Checksum | Integrity Status |
| :--- | :---: | :---: | :---: |
| [`data/processed/language_identification/train.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/train.jsonl) | 52,692,357 | `879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b` | **MATCH** |
| [`data/processed/language_identification/validation.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/validation.jsonl) | 5,900,569 | `3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b` | **MATCH** |
| [`data/processed/language_identification/test.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/test.jsonl) | 16,230,756 | `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca` | **MATCH** |
| [`data/processed/language_identification/dataset_manifest.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/dataset_manifest.json) | 3,224 | `8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d` | **MATCH** |
| `candidate_sentences.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **EMPTY** |
| `reviewed_sentences.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **EMPTY** |
| `rejected_sentences.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **EMPTY** |

* Zero model weights downloaded locally (`local_files_only=True` preserved).
* Zero model training executed locally.
* Zero predictions or test metrics generated.

---

## 11. Instructions for Opening & Running in Google Colab (Task 20)

1. **Launch Google Colab:** Navigate to [Google Colab](https://colab.research.google.com/).
2. **Upload Notebook:** Click the **Upload** tab and select [`training/colab/muril_lid_baseline.ipynb`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/training/colab/muril_lid_baseline.ipynb).
3. **Select GPU Accelerator:**
   * Go to **Runtime** $\rightarrow$ **Change runtime type**.
   * Choose **T4 GPU** (or A100 if available) and click **Save**.
4. **Execute Setup (Stages B – D):**
   * Run Stage B to mount your Google Drive for persistent artifact saving.
   * Run Stage C to verify the GPU name and CUDA VRAM.
   * Run Stage D to install dependencies (`transformers`, `datasets`, `accelerate`, etc.).
5. **Upload Data Bundle (Stage E):**
   * Run Stage E and upload [`artifacts/colab/muril_lid_data_bundle.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/artifacts/colab/muril_lid_data_bundle.zip).
6. **Pre-Training Verifications (Stages F – O):**
   * Run Stages F through O sequentially to verify the manifest, tokenize the dataset, verify 1-to-1 subword alignment, load the model, and execute the GPU smoke test.
7. **Execute Fine-Tuning (Stage P):**
   * Run Stage P (`trainer.train()`). Training will run for 4 epochs (~35-45 minutes on T4).
8. **Final Evaluation & Checkpoint Export (Stages Q – S):**
   * Run Stages Q and R to evaluate the best model on the validation split and export weights to Google Drive under `MyDrive/CodeMix_Intelligence/muril_lid_baseline/best_model/`.
