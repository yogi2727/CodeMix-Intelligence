# CodeMix Intelligence V2.0.0 Release Notes
## Stable Release Candidate — Unified Multilingual Language Identification & Hinglish Translation

**Release Name:** CodeMix Intelligence V2.0.0 — Dual-Model Architecture  
**Version:** `2.0.0`  
**Release Date:** 2026-11-03  
**Active Development Branch:** `feature/mt5-translation-v2`  
**Baseline V1 Protection:** V1 `main` and tag `v1.0.0` preserved at commit `c9509f0e9e10fe715c759edc09d1dacadb540f74`  

---

## 1. Executive Summary & Capabilities

CodeMix Intelligence V2.0.0 represents a major evolutionary milestone: expanding the platform from a single sequence-labeling model into a unified, dual-capability natural language processing system engineered specifically for Indian multilingual and code-mixed communications.

### Core Capabilities:
1. **Model 1: Token-Level Language Identification (MuRIL)**
   - Backbone: `google/muril-base-cased` (Multilingual Representations for Indian Languages).
   - Task: Word- and subword-level language classification across trilingual code-mixed inputs.
   - Classification Taxonomy: 4 classes — English (`EN: 0`), Hindi (`HI: 1`), Telugu (`TE: 2`), and Universal/Punctuation (`OTHER: 3`).
   - Loading Strategy: Eager initialization during FastAPI lifespan startup to guarantee zero cold-start latency on language identification queries.
   - Endpoint: `POST /api/predict`.

2. **Model 2: Romanized Hinglish-to-English Neural Translation (mT5-small)**
   - Backbone: `google/mt5-small` (multilingual Text-to-Text Transfer Transformer).
   - Task: Sequence-to-sequence translation converting informal, Romanized Hindi-English ("Hinglish") into clean, grammatical English.
   - Task Prefix: `"translate Hinglish to English: "`
   - Generation Strategy: deterministic 4-beam search decoding (`num_beams=4`, `do_sample=False`, `max_length=128`). `max_source_length=128` limits the encoder input, while `max_length=128` caps the generated decoder sequence. FP32 precision (`torch.float32`).
   - Loading Strategy: Lazy singleton loaded on the first translation request using thread-safe double-checked locking (`threading.Lock`), optimizing application startup speed and physical memory footprint.
   - Endpoint: `POST /api/translate`.

3. **Unified REST API & System Health Monitoring**
   - High-throughput FastAPI application running with Uvicorn.
   - Diagnostic endpoint `GET /api/health` providing live status, execution device (CPU/CUDA), and individual initialization flags for both models (`muril_loaded`, `mt5_loaded`).

4. **Unified "Linguist's Lab × Minimal Light" User Interface**
   - Pure vanilla HTML5, CSS3, and JavaScript — zero CDN dependencies, zero telemetry, fully offline capable.
   - Dual-capability switcher tabs allowing researchers to toggle seamlessly between Language Identification and Neural Translation.
   - Strict state isolation: query inputs, analysis tables, annotated badge views, translation outputs, and character counts are independently preserved across tab switches.
   - Accessible keyboard navigation (`role="tab"`, `aria-selected`, `aria-controls`, and `Enter`/`Ctrl+Enter` submit hotkeys).

---

## 2. Official Evaluation & Performance Benchmarks

### A. Model 1 (MuRIL Language Identification) Locked Benchmark Metrics
- **Supervised Evaluation Tokens:** 199,219 tokens across 14,855 records (COMI-LINGUA Hindi-English, Telugu-English Blog, Telugu-English Twitter).
- **Overall Accuracy:** **98.1744%**
- **Macro F1 Score:** **98.0092%**
- **Per-Class F1 Scores:**
  - English (`EN`): 97.5511% (Support: 64,221 tokens)
  - Hindi (`HI`): 98.7405% (Support: 69,130 tokens)
  - Telugu (`TE`): 98.7103% (Support: 45,252 tokens)
  - Universal/Punctuation (`OTHER`): 97.0349% (Support: 20,616 tokens)

### B. Model 2 (mT5 Hinglish-to-English Translation) Test Metrics
- **Training Corpus:** PHINC (Parallel Hinglish Dataset, CC BY 4.0).
- **Split Distribution:** 10,802 train, 1,350 validation, 1,351 locked test records.
- **Held-Out Test Corpus Metrics:**
  - **BLEU:** **25.3784**
  - **chrF:** **43.2323**
- **Validation Checkpoint Metrics:** BLEU 45.5, chrF 37.71, Validation Loss 2.3983.

> [!IMPORTANT]
> **Metric Interpretation & Scope Boundaries:**
> 1. BLEU (25.3784) and chrF (43.2323) are standard corpus n-gram overlap and character-level translation scores, **NOT** percentage accuracy metrics.
> 2. Model 2 is strictly evaluated on **Romanized Hinglish-to-English translation**. It has **not** been trained or established as a Telugu-English translation model. Telugu inputs should be analyzed via Model 1 for language identification.

---

## 3. Hardware & Runtime Resource Profile

All benchmarks were evaluated in the target local environment:
- **Operating System:** Microsoft Windows 11 AMD64
- **Runtime:** Python 3.14.3, PyTorch 2.15.0+cpu, Hugging Face Transformers 5.22.1
- **Hardware Architecture:** AMD CPU (FP32 execution, CUDA not active)

| Metric | Standalone In-Process | Live FastAPI / Uvicorn Server | Notes |
| :--- | :---: | :---: | :---: |
| **Model 1 Init Time** | ~1.42 s | ~1.85 s | Eager load during lifespan startup |
| **Model 2 Init Time (Lazy)** | ~6.19 s | Included in 1st request | Triggered on first `/api/translate` call |
| **Model 1 Latency (Inference)** | ~25 ms – 70 ms | ~45 ms – 90 ms | Per sentence (batch size = 1) |
| **Model 2 Cold-Start Request** | N/A | **34.98 s** | Combined weights load + first beam decode |
| **Model 2 Steady-State Latency** | **0.308 s** | **16.32 s** | Standalone PyTorch vs Uvicorn sync dispatch |
| **Memory Allocation (RAM)** | +1,505 MB RSS | ~800 MB active FP32 | Safe under available physical memory |

---

## 4. Testing & Verification Summary

A comprehensive 4-stage automated verification was executed:
1. **Regression & Integration Test Suites:**
   - `tests/test_inference_and_api.py`: 13 passed (MuRIL LID & API endpoints).
   - `tests/test_translation_inference.py`: 15 passed (mT5 standalone translation, beam decoding, error handling).
   - `tests/test_translation_api.py`: 12 passed (FastAPI `/api/translate`, validation, error propagation, lazy singleton).
   - **Total:** **40 passed, 0 failures, 0 errors** (100% pass rate).
2. **Bytecode Compilation Check:**
   - `src/inference/predictor.py`, `src/inference/translator.py`, `backend/main.py` compiled cleanly (`py_compile`).
3. **Frontend Syntax Check:**
   - `frontend/app.js` validated via `node -c` (valid ECMAScript, zero syntax errors).
4. **Git Hygiene & Line Check:**
   - `git diff --check` reported zero trailing whitespace or merge conflict markers.

> [!NOTE]
> **Visual Verification Boundary:**
> In accordance with strict audit integrity standards, visual graphical browser rendering is designated as **NOT TESTED / PENDING** due to the headless execution environment without a local display server. Core DOM structures, tab switching handlers, ARIA states, and CSS variables were syntactically and logically verified.

---

## 5. Artifacts and Release Distribution

- **Source Release Archive:** `outputs/releases/CodeMix_Intelligence_v2.0.0_source.zip`
- **Extracted Model Locations (Local Runtime):**
  - Model 1: `artifacts/models/muril_lid_baseline/best_model/`
  - Model 2: `artifacts/models/mt5_hinglish_translation/`
- **Model 2 Standalone Archive:** `artifacts/releases/CodeMix_Intelligence_MT5_Hinglish_English_v1.0.0.zip` (SHA-256: `0c3a1cd132d4ce7647bd206a81d72a674e08cdab7cad1a5158c542e6b09020e2`)

