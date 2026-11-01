# Step 30A: Validation Statistics Reconciliation and MuRIL Configuration Finalization

**Project:** CodeMix Intelligence: Multilingual Token-Level Language Identification  
**Step:** 30A — Validation Statistics Reconciliation & Technical Parameter Finalization  
**Workspace:** [`C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence)  
**Timestamp:** `2026-11-01T05:17:46.300746+00:00`  
**Status:** **RECONCILED & AUDIT VERIFIED**  

---

## 1. Executive Summary

This audit forensically reconciles the **200-token discrepancy** noted in the Step 30 validation label summary and finalizes the complete technical configuration for fine-tuning `google/muril-base-cased` on Google Colab GPU.

Key audit findings:
1. **Discrepancy Resolution:** The 200-token discrepancy was an arithmetic/transcription error in the conversational markdown chat summary of Step 30 (which stated 70,792 supervised tokens instead of 70,992). The underlying `validation.jsonl` file, the dataset manifest, and the Step 30 JSON and Markdown report artifacts were verified to have the exact true count: **70,992 supervised tokens** ($95.9909\%$) and **2,965 ignored tokens** ($4.0091\%$), summing exactly to **73,957 total tokens**.
2. **Training Set Verification:** An independent re-audit of `train.jsonl` confirmed zero discrepancy: **638,926 supervised tokens** ($96.0339\%$) and **26,387 ignored tokens** ($3.9661\%$), summing exactly to **665,313 total tokens**.
3. **Subword Alignment Policy Confirmed:** A 1-to-1 bijection exists between supervised original whitespace tokens and active first-subword prediction positions. Continuation subwords (`##...`), special tokens (`[CLS]`, `[SEP]`, `[PAD]`), and ignored source labels (`NE`, `MIXED`, `AMBIGUOUS`, `NULL`) receive `-100`.
4. **Sequence Length & `max_length = 256`:** Measured maximum subword lengths including `[CLS]` and `[SEP]` are **188** in train and **217** in validation. Setting `max_length = 256` guarantees **100.000% sentence preservation** (0 sentences truncated) across both splits.
5. **Colab Execution Recipe Finalized:** Effective batch size of 32 (`per_device_train_batch_size = 16`, `gradient_accumulation_steps = 2`), AdamW optimizer with learning rate $3 \times 10^{-5}$, 4 epochs (5,424 total optimization steps), 542 warmup steps (10%), dynamic padding, and validation evaluations every 500 steps (11 checkpoints, providing ample cycles for early stopping with patience 3).
6. **Zero Integrity Degradation:** All baseline dataset SHA-256 hashes are 100% identical. The locked test set remains completely unaccessed.

---

## 2. Validation Token Distribution Reconciliation (Task 1)

### Reconciled Validation Label Breakdown (`validation.jsonl`)

* **Total Records:** 4,820 sentences
* **Total Tokens:** 73,957 tokens
* **Supervised Tokens:** **70,992** ($95.9909\%$)
* **Ignored Tokens:** **2,965** ($4.0091\%$)
* **Length Mismatches:** 0
* **Malformed Records:** 0

| Source Annotation | Model Label ID | Token Count | % of Supervised Tokens | % of Total Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **English (`EN`)** | `0` | 19,135 | 26.9537% (26.95%) | 25.8731% (25.87%) |
| **Hindi (`HI`)** | `1` | 34,316 | 48.3378% (48.34%) | 46.3999% (46.40%) |
| **Telugu (`TE`)** | `2` | 10,380 | 14.6214% (14.62%) | 14.0352% (14.04%) |
| **Universal / Other (`OTHER`)** | `3` | 7,161 | 10.0871% (10.09%) | 9.6826% (9.68%) |
| **Named Entities (`NE`)** | `-100` | 2,804 | — | 3.7914% (3.79%) |
| **Mixed-Script Words (`MIXED`)** | `-100` | 0 | — | 0.0000% (0.00%) |
| **Ambiguous Tokens (`AMBIGUOUS`)** | `-100` | 0 | — | 0.0000% (0.00%) |
| **Null Annotations (`NULL`)** | `-100` | 161 | — | 0.2177% (0.22%) |
| **Supervised Total** | — | **70,992** | **100.0000%** | **95.9909%** |
| **Ignored Total** | — | **2,965** | — | **4.0091%** |
| **Sum of All 8 Annotations** | — | **73,957** | — | **100.0000%** |

$$\sum \text{All 8 Annotations} = 19,135 + 34,316 + 10,380 + 7,161 + 2,804 + 0 + 0 + 161 = 73,957 \equiv \text{Total Tokens}$$

### Root Cause Analysis of the 200-Token Discrepancy
* **Artifact Files vs. Chat Response:**
  * In the Step 30 JSON report ([`step30_lid_training_readiness.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step30_lid_training_readiness.json)), `supervised_tokens` was recorded as **70,992** and `ignored_tokens` as **2,965**.
  * In the Step 30 Markdown report ([`step30_lid_training_readiness.md`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/reports/step30_lid_training_readiness.md)), line 51 recorded **70,992** supervised and **2,965** ignored tokens.
  * In the conversational summary table rendered in the final chat turn, the supervised total was inadvertently typed as **70,792** ($70,992 - 200$), and the ignored count was typed as **3,165** ($2,965 + 200$).
* **Conclusion:** The underlying dataset `validation.jsonl`, manifest, audit script, and artifact files are completely accurate and have never been altered. The discrepancy was purely a conversational transcription error.

---

## 3. Independent Training Set Verification (Task 1)

An independent re-audit of [`train.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/train.jsonl) verified that no analogous clerical error exists in the training set:

* **Total Records:** 43,369 sentences
* **Total Tokens:** 665,313 tokens
* **Supervised Tokens:** **638,926** ($96.0339\%$)
* **Ignored Tokens:** **26,387** ($3.9661\%$)
* **Length Mismatches:** 0
* **Malformed Records:** 0

| Source Annotation | Model Label ID | Token Count | % of Supervised Tokens | % of Total Tokens |
| :--- | :---: | :---: | :---: | :---: |
| **English (`EN`)** | `0` | 174,059 | 27.2424% (27.24%) | 26.1620% (26.16%) |
| **Hindi (`HI`)** | `1` | 310,887 | 48.6577% (48.66%) | 46.7279% (46.73%) |
| **Telugu (`TE`)** | `2` | 91,036 | 14.2483% (14.25%) | 13.6832% (13.68%) |
| **Universal / Other (`OTHER`)** | `3` | 62,944 | 9.8515% (9.85%) | 9.4608% (9.46%) |
| **Named Entities (`NE`)** | `-100` | 24,878 | — | 3.7393% (3.74%) |
| **Mixed-Script Words (`MIXED`)** | `-100` | 0 | — | 0.0000% (0.00%) |
| **Ambiguous Tokens (`AMBIGUOUS`)** | `-100` | 0 | — | 0.0000% (0.00%) |
| **Null Annotations (`NULL`)** | `-100` | 1,509 | — | 0.2268% (0.23%) |
| **Supervised Total** | — | **638,926** | **100.0000%** | **96.0339%** |
| **Ignored Total** | — | **26,387** | — | **3.9661%** |
| **Sum of All 8 Annotations** | — | **665,313** | — | **100.0000%** |

$$\sum \text{All 8 Annotations} = 174,059 + 310,887 + 91,036 + 62,944 + 24,878 + 0 + 0 + 1,509 = 665,313 \equiv \text{Total Tokens}$$

---

## 4. Subword Alignment & Loss Mapping Verification (Tasks 2 & 5)

The WordPiece alignment mechanics for the slow `BertTokenizer` (`google/muril-base-cased`) were re-tested across 200 validation sequences with 100% pass rate:

1. **First-Subword Label Assignment:**
   * For any supervised original whitespace token $w_j$ with label $y_j \in \{0, 1, 2, 3\}$, the first subword $s_{j, 1}$ receives label $y_j$.
2. **Continuation Subwords:**
   * All continuation subwords $s_{j, k}$ ($k > 1$, e.g. `##ska`, `##ram`) receive label `-100`.
3. **Ignored Source Annotations:**
   * Any token with source label in $\{\text{NE}, \text{MIXED}, \text{AMBIGUOUS}, \text{NULL}\}$ receives `-100` across **all** of its subwords.
4. **Special & Padding Tokens:**
   * `[CLS]` (index 0) receives label `-100`.
   * `[SEP]` (last active index) receives label `-100`.
   * `[PAD]` (indices up to `max_length`) receive label `-100`.
5. **Exact 1-to-1 Bijection:**
   * Every supervised original whitespace token produces exactly one position where $y \neq -100$.
   * Evaluating metrics strictly at positions where ground-truth $y \neq -100$ produces exact whitespace token-level accuracy and Macro F1 with zero subword inflation or boundary distortion.

---

## 5. Sequence Length Distribution & Final `max_length` (Task 3)

### Length Profiling (With vs. Without Special Tokens)

| Split | Metric | Word-Level Length | Subword Length (Without Special Tokens) | Subword Length (With `[CLS]` + `[SEP]`) |
| :--- | :--- | :---: | :---: | :---: |
| **Train** | Mean | 15.34 | 23.92 | **25.92** |
| | Median | 15.00 | 23.00 | **25.00** |
| | 90th %ile | 24.00 | 38.00 | **40.00** |
| | 95th %ile | 27.00 | 44.00 | **46.00** |
| | 99th %ile | 37.00 | 65.00 | **67.00** |
| | **Maximum** | **89** | **186** | **188** (`lid_train_005811`) |
| **Validation** | Mean | 15.34 | 23.99 | **25.99** |
| | Median | 14.00 | 22.00 | **24.00** |
| | 90th %ile | 24.00 | 38.00 | **40.00** |
| | 95th %ile | 27.00 | 44.05 | **46.05** |
| | 99th %ile | 38.00 | 69.00 | **71.00** |
| | **Maximum** | **81** | **215** | **217** (`lid_validation_000041`) |

### Final `max_length` Determination
* **Evaluation of `max_length = 128`:**
  * Truncates 5 sentences in train ($0.0115\%$) and 5 sentences in validation ($0.1037\%$).
  * Requires non-trivial word-boundary truncation logic to drop words cleanly without creating dangling subwords.
* **Evaluation of `max_length = 256`:**
  * Train maximum with special tokens is **188** $\le 256$.
  * Validation maximum with special tokens is **217** $\le 256$.
  * **0 sentences truncated ($0.0000\%$)** across all 48,189 train and validation examples.
  * Preserves 100% of tokens, word boundaries, and labels.
  * Well within the model's hard context limit of 512.
* **Decision:** Adopt **`max_length = 256`** as the definitive baseline configuration.

---

## 6. Finalized Google Colab Training Configuration (Task 4 & 6)

### Primary Training Hyperparameters

```python
training_args = TrainingArguments(
    output_dir="./outputs/checkpoints/muril_base_lid",
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    gradient_accumulation_steps=2,          # Effective batch size = 32
    per_device_eval_batch_size=32,
    num_train_epochs=4,
    weight_decay=0.01,
    warmup_ratio=0.10,                      # 542 warmup steps
    lr_scheduler_type="linear",
    fp16=True,                              # Enable on NVIDIA T4 GPU
    eval_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=500,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_macro_f1",
    greater_is_better=True,
    logging_steps=50,
    dataloader_num_workers=2,
    report_to="none"
)
```

### Mathematical Step Schedule

* **Training Examples ($N$):** 43,369 sentences
* **Per-Device Batch Size ($B_m$):** 16
* **Gradient Accumulation Steps ($A$):** 2
* **Effective Batch Size ($B_{eff} = B_m \times A$):** 32
* **Steps per Epoch:** $\lceil 43,369 / 32 \rceil = \mathbf{1,356}$ optimization steps
* **Total Training Epochs:** 4
* **Total Optimization Steps:** $1,356 \times 4 = \mathbf{5,424}$ steps
* **Warmup Steps:** $\text{round}(5,424 \times 0.10) = \mathbf{542}$ steps
* **Evaluation Cadence:** Every **500** steps
* **Evaluation Checkpoints:** Steps 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, and 5424 (Total: **11** evaluation cycles)
* **Early Stopping Viability:** With `patience = 3`, 3 consecutive non-improving evaluation checkpoints ($1,500$ steps $\approx 1.1$ epochs) trigger early stopping. Having 11 evaluation cycles provides ample resolution while allowing the model to train for more than 1 full epoch before early stopping can trigger.

### Fallback Batch Configuration
* If GPU memory fragmentation or memory allocation limits occur on a shared Google Colab T4 instance:
  * Set `per_device_train_batch_size = 8`.
  * Set `gradient_accumulation_steps = 4`.
  * Effective batch size remains **32**, guaranteeing mathematically identical gradient updates while halving peak micro-batch activation memory.
* **Dynamic Padding:** Use `DataCollatorForTokenClassification(tokenizer, pad_to_multiple_of=8)` to pad dynamically to the batch's local maximum length (median length is 25-35 tokens), keeping VRAM consumption exceptionally low.
* **Disclaimer:** GPU memory fit cannot be guaranteed a priori without empirical execution of a forward-backward training step on Colab hardware.

---

## 7. Test Set Isolation Confirmation (Task 7)

* **Loader Binding:**
  * Training data loader binds strictly to [`data/processed/language_identification/train.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/train.jsonl).
  * Validation data loader binds strictly to [`data/processed/language_identification/validation.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/validation.jsonl).
  * Test set ([`data/processed/language_identification/test.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/test.jsonl)) is completely excluded from the training runtime.
* **Model Selection:**
  * Checkpoint selection, learning rate scheduling, and early stopping decisions depend strictly on `validation.jsonl` Macro F1.
  * Test set metrics will only be evaluated after training is finished and the final model checkpoint has been locked.

---

## 8. Integrity Baseline Verification (Task 9)

All file sizes and cryptographic SHA-256 hashes match baseline specifications:

| File Path | Verified Size (Bytes) | SHA-256 Checksum | Integrity Status |
| :--- | :---: | :---: | :---: |
| [`data/processed/language_identification/train.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/train.jsonl) | 52,692,357 | `879d8ca621c3063cec00cd498489f92dff32f8d9c359ede555e9688475244f2b` | **MATCH** |
| [`data/processed/language_identification/validation.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/validation.jsonl) | 5,900,569 | `3bc233527aac08cce37c28d53cf73c221e70b81a109c5e767ec249ef3960537b` | **MATCH** |
| [`data/processed/language_identification/test.jsonl`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/test.jsonl) | 16,230,756 | `58a222754ef1b293ae719fd0acc86f86b22fe3a504bbd31119d787361890daca` | **MATCH** |
| [`data/processed/language_identification/dataset_manifest.json`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/data/processed/language_identification/dataset_manifest.json) | 3,224 | `8502b021e0439e8af76cb445948fa3f4d9b7f456057149bd3fba8053d992e67d` | **MATCH** |
| `candidate_sentences.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **EMPTY** |
| `reviewed_sentences.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **EMPTY** |
| `rejected_sentences.jsonl` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **EMPTY** |

* **Zero Model Weights Downloaded:** Maintained `local_files_only=True`.
* **Zero Model Training Executed:** Pure read-only technical reconciliation.
* **Zero Predictions Generated:** Locked evaluation baseline preserved.
* **Zero Blockers Remaining:** The project is fully unblocked and ready for Colab notebook creation and training pipeline assembly.
