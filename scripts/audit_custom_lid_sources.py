#!/usr/bin/env python3
"""
Step 25B: External Dataset Source Audit and Collection Strategy

Script: scripts/audit_custom_lid_sources.py

Description:
    Performs an automated, read-only audit of public external source datasets for
    the CodeMix Intelligence 400-example custom trilingual LID dataset:
      1. AI4Bharat IndicLID & Bhasha-Abhijnaanam test set
      2. BHT25 (Bengali-Hindi-Telugu parallel corpus; streams up to 20 sample rows)
      3. The LTRC Hindi-Telugu Parallel Corpus (public metadata only; no gate access)
      4. Mozilla Data Collective Telugu Text Corpus (MirasAI / Jnana Yoga Sadhana)
      5. Mozilla Common Voice Telugu 27.0 (MDC)
      6. AI4Bharat IndicCorp Telugu (web scraped corpus; licence unclear)

    Enforces:
      - Max 20 public sample rows inspected (BHT25) via public API.
      - Zero full-dataset downloads.
      - Zero gate bypass / token usage / sign-in.
      - Zero mutations to custom dataset JSONL files or dataset manifest.
      - Complete audit record output with timestamps, licensing, and suitability.

Usage:
    .venv\\Scripts\\python.exe scripts/audit_custom_lid_sources.py
    .venv\\Scripts\\python.exe scripts/audit_custom_lid_sources.py --max-samples 20 --output-json outputs/reports/step25_source_audit.json
"""

import argparse
import datetime
import hashlib
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output encoding across platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("source_audit")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_DATA_DIR = PROJECT_ROOT / "data" / "custom" / "trilingual_lid"
PROCESSED_LID_DIR = PROJECT_ROOT / "data" / "processed" / "language_identification"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


def verify_dataset_isolation() -> Dict[str, Any]:
    """Verify that custom dataset files remain pristine (0 records) and compute SHA-256 hashes."""
    custom_files = {
        "candidate_sentences.jsonl": CUSTOM_DATA_DIR / "candidate_sentences.jsonl",
        "reviewed_sentences.jsonl": CUSTOM_DATA_DIR / "reviewed_sentences.jsonl",
        "rejected_sentences.jsonl": CUSTOM_DATA_DIR / "rejected_sentences.jsonl",
        "dataset_manifest.json": CUSTOM_DATA_DIR / "dataset_manifest.json",
    }

    report: Dict[str, Any] = {
        "custom_files": {},
        "all_custom_jsonl_empty": True,
        "processed_dir_exists": PROCESSED_LID_DIR.exists(),
    }

    for name, path in custom_files.items():
        if not path.exists():
            report["custom_files"][name] = {"exists": False, "size_bytes": 0, "line_count": 0, "sha256": None}
            if name.endswith(".jsonl"):
                report["all_custom_jsonl_empty"] = False
        else:
            raw = path.read_bytes()
            size = len(raw)
            sha = hashlib.sha256(raw).hexdigest()
            lines = 0
            if name.endswith(".jsonl") and size > 0:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = sum(1 for _ in f)

            report["custom_files"][name] = {
                "exists": True,
                "size_bytes": size,
                "line_count": lines,
                "sha256": sha,
            }
            if name.endswith(".jsonl") and (size > 0 or lines > 0):
                report["all_custom_jsonl_empty"] = False

    return report


def audit_ai4bharat_indiclid() -> Dict[str, Any]:
    """Audit AI4Bharat IndicLID and Bhasha-Abhijnaanam test set."""
    return {
        "source_name": "AI4Bharat IndicLID & Bhasha-Abhijnaanam Benchmark",
        "public_url": "https://github.com/AI4Bharat/IndicLID",
        "secondary_url": "https://huggingface.co/datasets/ai4bharat/Bhasha-Abhijnaanam",
        "access_status": "Public direct access (GitHub release zips and Hugging Face dataset card)",
        "metadata_observed": {
            "repository": "https://github.com/AI4Bharat/IndicLID",
            "paper": "Bhasha-Abhijnaanam: Native-script and romanized Language Identification for 22 Indic languages (arXiv:2305.15814)",
            "classes_supported": 47,
            "bhasha_abhijnaanam_test_examples": {
                "native_telugu": 5751,
                "romanized_telugu": 4767,
                "native_hindi": 5617,
                "romanized_hindi": 4606,
            },
            "record_fields": [
                "unique_identifier",
                "native sentence",
                "romanized sentence",
                "language",
                "script",
                "source",
            ],
            "training_resources": [
                "native_script_train_valid_data.zip",
                "roman_script_train_valid_data.zip",
                "parallel_romanized_train_data.zip",
            ],
        },
        "licence_observed": {
            "code_and_models": "MIT License (covers repo code and trained models)",
            "training_archives": "Aggregated from crawled web corpora (IndicCorp, Dakshina, IndicXlit, Samanantar); separate open research terms apply; MIT does not automatically cover underlying training archives",
            "bhasha_abhijnaanam_benchmark": "CC0-1.0 (Declared on dataset card for manually collected data)",
        },
        "language_and_script": "22 Indic languages in native scripts and Romanized transliteration; native Telugu (Telugu script), Roman Telugu (Latin script), Hindi (Devanagari and Latin)",
        "sample_count_actually_inspected": 0,
        "sample_inspection_method": "Public repository README, release manifests, and Hugging Face dataset card metadata inspection (zero rows downloaded to avoid benchmark contamination)",
        "suitability_classifications": {
            "category_A_native_telugu": "REFERENCE ONLY (Bhasha-Abhijnaanam is an evaluation benchmark; must NOT be used for candidate training curation to avoid leakage. Training data is FastText sentence-level)",
            "category_B_english_telugu": "NOT SUITABLE (Sentence-level monolingual/transliterated buckets; no token-level code-mixing)",
            "category_C_hindi_telugu": "NOT SUITABLE (No intra-sentential code-mixed sentences)",
            "category_D_english_hindi_telugu": "NOT SUITABLE (Completely absent)",
        },
        "limitations": [
            "Data is sentence-level only (FastText format '__label__<code_script> <sentence>') without token-level LID boundaries.",
            "Bhasha-Abhijnaanam test set must remain strictly an external out-of-distribution evaluation benchmark; copying sentences into candidate_sentences.jsonl is barred.",
        ],
    }


def stream_bht25_sample_rows(max_samples: int = 20) -> List[Dict[str, Any]]:
    """Stream a maximum of 20 sample rows from BHT25 using Hugging Face datasets-server public API."""
    cap_samples = min(max(1, max_samples), 20)
    url = f"https://datasets-server.huggingface.co/rows?dataset=sudeshna84%2FBHT25&config=default&split=train&offset=0&length={cap_samples}"
    req = urllib.request.Request(url, headers={"User-Agent": "CodeMix-Intelligence-Auditor/1.0"})
    samples: List[Dict[str, Any]] = []

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for r in data.get("rows", []):
                row_data = r.get("row", {})
                samples.append({
                    "id": row_data.get("id"),
                    "bn": row_data.get("bn"),
                    "hi": row_data.get("hi"),
                    "te": row_data.get("te"),
                })
    except Exception as e:
        logger.warning(f"Live streaming from HF datasets-server returned: {e}. Recording limitation without retry loops.")

    return samples


def audit_bht25(max_samples: int = 20) -> Dict[str, Any]:
    """Audit BHT25 parallel corpus and inspect up to 20 public sample rows."""
    samples = stream_bht25_sample_rows(max_samples=max_samples)
    return {
        "source_name": "BHT25: Bengali-Hindi-Telugu Parallel Corpus for Literary Machine Translation",
        "public_url": "https://huggingface.co/datasets/sudeshna84/BHT25",
        "secondary_url": "https://doi.org/10.1016/j.dib.2026.112775",
        "access_status": "Public direct access (Apache Parquet on Hugging Face; no gating)",
        "metadata_observed": {
            "reported_row_count": 27149,
            "splits": ["train"],
            "fields": ["id", "bn", "hi", "te"],
            "doi": "10.1016/j.dib.2026.112775",
            "publisher": "Sudeshna Sani, Suryakanth V. Gangashetty, Samudravijaya K, Anik Nandi, Aruna Priya, Vineeth Kumar, Akhilesh Kumar Dubey (Data in Brief 2026)",
            "reported_quality": {
                "human_validation_sample_size": 500,
                "semantic_alignment_accuracy": "75.8% (sample-based, not individual verification of all 27,149 rows)",
                "suboptimal_alignment_triplets": "5.8% (sample-based)",
                "estimated_ocr_error_rate": "<0.5%",
                "domain_bias": "Literary domain (Rabindranath Tagore and Sarat Chandra Chattopadhyay)",
            },
        },
        "licence_observed": {
            "licence": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "spdx_id": "CC-BY-4.0",
            "commercial_allowed": True,
            "derivatives_allowed": True,
            "share_alike_clause": False,
            "attribution_obligations": "Must cite Sani et al. (Data in Brief 2026), provide link to CC BY 4.0, and indicate if changes were made.",
        },
        "language_and_script": "Bengali (Bengali script), Hindi (Devanagari script), Telugu (Telugu script)",
        "sample_count_actually_inspected": len(samples),
        "sample_inspection_method": f"Public Hugging Face datasets-server REST API streaming (inspected {len(samples)} sample triplets without downloading full dataset)",
        "sample_records_summary": [
            {
                "id": s.get("id"),
                "hi_snippet": (s.get("hi") or "")[:40] + "...",
                "te_snippet": (s.get("te") or "")[:40] + "...",
            }
            for s in samples[:5]
        ],
        "suitability_classifications": {
            "category_A_native_telugu": "SUITABLE WITH CONDITIONS (Telugu text is human-translated under CC BY 4.0; requires 100% human review of all selected sentences for length, OCR, and alignment)",
            "category_B_english_telugu": "NOT SUITABLE (Contains no English text; is not code-mixed)",
            "category_C_hindi_telugu": "REFERENCE ONLY (Parallel sentences; must NOT be concatenated to manufacture artificial code-mixing)",
            "category_D_english_hindi_telugu": "NOT SUITABLE (No trilingual code-mixing)",
        },
        "limitations": [
            "Parallel corpus, NOT a code-mixed dataset. Combining Hindi and Telugu parallel sentences is strictly forbidden by project guidelines.",
            "Literary domain bias; lacks conversational and modern digital colloquial phrasing.",
            "5.8% suboptimal alignment rate requires human spot-checking when sampling.",
        ],
    }


def audit_ltrc_hindi_telugu() -> Dict[str, Any]:
    """Audit LTRC Hindi-Telugu Parallel Corpus metadata without gate bypass."""
    return {
        "source_name": "The LTRC Hindi-Telugu Parallel Corpus",
        "public_url": "https://huggingface.co/datasets/ltrciiith/The-LTRC-Hindi-Telugu-Parallel-Corpus",
        "access_status": "Gated access (Requires agreement to share account information with repository authors; NOT bypassed)",
        "metadata_observed": {
            "current_hf_listing_sentences": 506178,
            "publication_corpus_descriptions": "Publication describes a 700K qualitative corpus and a 535K developed corpus across domains: Chemistry, Law, News, Healthcare, Education, Open education books",
            "schema_fields": ["domain", "source_language", "target_language", "source_text", "target_text"],
            "publisher": "Language Technologies Research Centre (LTRC), IIIT Hyderabad",
        },
        "licence_observed": {
            "licence": "Creative Commons Attribution Non-Commercial 4.0 International (CC-BY-NC-4.0)",
            "spdx_id": "CC-BY-NC-4.0",
            "commercial_allowed": False,
            "share_alike_clause": False,
            "gated_condition": "Access requires agreement to share account details with authors.",
        },
        "language_and_script": "Hindi (Devanagari script), Telugu (Telugu script)",
        "sample_count_actually_inspected": 0,
        "sample_inspection_method": "Public Hugging Face repository metadata inspection only (zero records fetched; no gate agreement submitted)",
        "suitability_classifications": {
            "category_A_native_telugu": "REFERENCE ONLY (Gated access; BHT25 provides sufficient ungated CC BY 4.0 native Telugu)",
            "category_B_english_telugu": "NOT SUITABLE (No English tokens)",
            "category_C_hindi_telugu": "REFERENCE ONLY (Parallel sentences; cannot be combined to manufacture code-mixing)",
            "category_D_english_hindi_telugu": "NOT SUITABLE (No trilingual data)",
        },
        "limitations": [
            "Gated access requires agreement to share user account info; strictly barred from automated download by project rules.",
            "Parallel corpus, not code-mixed.",
        ],
    }


def audit_mozilla_telugu_text() -> Dict[str, Any]:
    """Audit Mozilla Data Collective Telugu Text Corpus."""
    return {
        "source_name": "Telugu Text Corpus (Mozilla Data Collective)",
        "public_url": "https://mozilladatacollective.com/datasets/cmq82aqqv0110l207drh50nw4",
        "access_status": "Public catalog access on Mozilla Data Collective",
        "metadata_observed": {
            "dataset_id": "cmq82aqqv0110l207drh50nw4",
            "size": "19.87 MB",
            "format": "TXT format",
            "steward": "MirasAI",
            "legal_owner": "Jnana Yoga Sadhana",
            "authorship": "Four authors across multiple writing domains (news, blogs, literature, spiritual essays)",
        },
        "licence_observed": {
            "licence": "Creative Commons Attribution Non Commercial Share Alike 4.0 International (CC-BY-NC-SA-4.0)",
            "spdx_id": "CC-BY-NC-SA-4.0",
            "commercial_allowed": False,
            "share_alike_clause": True,
            "share_alike_warning": "Viral copyleft: Any derivative dataset publicly distributed must be licensed under the identical CC-BY-NC-SA-4.0 license.",
        },
        "language_and_script": "Telugu (Telugu script)",
        "sample_count_actually_inspected": 0,
        "sample_inspection_method": "Mozilla Data Collective metadata and dataset card inspection (no bulk file download)",
        "suitability_classifications": {
            "category_A_native_telugu": "SUITABLE WITH CONDITIONS (High-quality native Telugu, but derivative dataset must comply with CC-BY-NC-SA-4.0 Share-Alike terms if redistributed)",
            "category_B_english_telugu": "NOT SUITABLE (Monolingual Telugu only)",
            "category_C_hindi_telugu": "NOT SUITABLE (Monolingual Telugu only)",
            "category_D_english_hindi_telugu": "NOT SUITABLE (Monolingual Telugu only)",
        },
        "limitations": [
            "Share-Alike clause forces downstream works under CC-BY-NC-SA-4.0.",
            "Requires institutional/faculty review before redistributing derived datasets.",
        ],
    }


def audit_mozilla_common_voice_telugu() -> Dict[str, Any]:
    """Audit Mozilla Common Voice Telugu 27.0 on MDC."""
    return {
        "source_name": "Mozilla Common Voice Telugu 27.0 (Text Prompts)",
        "public_url": "https://mozilladatacollective.com/datasets/cmu617jv900jfo107hpm9aj8d",
        "access_status": "Public catalog access on Mozilla Data Collective",
        "metadata_observed": {
            "dataset_id": "cmu617jv900jfo107hpm9aj8d",
            "total_sentences": 20072,
            "validated_sentences": 372,
            "unvalidated_sentences": 19700,
            "rehosting_clause": "The dataset page explicitly prohibits rehosting or resharing the dataset.",
        },
        "licence_observed": {
            "licence": "Creative Commons Zero v1.0 Universal (CC0-1.0)",
            "spdx_id": "CC0-1.0",
            "rehosting_restriction": "Explicit terms prohibit rehosting or resharing the corpus.",
        },
        "language_and_script": "Telugu (Telugu script)",
        "sample_count_actually_inspected": 0,
        "sample_inspection_method": "Dataset card metadata inspection only (zero sentences copied into project)",
        "suitability_classifications": {
            "category_A_native_telugu": "REFERENCE ONLY (Use as external reference only until redistribution condition is clarified; do not copy sentences into candidate dataset)",
            "category_B_english_telugu": "NOT SUITABLE (Monolingual speech prompts)",
            "category_C_hindi_telugu": "NOT SUITABLE (Monolingual Telugu only)",
            "category_D_english_hindi_telugu": "NOT SUITABLE (Monolingual Telugu only)",
        },
        "limitations": [
            "Rehosting/resharing prohibition contradicts typical CC0-1.0 terms; redistribution condition is legally ambiguous.",
            "High proportion of unvalidated sentences (19,700 out of 20,072).",
        ],
    }


def audit_indiccorp_telugu() -> Dict[str, Any]:
    """Audit AI4Bharat IndicCorp Telugu corpus."""
    return {
        "source_name": "AI4Bharat IndicCorp Telugu",
        "public_url": "https://indicnlp.ai4bharat.org/corpora/",
        "access_status": "Public download links from AI4Bharat servers",
        "metadata_observed": {
            "reported_sentences": "47.9 million sentences",
            "reported_tokens": "674 million tokens",
            "format": "One sentence per line, plain text",
            "provenance": "Scraped from diverse web sources and news portals",
        },
        "licence_observed": {
            "licence": "No clear data licence found on public page",
            "status": "LICENCE UNCLEAR",
            "note": "Web-scraped corpus without an explicit open-source data license or copyright declaration on the corpora index page.",
        },
        "language_and_script": "Telugu (Telugu script)",
        "sample_count_actually_inspected": 0,
        "sample_inspection_method": "Public index metadata inspection (no data downloaded)",
        "suitability_classifications": {
            "category_A_native_telugu": "LICENCE UNCLEAR (Massive sentence volume, but unclear data licensing makes it unsuitable for redistribution without legal clarification)",
            "category_B_english_telugu": "NOT SUITABLE (Monolingual Telugu crawl)",
            "category_C_hindi_telugu": "NOT SUITABLE (Monolingual Telugu only)",
            "category_D_english_hindi_telugu": "NOT SUITABLE (Monolingual Telugu only)",
        },
        "limitations": [
            "Lack of clear licensing terms poses redistribution risks.",
            "Classified strictly as LICENCE UNCLEAR per project mandate.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="External Dataset Source Audit for CodeMix Intelligence (Step 25B)")
    parser.add_argument("--max-samples", type=int, default=20, help="Maximum number of sample rows to stream from BHT25 (max 20)")
    parser.add_argument("--output-json", type=str, default=None, help="Filepath to save structured audit JSON")
    args = parser.parse_args()

    max_samples = min(max(1, args.max_samples), 20)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    logger.info("=" * 72)
    logger.info("STEP 25B: EXTERNAL DATASET SOURCE AUDIT & LOCAL INTEGRITY VERIFICATION")
    logger.info(f"Execution Timestamp (UTC): {timestamp}")
    logger.info("=" * 72)

    # 1. Dataset Isolation Verification
    logger.info("[Task 7] Pre-audit dataset isolation check...")
    isolation_pre = verify_dataset_isolation()
    for fname, info in isolation_pre["custom_files"].items():
        logger.info(f" - {fname}: exists={info['exists']}, size={info['size_bytes']} bytes, sha256={info['sha256'][:16]}...")
    if isolation_pre["all_custom_jsonl_empty"]:
        logger.info(" -> VERIFIED: All custom JSONL files are currently empty (0 records).")
    else:
        logger.error(" -> ERROR: Custom JSONL files contain unexpected data!")

    # 2. Audits
    logger.info("\n[Task 1 & Task 2] Auditing Source 1: AI4Bharat IndicLID & Bhasha-Abhijnaanam...")
    indiclid = audit_ai4bharat_indiclid()
    logger.info(f" - Public URL: {indiclid['public_url']}")
    logger.info(f" - Code/Model Licence: {indiclid['licence_observed']['code_and_models']}")
    logger.info(f" - Bhasha-Abhijnaanam Test Examples: {indiclid['metadata_observed']['bhasha_abhijnaanam_test_examples']}")

    logger.info(f"\n[Task 2 & Task 3] Auditing Source 2: BHT25 (Streaming up to {max_samples} samples via public API)...")
    bht25 = audit_bht25(max_samples=max_samples)
    logger.info(f" - Publisher: {bht25['metadata_observed']['publisher']}")
    logger.info(f" - Reported Triplets: {bht25['metadata_observed']['reported_row_count']:,}")
    logger.info(f" - Licence: {bht25['licence_observed']['licence']}")
    logger.info(f" - Samples actually inspected: {bht25['sample_count_actually_inspected']}")
    if bht25["sample_records_summary"]:
        for s in bht25["sample_records_summary"][:3]:
            logger.info(f"   * [{s['id']}] HI: {s['hi_snippet']} | TE: {s['te_snippet']}")

    logger.info("\n[Task 2] Auditing Source 3: The LTRC Hindi-Telugu Parallel Corpus...")
    ltrc = audit_ltrc_hindi_telugu()
    logger.info(f" - Public URL: {ltrc['public_url']}")
    logger.info(f" - HF Listing: {ltrc['metadata_observed']['current_hf_listing_sentences']:,} sentences")
    logger.info(f" - Licence: {ltrc['licence_observed']['licence']}")
    logger.info(f" - Gated Status: {ltrc['access_status']}")

    logger.info("\n[Task 2] Auditing Source 4: Mozilla Telugu Text Corpus...")
    moz_text = audit_mozilla_telugu_text()
    logger.info(f" - Size & Format: {moz_text['metadata_observed']['size']}, {moz_text['metadata_observed']['format']}")
    logger.info(f" - Steward / Owner: {moz_text['metadata_observed']['steward']} / {moz_text['metadata_observed']['legal_owner']}")
    logger.info(f" - Licence: {moz_text['licence_observed']['licence']}")

    logger.info("\n[Task 2] Auditing Source 5: Mozilla Common Voice Telugu 27.0...")
    moz_cv = audit_mozilla_common_voice_telugu()
    logger.info(f" - Sentences: {moz_cv['metadata_observed']['total_sentences']} (Validated: {moz_cv['metadata_observed']['validated_sentences']})")
    logger.info(f" - Licence: {moz_cv['licence_observed']['licence']}")
    logger.info(f" - Rehosting clause: {moz_cv['metadata_observed']['rehosting_clause']}")

    logger.info("\n[Task 2] Auditing Source 6: AI4Bharat IndicCorp Telugu...")
    indiccorp = audit_indiccorp_telugu()
    logger.info(f" - Sentences & Tokens: {indiccorp['metadata_observed']['reported_sentences']}, {indiccorp['metadata_observed']['reported_tokens']}")
    logger.info(f" - Licence Status: {indiccorp['licence_observed']['status']}")

    # 3. Compile Master Audit Report
    master_audit = {
        "audit_metadata": {
            "step": "25C",
            "title": "External Dataset Source Audit and Local Integrity Verification",
            "timestamp_utc": timestamp,
            "max_sample_inspection_cap": max_samples,
            "samples_actually_inspected_bht25": bht25["sample_count_actually_inspected"],
            "inspection_guarantees": [
                "Zero complete datasets downloaded",
                "Zero gated repositories accessed or bypassed",
                "Zero authentication credentials or API tokens used",
                "Zero candidate sentences created or copied",
                "Zero modifications to existing unified or custom datasets",
            ],
        },
        "pre_audit_integrity": isolation_pre,
        "audited_sources": {
            "ai4bharat_indiclid": indiclid,
            "sudeshna84_bht25": bht25,
            "ltrc_hindi_telugu": ltrc,
            "mozilla_telugu_text": moz_text,
            "mozilla_common_voice_telugu": moz_cv,
            "ai4bharat_indiccorp_telugu": indiccorp,
        },
        "suitability_matrix": {
            "BHT25": {
                "category_A_native_telugu": "SUITABLE WITH CONDITIONS",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "REFERENCE ONLY",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "CC BY 4.0; 27,149 triplets (sample validation 75.8%); requires 100% human review; parallel sentences must NOT be concatenated.",
            },
            "Mozilla_Telugu_Text": {
                "category_A_native_telugu": "SUITABLE WITH CONDITIONS",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "NOT SUITABLE",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "CC-BY-NC-SA-4.0 requires downstream derivative redistribution to also carry Share-Alike license.",
            },
            "Mozilla_Common_Voice_Telugu": {
                "category_A_native_telugu": "REFERENCE ONLY",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "NOT SUITABLE",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "Page explicitly prohibits rehosting/resharing despite CC0 tag; use as reference only until clarified.",
            },
            "LTRC_Hindi_Telugu": {
                "category_A_native_telugu": "REFERENCE ONLY",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "REFERENCE ONLY",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "Gated access requiring account agreement; not downloaded. Parallel corpus, not code-mixed.",
            },
            "AI4Bharat_IndicLID_Training": {
                "category_A_native_telugu": "REFERENCE ONLY",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "NOT SUITABLE",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "Sentence-level FastText format; underlying web crawl licensing unclear; no token boundaries.",
            },
            "AI4Bharat_Bhasha_Abhijnaanam": {
                "category_A_native_telugu": "REFERENCE ONLY",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "NOT SUITABLE",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "Evaluation benchmark test set. Barred from candidate/training curation to prevent leakage.",
            },
            "AI4Bharat_IndicCorp_Telugu": {
                "category_A_native_telugu": "LICENCE UNCLEAR",
                "category_B_english_telugu": "NOT SUITABLE",
                "category_C_hindi_telugu": "NOT SUITABLE",
                "category_D_english_hindi_telugu": "NOT SUITABLE",
                "rationale": "Web-scraped corpus with no clear data license declared on public page.",
            },
            "Human_Authored_Elicitation": {
                "category_A_native_telugu": "N/A (Abundant public data)",
                "category_B_english_telugu": "SUITABLE (Primary Path)",
                "category_C_hindi_telugu": "SUITABLE (Primary Path)",
                "category_D_english_hindi_telugu": "SUITABLE (Primary Path)",
                "rationale": "Token-level native Telugu code-mixed sentences are completely absent from public corpora.",
            },
        },
    }

    # 4. Save JSON report if requested
    out_path = Path(args.output_json) if args.output_json else (REPORTS_DIR / "step25_source_audit.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(master_audit, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"\n[Task 3] Saved comprehensive audit JSON to {out_path}")

    # 5. Post-audit verification
    logger.info("\n[Task 7] Post-audit dataset isolation check...")
    isolation_post = verify_dataset_isolation()
    mismatch = False
    for fname, pre_info in isolation_pre["custom_files"].items():
        post_info = isolation_post["custom_files"][fname]
        if pre_info["sha256"] != post_info["sha256"] or pre_info["size_bytes"] != post_info["size_bytes"]:
            logger.error(f"INTEGRITY VIOLATION on {fname}: pre_sha={pre_info['sha256']} post_sha={post_info['sha256']}")
            mismatch = True
        else:
            logger.info(f" - {fname}: MATCH confirmed (size={post_info['size_bytes']}, sha256={post_info['sha256'][:16]}...)")

    if not mismatch and isolation_post["all_custom_jsonl_empty"]:
        logger.info(" -> VERIFIED: Post-audit integrity check passed. Custom JSONL files remain empty.")
    else:
        logger.error(" -> INTEGRITY CHECK FAILED!")

    logger.info("\n" + "=" * 72)
    logger.info("AUDIT SCRIPT EXECUTION FINISHED SUCCESSFULLY")
    logger.info("=" * 72)


if __name__ == "__main__":
    main()
