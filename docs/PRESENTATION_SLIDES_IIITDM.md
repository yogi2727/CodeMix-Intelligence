# PRESENTATION SLIDES: CodeMix Intelligence
## A Transformer-Based Trilingual Code-Mixed Language Understanding and Machine Translation System

---

<!-- slide 1 -->
# Slide 1: Title Slide

### CodeMix Intelligence: A Transformer-Based Trilingual Code-Mixed Language Understanding and Machine Translation System

- **Course:** Natural Language Processing
- **Department:** Department of Computer Science and Engineering
- **Institution:** Indian Institute of Information Technology, Design and Manufacturing, Kurnool (IIITDM Kurnool)
- **Student Presenter:** T. Yogeswar
- **Roll Number:** 124AD0065
- **Project Supervisor:** Dr. Santha Babu (Assistant Professor, Dept. of CSE)
- **Academic Session:** 2026–2027

> **Presenter Notes (What to say):**  
> *"Good morning/afternoon, Sir. I am T. Yogeswar (Roll No: 124AD0065). Today, I am presenting my NLP project titled 'CodeMix Intelligence'. This project focuses on solving two foundational problems in Indic natural language processing: Token-level Language Identification and Machine Translation for trilingual code-mixed text involving English, Hindi, and Telugu."*

---

<!-- slide 2 -->
# Slide 2: Motivation & The Code-Mixing Problem

### Why is Code-Mixed NLP Difficult?

- **Real-World Reality:** In India, speakers rarely communicate in pure textbook monolingual languages. Digital communication (WhatsApp, Instagram, Twitter/X) is dominated by:
  - **Code-Switching (Inter-sentential):** Switching languages between sentences.
  - **Code-Mixing (Intra-sentential):** Mixing words and morphemes within the same syntactic sentence.
- **The Roman Script Bottleneck:**
  - Native speakers almost exclusively write Hindi and Telugu using the **Latin (Roman) keyboard**.
  - Creates non-standardized sociolects: **Hinglish** (Hindi + English) and **Tenglish** (Telugu + English).
- **Catastrophic Failure of Standard NLP Models:**
  - Standard models (BERT, GPT, MarianMT, NLLB) assume formal orthography and native scripts (Devanagari, Telugu lipi).
  - On Romanized code-mixed text, subword tokenizers break words into meaningless fragments, leading to hallucination and translation failure.

> **Presenter Notes:**  
> *"Sir, if we take everyday social media or customer chat, people don't type in pure Devanagari or Telugu script; they type phonetically using Latin letters. When we feed sentences like 'Nenu repu vastanu' or 'Kal meeting hai slides bhej dena' into standard translation models, they fail because the models expect standard native scripts and formal grammatical syntax."*

---

<!-- slide 3 -->
# Slide 3: Problem Statement & Project Objectives

### Formal Problem Formulation

Given a Romanized code-mixed sentence $S = (w_1, w_2, \dots, w_N)$ where each token $w_i$ may belong to English, Hindi, Telugu, or punctuation:

1. **Task 1: Token-Level Language Identification (Sequence Labeling)**
   - Predict tag sequence $Y = (y_1, y_2, \dots, y_N)$ where $y_i \in \{\text{EN}, \text{HI}, \text{TE}, \text{OTHER}\}$.
   - Must handle intra-word transitions, abbreviations, and chat slang.

2. **Task 2: Code-Mixed to English Translation (Seq2Seq Generation)**
   - Translate $S$ into a grammatical, natural English sentence $T = (t_1, t_2, \dots, t_M)$.
   - Resolve linguistic switches, post-positions, and colloquial vocabulary without losing semantic meaning.

### Concrete Measurable Objectives
- Train a trilingual token LID model with **Macro-F1 > 0.95**.
- Build an end-to-end seq2seq baseline using **`google/mt5-small`**.
- Design an engineered **IndicTrans2 Hybrid Pipeline** that beats the baseline.
- Evaluate rigorously on the **1,351-sentence locked PHINC test set** with statistical significance tests.

> **Presenter Notes:**  
> *"Our project tackles two concrete tasks: first, token-level language tagging to know which word belongs to which language, and second, translating that code-mixed sequence into clear English. We set high benchmarks: Macro-F1 above 0.95 for LID, and beating the fine-tuned mT5 baseline on the standard 1,351 PHINC benchmark."*

---

<!-- slide 4 -->
# Slide 4: What Makes This Project Unique? (The Telugu / Tenglish Challenge)

### Bridging the Dravidian Gap in Code-Mixed NLP

| Dimension | Typical Code-Mixed Research | Our Project: CodeMix Intelligence |
| :--- | :--- | :--- |
| **Language Scope** | Exclusively bilingual (Hindi + English) | **Trilingual:** English + Hindi (Indo-Aryan) + **Telugu (Dravidian)** |
| **Morphological Family** | Indo-Aryan (separate prepositions) | **Agglutinative Dravidian** (inflected post-position markers) |
| **Dataset Availability** | Moderate parallel corpora (PHINC, LinCE) | **Extremely scarce**; virtually zero parallel Romanized Tenglish data |
| **Vowel Phonology** | 5 Latin vowels map reasonably to Hindi | **Severe vowel ambiguity** (short $e$ vs long $ee$; short $o$ vs long $oo$) |
| **Translation Approach** | Single language tag forced on sentence | **Clause-level segmentation** allowing per-clause language tags |

### The Telugu Practical Feasibility Problem
- In Telugu, post-positions attach directly to nouns:
  - *college-ki* (to college), *manager-tho* (with manager), *deadline-gurinchi* (about deadline).
- Standard tokenizers cannot separate the noun from the case marker.
- We solved this practical barrier by designing a **phonetic transliterator grounded in a curated Telugu lexicon (`te_lexicon.csv`)**, making Tenglish translation feasible and robust.

> **Presenter Notes:**  
> *"Sir, what sets this project apart is our inclusion of Telugu. Almost all existing literature only looks at Hindi-English. Telugu is a Dravidian language with an agglutinative structure—words take case markers like 'college-ki' or 'manager-tho'. Furthermore, there are no large parallel datasets for Romanized Telugu to English. We overcame this by using a linguistically informed transliteration engine with lexical grounding."*

---

<!-- slide 5 -->
# Slide 5: High-Level System Architecture

### The Dual-Track Architectural Paradigm

```
                        [ Input: Romanized Code-Mixed Text ]
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [ Track 1: Baseline MT ]                      [ Track 2: Hybrid Pipeline ]
     • Model: google/mt5-small                     • Stage 1: Text Normalizer
     • Paradigm: End-to-End Seq2Seq                • Stage 2: MuRIL Token LID (EN/HI/TE)
     • Generation: 4 Beams, FP32                   • Stage 3: Script Transliteration
     • Task Prefix: 'translate Hinglish...'        • Stage 4: Clause-Level Segmenter
                 │                                 • Stage 5: IndicTrans2 Engine
                 ▼                                               │
     [ English Output (43.09 chrF) ]                             ▼
                                                   [ English Output (53.17 chrF) ]
                                                   [ Net Gain: +9.74 chrF (p < 0.0001) ]
```

- **Track 1:** Tests whether a single monolithic Transformer can learn Romanized code-mixing end-to-end.
- **Track 2:** Breaks the problem into linguistically sound modules: clean noise $\rightarrow$ detect language $\rightarrow$ convert to native script $\rightarrow$ segment clauses $\rightarrow$ translate using a high-resource Indic model.

> **Presenter Notes:**  
> *"Here is our high-level architecture. We compare two distinct approaches: Track 1 is the monolithic approach using fine-tuned mT5-small. Track 2 is our engineered modular pipeline. Our experiments prove that the modular pipeline outperforms the black-box approach by nearly 10 chrF points."*

---

<!-- slide 6 -->
# Slide 6: Dataset Curation & Cryptographic Split Integrity

### Zero-Leakage Data Partitioning

```
PHINC Dataset (13,503 Pairs)
  ├── Near-Duplicate Jaccard Clustering
  ├── Train Split:      10,802 pairs (80.0%)  [SHA-256: f9b9b4e5...]
  ├── Validation Split:  1,350 pairs (10.0%)  [SHA-256: b63971bb...]
  └── Locked Test Split: 1,351 pairs (10.0%)  [SHA-256: 7cd192e2...]
```

### Rigorous Audit Guarantees
1. **Mathematical Disjointness:**
   $$\text{Train IDs} \cap \text{Val IDs} = \emptyset, \quad \text{Train IDs} \cap \text{Test IDs} = \emptyset$$
2. **Near-Duplicate Protection:** Sentences with $>0.8$ lexical Jaccard similarity (e.g., retweets) were grouped into common clusters before splitting to prevent train-test memorization.
3. **Trilingual LID Benchmark Corpus:**
   - 665,313 training tokens (43,369 sentences).
   - 199,219 locked test tokens (14,855 sentences) combining CoMi-Lingua, Twitter dumps, and verified blogs.
4. **Curated Trilingual Benchmark ($n=50$):**
   - 40 multi-clause and 10 intra-clause sentences featuring Telugu-Hindi-English switches.

> **Presenter Notes:**  
> *"To ensure scientific validity, all data splits were cryptographically locked with SHA-256 hashes. We clustered near-duplicates before splitting to ensure the test set evaluates genuine generalization, with zero data leakage."*

---

<!-- slide 7 -->
# Slide 7: NLP Core 1: Token-Level Language Identification

### Fine-Tuning MuRIL for Sequence Tagging

- **Backbone Model:** `google/muril-base-cased` (12 layers, 768 hidden dimension, 237M parameters), pretrained on 17 Indic languages and Latin-transliterated text.
- **Subword Alignment & First-Token Labeling:**
  - Words split into WordPieces: e.g., *"vastanu"* $\rightarrow$ `["vas", "##tan", "##u"]`.
  - First subword gets ground-truth label; subsequent subwords get PyTorch ignore index ($-100$).
- **Masked Cross-Entropy Loss:**
  $$\mathcal{L}_{\text{CE}} = - \sum_{i=1}^{N} \sum_{c \in \{\text{EN, HI, TE, OTHER}\}} \mathbb{I}(y_i = c) \log P(y_i = c \mid s_{i,1})$$
- **Sliding Window for Long Sentences:**
  - Sequences $>254$ WordPieces are chunked using a sliding window with a 32-token overlap.
  - Overlapping predictions are resolved via majority probability voting.

> **Presenter Notes:**  
> *"For Token LID, we fine-tune Google's MuRIL model. Because MuRIL uses WordPiece tokenization, a single word can split into multiple subwords. We supervise only the first subword and mask the rest with -100 in the Cross-Entropy loss. For long inputs, we use a sliding window with 32-token overlap."*

---

<!-- slide 8 -->
# Slide 8: NLP Core 2: End-to-End Seq2Seq Baseline (mT5-Small)

### Architecture, Setup & Critical Debugging Discovery

- **Model:** `google/mt5-small` (6 encoder layers, 6 decoder layers, 8 attention heads, $d_{\text{model}}=512$, 300M parameters).
- **Formulation:** Formulated as sequence-to-sequence generation:
  - Input: `"translate Hinglish to English: " + source_text`
  - Target: Natural English reference translation.
- **Training Hyperparameters:**
  - 3 epochs on 10,802 PHINC pairs, AdamW optimizer, LR: $1 \times 10^{-4}$, effective batch size 16.
  - Inference: Deterministic Beam Search (4 beams, `max_length=128`, FP32 precision).

### The Untied Embedding Discovery (`tie_word_embeddings = False`)
- In `google/mt5-small`, `config.json` defaults to `tie_word_embeddings: true`.
- During fine-tuning on PyTorch/Transformers, the output projection matrix (`lm_head.weight`, shape $[250112, 512]$) and input token embeddings (`shared.weight`) drift apart.
- If loaded with `tie_word_embeddings: true`, the library forcibly overwrites `lm_head` with `shared.weight`, corrupting generation into repetitive tokens (e.g., `proxy[2][3]...`).
- **Fix:** Setting `tie_word_embeddings: false` restores the correct learned projection weights, achieving the true 43.09 chrF baseline.

> **Presenter Notes:**  
> *"When benchmarking the mT5 baseline, we discovered an important technical detail: during fine-tuning, the LM head weights untie from the shared embedding layer. Forcibly tying them causes degenerative repetitive loops. Setting tie_word_embeddings to false in the config resolved this, allowing mT5 to generate clean translations."*

---

<!-- slide 9 -->
# Slide 9: Pipeline Breakdown: Stages 1, 2 & 3

### From Raw Chat Noise to Native Scripts

```
[ Raw: "NENU REPU college ki vastanuuuu plz" ]
                  │
                  ▼  Stage 1: Normalization
[ Normalized: "nenu repu college ki vastanu plz" ]
                  │
                  ▼  Stage 2: MuRIL Token LID
[ Tokens: nenu(TE), repu(TE), college(EN), ki(TE), vastanu(TE), plz(OTHER) ]
                  │
                  ▼  Stage 3: Transliteration Engine + Lexicon Check
[ Native Script: "నేను రేపు కాలేజ్ కి వస్తాను plz" ]
```

1. **Stage 1 (Phonetic Normalization):**
   - Collapses character elongations using regex: `r'([a-zA-Z])\1{2,}'` $\rightarrow$ `r'\1\1'`.
   - Converts all-caps chat slang into readable sentence casing.
2. **Stage 2 (Token-Level LID Gating):**
   - Tags each token with language and confidence. English and universal words remain in Latin script.
   - Calculates overall sentence language ratio: $\text{Ratio}_{\text{TE}} = \frac{N_{\text{TE}}}{N_{\text{HI}} + N_{\text{TE}}}$.
3. **Stage 3 (Phonetic Transliteration Engine):**
   - Hindi words $\rightarrow$ Devanagari Unicode ($U+0900$ to $U+097F$).
   - Telugu words $\rightarrow$ Telugu lipi ($U+0C00$ to $U+0C7F$) using `te_lexicon.csv` to resolve ambiguous vowels.

> **Presenter Notes:**  
> *"Stage 1 collapses repeated characters like 'vastanuuuu' to 'vastanu'. Stage 2 identifies token languages using MuRIL. In Stage 3, we transliterate Hindi words into Devanagari and Telugu words into Telugu script, while keeping English loan words intact in Latin script."*

---

<!-- slide 10 -->
# Slide 10: Pipeline Breakdown: Stages 4 & 5

### Clause Segmentation & IndicTrans2 Translation

```
Input: "Nenu repu college ki vastanu, tum bhi aao na"
                           │
                           ▼  Stage 4: Clause Boundary Detection
  Clause 1: "Nenu repu college ki vastanu"      Clause 2: "tum bhi aao na"
  • Matrix: Telugu                             • Matrix: Hindi
  • Translit: "నేను రేపు కాలేజ్ కి వస్తాను"      • Translit: "तुम भी आओ ना"
  • Tag: _tel_Telu_                            • Tag: _hin_Deva_
                           │
                           ▼  Stage 5: IndicTrans2 Independent Generation
  Hypothesis 1: "I will come to college tomorrow"   Hypothesis 2: "you also come"
                           │
                           ▼  Reassembly & Detokenization
Final Output: "I will come to college tomorrow, you also come"
```

- **Solving the Single-Tag Bottleneck:** IndicTrans2 requires an exact source tag prefix. In multi-lingual sentences, a single tag corrupts the non-matrix clause.
- **Stage 4 (Clause Segmentation):** Detects conjunctions (*but*, *aur*, *kani*) and punctuation, isolating language-consistent clauses.
- **Stage 5 (IndicTrans2 Neural MT):** AI4Bharat IndicTrans2 translates each native-script clause with its matching language tag (`_tel_Telu_` or `_hin_Deva_`).

> **Presenter Notes:**  
> *"Standard neural MT models can only take one language tag. If someone says 'Nenu college ki vastanu, tum bhi aao na', it has both Telugu and Hindi. If we give a Hindi tag, the Telugu part fails; if we give a Telugu tag, the Hindi part fails. Our clause segmenter splits them, translates each with its respective tag, and recombines them seamlessly."*

---

<!-- slide 11 -->
# Slide 11: NLP Formulation: Decoding & Evaluation Metrics

### Mathematical Formulations

1. **Beam Search Decoding with Length Normalization:**
   $$\text{Score}(\mathbf{y}) = \frac{1}{|\mathbf{y}|^\alpha} \sum_{t=1}^{|\mathbf{y}|} \log P(y_t \mid y_{<t}, X), \quad \alpha = 1.0, \; K = 4$$

2. **sacreBLEU (Corpus Word $n$-gram Precision):**
   $$\text{BLEU} = \text{BP} \cdot \exp\left( \sum_{n=1}^4 \frac{1}{4} \log p_n \right), \quad \text{BP} = \min\left(1, e^{1 - r/c}\right)$$
   *Signature:* `nrefs:1|case:mixed|eff:no|tok:13a|smooth:exp|version:2.6.0`

3. **chrF++ (Character $n$-gram F-score, $\beta=2$):**
   $$\text{chrF}2 = (1 + 2^2) \frac{\text{CHRP} \cdot \text{CHRR}}{2^2 \cdot \text{CHRP} + \text{CHRR}}$$
   - Measures character $n$-grams from $n=1$ to $6$.
   - $\beta=2$ weights recall higher than precision, penalizing missing root words and case markers.
   *Signature:* `nrefs:1|case:mixed|eff:yes|nc:6|nw:0|space:no|version:2.6.0`

> **Presenter Notes:**  
> *"For evaluation, we follow official WMT and sacreBLEU standards. We use BLEU for word precision and chrF++ for character n-gram overlap. In code-mixing, chrF is especially critical because it rewards correct subwords and roots even when spelling or morphology varies slightly."*

---

<!-- slide 12 -->
# Slide 12: Experimental Setup & Compute Environment

### Reproducible Experimental Parameters

```
Hardware & Runtime
├── Workstation CPU:    Intel Core i7 / AMD Ryzen (18 threads, 32 GB RAM)
├── Cloud Acceleration: Google Colab NVIDIA Tesla T4 GPU (16 GB VRAM)
├── Environments:       Python 3.11.9 (codemix311) & Python 3.14.3 (.venv)
└── Core Libraries:     PyTorch 2.11+, Transformers 4.46+, SacreBLEU 2.6.0
```

### Model Hyperparameter Specifications

| Hyperparameter | MuRIL Token LID | mT5 Baseline | IndicTrans2 Engine |
| :--- | :---: | :---: | :---: |
| **Parameters** | 237M | 300M | 418M / 1B |
| **Learning Rate** | $3 \times 10^{-5}$ | $1 \times 10^{-4}$ | Pretrained Frozen Backbone |
| **Optimizer** | AdamW | AdamW | — |
| **Batch Size** | 64 (eff) | 16 (eff) | Batch 32 (CPU Inference) |
| **Precision** | FP32 | FP32 / FP16 | FP32 (CPU) |
| **Search Strategy** | Softmax ArgMax | Beam Search ($K=4$) | Beam Search ($K=4$) |

> **Presenter Notes:**  
> *"All models were trained and verified under reproducible environments. The mT5 model was fine-tuned on an NVIDIA T4 GPU and evaluated on CPU in batches of 32. MuRIL was trained with AdamW using an effective batch size of 64."*

---

<!-- slide 13 -->
# Slide 13: Results 1: Token-Level Language Identification

### Test Set Performance (199,219 Tokens across 14,855 Sentences)

| Class Label | Precision | Recall | F1-Score | Evaluated Tokens | Class Percentage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **English (`EN`)** | 0.990 | 0.986 | **0.988** | 53,788 | 27.0% |
| **Hindi (`HI`)** | 0.968 | 0.978 | **0.973** | 98,412 | 49.4% |
| **Telugu (`TE`)** | 0.990 | 0.986 | **0.988** | 28,104 | 14.1% |
| **Other / Punctuation (`OTHER`)** | 0.971 | 0.969 | **0.970** | 18,915 | 9.5% |
| **Overall Macro Average** | **0.983** | **0.983** | **0.983** | **199,219** | **Overall Accuracy: 98.17%** |

### Key Observations
- Exceptional discriminative ability: **Macro-F1 of 0.983**.
- Cross-lingual confusion between Hindi and Telugu was less than **0.1%**.
- English loanwords embedded in Telugu/Hindi sentences were accurately isolated in **98.8%** of cases.

> **Presenter Notes:**  
> *"Sir, on our locked test set of nearly 200,000 tokens, the MuRIL LID model achieved a Macro-F1 of 0.983 and 98.17% overall accuracy. Telugu and English both reached 0.988 F1. Confusion between Hindi and Telugu was practically zero, showing that MuRIL strongly separates Indo-Aryan and Dravidian phonetic structures."*

---

<!-- slide 14 -->
# Slide 14: Results 2: Head-to-Head Translation on PHINC ($n=1,351$)

### Apples-to-Apples Benchmark on the SAME 1,351 Test Sentences

| System / Experimental Variant | chrF Score | BLEU Score | CPU Latency | Core Architectural Characteristics |
| :--- | :---: | :---: | :---: | :--- |
| **mT5 Baseline (earlier model)** | 43.09 | 24.19 | ~3297 ms/sent | Direct Seq2Seq translation on raw Hinglish |
| **Direct (`direct`, HI hint)** | 42.83 | 23.30 | 744 ms/sent | IndicTrans2 on raw Latin input with language hint |
| **LID Only (`lid_only`)** | 44.17 | 24.98 | 682 ms/sent | IndicTrans2 with LID-gated tag, no transliteration |
| **Full Pipeline (`full`)** | **53.17** | **31.21** | **568 ms/sent** | **Norm + MuRIL LID + Transliteration + IndicTrans2** |

```
PHINC 1,351 Test Evaluation (chrF Comparison)
─────────────────────────────────────────────────────────────────────────────
Full Pipeline:    ████████████████████████████████████ 53.17 chrF  (+9.74 gain)
LID Only:         ████████████████████ 44.17 chrF
mT5 Baseline:     ███████████████████ 43.09 chrF
Direct (HI hint): ██████████████████ 42.83 chrF
─────────────────────────────────────────────────────────────────────────────
```

- **Key Finding:** The Full Pipeline delivers a massive **+9.74 chrF** and **+7.02 BLEU** improvement over the fine-tuned mT5 baseline, while running **$5.8\times$ faster** per sentence on CPU.

> **Presenter Notes:**  
> *"This is the central finding of our work. On the exact same 1,351 test sentences, our Full Pipeline achieves 53.17 chrF and 31.21 BLEU. It beats the fine-tuned mT5 baseline by nearly 10 chrF points and 7 BLEU points, while also being significantly faster on CPU."*

---

<!-- slide 15 -->
# Slide 15: Statistical Significance: Paired Bootstrap Resampling

### Validating That Gains Are Not Due to Random Chance

- **Methodology:** Non-parametric Paired Bootstrap Resampling ($B=2,000$ iterations) on sentence-level chrF differences:
  $$\delta_i = \text{chrF}(\text{Full}_i, R_i) - \text{chrF}(\text{mT5}_i, R_i), \quad i \in \{1, \dots, 1351\}$$
- In each iteration $b \in \{1, \dots, 2000\}$, draw 1,351 sentences with replacement and compute mean difference $\bar{\delta}^{*b}$.

```
Bootstrap Distribution of Mean chrF Gain (Full Pipeline minus mT5 Baseline)
                             95% CI: [+8.92, +10.60]
                                     │
                             ╭───────┴───────╮
               ▲             │       ▲       │
             Frequency       │     +9.74     │
               │             │  (Empirical)  │
               │         ┌───┴───────────────┴───┐
               │       ┌─┤                       ├─┐
               │     ┌─┤ │                       │ ├─┐
               └─────┴─┴─┴───────────────────────┴─┴─┴────────► chrF Gain
                         +8.5       +9.74       +11.0
```

- **Results:**
  - Mean chrF Gain: **+9.74**
  - **95% Confidence Interval: $[+8.92, +10.60]$**
  - Empirical $p$-value: **$p < 0.0001$** (Zero resamples yielded $\delta \le 0$).

> **Presenter Notes:**  
> *"To prove statistical significance to academic standards, we performed 2,000 paired bootstrap resamples. The 95% confidence interval for the gain is strictly positive between +8.92 and +10.60 chrF, with a p-value less than 0.0001. This confirms our gains are statistically undeniable."*

---

<!-- slide 16 -->
# Slide 16: Ablation Studies & Empirical Negative Results

### 1. Transliteration Ablation (80-sentence Dev Set)
Transliterating Latin characters to native Indic scripts was ablated:
- **No Transliteration (`none`):** 28.71 chrF / 6.29 BLEU
- **Telugu Rules Only:** 44.84 chrF / 20.63 BLEU ($+16.13\text{ chrF}$)
- **Full Telugu + Hindi Rules:** **65.56 chrF / 40.13 BLEU** (**$+36.85\text{ chrF}$ net gain**)
- *Takeaway:* Native script transliteration is the single most critical step.

### 2. Clause Segmentation Ablation (Multi-Clause Mixed Set, $n=40$)
- **Sentence-Level Translation:** 56.10 chrF
- **Clause-Segmented Translation:** **64.40 chrF** (**$+8.30\text{ chrF}$ net gain**)
- *Takeaway:* Eliminates the single-language tag bottleneck for intra-sentential switches.

### 3. Documented Negative Results (What Did NOT Work)
- **Collapsing Punctuation (*???* $\rightarrow$ *?*):** $\Delta\text{chrF} = -0.06$ (no effect; stripped sentiment).
- **Entity Masking Wrapping (@mentions/URLs):** $\Delta\text{chrF} = +0.20$ (within statistical noise).
- **LID Gating Without Transliteration:** Only $+1.34\text{ chrF}$ gain (script mismatch still ruins MT).

> **Presenter Notes:**  
> *"Our ablation studies reveal two key insights: First, transliterating to native scripts accounts for an astounding +36.85 chrF boost. Second, clause segmentation gives an +8.30 chrF gain on multi-clause sentences. We also documented negative results—such as entity masking and punctuation collapsing—which added complexity without meaningful gains."*

---

<!-- slide 17 -->
# Slide 17: Qualitative Case Studies & Error Analysis

### Representative Test Set Outputs

#### Example 1: Interrogatives & Lexical Meaning (Hinglish)
- **Input:** `@DramebaazKudi cake kaha hai ??`
- **mT5 Baseline:** `@DramebaazKudi cake is a cake?` *(Fails on interrogative 'kaha')*
- **Full Pipeline:** **`@DramebaazKudi Where is the cake??`** *(Accurate interrogative resolution)*

#### Example 2: Colloquial Slang & Sentiment (Hinglish)
- **Input:** `kaun hai ye zaleel insaan?`
- **mT5 Baseline:** `what is this zaleel insaan?` *(Copies untranslated words)*
- **Full Pipeline:** **`Who is this disgraced person?`** *(Correct semantic translation)*

#### Example 3: Temporal Semantics (Hinglish)
- **Input:** `Kal meeting hai please slides bhej dena`
- **mT5 Baseline:** `it is a meeting please send slides.` *(Loses meaning of 'Kal')*
- **Full Pipeline:** **`There is a meeting tomorrow, please send the slides.`** *(Captures 'tomorrow')*

#### Example 4: Agglutinative Telugu + English (Tenglish)
- **Input:** `Meeru ee project deadline gurinchi manager tho matladara?`
- **mT5 Baseline:** *(Produces corrupted Hindi gibberish)*
- **Full Pipeline:** **`Did you speak with the manager about this project deadline?`** *(Resolves Telugu post-positions '-gurinchi' [about] and '-tho' [with])*

> **Presenter Notes:**  
> *"Looking at real examples: In sentence 1, mT5 says 'cake is a cake?' whereas our pipeline accurately says 'Where is the cake??'. In sentence 3, mT5 misses the word 'Kal' (tomorrow), while our pipeline captures it completely. In sentence 4, which is Telugu, mT5 fails completely, whereas our pipeline translates the complex post-positions perfectly."*

---

<!-- slide 18 -->
# Slide 18: System Implementation & Live Demo Architecture

### Software Engineering Highlights

```
┌──────────────────────────────────────┐       HTTP REST       ┌──────────────────────────────────────┐
│       FASTAPI BACKEND ENGINE         │ ◄───────────────────► │        VANILLA JS WEB UI             │
│ • GET  /health (Instant readiness)   │                       │ • Tab 1: Token LID Chip Visualizer   │
│ • POST /api/predict (MuRIL LID)      │                       │ • Tab 2: Earlier mT5 Baseline        │
│ • POST /api/mt/translate (Pipeline)  │                       │ • Tab 3: Pipeline MT + Strategy Diff │
│ • Daemon Background Warm-Up Thread   │                       │ • Tab 4: Live Experiments Dashboard  │
│ • Mutex Lock for Concurrency Safety  │                       │ • Offline Fallback: demo_cache.json  │
└──────────────────────────────────────┘                       └──────────────────────────────────────┘
```

1. **Non-Blocking Lifespan Warm-Up:**
   - IndicTrans2 model takes $\approx 10\text{ seconds}$ to load weights into RAM.
   - An asynchronous daemon thread warms up models on startup; the server responds to `/health` probes immediately without timing out.
2. **Thread-Safe Concurrency:**
   - Wrapped `model.generate()` blocks in `threading.Lock()` mutexes to guarantee race-free execution during concurrent multi-user requests.
3. **Interactive Frontend:**
   - Token chips color-coded by language with sub-labels for native script transliteration.
   - **"Compare strategies"** runs `direct`, `lid_only`, `full`, `clause`, and `mT5` sequentially with word-level difference highlighting and client-side approximate chrF.

> **Presenter Notes:**  
> *"For deployment, we built a production-ready FastAPI backend with background model warm-up so the server starts instantly. On the frontend, we built a 4-tab interface with interactive token chips, side-by-side strategy diffs, and an offline demo cache so the system works even without an active GPU."*

---

<!-- slide 19 -->
# Slide 19: Critical Limitations & Future Scope

### Acknowledged Constraints & Engineering Challenges

1. **Rule-Based Ambiguity on Rare Telugu Proper Nouns:**
   - While rule-based transliteration avoids neural hallucinations, rare proper nouns or ambiguous surnames can occasionally be mis-transliterated.
2. **Dataset Asymmetry:**
   - While Hindi-English has 13k PHINC pairs, public Telugu-English code-mixed datasets remain extremely limited, necessitating reliance on curated slices.
3. **CPU Generation Latency:**
   - While $5.8\times$ faster than mT5, IndicTrans2 CPU inference takes $\approx 568\text{ ms}$ per sentence due to deep 18-layer encoder-decoder cross-attention.

### Concrete Future Directions
1. **Neural Grapheme-to-Phoneme Transliteration:** Train a compact, distilled Seq2Seq transliteration model specifically for ambiguous Dravidian vowel lengths.
2. **Expansion to South Indian Languages:** Extend the trilingual pipeline to **Tamil (Tanglish)** and **Kannada (Kanglish)**.
3. **Multimodal Code-Mixed Speech Translation:** Couple Whisper-Indic acoustic encoders with the pipeline for direct speech-to-text translation of spoken code-mixed audio.

> **Presenter Notes:**  
> *"We also acknowledge practical limitations: rule-based transliteration can struggle with rare proper nouns, and parallel Telugu code-mixed data remains scarce. In the future, we plan to train lightweight neural transliterators for Dravidian vowels and expand the system to Tamil and Kannada."*

---

<!-- slide 20 -->
# Slide 20: Summary & Conclusion

### Summary of Major Contributions

1. **Trilingual Scope:** Successfully extended code-mixed NLP beyond bilingual Hinglish to include **Telugu (Tenglish)**, addressing Dravidian agglutination and severe data scarcity.
2. **High-Accuracy Token LID:** Fine-tuned MuRIL achieves **0.983 Macro-F1** (98.17% Accuracy) on 199,219 locked test tokens.
3. **Empirical Superiority Over Baseline:**
   - Full Pipeline achieves **53.17 chrF / 31.21 BLEU** on the 1,351 PHINC test set.
   - Outperforms fine-tuned `google/mt5-small` baseline by **+9.74 chrF / +7.02 BLEU** ($p < 0.0001$, 95% CI: $[+8.92, +10.60]$).
4. **Architectural Breakthroughs:** Native script transliteration yields **+36.85 chrF**; clause segmentation yields **+8.30 chrF** on multi-clause sentences.
5. **Full-Stack Deployment:** Live FastAPI backend and interactive 4-tab web application with offline resilience.

---

### Thank You!

**Supervisor:** Dr. Santha Babu | **Department of Computer Science and Engineering**  
**Indian Institute of Information Technology, Design and Manufacturing, Kurnool (IIITDM Kurnool)**  

*Open for Questions & Discussion.*

> **Presenter Notes:**  
> *"In conclusion, our project proves that a linguistically grounded hybrid pipeline vastly outperforms monolithic black-box models on code-mixed Indic text. Thank you very much, Dr. Santha Babu Sir. I am now open to your questions and feedback."*
