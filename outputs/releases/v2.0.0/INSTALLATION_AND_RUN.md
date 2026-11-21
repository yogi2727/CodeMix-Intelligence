# CodeMix Intelligence V2.0.0 — Installation and Run Guide

This guide provides step-by-step, verified PowerShell instructions for setting up, testing, and running CodeMix Intelligence V2 on a Windows system.

---

## 1. Prerequisites and Environment Setup

- **Operating System:** Windows 10/11 (AMD64 / x86_64)
- **Python:** Python 3.10+ (Verified on Python 3.14.3)
- **Memory Requirements:** Minimum 4 GB physical RAM (8 GB+ recommended)
- **Free Disk Space:** Minimum 5 GB free disk space for model weights and virtual environment

### A. Clone or Extract the Project
Open Windows PowerShell and navigate to the project directory:

```powershell
cd C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence
```

### B. Virtual Environment Setup
Ensure the Python virtual environment is activated:

```powershell
# Create virtual environment if not already present
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Verify installed versions
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\pip.exe list
```

Required packages in `.venv`:
- `torch` (>= 2.15.0+cpu)
- `transformers` (>= 5.22.0)
- `sentencepiece` (>= 0.2.0)
- `safetensors` (>= 0.8.0)
- `fastapi` (>= 0.115.0)
- `uvicorn` (>= 0.30.0)
- `pydantic` (>= 2.8.0)

---

## 2. Model Artifact Placement

CodeMix Intelligence requires model weights in the designated local directories:

### Model 1: MuRIL Language Identification
Ensure the fine-tuned checkpoint exists at:
`artifacts/models/muril_lid_baseline/best_model/`
Required files:
- `config.json`
- `model.safetensors` (~948 MB)
- `tokenizer_config.json`
- `vocab.txt`
- `special_tokens_map.json`

### Model 2: mT5 Hinglish Translation
Ensure the extracted model directory exists at:
`artifacts/models/mt5_hinglish_translation/`
Required files:
- `config.json`
- `generation_config.json`
- `model.safetensors` (~1.14 GB)
- `tokenizer.json` (~16 MB)
- `tokenizer_config.json`
- `release_manifest.json`

If extracting from the verified release archive:
```powershell
# Extract release archive into target directory
$archive = "artifacts/releases/CodeMix_Intelligence_MT5_Hinglish_English_v1.0.0.zip"
$dest = "artifacts/models/mt5_hinglish_translation"
Expand-Archive -Path $archive -DestinationPath $dest -Force
```

---

## 3. Running Automated Tests

Before launching the server, verify the integrity of both models and the API:

```powershell
# 1. Run MuRIL Language Identification & API tests (13 tests)
.\.venv\Scripts\python.exe -m unittest tests/test_inference_and_api.py

# 2. Run mT5 Translation standalone inference tests (15 tests)
.\.venv\Scripts\python.exe -m unittest tests/test_translation_inference.py

# 3. Run mT5 Translation FastAPI route and singleton tests (12 tests)
.\.venv\Scripts\python.exe -m unittest tests/test_translation_api.py

# Expected Output: Total 40 tests passed across all three suites.
```

---

## 4. Launching the Application

Start the unified FastAPI server via Uvicorn:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Console output will confirm:
```text
Loading MuRIL LID Predictor on application startup...
MuRIL LID Predictor loaded successfully on device: cpu
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 5. Using the Application

### A. Accessing the Web Interface
Open any modern web browser (Chrome, Edge, Firefox) and navigate to:
```
http://127.0.0.1:8000/
```
- Click the **Language Identification (MuRIL)** tab to inspect token-level language tags.
- Click the **Hinglish Translation (mT5)** tab to translate Romanized Hinglish sentences to English.

### B. Interacting via PowerShell CLI

#### 1. System Health Check
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -Method Get | ConvertTo-Json
```
Response:
```json
{
  "status": "healthy",
  "device": "cpu",
  "muril_loaded": true,
  "mt5_loaded": false,
  "supported_labels": ["EN", "HI", "TE", "OTHER"],
  "tasks": ["token_level_language_identification", "hinglish_to_english_translation"]
}
```

#### 2. Test Language Identification (`POST /api/predict`)
```powershell
$body = @{ text = "Main kal Hyderabad ja raha hu and will attend meeting" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/predict" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
```

#### 3. Test Hinglish Translation (`POST /api/translate`)
```powershell
$body = @{ text = "Mujhe thoda paani chahiye please" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/translate" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json
```
Response:
```json
{
  "original_text": "Mujhe thoda paani chahiye please",
  "translated_text": "I need some water please",
  "source_length": 32,
  "translated_length": 24,
  "model": "google/mt5-small"
}
```

---

## 6. Stopping the Server

To stop the running application, press `Ctrl+C` in the active PowerShell terminal. The lifespan shutdown hook will cleanly release loaded models and free memory:
```text
Shutting down models...
INFO:     Finished server process
```

