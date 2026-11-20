# CodeMix Intelligence: Trilingual Code-Mixed Language Understanding System

**Project Title:** A Transformer-Based Trilingual Code-Mixed Language Understanding System for English, Hindi, and Telugu

---

## 📌 Project Overview & Objective

In multilingual societies, speakers frequently alternate between languages within a single utterance or conversation—a linguistic phenomenon known as **code-mixing** and **code-switching**. In the Indian subcontinent, code-mixed sentences involving **English, Hindi, and Telugu** are pervasive across social media, customer service chats, conversational agents, and everyday communication.

Standard Natural Language Processing (NLP) pipelines trained on monolingual corpora degrade significantly when processing code-mixed text due to syntactic divergence, non-standard spellings, lexical borrowing, and script variations (both native scripts and Romanized transliterations).

**Core Objective:**  
To build, fine-tune, and evaluate a robust multilingual Transformer-based system (utilizing architectures such as XLM-RoBERTa, IndicBERT, or multilingual BERT) capable of performing **token-level language identification (LID)**. The model identifies the language tag of individual words/tokens in sentences composed of English, Hindi, Telugu, or any mixture thereof.

---

## 🗺️ Roadmap & Scope

The project is structured in modular phases:
1. **Token-Level Language Identification:** Classify each token into target language tags (e.g., `en`, `hi`, `te`, `univ`/`other`).
2. **Trilingual Support:** Unified handling of English, Hindi, and Telugu within a single model.
3. **Native-Script Code-Mixed Input:** Processing text in Devanagari (Hindi), Telugu script, and Latin script (English).
4. **Romanized Code-Mixed Input (Extension):** Handling transliterated Hindi (Hinglish) and Telugu (Tenglish) written in Latin characters.
5. **Downstream Sequence Tasks (Optional Extension):** Evaluating the backbone representation on Code-Mixed Part-of-Speech (POS) tagging or Named Entity Recognition (NER).
6. **Model Evaluation Dashboard:** Generating comprehensive evaluation metrics (Precision, Recall, F1-score, Confusion Matrix) per language class.
7. **Interactive Web Application:** Deploying an intuitive user interface and REST API for real-time code-mixed sentence analysis and token visualization.

---

## 🛠️ Planned Technology Stack

- **Deep Learning Framework:** PyTorch
- **Transformers & NLP:** Hugging Face `transformers`, `datasets`, `tokenizers`, `accelerate`, `seqeval`, `evaluate`
- **Candidate Pretrained Backbones:** XLM-RoBERTa (`xlm-roberta-base`), IndicBERT, Multilingual BERT (`bert-base-multilingual-cased`)
- **Data & Numerical Processing:** NumPy, Pandas, Scikit-learn
- **Visualization & Logging:** Matplotlib, Seaborn, TensorBoard
- **Backend API:** FastAPI, Uvicorn, Pydantic
- **Frontend Interface:** Modern HTML5, Vanilla CSS, JavaScript
- **Testing & Tooling:** PyTest, PyYAML, python-dotenv

---

## 📂 Project Architecture & Directory Structure

```text
CodeMix-Intelligence/
├── .gitignore               # Git ignore rules for environments, checkpoints, and data
├── README.md                # Project documentation and setup guide
├── requirements.txt         # Project dependencies
├── configs/                 # Experiment configuration files (YAML/JSON)
├── data/                    # Data directory (excluded from version control)
│   ├── raw/                 # Raw datasets and corpora
│   ├── processed/           # Preprocessed, tokenized, and split datasets
│   └── custom/              # Custom trilingual LID dataset (Schema v1.3.0) & pilot governance
├── notebooks/               # Jupyter notebooks for EDA and rapid prototyping
├── src/                     # Core source code modules
│   ├── data/                # Dataset loaders, download scripts, and batch collators
│   ├── preprocessing/       # Text cleaning, normalization, and tokenization utilities
│   ├── models/              # Transformer model wrappers and classification heads
│   ├── training/            # Training loop, optimizer setups, and learning rate schedulers
│   ├── evaluation/          # Token-level metric computation (seqeval, confusion matrices)
│   └── inference/           # Inference pipeline and real-time predictor classes
├── backend/                 # FastAPI REST API services and request/response schemas
├── frontend/                # Interactive web client for real-time visualization
├── checkpoints/             # Trained model weights and tokenizer artifacts (gitignored)
├── outputs/                 # Generated experiment artifacts
│   ├── metrics/             # Evaluation reports, JSON metrics, and classification reports
│   ├── predictions/         # Validation and test prediction dumps
│   └── plots/               # Training curves, attention maps, and confusion matrix plots
└── tests/                   # Unit and integration tests
```

---

## 🔍 Module Descriptions

- **`configs/`**: Centralized configuration management for model hyperparameters, training arguments, learning rates, batch sizes, and data paths without hardcoding values in scripts.
- **`data/`**: Structured data storage separated into `raw/` (unmodified sources), `processed/` (cleaned, tagged, and split datasets), and `custom/` (ad-hoc validation samples).
- **`notebooks/`**: Exploratory data analysis, label distribution checks, and experimental proof-of-concept workflows.
- **`src/data/`**: Data ingestion pipelines, PyTorch `Dataset` and `DataLoader` abstractions.
- **`src/preprocessing/`**: Text cleaning, script normalization, punctuation handling, and subword-to-word label alignment logic.
- **`src/models/`**: Neural network definitions, Transformer classification heads, and model initialization logic.
- **`src/training/`**: Model training and validation loops, checkpointing, early stopping, and metric logging.
- **`src/evaluation/`**: Token-level sequence labeling evaluation using `seqeval`, F1 scoring, and error analysis.
- **`src/inference/`**: Lightweight inference engine for single-sentence and batch predictions.
- **`backend/`**: Web service layer hosting inference endpoints for integration with web interfaces or external clients.
- **`frontend/`**: Web application allowing users to input code-mixed sentences and visually inspect color-coded language tags for each word.
- **`checkpoints/`**: Storage for saved model weights (`.pt`, `.safetensors`) and tokenizer configs.
- **`outputs/`**: Dedicated space for experiment results, confusion matrix figures, training loss curves, and prediction logs.
- **`tests/`**: Automated test suites verifying data preprocessing, pipeline integrity, and model inference.

---

## 🚀 Getting Started (Initial Environment Setup)

### 1. Clone & Navigate to Workspace
```bash
git clone <repository-url>
cd CodeMix-Intelligence
```

### 2. Create and Activate a Virtual Environment
```bash
# Using Python venv (Python 3.10+ recommended)
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎬 Run the demo

Follow these steps to launch the dual-model backend and the interactive web interface:

### 1. Start the FastAPI Backend
Start the server hosting MuRIL LID, mT5 translation, and the IndicTrans2 pipeline with background warm-up:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend initializes MuRIL for token-level LID immediately and automatically warms up the IndicTrans2 translation pipeline in a background daemon thread.

### 2. Start the Frontend Server
In a separate terminal, serve the static web interface over HTTP:
```bash
python -m http.server 5500 --directory frontend
```

### 3. Open in Browser
Open [http://127.0.0.1:5500](http://127.0.0.1:5500) (or [http://localhost:5500](http://localhost:5500)) in your web browser:
- **Language Identification tab**: Token-level LID with MuRIL.
- **Hinglish Translation tab**: Romanized Hinglish-to-English translation with fine-tuned mT5.
- **Pipeline Translate tab**: Trilingual Hindi/Telugu/English translation with IndicTrans2 and strategy ablations (`direct`, `lid_only`, `full`, `clause`).
- **Experiments tab**: Benchmarks, ablations, and negative results.

### 4. Verify Pipeline Health via Smoke Test
Run the automated end-to-end smoke test against the live backend:
```bash
python scripts/smoke_mt.py
```
This tests Telugu (`full`), Hindi (`full`), and mixed Telugu+Hindi (`clause`) translations sequentially.

---

## 👥 Contributors & Academic Context

- **Institution:** University NLP Project
- **Domain:** Multilingual & Code-Mixed Natural Language Processing
