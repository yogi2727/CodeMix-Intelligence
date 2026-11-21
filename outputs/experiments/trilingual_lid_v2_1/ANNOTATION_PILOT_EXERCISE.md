# CodeMix Intelligence V2.1 — Annotation Pilot Calibration Exercise
## Eighteen Gold-Standard Reference Walkthroughs for Trilingual Code-Mixed Text

**Document Version:** `2.0.0`  
**Date:** 2026-11-13  
**Status:** Mandatory Annotator Calibration & Training Repository  
**Target Directory:** [`outputs/experiments/trilingual_lid_v2_1/`](file:///C:/Users/YOGESWAR/OneDrive/Apps/CodeMix-Intelligence/outputs/experiments/trilingual_lid_v2_1/)  

> [!IMPORTANT]
> **ILLUSTRATIVE GUIDELINE REFERENCE ONLY — NOT TRAINING OR TEST DATA:**  
> The 18 annotated sentences in this document are strictly designed as educational and calibrating reference examples for human annotators, reviewers, and adjudicators. Under no circumstances should these sentences be imported into model training corpora, validation splits, or benchmark test files.

---

## 1. Overview and Purpose of the Exercise

This document provides 18 diverse, gold-standard annotated examples spanning the full spectrum of linguistic difficulty in English-Hindi-Telugu code-mixed text. Each example provides:
- Verbatim sentence text and contextual classification.
- Token-by-token character offsets mathematically verified against the raw text string.
- Target language tag (`EN`, `HI`, `TE`, `OTHER`) or non-target loss mask (`AMBIGUOUS`, `NE`, `MIXED` $\rightarrow -100$).
- Writing system taxonomy (`latin_romanized`, `devanagari`, `telugu_script`, `numeric_symbol`).
- Syntactic and linguistic justification.
- Adjudication criteria explaining why alternative annotations are unacceptable.

---

## 2. The 18 Calibration Walkthroughs

### Example 001: Diagnosed Trilingual Turn with Romanized Hindi, English Nouns & Telugu Predicate
**Sentence ID:** `guide_ex_001`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Diagnosed contextual interference test case; validates Romanized Hindi recovery alongside Telugu predicate.  
**Sentence Text:** `"mai kal morning school ku aatta huu, akkada adukundam."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `mai` | `[0..3]` | **`HI`** | `1` | `latin_romanized` | Hindi 1st-person pronoun ('I') | Unambiguous Romanized Hindi pronoun. |
| 1 | `kal` | `[4..7]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb ('tomorrow') | Temporal adverb in Hindi matrix clause. |
| 2 | `morning` | `[8..15]` | **`EN`** | `0` | `latin_romanized` | English temporal noun | English lexical time noun. |
| 3 | `school` | `[16..22]` | **`EN`** | `0` | `latin_romanized` | English locational noun | English noun taking separate postposition. |
| 4 | `ku` | `[23..25]` | **`TE`** | `2` | `latin_romanized` | Telugu dative postposition ('to') | Telugu dative case marker governing destination. |
| 5 | `aatta` | `[26..31]` | **`HI`** | `1` | `latin_romanized` | Hindi habitual verb ('aata' = come) | Phonetic informal spelling of Hindi verb; tag as HI, not typo. |
| 6 | `huu` | `[32..35]` | **`HI`** | `1` | `latin_romanized` | Hindi 1st-person auxiliary ('hoon') | Phonetic informal spelling of Hindi auxiliary; tag as HI. |
| 7 | `,` | `[35..36]` | **`OTHER`** | `3` | `numeric_symbol` | Clause boundary comma | Punctuation separating coordinate clauses. |
| 8 | `akkada` | `[37..43]` | **`TE`** | `2` | `latin_romanized` | Telugu distal locative adverb ('there') | Telugu spatial adverb opening coordinate clause. |
| 9 | `adukundam` | `[44..53]` | **`TE`** | `2` | `latin_romanized` | Telugu cohortative verb ('let us play') | Telugu 1st-person plural hortative verb. |
| 10 | `.` | `[53..54]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal full stop | Sentence boundary delimiter. |

---

### Example 002: Continuous Unpunctuated Trilingual Turn
**Sentence ID:** `guide_ex_002`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Unpunctuated  
**Linguistic Focus:** Boundary detection in informal chat lacking punctuation cues; validates model behavior on continuous streaming input.  
**Sentence Text:** `"mai kal morning school ku aatta huu akkada adukundam"`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `mai` | `[0..3]` | **`HI`** | `1` | `latin_romanized` | Hindi 1st-person pronoun | Hindi pronoun initiates sentence. |
| 1 | `kal` | `[4..7]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb | Temporal adverb modifying Hindi clause. |
| 2 | `morning` | `[8..15]` | **`EN`** | `0` | `latin_romanized` | English time noun | English lexical insertion. |
| 3 | `school` | `[16..22]` | **`EN`** | `0` | `latin_romanized` | English location noun | English head noun. |
| 4 | `ku` | `[23..25]` | **`TE`** | `2` | `latin_romanized` | Telugu dative marker | Telugu postposition governing destination. |
| 5 | `aatta` | `[26..31]` | **`HI`** | `1` | `latin_romanized` | Hindi verb form | Informal spelling of Hindi 'aata'. |
| 6 | `huu` | `[32..35]` | **`HI`** | `1` | `latin_romanized` | Hindi auxiliary | Informal spelling of Hindi 'hu/hoon'. |
| 7 | `akkada` | `[36..42]` | **`TE`** | `2` | `latin_romanized` | Telugu locative adverb | Unpunctuated clause boundary switch to Telugu. |
| 8 | `adukundam` | `[43..52]` | **`TE`** | `2` | `latin_romanized` | Telugu cohortative verb | Telugu cohortative verb completes predicate. |

---

### Example 003: Trilingual Professional Chat with Telugu Locative and Adverbial Clitics
**Sentence ID:** `guide_ex_003`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Whitespace-separated clitics ('lo', 'ga') modifying English nouns/adverbs.  
**Sentence Text:** `"aaj office lo bahut work undi, so late ga vasthanu."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `aaj` | `[0..3]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb ('today') | Hindi adverb opening clause. |
| 1 | `office` | `[4..10]` | **`EN`** | `0` | `latin_romanized` | English noun ('office') | English workplace noun. |
| 2 | `lo` | `[11..13]` | **`TE`** | `2` | `latin_romanized` | Telugu locative postposition ('in') | Postposition modifying English 'office'. |
| 3 | `bahut` | `[14..19]` | **`HI`** | `1` | `latin_romanized` | Hindi quantifier ('a lot') | Hindi intensifier modifying 'work'. |
| 4 | `work` | `[20..24]` | **`EN`** | `0` | `latin_romanized` | English noun ('work') | English lexical noun. |
| 5 | `undi` | `[25..29]` | **`TE`** | `2` | `latin_romanized` | Telugu existential verb ('there is') | Telugu 3rd-person neuter existential copula. |
| 6 | `,` | `[29..30]` | **`OTHER`** | `3` | `numeric_symbol` | Clause separating comma | Standard clause break. |
| 7 | `so` | `[31..33]` | **`EN`** | `0` | `latin_romanized` | English conjunction ('so') | English discourse connective. |
| 8 | `late` | `[34..38]` | **`EN`** | `0` | `latin_romanized` | English adjective/adverb ('late') | English time descriptor. |
| 9 | `ga` | `[39..41]` | **`TE`** | `2` | `latin_romanized` | Telugu adverbial suffix ('-ly') | Telugu particle converting 'late' into adverbial predicate. |
| 10 | `vasthanu` | `[42..50]` | **`TE`** | `2` | `latin_romanized` | Telugu 1st-person future verb ('will come') | Telugu inflected finite verb. |
| 11 | `.` | `[50..51]` | **`OTHER`** | `3` | `numeric_symbol` | Sentence terminating period | Punctuation mark. |

---

### Example 004: Named Entity and Shared Sanskrit Cognate in Conversational Frame
**Sentence ID:** `guide_ex_004`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Named entity masking ('Hyderabad' -> NE), Sanskrit cognate disambiguation ('samay' -> HI via demonstrative 'ye').  
**Sentence Text:** `"Hyderabad lo ye samay traffic chaala ekkuva untadi bhaiyya."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `Hyderabad` | `[0..9]` | **`NE`** | `-100` | `latin_romanized` | Proper geographic noun (City) | Geographic entity; must be labeled NE (-100), never EN or HI. |
| 1 | `lo` | `[10..12]` | **`TE`** | `2` | `latin_romanized` | Telugu locative postposition ('in') | Locative marker governing city entity. |
| 2 | `ye` | `[13..15]` | **`HI`** | `1` | `latin_romanized` | Hindi proximal demonstrative pronoun ('this') | Hindi determiner governing 'samay'. |
| 3 | `samay` | `[16..21]` | **`HI`** | `1` | `latin_romanized` | Hindi noun ('time', Sanskrit cognate) | Governed by Hindi determiner 'ye'; tag as HI. In isolation would be AMBIGUOUS. |
| 4 | `traffic` | `[22..29]` | **`EN`** | `0` | `latin_romanized` | English noun ('traffic') | English transportation noun. |
| 5 | `chaala` | `[30..36]` | **`TE`** | `2` | `latin_romanized` | Telugu intensifier ('very / much') | Telugu degree adverb. |
| 6 | `ekkuva` | `[37..43]` | **`TE`** | `2` | `latin_romanized` | Telugu adjective ('high / heavy') | Telugu quantifier adjective. |
| 7 | `untadi` | `[44..50]` | **`TE`** | `2` | `latin_romanized` | Telugu habitual verb ('remains / is') | Telugu 3rd-person habitual copula. |
| 8 | `bhaiyya` | `[51..58]` | **`HI`** | `1` | `latin_romanized` | Hindi kinship/honorific address ('brother') | Colloquial vocative marker widely borrowed; tag as HI. |
| 9 | `.` | `[58..59]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal punctuation | Standard full stop. |

---

### Example 005: Code-Switching Across Conjunction with Verb Phrases
**Sentence ID:** `guide_ex_005`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** English verbal compound ('call chesanu', 'switch off aindi') in trilingual coordinate structure.  
**Sentence Text:** `"nenu kal subah call chesanu, but phone switch off aindi."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `nenu` | `[0..4]` | **`TE`** | `2` | `latin_romanized` | Telugu 1st-person pronoun ('I') | Telugu subject pronoun. |
| 1 | `kal` | `[5..8]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb ('yesterday') | Hindi adverbial modifier. |
| 2 | `subah` | `[9..14]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal noun ('morning') | Hindi temporal modifier forming 'kal subah'. |
| 3 | `call` | `[15..19]` | **`EN`** | `0` | `latin_romanized` | English noun/verb stem ('call') | English loanword functioning as light verb head. |
| 4 | `chesanu` | `[20..27]` | **`TE`** | `2` | `latin_romanized` | Telugu past verb ('did / made') | Telugu auxiliary forming compound verb 'call chesanu'. |
| 5 | `,` | `[27..28]` | **`OTHER`** | `3` | `numeric_symbol` | Clause separating comma | Boundary marker. |
| 6 | `but` | `[29..32]` | **`EN`** | `0` | `latin_romanized` | English adversative conjunction ('but') | English coordinate connector. |
| 7 | `phone` | `[33..38]` | **`EN`** | `0` | `latin_romanized` | English device noun ('phone') | English technology noun. |
| 8 | `switch` | `[39..45]` | **`EN`** | `0` | `latin_romanized` | English particle verb component | English phrasal verb component. |
| 9 | `off` | `[46..49]` | **`EN`** | `0` | `latin_romanized` | English preposition/particle | English phrasal verb component. |
| 10 | `aindi` | `[50..55]` | **`TE`** | `2` | `latin_romanized` | Telugu 3rd-person neuter past verb ('became') | Telugu light verb completing compound. |
| 11 | `.` | `[55..56]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 006: Syntactically Governed Sanskrit Cognate in Hindi Possessive Frame
**Sentence ID:** `guide_ex_006`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Syntactic frame resolution: Sanskrit cognate 'pustak' governed by Hindi feminine possessive 'meri'.  
**Sentence Text:** `"meri pustak akkada undi, please teeskoni raa."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `meri` | `[0..4]` | **`HI`** | `1` | `latin_romanized` | Hindi 1st-person feminine possessive ('my') | Unambiguous Hindi possessive determiner. |
| 1 | `pustak` | `[5..11]` | **`HI`** | `1` | `latin_romanized` | Sanskrit cognate noun ('book') | Governed by Hindi possessive 'meri'; must be tagged HI, not AMBIGUOUS. |
| 2 | `akkada` | `[12..18]` | **`TE`** | `2` | `latin_romanized` | Telugu locative adverb ('there') | Telugu distal adverb. |
| 3 | `undi` | `[19..23]` | **`TE`** | `2` | `latin_romanized` | Telugu existential verb ('is') | Telugu copula. |
| 4 | `,` | `[23..24]` | **`OTHER`** | `3` | `numeric_symbol` | Clause separating comma | Punctuation. |
| 5 | `please` | `[25..31]` | **`EN`** | `0` | `latin_romanized` | English politeness marker ('please') | English conversational particle. |
| 6 | `teeskoni` | `[32..40]` | **`TE`** | `2` | `latin_romanized` | Telugu non-finite participle ('taking') | Telugu converb ('teeskoni'). |
| 7 | `raa` | `[41..44]` | **`TE`** | `2` | `latin_romanized` | Telugu imperative verb ('come') | Telugu imperative. |
| 8 | `.` | `[44..45]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 007: Syntactically Governed Cognate with Telugu Nominal Suffix
**Sentence ID:** `guide_ex_007`  
**Category:** HI-TE Bilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Direct Hindi-Telugu code-mixing (0 English); cognate carries Telugu morphological marker '-am'.  
**Sentence Text:** `"ee pustakam bahut purani hai, chala bagundi."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `ee` | `[0..2]` | **`TE`** | `2` | `latin_romanized` | Telugu proximal demonstrative ('this') | Telugu determiner. |
| 1 | `pustakam` | `[3..11]` | **`TE`** | `2` | `latin_romanized` | Telugu nominalized Sanskrit cognate ('book') | Telugu nominal suffix '-am' makes this unambiguously TE. |
| 2 | `bahut` | `[12..17]` | **`HI`** | `1` | `latin_romanized` | Hindi degree adverb ('very') | Hindi quantifier. |
| 3 | `purani` | `[18..24]` | **`HI`** | `1` | `latin_romanized` | Hindi feminine adjective ('old') | Hindi inflected adjective. |
| 4 | `hai` | `[25..28]` | **`HI`** | `1` | `latin_romanized` | Hindi present copula ('is') | Hindi finite auxiliary. |
| 5 | `,` | `[28..29]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation. |
| 6 | `chala` | `[30..35]` | **`TE`** | `2` | `latin_romanized` | Telugu intensifier ('very') | Telugu degree modifier. |
| 7 | `bagundi` | `[36..43]` | **`TE`** | `2` | `latin_romanized` | Telugu evaluative predicate ('is good') | Telugu inflected stative verb. |
| 8 | `.` | `[43..44]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 008: Trilingual Mixed-Script Turn with Devanagari, Latin & Telugu Script
**Sentence ID:** `guide_ex_008`  
**Category:** EN-HI-TE Trilingual | Mixed Scripts (Devanagari + Latin + Telugu) | Punctuated  
**Linguistic Focus:** Multi-script tokenization; validates that script does not override language taxonomy.  
**Sentence Text:** `"मैं kal office ki వచ్చాను, meeting cancelled aindi."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `मैं` | `[0..3]` | **`HI`** | `1` | `devanagari` | Hindi 1st-person pronoun in Devanagari script | Script is devanagari; language label is HI. |
| 1 | `kal` | `[4..7]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb in Latin script | Script is latin_romanized; language is HI. |
| 2 | `office` | `[8..14]` | **`EN`** | `0` | `latin_romanized` | English workplace noun | English noun. |
| 3 | `ki` | `[15..17]` | **`TE`** | `2` | `latin_romanized` | Telugu dative postposition ('to') | Telugu dative case marker. |
| 4 | `వచ్చాను` | `[18..25]` | **`TE`** | `2` | `telugu_script` | Telugu 1st-person past verb in Telugu script | Script is telugu_script; language label is TE. |
| 5 | `,` | `[25..26]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation. |
| 6 | `meeting` | `[27..34]` | **`EN`** | `0` | `latin_romanized` | English business noun | English noun. |
| 7 | `cancelled` | `[35..44]` | **`EN`** | `0` | `latin_romanized` | English past participle adjective | English predicate adjective. |
| 8 | `aindi` | `[45..50]` | **`TE`** | `2` | `latin_romanized` | Telugu 3rd-person past verb | Telugu auxiliary. |
| 9 | `.` | `[50..51]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 009: Mixed-Script Imperative with Native Devanagari & Telugu Script
**Sentence ID:** `guide_ex_009`  
**Category:** EN-HI-TE Trilingual | Mixed Scripts (Devanagari + Telugu + Latin) | Punctuated  
**Linguistic Focus:** Trilingual imperative mixing Devanagari Hindi, Telugu script verb, and English frame.  
**Sentence Text:** `"कल morning meeting ki రావాలి, do not forget."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `कल` | `[0..2]` | **`HI`** | `1` | `devanagari` | Hindi temporal adverb in Devanagari script | Script: devanagari, Language: HI. |
| 1 | `morning` | `[3..10]` | **`EN`** | `0` | `latin_romanized` | English temporal noun | English noun. |
| 2 | `meeting` | `[11..18]` | **`EN`** | `0` | `latin_romanized` | English business noun | English noun. |
| 3 | `ki` | `[19..21]` | **`TE`** | `2` | `latin_romanized` | Telugu dative marker ('to / for') | Telugu postposition. |
| 4 | `రావాలి` | `[22..28]` | **`TE`** | `2` | `telugu_script` | Telugu obligative modal verb in Telugu script ('must come') | Script: telugu_script, Language: TE. |
| 5 | `,` | `[28..29]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation. |
| 6 | `do` | `[30..32]` | **`EN`** | `0` | `latin_romanized` | English auxiliary verb | English auxiliary. |
| 7 | `not` | `[33..36]` | **`EN`** | `0` | `latin_romanized` | English negative particle | English negator. |
| 8 | `forget` | `[37..43]` | **`EN`** | `0` | `latin_romanized` | English infinitive verb | English verb. |
| 9 | `.` | `[43..44]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 010: Fused Intra-Word Compound Morphology and Named Entity
**Sentence ID:** `guide_ex_010`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Fused compound token ('officeku' -> MIXED / -100) and commercial entity ('Google' -> NE / -100).  
**Sentence Text:** `"Google officeku velli form submit cheyali."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `Google` | `[0..6]` | **`NE`** | `-100` | `latin_romanized` | Proper commercial brand noun | Named entity; label as NE (-100). Never force to EN. |
| 1 | `officeku` | `[7..15]` | **`MIXED`** | `-100` | `latin_romanized` | Fused English noun ('office') + Telugu clitic ('ku') | Single token combines EN stem with TE case marker; label as MIXED (-100). |
| 2 | `velli` | `[16..21]` | **`TE`** | `2` | `latin_romanized` | Telugu non-finite converb ('having gone') | Telugu participial verb. |
| 3 | `form` | `[22..26]` | **`EN`** | `0` | `latin_romanized` | English document noun | English noun. |
| 4 | `submit` | `[27..33]` | **`EN`** | `0` | `latin_romanized` | English verb stem | English action verb. |
| 5 | `cheyali` | `[34..41]` | **`TE`** | `2` | `latin_romanized` | Telugu obligative modal verb ('must do') | Telugu modal auxiliary completing verbal complex. |
| 6 | `.` | `[41..42]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 011: Hyphenated Clitic Boundary Disambiguation
**Sentence ID:** `guide_ex_011`  
**Category:** EN-TE Bilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Hyphenated tokenization separates English noun and Telugu clitic into distinct tokens.  
**Sentence Text:** `"meeting-lo tickets discuss chesara?"`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `meeting` | `[0..7]` | **`EN`** | `0` | `latin_romanized` | English noun ('meeting') | Punctuation hyphen allows clean separation of EN stem. |
| 1 | `-` | `[7..8]` | **`OTHER`** | `3` | `numeric_symbol` | Hyphen delimiter | Punctuation symbol. |
| 2 | `lo` | `[8..10]` | **`TE`** | `2` | `latin_romanized` | Telugu locative postposition ('in') | Telugu postposition cleanly separated; tagged TE. |
| 3 | `tickets` | `[11..18]` | **`EN`** | `0` | `latin_romanized` | English plural noun ('tickets') | English plural noun. |
| 4 | `discuss` | `[19..26]` | **`EN`** | `0` | `latin_romanized` | English verb ('discuss') | English verb. |
| 5 | `chesara` | `[27..34]` | **`TE`** | `2` | `latin_romanized` | Telugu honorific past interrogative verb ('did you do?') | Telugu interrogative finite verb. |
| 6 | `?` | `[34..35]` | **`OTHER`** | `3` | `numeric_symbol` | Question mark | Interrogative terminal punctuation. |

---

### Example 012: Phonetic Character Elongation and Discourse Particles
**Sentence ID:** `guide_ex_012`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Emotional character lengthening ('chaalaaa') and Hindi modal particle ('na').  
**Sentence Text:** `"chaalaaa urgent meeting undi, kal aana na please!"`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `chaalaaa` | `[0..8]` | **`TE`** | `2` | `latin_romanized` | Telugu intensifier with character elongation ('very') | Phonetic lengthening of Telugu 'chala'; tag as TE. |
| 1 | `urgent` | `[9..15]` | **`EN`** | `0` | `latin_romanized` | English adjective ('urgent') | English modifier. |
| 2 | `meeting` | `[16..23]` | **`EN`** | `0` | `latin_romanized` | English noun ('meeting') | English noun. |
| 3 | `undi` | `[24..28]` | **`TE`** | `2` | `latin_romanized` | Telugu existential verb ('there is') | Telugu stative copula. |
| 4 | `,` | `[28..29]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation. |
| 5 | `kal` | `[30..33]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb ('tomorrow') | Hindi temporal adverb. |
| 6 | `aana` | `[34..38]` | **`HI`** | `1` | `latin_romanized` | Hindi infinitive / imperative verb ('to come') | Hindi verb. |
| 7 | `na` | `[39..41]` | **`HI`** | `1` | `latin_romanized` | Hindi modal request particle ('please/right?') | Hindi polite urging particle; tag as HI. |
| 8 | `please` | `[42..48]` | **`EN`** | `0` | `latin_romanized` | English politeness marker ('please') | English conversational particle. |
| 9 | `!` | `[48..49]` | **`OTHER`** | `3` | `numeric_symbol` | Exclamation mark | Terminal expressive punctuation. |

---

### Example 013: Direct Hindi-Telugu Bilingual Switch Without English Matrix Scaffolding
**Sentence ID:** `guide_ex_013`  
**Category:** HI-TE Bilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Pure bilingual Hindi-Telugu code-mixing (0 English tokens). Tests cross-lingual boundary resilience.  
**Sentence Text:** `"bhot thand hai aaj, bayataki vellaku."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `bhot` | `[0..4]` | **`HI`** | `1` | `latin_romanized` | Hindi colloquial quantifier ('very', variant of 'bahut') | Hindi colloquial degree adverb. |
| 1 | `thand` | `[5..10]` | **`HI`** | `1` | `latin_romanized` | Hindi noun ('cold') | Hindi weather noun. |
| 2 | `hai` | `[11..14]` | **`HI`** | `1` | `latin_romanized` | Hindi copula ('is') | Hindi present copula. |
| 3 | `aaj` | `[15..18]` | **`HI`** | `1` | `latin_romanized` | Hindi temporal adverb ('today') | Hindi adverb completing first clause. |
| 4 | `,` | `[18..19]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation delimiter. |
| 5 | `bayataki` | `[20..28]` | **`TE`** | `2` | `latin_romanized` | Telugu dative locative noun ('outside-to') | Telugu noun inflected with dative case '-ki'. |
| 6 | `vellaku` | `[29..36]` | **`TE`** | `2` | `latin_romanized` | Telugu negative imperative verb ('do not go') | Telugu prohibitive verb form. |
| 7 | `.` | `[36..37]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 014: Multi-Switch Alternation with Imperative and Demonstrative
**Sentence ID:** `guide_ex_014`  
**Category:** EN-HI-TE Trilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Alternating switch pattern: TE -> HI -> TE -> EN -> TE.  
**Sentence Text:** `"akkada mat jao, chala dangerous place adi."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `akkada` | `[0..6]` | **`TE`** | `2` | `latin_romanized` | Telugu distal adverb ('there') | Telugu spatial adverb. |
| 1 | `mat` | `[7..10]` | **`HI`** | `1` | `latin_romanized` | Hindi negative prohibitive particle ('do not') | Hindi prohibitive particle. |
| 2 | `jao` | `[11..14]` | **`HI`** | `1` | `latin_romanized` | Hindi imperative verb ('go') | Hindi action verb. |
| 3 | `,` | `[14..15]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation. |
| 4 | `chala` | `[16..21]` | **`TE`** | `2` | `latin_romanized` | Telugu intensifier ('very') | Telugu degree adverb. |
| 5 | `dangerous` | `[22..31]` | **`EN`** | `0` | `latin_romanized` | English adjective ('dangerous') | English descriptive adjective. |
| 6 | `place` | `[32..37]` | **`EN`** | `0` | `latin_romanized` | English noun ('place') | English predicate noun. |
| 7 | `adi` | `[38..41]` | **`TE`** | `2` | `latin_romanized` | Telugu distal demonstrative pronoun ('that') | Telugu demonstrative pronoun completing clause. |
| 8 | `.` | `[41..42]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 015: Unresolved Ambiguous Sanskrit Cognates at Syntactic Switch Junction
**Sentence ID:** `guide_ex_015`  
**Category:** HI-TE Bilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Ambiguous shared lexemes ('samay', 'pustak') at an unnatural switch boundary; demonstrates proper use of AMBIGUOUS (-100).  
**Sentence Text:** `"ye samay pustak chaduvutunnam."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `ye` | `[0..2]` | **`HI`** | `1` | `latin_romanized` | Hindi proximal demonstrative ('this') | Hindi demonstrative determiner. |
| 1 | `samay` | `[3..8]` | **`AMBIGUOUS`** | `-100` | `latin_romanized` | Shared Sanskrit cognate ('time') | Positioned between Hindi demonstrative and direct Telugu verb; adjudicator marks AMBIGUOUS (-100). |
| 2 | `pustak` | `[9..15]` | **`AMBIGUOUS`** | `-100` | `latin_romanized` | Shared Sanskrit cognate ('book') | Uninflected cognate lacking clear case marking before Telugu verb; adjudicator marks AMBIGUOUS (-100). |
| 3 | `chaduvutunnam` | `[16..29]` | **`TE`** | `2` | `latin_romanized` | Telugu 1st-person plural continuous verb ('we are reading') | Telugu inflected finite verb. |
| 4 | `.` | `[29..30]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation. |

---

### Example 016: English Loanword with Telugu Plural Clitic and Telugu Script Conjunction
**Sentence ID:** `guide_ex_016`  
**Category:** EN-HI-TE Trilingual | Mixed Scripts (Latin + Telugu) | Punctuated  
**Linguistic Focus:** English noun taking separate Telugu plural clitic ('ticket lu') and Telugu script disjunction ('లేక').  
**Sentence Text:** `"bhaiyya ticket lu teeskunnara లేక cancel aindha?"`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `bhaiyya` | `[0..7]` | **`HI`** | `1` | `latin_romanized` | Hindi honorific vocative address ('brother') | Colloquial address term; labeled HI. |
| 1 | `ticket` | `[8..14]` | **`EN`** | `0` | `latin_romanized` | English travel noun ('ticket') | English root noun; retains EN label. |
| 2 | `lu` | `[15..17]` | **`TE`** | `2` | `latin_romanized` | Telugu plural nominal suffix | Telugu plural marker in separate token; labeled TE. |
| 3 | `teeskunnara` | `[18..29]` | **`TE`** | `2` | `latin_romanized` | Telugu 2nd-person honorific past verb ('did you take?') | Telugu inflected interrogative verb. |
| 4 | `లేక` | `[30..33]` | **`TE`** | `2` | `telugu_script` | Telugu disjunctive conjunction in Telugu script ('or') | Script: telugu_script, Language: TE. |
| 5 | `cancel` | `[34..40]` | **`EN`** | `0` | `latin_romanized` | English verb stem ('cancel') | English verbal head in light-verb construction. |
| 6 | `aindha` | `[41..47]` | **`TE`** | `2` | `latin_romanized` | Telugu past interrogative auxiliary ('did it become?') | Telugu interrogative auxiliary. |
| 7 | `?` | `[47..48]` | **`OTHER`** | `3` | `numeric_symbol` | Question mark | Interrogative terminal delimiter. |

---

### Example 017: Digital Chat Slang, Transliteration Noise & English Verb Borrowing
**Sentence ID:** `guide_ex_017`  
**Category:** EN-TE Bilingual | Romanized Latin | Punctuated  
**Linguistic Focus:** Transliteration noise ('plzzz') and English root in light verb construction ('wait chestunna').  
**Sentence Text:** `"plzzz reply fast, nenu wait chestunna!"`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `plzzz` | `[0..5]` | **`EN`** | `0` | `latin_romanized` | English colloquial abbreviation with noise ('please') | Phonetic elongation of 'please'; labeled EN. |
| 1 | `reply` | `[6..11]` | **`EN`** | `0` | `latin_romanized` | English imperative verb ('reply') | English verb. |
| 2 | `fast` | `[12..16]` | **`EN`** | `0` | `latin_romanized` | English adverb ('fast') | English manner adverb. |
| 3 | `,` | `[16..17]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation delimiter. |
| 4 | `nenu` | `[18..22]` | **`TE`** | `2` | `latin_romanized` | Telugu 1st-person pronoun ('I') | Telugu subject pronoun. |
| 5 | `wait` | `[23..27]` | **`EN`** | `0` | `latin_romanized` | English verb stem ('wait') | English verbal root in light-verb complex. |
| 6 | `chestunna` | `[28..37]` | **`TE`** | `2` | `latin_romanized` | Telugu 1st-person continuous auxiliary ('am doing') | Telugu inflected auxiliary verb. |
| 7 | `!` | `[37..38]` | **`OTHER`** | `3` | `numeric_symbol` | Exclamation mark | Terminal punctuation. |

---

### Example 018: Pure Native Scripts Bilingual Hindi-Telugu Turn
**Sentence ID:** `guide_ex_018`  
**Category:** HI-TE Bilingual | Native Scripts (Devanagari + Telugu) | Punctuated  
**Linguistic Focus:** Direct code-switching using pure native orthographies (Devanagari Hindi and Telugu script Telugu).  
**Sentence Text:** `"कल घर आ जाना, అక్కడ అందరం కలుద్దాం."`

| Token Index | Token | Offsets | Label | Model ID | Script | Linguistic Justification | Adjudication Resolution Criteria |
| :-: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| 0 | `कल` | `[0..2]` | **`HI`** | `1` | `devanagari` | Hindi temporal adverb in Devanagari script ('tomorrow') | Script: devanagari, Language: HI. |
| 1 | `घर` | `[3..5]` | **`HI`** | `1` | `devanagari` | Hindi location noun in Devanagari script ('home') | Script: devanagari, Language: HI. |
| 2 | `आ` | `[6..7]` | **`HI`** | `1` | `devanagari` | Hindi imperative root in Devanagari script ('come') | Script: devanagari, Language: HI. |
| 3 | `जाना` | `[8..12]` | **`HI`** | `1` | `devanagari` | Hindi compound verb auxiliary in Devanagari script | Script: devanagari, Language: HI. |
| 4 | `,` | `[12..13]` | **`OTHER`** | `3` | `numeric_symbol` | Clause comma | Punctuation delimiter. |
| 5 | `అక్కడ` | `[14..19]` | **`TE`** | `2` | `telugu_script` | Telugu distal adverb in Telugu script ('there') | Script: telugu_script, Language: TE. |
| 6 | `అందరం` | `[20..25]` | **`TE`** | `2` | `telugu_script` | Telugu collective pronoun in Telugu script ('all of us') | Script: telugu_script, Language: TE. |
| 7 | `కలుద్దాం` | `[26..34]` | **`TE`** | `2` | `telugu_script` | Telugu 1st-person cohortative verb in Telugu script ('let us meet') | Script: telugu_script, Language: TE. |
| 8 | `.` | `[34..35]` | **`OTHER`** | `3` | `numeric_symbol` | Terminal period | Punctuation delimiter. |

---
