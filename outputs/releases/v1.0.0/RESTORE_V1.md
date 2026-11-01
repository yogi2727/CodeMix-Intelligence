# Restoring CodeMix Intelligence V1.0.0

This runbook provides non-destructive, step-by-step instructions to restore and verify the stable **CodeMix Intelligence V1.0.0** release if needed during or after subsequent development phases.

---

## Prerequisites
- Local repository location: `C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence`
- Python 3.14+ virtual environment located at `.venv/`
- PowerShell terminal

---

## Step 1: Switch Git to the V1.0.0 Release

Switch to the annotated release tag `v1.0.0` or checkout a clean recovery branch from the tag:

```powershell
cd "C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence"

# Option A: Inspect the release tag in detached HEAD state
git checkout v1.0.0

# Option B (Recommended): Checkout a recovery branch from the V1.0.0 tag
git checkout -b restore/v1.0.0-recovery v1.0.0
```

> [!IMPORTANT]
> Never use destructive commands such as `git reset --hard` or `git clean -fdx`.

---

## Step 2: Verify or Restore Model Weights

Check if `artifacts/models/muril_lid_baseline/best_model/model.safetensors` exists and is intact:

```powershell
Get-FileHash -Path "artifacts\models\muril_lid_baseline\best_model\model.safetensors" -Algorithm SHA256
```

**Expected Hash:**
```text
714DEFC6F90659EBC25E5E011A9101579D36CF9F3B4C57165C0614F1BC744BAE
```

### If the extracted model folder is missing or corrupted:
Extract the original backup archive [`muril_lid_best_model.zip`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/muril_lid_best_model.zip) directly into the model directory:

```powershell
# Verify the ZIP archive integrity
Get-FileHash -Path "muril_lid_best_model.zip" -Algorithm SHA256
# Expected: A5439181F02FECE996BF526629C70DA20166A53450FB615A44F343D8CBF8A827

# Re-extract model files
.\.venv\Scripts\python.exe scripts/integrate_step33A_artifacts.py
```

---

## Step 3: Run the Verification Test Suite

Run the 13 backend unit and integration tests to confirm the inference engine and REST API operate correctly:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_inference_and_api.py -q
```
**Expected Output:** `13 passed in ~10s`.

---

## Step 4: Start the Services

### Terminal 1 — Backend (FastAPI / Uvicorn)
```powershell
cd "C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
*Health check verify: navigate to `http://127.0.0.1:8000/api/health` -> should report `status: "ready"`.*

### Terminal 2 — Frontend (HTTP Server)
```powershell
cd "C:\Users\YOGESWAR\OneDrive\Apps\CodeMix-Intelligence"
.\.venv\Scripts\python.exe -m http.server 5500 --directory frontend
```

---

## Step 5: Open the Application in Browser

Navigate your browser to:
```text
http://127.0.0.1:5500
```

Verify that the status pill shows **Model ready** with a green indicator, enter a test sentence (or click a sample pill), and click **Detect languages**.
