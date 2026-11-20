# CodeMix Intelligence — Frontend Web Client

The **CodeMix Intelligence** web interface is a high-performance, accessible, dependency-free single-page application (SPA) designed for real-time analysis, token-level language identification, transliteration, and neural machine translation of trilingual code-mixed text (English, Hindi, Telugu).

Designed with a **"Linguist's Modern Laboratory"** aesthetic, the application operates entirely on vanilla web standards (HTML5, CSS3, ES6+ JavaScript) without requiring Node.js, Webpack, React, or third-party client libraries.

---

## 📑 Tabs and Capabilities

The interface provides four specialized modes accessible via the top capability switcher:

```
[ Mode A: Language Identification ]  [ Mode B: Hinglish Translation ]  [ Mode C: Pipeline Translate ]  [ Mode D: Experiments & Benchmark ]
```

### 1. Language Identification (Mode A)
* **DOM Container:** `#mode-lid` | **Tab Trigger:** `#tab-lid`
* **Underlying Model:** Fine-tuned MuRIL (`google/muril-base-cased`) with token classification head.
* **Capabilities:**
  - Token-level language tagging for code-mixed sentences containing English (`EN`), Hindi (`HI`), Telugu (`TE`), and Other (`OTHER`/`UNIV`).
  - Interactive **Word Flow** visualization displaying each token with an animated language-colored underline and confidence percentage.
  - **Summary Metrics Dashboard**: Displays dominant language tag, total token count, average prediction confidence, and server latency.
  - **Tabular Data View**: Detailed table with per-token confidence breakdown and one-click JSON payload export.
  - Quick-load trilingual sample sentences for rapid testing.

### 2. Hinglish Translation (Mode B)
* **DOM Container:** `#mode-trans` | **Tab Trigger:** `#tab-trans`
* **Underlying Model:** Fine-tuned mT5-small (`google/mt5-small`) sequence-to-sequence translation model.
* **Capabilities:**
  - Translates Romanized Hindi (Hinglish) text into fluent, grammatically sound English.
  - Live character counter with an enforced 1000-character ceiling.
  - Keyboard accelerator: `Ctrl + Enter` (or `Cmd + Enter`) triggers instant translation.
  - One-click clipboard copy button with visual checkmark and alert toast.
  - **Intelligent Script Detection**: Analyzes input and warns if Telugu vocabulary is detected, gently recommending the trilingual Pipeline Translate tab.

### 3. Pipeline Translate (Mode C)
* **DOM Container:** `#mode-pipeline` | **Tab Trigger:** `#tab-pipeline`
* **Underlying Pipeline:** MuRIL LID + Rule-based ITRANS Transliteration + IndicTrans2 NMT.
* **Capabilities:**
  - **Trilingual Translation Strategies**:
    1. `full` *(Full pipeline - recommended)*: Token-level LID, rule-based Roman-to-Indic script transliteration, followed by IndicTrans2 NMT.
    2. `clause` *(Mixed Hindi+Telugu)*: Clause-by-clause segmentation, per-clause transliteration, individual clause translation, and stitched English output.
    3. `lid_only` *(Language ID only)*: Uses sentence-level dominant language tag to direct untransliterated text straight to the MT engine.
    4. `direct` *(Direct baseline)*: Direct translation with user-selectable source language hint (`TE` or `HI`).
  - **Interactive Token Chips**:
    - High-contrast language badges (`EN`, `HI`, `TE`, `OTHER`) ensuring accessibility without relying on color alone.
    - Native script preview (Telugu/Devanagari) rendered beneath Romanized words.
    - Accessible hover and keyboard-focused (`Tab`) tooltips displaying full language name, confidence score, native form, and approximate word meanings.
    - Dotted outline indicator for low-confidence tokens (<60%).
  - **Strategy Comparison View**:
    - "Compare strategies" button runs all 4 strategies sequentially (safe for CPU backends).
    - Side-by-side card grid highlighting lexical differences against the full pipeline result.
    - Optional Reference English Translation box computing character n-gram F-score (approximate chrF, $\beta=2$, $n=1..6$).
  - **Convenience & Productivity**:
    - 6 pre-configured trilingual test sentence chips.
    - Local translation history persisting the last 10 queries in `localStorage` (`codemix_history`), with instant reload and clear actions.
    - One-click `codemix-result.json` export containing translation, strategy metadata, token annotations, and timing breakdown.

### 4. Experiments & Benchmark (Mode D)
* **DOM Container:** `#mode-experiments` | **Tab Trigger:** `#tab-experiments`
* **Data Source:** `frontend/results.json`
* **Capabilities:**
  - Comprehensive empirical evaluation and ablation study dashboard.
  - **Headline Metric Callouts**: PHINC +12.5 chrF (full vs direct), LID gating +6.6 chrF, Token LID Macro-F1 0.983, Speedup (571 ms full vs 707 ms direct).
  - Pure CSS/HTML bar charts: PHINC benchmarks (chrF & BLEU), Development set ablation, Transliteration module ablation, and Mixed-language performance.
  - Complete Token-Level LID Evaluation Table (Precision, Recall, F1 for EN, HI, TE).
  - Transparent documentation of negative results (subword LID, dictionary transliteration) and technical limitations.
  - Sample sizes and statistical significance notes ($\text{sacreBLEU}$, bootstrap 95% confidence intervals).

---

## 🚀 How to Run

### Step 1: Start the FastAPI Backend
From the workspace root, activate your virtual environment and start Uvicorn on port `8000`:
```bash
# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# On Linux/macOS
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The server will initialize MuRIL LID immediately and launch a background daemon thread to warm up the IndicTrans2 pipeline models into RAM/VRAM.

### Step 2: Serve the Frontend
In a second terminal window, serve the `frontend/` directory over HTTP on port `5500`:
```bash
python -m http.server 5500 --directory frontend
```

### Step 3: Open in Browser
Navigate to:
```
http://127.0.0.1:5500
```
*(or `http://localhost:5500`)*

### Step 4: Verify Pipeline Health via Smoke Test
To verify the end-to-end backend connectivity without opening a browser:
```bash
python scripts/smoke_mt.py
```
This script executes sequential tests for Telugu (`full`), Hindi (`full`), and mixed Telugu+Hindi (`clause`), printing execution times and asserting HTTP 200 responses.

---

## 📴 Offline Demo Mode Mechanics

The frontend includes an **Offline Demo Mode** allowing complete functionality without a running backend:

### 1. Automatic Activation & Triggering
Demo mode is triggered automatically when:
- The periodic health check (`GET /api/mt/translate/health`, polled every 15s) fails or times out.
- The URL includes the query parameter `?demo=1` (e.g. `http://127.0.0.1:5500/?demo=1`).

### 2. Visual Banner
When active, an alert banner is displayed at the top of the Pipeline Translate tab:
```
[Demo mode - showing pre-computed results]
```

### 3. Pre-computed Cache (`frontend/demo_cache.json`)
The demo mode is backed by `frontend/demo_cache.json`, which pre-computes complete responses for all 6 standard example sentences across all 4 translation strategies (`direct`, `lid_only`, `full`, `clause`):
1. *"Nenu repu college ki vastanu, but assignment complete cheyyaledu"*
2. *"Meeru ee project deadline gurinchi manager tho matladara?"*
3. *"Kal meeting hai please slides bhej dena"*
4. *"Tum kab tak college aaoge?"*
5. *"NENU REPU college ki vastanuuuu plz"*
6. *"Nenu repu college ki vastanu, tum bhi aao na"*

### 4. Cache Lookups & Comparisons
- Clicking any example chip and pressing **Translate** retrieves the exact cached response, including word tokens, native script transliterations, tooltips, and server timings.
- Clicking **Compare strategies** runs the comparison view using cached results for all 4 strategies, with word-level diff highlighting and chrF calculations.
- If custom un-cached text is entered while offline, the app displays:
  `"This sentence is not in the offline demo. Choose one of the example chips."`

### 5. Auto-Recovery
When the FastAPI backend becomes reachable again, the health poller automatically dismisses the demo banner and seamlessly switches back to live API requests.

### 6. Remote Host Configuration
Click the gear icon in the top navigation to open the **Pipeline Settings** popover:
- Allows overriding `MT_API_BASE` (e.g., pointing to an ngrok tunnel or remote GPU machine `https://xxxx.ngrok-free.app`).
- The override is persisted across reloads in `localStorage` under `codemix_mt_base`.
- A **Reset** button returns the target URL back to `http://127.0.0.1:8000`.

---

## 📸 Screenshot Checklist

For project presentations, portfolio showcases, and academic reports, capture the following key states:

- [ ] **1. Pipeline Translate Result View**
  - **Setup:** Mode C tab with sentence *"Nenu repu college ki vastanu, but assignment complete cheyyaledu"*, strategy set to `full`, gloss checkbox checked.
  - **Focus:** Show the prominent English translation, normalized text banner, word meaning pills, and token chips with dual-script annotations and language badges.
  - **Interaction:** Hover or tab to a token chip to capture the active tooltip displaying confidence, native script, and approximate gloss.

- [ ] **2. Strategy Comparison View**
  - **Setup:** Click "Compare strategies" with a reference sentence (e.g., *"I will come to college tomorrow, but did not complete the assignment"*).
  - **Focus:** Side-by-side columns (`Direct`, `LID Only`, `Full Pipeline`, `Clause Mode`) displaying latency badges, approximate chrF chips, and highlighted diff tags (`<mark class="diff-word">`).

- [ ] **3. Experiments & Benchmark Dashboard**
  - **Setup:** Mode D tab loaded from `results.json`.
  - **Focus:** The 4 top headline metric callouts, the pure CSS horizontal bar charts for PHINC and Dev-set systems, the token LID precision/recall table, and the qualitative limitations panel.

- [ ] **4. Language Identification Tab (Mode A)**
  - **Setup:** Mode A tab with a trilingual mixed sentence.
  - **Focus:** Animated word chips with colored language underlines, the summary metrics grid (dominant language, confidence, speed), and the tabular token inspection table.

- [ ] **5. Offline Demo Mode Banner**
  - **Setup:** Navigate to `http://127.0.0.1:5500/?demo=1`.
  - **Focus:** Prominent demo mode banner with example chips and pre-computed pipeline output.

---

## ♿ Accessibility & Quality Standards

- **Keyboard Navigation:** Every control is fully accessible via `Tab` / `Shift+Tab`. Active controls feature high-contrast `:focus-visible` rings (`outline: 2px solid var(--ink)`).
- **Escape Key Handling:** Pressing `Escape` instantly closes open settings popovers, dismisses active tooltips, and blurs focused chips.
- **Color Independence:** Token chips and clause rows feature explicit textual language badges (`EN`, `HI`, `TE`, `OTHER`), fully complying with WCAG guidelines against color-only information encoding.
- **Screen Reader Support:** All form fields possess explicit `<label for="...">` and descriptive `aria-label` tags. Dynamic state updates, character counters, comparison progress, and copy notices utilize `aria-live="polite"` regions.
- **Responsive Layout:** Optimized across mobile (360px), tablet (768px), and desktop (1280px+) viewport widths with zero horizontal overflow.
- **Zero Console Noise:** Free of unhandled exceptions, runtime errors, and stray `console.log` statements.

---

## ⚠️ Known Technical Constraints

1. **Browser `file://` Origin Restrictions**:
   Opening `frontend/index.html` directly via the browser's file protocol (`file:///...`) triggers browser CORS security restrictions that prevent `fetch()` from loading `demo_cache.json` and `results.json`. The frontend must be served over HTTP (e.g. `python -m http.server 5500` or via FastAPI static file mounting).
2. **First-Request CPU Cold Start**:
   The IndicTrans2 pipeline models are ~1.2 GB in size. On CPU-only environments without GPU acceleration, model loading during server startup or the first translation request may require 20–45 seconds. The backend's background warm-up thread mitigates this by pre-loading models upon server initialization.

