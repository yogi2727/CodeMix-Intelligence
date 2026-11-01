# CodeMix Intelligence V1.0.0 Release Notes
## Stable Release — MuRIL Token-Level Language Identification Baseline

**Release Name:** CodeMix Intelligence V1.0.0 — MuRIL Language Identification Baseline  
**Version:** `1.0.0`  
**Release Date:** 2026-11-01  
**Architecture:** `google/muril-base-cased` (Multilingual Representations for Indian Languages)  
**Task:** Token-Level Language Identification (LID)  
**Taxonomy:** 4 Classes (`EN: 0`, `HI: 1`, `TE: 2`, `OTHER: 3`)  

---

## 1. Project Objective

CodeMix Intelligence is engineered to address the linguistic divergence and code-mixing phenomena prevalent across Indian digital communications. In multilingual contexts, speakers frequently alternate between English, Hindi, and Telugu within a single sentence across both native scripts (Devanagari, Telugu script, Latin) and Romanized transliterations (Hinglish, Tenglish).

**Version 1.0.0 Core Objective:** Deliver a production-grade, fine-tuned multilingual sequence-labeling system that performs word-level language identification across trilingual (English, Hindi, Telugu, and Universal/Punctuation) code-mixed text with real-time inference, high precision, and an accessible researcher-oriented user interface.

> [!NOTE]
> **V1 Scope Boundary:** Version 1.0.0 is dedicated strictly to Token-Level Language Identification. Machine translation (mT5 English/Hindi/Telugu translation) is not part of V1 and is reserved for Version 2 (V2.0.0).

---

## 2. Model & Training Configuration Summary

* **Pretrained Backbone:** `google/muril-base-cased` (12 layers, 768 hidden dimension, 12 attention heads, 199M parameters).
* **Classification Head:** Linear sequence labeling head mapped to 4 canonical classes (`EN`, `HI`, `TE`, `OTHER`).
* **Subword Alignment Strategy:** First-WordPiece token alignment during training and inference; whitespace tokens receive the prediction of their leading subword token.
* **Best Checkpoint:** `checkpoint-5000` (selected via highest validation macro F1 score).
* **Epochs Trained:** 4 complete epochs.
* **Completed Training Steps:** 5,420 steps.
* **Loss Function:** Cross-entropy loss with padding token masking (`label_id = -100`).
* **Hardware Environment:** Google Colab GPU (NVIDIA A100-SXM4-40GB) with FP16 mixed precision.

---

## 3. Official Benchmark Evaluation Metrics

Evaluation was conducted against the locked benchmark test set comprising **14,855 records** and **199,219 supervised evaluation tokens** across COMI-LINGUA (Hindi-English), Telugu-English Blog, and Telugu-English Twitter corpora.

### A. Overall Model Performance

| Metric | Validation Set | Locked Test Set | Generalization Delta |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 97.8195% | **98.1744%** | +0.3549 pp |
| **Macro F1** | 97.4904% | **98.0092%** | +0.5188 pp |
| **Supervised Tokens** | 24,902 | **199,219** | — |

*The positive generalization delta (+0.5188 pp Macro F1) verifies that the baseline model generalizes without empirical overfitting.*

### B. Per-Class Evaluation Summary (Locked Test Set: 199,219 Tokens)

| Language Class | Label ID | Precision | Recall | F1-Score | Support (Tokens) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **English (`EN`)** | 0 | 97.47% | 97.63% | **97.5511%** | 64,221 |
| **Hindi (`HI`)** | 1 | 98.59% | 98.89% | **98.7405%** | 69,130 |
| **Telugu (`TE`)** | 2 | 98.81% | 98.61% | **98.7103%** | 45,252 |
| **Other / Univ (`OTHER`)** | 3 | 97.56% | 96.51% | **97.0349%** | 20,616 |

### C. Test Confusion Matrix ($4 \times 4$)

```text
True \ Pred        EN        HI        TE     OTHER
EN             62,701       704       449       367
HI                678    68,362         1        89
TE                427       162    44,622        41
OTHER             523       110        86    19,897
```

---

## 4. Implemented Software Architecture

### A. Local Inference Engine (`src/inference/predictor.py`)
- Single-point `MuRILLIDPredictor` interface.
- Loads fine-tuned PyTorch safetensors directly into CPU/CUDA with `torch.no_grad()`.
- Implements subword chunking for long paragraphs exceeding 254 WordPieces without dropping tokens.
- Arithmetic mean confidence scoring per original token.

### B. FastAPI REST API Backend (`backend/main.py`)
- High-performance asynchronous REST endpoints:
  - `GET /health`: Lightweight service liveness check.
  - `GET /api/health`: Comprehensive system status, loaded model identity, device, and label schema.
  - `POST /api/predict`: Token-level prediction pipeline accepting `{"text": string}`.
- Pydantic validation schemas with HTTP 400/422 error handling.
- Full CORS middleware configuration.

### C. Frontend Interface (`frontend/`)
- Design Theme: *"Linguist's Lab"* × *"Minimal Light"* manuscript styling.
- Pure Vanilla HTML5, CSS3, and JavaScript — zero external CDN font or script dependencies.
- **Annotated View (Signature Element):** Renders words in high-legibility Serif with color-coded underlines and language tags (`EN`: Blue, `HI`: Vermilion, `TE`: Green, `OTHER`: Slate).
- **Table View:** Clean, accessible tabular breakdown with sortable/copyable columns.
- **Statistical Analytics:** Token count, language counts with `font-variant-numeric: lining-nums tabular-nums`, proportional distribution bar, and average model confidence.
- **Copy Results:** Tab-separated TSV export to clipboard with auto-expiring feedback notification.
- **Cancellation:** AbortController support when clearing active queries.
- **Responsive Architecture:** Fully verified at desktop (1280px), tablet (768px), and mobile (390px) viewports with zero horizontal overflow.

---

## 5. Local Run Instructions

### 1. Backend Server (Terminal 1)
```powershell
cd "C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend Client (Terminal 2)
```powershell
cd "C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence"
.\.venv\Scripts\python.exe -m http.server 5500 --directory frontend
```

### 3. Access in Browser
Navigate to:
```text
http://127.0.0.1:5500
```

---

## 6. Known Limitations & V2 Roadmap

1. **Romanized Telugu vs. Native Telugu:** The V1 training corpus predominantly features Romanized Telugu (Tenglish) alongside native Devanagari Hindi and English. Native script Telugu evaluation has not been formally benchmarked.
2. **Ambiguous Short Words:** Monosyllabic functional words shared across Indo-Aryan and Dravidian transliterations (e.g., *"ki"*, *"na"*) rely heavily on local contextual cues.
3. **Model 2 Scope:** Translation from code-mixed sentences into standardized monolingual English or Hindi will be implemented in Version 2 via sequence-to-sequence pretrained mT5.
