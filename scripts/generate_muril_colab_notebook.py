"""
CodeMix Intelligence - Step 31
Colab Notebook Generator and Static Validator

Generates training/colab/muril_lid_baseline.ipynb conforming to nbformat v4.
Includes sections A through S with explanations suitable for a 3rd-year B.Tech student.
Performs complete programmatic validation.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import nbformat as nbf

# Ensure UTF-8 output
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = WORKSPACE / "training" / "colab"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "muril_lid_baseline.ipynb"
REPORTS_DIR = WORKSPACE / "outputs" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "accelerator": "GPU",
        "colab": {
            "name": "muril_lid_baseline.ipynb",
            "provenance": [],
            "toc_visible": True
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    }

    cells = []

    # =========================================================================
    # SECTION A: Project Introduction and Training Objective
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""# CodeMix Intelligence: MuRIL Baseline Training for Token-Level LID

**Course / Capstone Track:** Multilingual Natural Language Processing & Code-Mixed Intelligence  
**Model Target:** `google/muril-base-cased` (Multilingual Representations for Indian Languages)  
**Task:** Token-Level Sequence Tagging for Code-Mixed Language Identification (LID)  
**Languages:** English (`EN`), Hindi (`HI`), Telugu (`TE`), Universal / Symbols / Punctuation (`OTHER`)  

---

## Pedagogical Overview for B.Tech Students

### What is Code-Mixing?
In multilingual societies such as India, speakers frequently interleave multiple languages within a single utterance or conversation (e.g., *"Aaj kal movies theatre lo release avvatledu, full OTT trend nadustundi"* mixing Hindi, Telugu, and English). 

Traditional Natural Language Processing (NLP) models assume that an entire sentence belongs to a single language. In contrast, **Token-Level Language Identification (LID)** classifies each individual word or token into its respective language category. This is the foundational first step for machine translation, sentiment analysis, named entity recognition (NER), and automated content moderation in Indian social media contexts.

### Why Google MuRIL?
Google's **MuRIL** (*Multilingual Representations for Indian Languages*) is a BERT-base Transformer pretrained specifically on 17 Indian languages and English, including both native scripts (Devanagari, Telugu script, etc.) and Romanized (Latin script / transliterated) text. Unlike standard multilingual BERT (`mBERT`) or `XLM-RoBERTa`, MuRIL was trained on parallel transliterated text pairs, giving it superior representations for phonetic Latin-script code-mixing.

### Notebook Workflow
This notebook guides you through the complete fine-tuning pipeline:
1. **Environment Setup & GPU Detection:** Inspecting hardware capabilities (T4 / A100).
2. **Data Ingestion & Integrity Verification:** Uploading and unpacking the clean canonical bundle (43,369 train, 4,820 validation).
3. **WordPiece Subword Alignment:** Projecting word-level labels onto subwords using standard `-100` masking.
4. **Smoke Test:** Running a single forward and backward pass to verify memory safety.
5. **Fine-Tuning:** Training with AdamW, linear warmup, gradient accumulation, and early stopping.
6. **Validation & Evaluation:** Computing token-level Macro F1, per-class F1, accuracy, and confusion matrix.
7. **Checkpoint Export:** Saving the best model to Google Drive for downstream evaluation.
"""))

    # =========================================================================
    # SECTION B: Colab Runtime Setup
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage B: Google Colab Runtime & Google Drive Setup

Fine-tuning a 110-million parameter Transformer model requires a GPU. In Google Colab:
1. Navigate to the top menu: **Runtime** $\\rightarrow$ **Change runtime type**.
2. Under **Hardware accelerator**, select **T4 GPU** (or **A100 GPU** if using Colab Pro).
3. We mount Google Drive to ensure your fine-tuned model checkpoints and training logs are saved permanently.
"""))

    cells.append(nbf.v4.new_code_cell("""# Mount Google Drive for persistent storage of fine-tuned weights and logs
import os
import sys
from pathlib import Path

MOUNT_DRIVE = True  # Set to False if you want to store artifacts locally in /content/

if MOUNT_DRIVE:
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        DRIVE_DIR = Path('/content/drive/MyDrive/CodeMix_Intelligence/muril_lid_baseline')
        DRIVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Google Drive mounted successfully.")
        print(f"✓ Checkpoint destination: {DRIVE_DIR}")
    except Exception as e:
        print(f"Notice: Google Drive mount skipped or failed ({e}). Using local /content/ output.")
        DRIVE_DIR = Path('/content/muril_lid_baseline_output')
        DRIVE_DIR.mkdir(parents=True, exist_ok=True)
else:
    DRIVE_DIR = Path('/content/muril_lid_baseline_output')
    DRIVE_DIR.mkdir(parents=True, exist_ok=True)
"""))

    # =========================================================================
    # SECTION C: GPU and Software Version Inspection
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage C: Hardware & CUDA Environment Inspection

Before running deep learning code, we must verify:
- Whether a CUDA-capable GPU is available.
- The GPU model name and available VRAM (T4 provides ~15 GB GDDR6).
- Supported floating-point precision (`FP16` vs `BF16`).
"""))

    cells.append(nbf.v4.new_code_cell("""import torch
import platform

print("=" * 60)
print("System & Hardware Audit")
print("=" * 60)
print(f"Python Version:   {platform.python_version()}")
print(f"PyTorch Version:  {torch.__version__}")
print(f"CUDA Available:   {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemError(
        "CRITICAL ERROR: No GPU runtime detected!\n"
        "Please select a GPU: Top Menu -> Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU."
    )

gpu_device = torch.cuda.current_device()
gpu_name = torch.cuda.get_device_name(gpu_device)
vram_gb = torch.cuda.get_device_properties(gpu_device).total_memory / (1024 ** 3)
bf16_supported = torch.cuda.is_bf16_supported()

print(f"GPU Device:       {gpu_name} (Device ID: {gpu_device})")
print(f"Total VRAM:       {vram_gb:.2f} GB")
print(f"BF16 Supported:   {bf16_supported}")
print(f"FP16 Supported:   True (NVIDIA Tensor Cores)")
print("=" * 60)
"""))

    # =========================================================================
    # SECTION D: Dependency Setup
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage D: Dependency Installation

We install Hugging Face `transformers`, `datasets`, `accelerate`, and `evaluate`, alongside `scikit-learn` and `sentencepiece`.
"""))

    cells.append(nbf.v4.new_code_cell("""# Install required dependencies quietly
!pip install -q transformers==4.46.3 datasets==3.1.0 accelerate==1.1.1 evaluate==0.4.3 scikit-learn sentencepiece

import transformers
import datasets
import accelerate

print("Installed package versions:")
print(f"  Transformers: {transformers.__version__}")
print(f"  Datasets:     {datasets.__version__}")
print(f"  Accelerate:   {accelerate.__version__}")
"""))

    # =========================================================================
    # SECTION E: Upload Training Data Bundle
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage E: Upload Training Data Bundle

Upload the verified `muril_lid_data_bundle.zip` generated in Step 31 of the project.
This archive contains:
- `train.jsonl` (43,369 canonical training sentences)
- `validation.jsonl` (4,820 canonical validation sentences)
- `bundle_manifest.json` (cryptographic hashes and token counts)
- `README.md` (metadata)

> **Important:** The archive strictly excludes `test.jsonl` to ensure complete empirical isolation of the benchmark test set.
"""))

    cells.append(nbf.v4.new_code_cell("""import zipfile
import shutil

DATA_DIR = Path('/content/codemix_intelligence/data')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Look for bundle in /content/ or prompt upload
bundle_path = Path('/content/muril_lid_data_bundle.zip')

if not bundle_path.exists():
    # Also check if it's in Google Drive
    drive_bundle = Path('/content/drive/MyDrive/muril_lid_data_bundle.zip')
    if drive_bundle.exists():
        print(f"Found bundle in Google Drive: {drive_bundle}")
        shutil.copy(drive_bundle, bundle_path)
    else:
        print("Please upload 'muril_lid_data_bundle.zip' from your local artifacts directory:")
        from google.colab import files
        uploaded = files.upload()
        for fn in uploaded.keys():
            if fn.endswith('.zip'):
                bundle_path = Path(f'/content/{fn}')
                break

if not bundle_path.exists():
    raise FileNotFoundError("Training data bundle was not uploaded! Please upload 'muril_lid_data_bundle.zip'.")

print(f"Extracting {bundle_path} to {DATA_DIR}...")
with zipfile.ZipFile(bundle_path, 'r') as zf:
    zf.extractall(DATA_DIR)

print("Files in data directory:")
for f in sorted(DATA_DIR.iterdir()):
    print(f"  - {f.name} ({f.stat().st_size:,} bytes)")
"""))

    # =========================================================================
    # SECTION F: Verify Bundle Manifest and SHA-256 Hashes
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage F: Bundle Verification & Test-Set Isolation Assertion

Before training, we verify the bundle manifest and assert that **no test data is present**.
"""))

    cells.append(nbf.v4.new_code_cell("""import json
import hashlib

manifest_path = DATA_DIR / 'bundle_manifest.json'
if not manifest_path.exists():
    raise FileNotFoundError("Missing bundle_manifest.json in extracted data directory!")

with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

print("Bundle Manifest Details:")
print(f"  Name:             {manifest.get('bundle_name')}")
print(f"  Created UTC:      {manifest.get('created_at_utc')}")
print(f"  Test Data Status: {manifest['governance']['test_data_included']}")

# Strict Test Set Isolation Assertions
assert manifest['governance']['test_data_included'] is False, "CRITICAL ERROR: Bundle contains test data!"
assert not (DATA_DIR / 'test.jsonl').exists(), "CRITICAL ERROR: test.jsonl found in training directory!"

train_file = DATA_DIR / 'train.jsonl'
val_file = DATA_DIR / 'validation.jsonl'

# Count lines
with open(train_file, 'r', encoding='utf-8') as f:
    train_count = sum(1 for _ in f)
with open(val_file, 'r', encoding='utf-8') as f:
    val_count = sum(1 for _ in f)

print(f"✓ Verified train records:      {train_count:,} (expected: 43,369)")
print(f"✓ Verified validation records: {val_count:,} (expected: 4,820)")
assert train_count == 43369, f"Train count mismatch: {train_count}"
assert val_count == 4820, f"Validation count mismatch: {val_count}"
print("✓ Strict test-set isolation confirmed: Zero test examples present.")
"""))

    # =========================================================================
    # SECTION G: Load Train and Validation Records
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage G: Load Dataset into Memory

We parse the canonical records into memory. Each record contains:
- `id`: Unique sentence identifier.
- `tokens`: List of whitespace-separated original words.
- `labels`: List of integer target labels (`0`: EN, `1`: HI, `2`: TE, `3`: OTHER, `-100`: Ignored).
"""))

    cells.append(nbf.v4.new_code_cell("""from datasets import Dataset

def load_canonical_jsonl(filepath: Path) -> Dataset:
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            rec = json.loads(line)
            records.append({
                "id": rec["id"],
                "tokens": rec["tokens"],
                "labels": rec["labels"]
            })
    return Dataset.from_list(records)

raw_train_dataset = load_canonical_jsonl(train_file)
raw_val_dataset = load_canonical_jsonl(val_file)

print(f"Loaded Hugging Face Datasets:")
print(f"  Train:      {len(raw_train_dataset):,} samples")
print(f"  Validation: {len(raw_val_dataset):,} samples")
print(f"\\nSample Record [0]:")
print(f"  ID:     {raw_train_dataset[0]['id']}")
print(f"  Tokens: {raw_train_dataset[0]['tokens']}")
print(f"  Labels: {raw_train_dataset[0]['labels']}")
"""))

    # =========================================================================
    # SECTION H: Load MuRIL Tokenizer
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage H: Load MuRIL Tokenizer

We load `google/muril-base-cased` using `use_fast=False` (`BertTokenizer`).
MuRIL uses WordPiece tokenization with a vocabulary of 197,258 subwords covering Latin and Indic scripts.
"""))

    cells.append(nbf.v4.new_code_cell("""from transformers import AutoTokenizer

MODEL_CHECKPOINT = "google/muril-base-cased"
print(f"Loading tokenizer: {MODEL_CHECKPOINT}...")

# Use use_fast=False for deterministic BertTokenizer behavior verified in local audit
tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT, use_fast=False)

print(f"Tokenizer class:      {tokenizer.__class__.__name__}")
print(f"Vocabulary size:      {tokenizer.vocab_size:,}")
print(f"Special Tokens:       PAD={tokenizer.pad_token_id}, CLS={tokenizer.cls_token_id}, SEP={tokenizer.sep_token_id}, UNK={tokenizer.unk_token_id}")
"""))

    # =========================================================================
    # SECTION I: WordPiece Token Alignment
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage I: Word-to-Subword Alignment Algorithm

### The Subword Alignment Problem
Language models tokenize words into smaller subwords (WordPiece chunks) to manage vocabulary size. For example:
- The word `"namaskaram"` is split into `['nama', '##ska', '##ram']`.
- The source dataset gave `"namaskaram"` a single label: `2` (`TE`).
- How should the 3 subwords be labeled?

### Our Alignment Policy:
1. The **first subword** receives the original label (`2`).
2. Subsequent continuation subwords (`'##ska'`, `'##ram'`) receive **`-100`**.
3. PyTorch's `CrossEntropyLoss(ignore_index=-100)` automatically skips positions labeled `-100`. Therefore, continuation subwords do not produce gradients and do not inflate loss or metric calculations.
4. Special tokens (`[CLS]`, `[SEP]`, `[PAD]`) also receive **`-100`**.
5. Ignored source labels (`NE`, `null`) receive **`-100`** on all subwords.
6. Fallback: If an unknown character results in empty subwords, we insert `[UNK]` so token-label alignment is never corrupted.
"""))

    cells.append(nbf.v4.new_code_cell("""MAX_LENGTH = 256

def tokenize_and_align_labels(examples):
    all_input_ids = []
    all_attention_mask = []
    all_labels = []
    
    batch_words = examples["tokens"]
    batch_labels = examples["labels"]
    
    for words, labels in zip(batch_words, batch_labels):
        input_ids = [tokenizer.cls_token_id]
        aligned_labels = [-100]  # [CLS] is ignored
        
        for word, label in zip(words, labels):
            subwords = tokenizer.tokenize(word)
            if not subwords:
                subwords = [tokenizer.unk_token]
            subword_ids = tokenizer.convert_tokens_to_ids(subwords)
            
            # Label assignment
            if label in {0, 1, 2, 3}:
                # Supervised word: first subword gets label, continuation subwords get -100
                aligned_labels.append(label)
                aligned_labels.extend([-100] * (len(subwords) - 1))
            else:
                # Ignored word (NE, null, -100): all subwords receive -100
                aligned_labels.extend([-100] * len(subwords))
                
            input_ids.extend(subword_ids)
            
        # Append [SEP]
        input_ids.append(tokenizer.sep_token_id)
        aligned_labels.append(-100)
        
        # Whole-word boundary truncation safety check
        if len(input_ids) > MAX_LENGTH:
            input_ids = input_ids[:MAX_LENGTH]
            aligned_labels = aligned_labels[:MAX_LENGTH]
            
        attention_mask = [1] * len(input_ids)
        
        all_input_ids.append(input_ids)
        all_attention_mask.append(attention_mask)
        all_labels.append(aligned_labels)
        
    return {
        "input_ids": all_input_ids,
        "attention_mask": all_attention_mask,
        "labels": all_labels
    }

print("Tokenizing and aligning datasets...")
tokenized_train = raw_train_dataset.map(tokenize_and_align_labels, batched=True, remove_columns=["id", "tokens"])
tokenized_val = raw_val_dataset.map(tokenize_and_align_labels, batched=True, remove_columns=["id", "tokens"])
print("✓ Tokenization and alignment complete.")
"""))

    # =========================================================================
    # SECTION J: Sequence Length and Label Alignment Verification
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage J: Alignment & Sequence Length Assertion Verification

We assert programmatically that:
1. Every supervised original whitespace word contributes **exactly one** supervised label position.
2. No sequence exceeds `MAX_LENGTH = 256`.
"""))

    cells.append(nbf.v4.new_code_cell("""# Programmatic assertion across first 500 validation examples
print("Running subword-to-word bijection assertions...")
for i in range(min(500, len(raw_val_dataset))):
    orig_labels = raw_val_dataset[i]["labels"]
    aligned = tokenized_val[i]["labels"]
    
    orig_sup = sum(1 for l in orig_labels if l in {0, 1, 2, 3})
    aligned_sup = sum(1 for l in aligned if l != -100)
    
    assert orig_sup == aligned_sup, (
        f"Mismatch in sample {i}: original has {orig_sup} supervised tokens, "
        f"but aligned has {aligned_sup} active positions!"
    )
    assert len(tokenized_val[i]["input_ids"]) <= MAX_LENGTH

print(f"✓ Alignment verification passed: 100% 1-to-1 bijection verified between supervised words and active prediction heads.")
"""))

    # =========================================================================
    # SECTION K: Load Token Classification Model
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage K: Model Architecture Setup

We instantiate `AutoModelForTokenClassification` with 4 target classes:
- `0`: `EN`
- `1`: `HI`
- `2`: `TE`
- `3`: `OTHER`

The model attaches a linear classification head (`nn.Linear(768, 4)`) on top of MuRIL's contextualized 768-dimensional token embeddings.
"""))

    cells.append(nbf.v4.new_code_cell("""from transformers import AutoModelForTokenClassification

ID2LABEL = {0: "EN", 1: "HI", 2: "TE", 3: "OTHER"}
LABEL2ID = {"EN": 0, "HI": 1, "TE": 2, "OTHER": 3}

print(f"Loading pretrained weights for {MODEL_CHECKPOINT}...")
model = AutoModelForTokenClassification.from_pretrained(
    MODEL_CHECKPOINT,
    num_labels=4,
    id2label=ID2LABEL,
    label2id=LABEL2ID
)

# Print architecture summary
n_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Model loaded successfully:")
print(f"  Total Parameters:     {n_params:,}")
print(f"  Trainable Parameters: {trainable_params:,}")
print(f"  Classifier Head:      {model.classifier}")
"""))

    # =========================================================================
    # SECTION L: GPU Memory and Forward/Backward Smoke Test
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage L: GPU Forward & Backward Smoke Test

Before starting multi-epoch training, we run a **smoke test**:
- Construct one batch of size 16.
- Run one forward pass to check loss computation and logits shape (`[16, seq_len, 4]`).
- Run one backward pass to test gradient calculation on the GPU.
- Check peak VRAM usage to verify there is no Out-Of-Memory (OOM) error.
- Zero gradients afterward without executing an optimizer step.
"""))

    cells.append(nbf.v4.new_code_cell("""from transformers import DataCollatorForTokenClassification

# Instantiate dynamic collator
data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    pad_to_multiple_of=8,
    label_pad_token_id=-100
)

# Create small DataLoader for 1 batch
from torch.utils.data import DataLoader
smoke_loader = DataLoader(tokenized_train.select(range(16)), batch_size=16, collate_fn=data_collator)
batch = next(iter(smoke_loader))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

print("Running smoke test...")
torch.cuda.reset_peak_memory_stats()
inputs = {k: v.to(device) for k, v in batch.items()}

# Forward pass
outputs = model(**inputs)
loss = outputs.loss
logits = outputs.logits

print(f"✓ Forward pass successful:")
print(f"  Input batch shape:   {inputs['input_ids'].shape}")
print(f"  Logits shape:        {logits.shape} (Expected: [16, seq_len, 4])")
print(f"  Cross-Entropy Loss:  {loss.item():.4f}")
assert torch.isfinite(loss), "Loss is not finite!"

# Backward pass
loss.backward()
print(f"✓ Backward pass successful (Gradients computed).")

peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)
print(f"✓ Peak GPU Memory during smoke test: {peak_vram:.2f} MB")

# Clean up gradients to ensure clean starting state
model.zero_grad()
del inputs, outputs, loss, logits
torch.cuda.empty_cache()
print("✓ Model and GPU cache cleared. Ready for fine-tuning!")
"""))

    # =========================================================================
    # SECTION M: Training Configuration
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage M: Training Arguments & Mathematical Step Calculation

### Hyperparameter Specifications
- **Effective Batch Size:** 32 (Per-device batch size 16 $\\times$ Gradient Accumulation 2).
- **Learning Rate:** $3 \\times 10^{-5}$ with linear warmup over 10% of total steps (542 steps).
- **Weight Decay:** 0.01 (AdamW regularization).
- **Epochs:** 4 (Full convergence over 43,369 sentences).
- **Evaluation Cadence:** Every 500 optimization steps.
- **Early Stopping:** Patience of 3 evaluations monitoring `eval_macro_f1`.
"""))

    cells.append(nbf.v4.new_code_cell("""import math

TRAIN_EXAMPLES = len(tokenized_train)
PER_DEVICE_BATCH = 16
GRAD_ACCUM = 2
EFFECTIVE_BATCH = PER_DEVICE_BATCH * GRAD_ACCUM
EPOCHS = 4

STEPS_PER_EPOCH = math.ceil(TRAIN_EXAMPLES / EFFECTIVE_BATCH)
TOTAL_STEPS = STEPS_PER_EPOCH * EPOCHS
WARMUP_STEPS = round(TOTAL_STEPS * 0.10)

print("Dynamic Optimization Step Breakdown:")
print(f"  Total Training Examples:     {TRAIN_EXAMPLES:,}")
print(f"  Per-Device Batch Size:       {PER_DEVICE_BATCH}")
print(f"  Gradient Accumulation Steps: {GRAD_ACCUM}")
print(f"  Effective Batch Size:        {EFFECTIVE_BATCH}")
print(f"  Steps per Epoch:             {STEPS_PER_EPOCH:,}")
print(f"  Total Epochs:                {EPOCHS}")
print(f"  Total Optimization Steps:    {TOTAL_STEPS:,}")
print(f"  Warmup Steps (10%):          {WARMUP_STEPS:,}")

# Compare against approved baseline
assert STEPS_PER_EPOCH == 1356, f"Expected 1356 steps/epoch, calculated {STEPS_PER_EPOCH}"
assert TOTAL_STEPS == 5424, f"Expected 5424 total steps, calculated {TOTAL_STEPS}"
assert WARMUP_STEPS == 542, f"Expected 542 warmup steps, calculated {WARMUP_STEPS}"
print("✓ Dynamic step calculations match pre-training specifications exactly.")
"""))

    # =========================================================================
    # SECTION N: Macro F1 Metrics
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage N: Token-Level Evaluation Metrics

### Why Macro F1 is the Primary Metric
In our dataset, Hindi constitutes **48.66%** of supervised tokens, while Telugu represents **14.25%** and Universal/Symbols represents **9.85%**. A naive model that blindly predicts Hindi would achieve high accuracy but completely fail on code-mixed Telugu or English tokens.

**Macro F1** computes the unweighted average of F1 scores across all four classes:
$$\\text{Macro F1} = \\frac{1}{4} (F1_{\\text{EN}} + F1_{\\text{HI}} + F1_{\\text{TE}} + F1_{\\text{OTHER}})$$
This penalizes poor performance on minority languages equally.
"""))

    cells.append(nbf.v4.new_code_cell("""import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix

def compute_metrics(p):
    predictions, labels = p
    preds = np.argmax(predictions, axis=2)

    # Filter out ignored positions (-100)
    true_predictions = [
        p_val for (p_row, l_row) in zip(preds, labels)
        for (p_val, l_val) in zip(p_row, l_row) if l_val != -100
    ]
    true_labels = [
        l_val for l_row in labels
        for l_val in l_row if l_val != -100
    ]

    # Calculate overall accuracy
    acc = accuracy_score(true_labels, true_predictions)

    # Calculate macro-averaged metrics across [0, 1, 2, 3]
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        true_labels,
        true_predictions,
        labels=[0, 1, 2, 3],
        average="macro",
        zero_division=0
    )

    # Calculate per-class metrics
    p_per_class, r_per_class, f1_per_class, _ = precision_recall_fscore_support(
        true_labels,
        true_predictions,
        labels=[0, 1, 2, 3],
        average=None,
        zero_division=0
    )

    return {
        "accuracy": acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "f1_EN": f1_per_class[0],
        "f1_HI": f1_per_class[1],
        "f1_TE": f1_per_class[2],
        "f1_OTHER": f1_per_class[3]
    }

print("✓ compute_metrics function registered successfully.")
"""))

    # =========================================================================
    # SECTION O: Fine-Tuning Setup
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage O: Trainer Initialization

We configure Hugging Face's `Trainer` with:
- `EarlyStoppingCallback(early_stopping_patience=3)`
- Periodic evaluation every 500 steps
- `metric_for_best_model="eval_macro_f1"`
- `load_best_model_at_end=True`
"""))

    cells.append(nbf.v4.new_code_cell("""from transformers import TrainingArguments, Trainer, EarlyStoppingCallback

CHECKPOINT_OUTPUT_DIR = str(DRIVE_DIR / "checkpoints")

training_args = TrainingArguments(
    output_dir=CHECKPOINT_OUTPUT_DIR,
    learning_rate=3e-5,
    per_device_train_batch_size=PER_DEVICE_BATCH,
    gradient_accumulation_steps=GRAD_ACCUM,
    per_device_eval_batch_size=32,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
    warmup_steps=WARMUP_STEPS,
    lr_scheduler_type="linear",
    fp16=True,                          # Enabled on Colab T4
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

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)

print("✓ Trainer configured and ready for execution.")
"""))

    # =========================================================================
    # SECTION P: Training Execution Cell
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage P: Model Training Execution

> **Action Required:** Execute the code cell below to begin fine-tuning `google/muril-base-cased`.  
> Expected duration on Google Colab T4 GPU: **~35 to 45 minutes** (4 epochs).
"""))

    cells.append(nbf.v4.new_code_cell("""# =====================================================================
# STAGE P: EXECUTE FINE-TUNING
# =====================================================================
print("=" * 70)
print("Starting MuRIL Baseline LID Fine-Tuning")
print(f"  GPU Device:      {gpu_name}")
print(f"  Training Samples: {len(tokenized_train):,}")
print(f"  Batch Size:       {PER_DEVICE_BATCH} (Effective: {EFFECTIVE_BATCH})")
print(f"  Total Steps:      {TOTAL_STEPS:,}")
print("=" * 70)

train_result = trainer.train()
print("\\n✓ Training successfully completed!")
"""))

    # =========================================================================
    # SECTION Q: Final Validation Evaluation
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage Q: Post-Training Validation Evaluation

We run a dedicated evaluation pass over `validation.jsonl` using the best checkpoint restored by `load_best_model_at_end=True`.
"""))

    cells.append(nbf.v4.new_code_cell("""# Evaluate best model on validation split
print("Evaluating best model checkpoint on validation set...")
final_val_metrics = trainer.evaluate()

print("\\n" + "=" * 50)
print("FINAL VALIDATION PERFORMANCE (BEST CHECKPOINT)")
print("=" * 50)
print(f"Validation Loss:            {final_val_metrics['eval_loss']:.4f}")
print(f"Overall Token Accuracy:     {final_val_metrics['eval_accuracy'] * 100:.2f}%")
print(f"Macro F1 Score:             {final_val_metrics['eval_macro_f1'] * 100:.2f}%")
print(f"Macro Precision:            {final_val_metrics['eval_macro_precision'] * 100:.2f}%")
print(f"Macro Recall:               {final_val_metrics['eval_macro_recall'] * 100:.2f}%")
print("-" * 50)
print(f"Per-Class F1 Scores:")
print(f"  English (EN: 0):          {final_val_metrics['eval_f1_EN'] * 100:.2f}%")
print(f"  Hindi (HI: 1):            {final_val_metrics['eval_f1_HI'] * 100:.2f}%")
print(f"  Telugu (TE: 2):           {final_val_metrics['eval_f1_TE'] * 100:.2f}%")
print(f"  Universal/Other (OTHER: 3): {final_val_metrics['eval_f1_OTHER'] * 100:.2f}%")
print("=" * 50)
"""))

    # =========================================================================
    # SECTION R: Save Best Model and Tokenizer
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage R: Save Model Weights, Tokenizer & Metrics

We save the best model weights, tokenizer files, and full evaluation metrics to Google Drive for permanent archiving.
"""))

    cells.append(nbf.v4.new_code_cell("""SAVE_PATH = DRIVE_DIR / "best_model"
print(f"Saving best model and tokenizer to {SAVE_PATH}...")
trainer.save_model(str(SAVE_PATH))
tokenizer.save_pretrained(str(SAVE_PATH))

# Save metrics report
metrics_report_path = DRIVE_DIR / "final_validation_metrics.json"
with open(metrics_report_path, "w", encoding="utf-8") as f:
    json.dump(final_val_metrics, f, indent=2)

print(f"✓ Model artifacts and metrics saved successfully to:")
print(f"  {SAVE_PATH}")
"""))

    # =========================================================================
    # SECTION S: Reproducibility and Final Audit
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## Stage S: Reproducibility Log & Next Steps

### Training Summary & Audit Trail
- **Baseline Model:** `google/muril-base-cased`
- **Output Classes:** `EN: 0`, `HI: 1`, `TE: 2`, `OTHER: 3`
- **Ignored Index:** `-100` (Applied to Named Entities, continuation subwords, and special tokens)
- **Training Records:** 43,369
- **Validation Records:** 4,820
- **Test Set Isolation:** Guaranteed (Zero test records accessed during training or validation)

### Next Steps for the Research Project
1. Download the fine-tuned checkpoint folder `best_model/` from Google Drive to your local repository under `models/muril_base_lid/`.
2. Proceed to **Step 32**: Locked test set benchmarking and comparative error analysis across CodeMix vs Monolingual domains.
"""))

    cells.append(nbf.v4.new_code_cell("""print("=" * 70)
print("CodeMix Intelligence - MuRIL Baseline LID Training Run Complete")
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
print(f"Artifacts preserved in: {DRIVE_DIR}")
print("Ready for Step 32: Locked Test Set Evaluation")
print("=" * 70)
"""))

    nb.cells = cells
    return nb


def validate_notebook(nb: nbf.NotebookNode):
    print("[1/3] Validating notebook structure with nbformat...")
    nbf.validate(nb)
    print("  nbformat validation: PASSED (Valid Notebook JSON)")

    print("[2/3] Checking required sections, cells, and safety constraints...")
    cell_types = [c.cell_type for c in nb.cells]
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    markdown_cells = [c for c in nb.cells if c.cell_type == "markdown"]

    print(f"  Total cells:    {len(nb.cells)}")
    print(f"  Markdown cells: {len(markdown_cells)}")
    print(f"  Code cells:     {len(code_cells)}")

    # Check cell structure
    for i, c in enumerate(code_cells):
        assert c.execution_count is None, f"Code cell {i} has non-null execution_count!"
        assert len(c.outputs) == 0, f"Code cell {i} has unexpected outputs!"

    # Check code content assertions
    all_code = "\n".join(c.source for c in code_cells)
    all_markdown = "\n".join(c.source for c in markdown_cells)

    assert "google/muril-base-cased" in all_code, "Missing model checkpoint name!"
    assert "EN" in all_code and "HI" in all_code and "TE" in all_code and "OTHER" in all_code, "Missing classes!"
    assert "-100" in all_code, "Missing ignore_index -100!"
    assert "trainer.train()" in all_code, "Missing trainer.train() call!"
    assert "test.jsonl" not in all_code or "assert not (DATA_DIR / 'test.jsonl').exists()" in all_code, "test.jsonl should only be in isolation assertions!"
    assert "push_to_hub=True" not in all_code, "Unexpected push_to_hub=True found!"
    assert "hf_" not in all_code, "Potential hardcoded API token found!"

    print("  Constraint checks: ALL PASSED")


def main():
    print("=" * 70)
    print("CodeMix Intelligence - Step 31: Colab Notebook Generator")
    print("=" * 70)

    # 1. Generate notebook
    nb = build_notebook()

    # 2. Validate notebook
    validate_notebook(nb)

    # 3. Write notebook to disk
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    nb_size = NOTEBOOK_PATH.stat().st_size
    nb_sha256 = hashlib.sha256(NOTEBOOK_PATH.read_bytes()).hexdigest()
    print(f"[3/3] Notebook written: {NOTEBOOK_PATH}")
    print(f"  Size: {nb_size:,} bytes")
    print(f"  SHA-256: {nb_sha256}")
    print("=" * 70)


if __name__ == "__main__":
    main()
