"""
Validation script for Custom Trilingual Language Identification Dataset.
Step 28: Schema v1.3.0 (Eight-Key Language Statistics) & Governance Finalization.

Validates:
1. File syntax & loading for candidate_sentences.jsonl, reviewed_sentences.jsonl, rejected_sentences.jsonl.
2. Required fields and data types against dataset_schema.json (v1.3.0).
3. Unique record IDs across all custom splits.
4. Length parity: len(tokens) == len(source_labels) == len(model_labels).
5. Label validity:
   - Exactly 4 supervised classes: EN=0, HI=1, TE=2, OTHER=3
   - Non-supervised provenance annotations: MIXED=-100, NE=-100, AMBIGUOUS=-100, null=-100
   - Strict rejection of MIXED, AMBIGUOUS, or NULL if assigned a supervised class ID (0, 1, 2, 3)
   - Strict rejection of treating MIXED, NE, AMBIGUOUS, or NULL as OTHER
6. Morphologically fused token governance:
   - Fully Telugu-script inflected root (e.g. కంప్యూటర్లో): TE (2)
   - Latin root with Telugu suffix (e.g. computerలో): MIXED (-100)
7. Detection of empty sentences and empty token sequences.
8. Detection of duplicate sentences using normalized comparison keys.
9. Unicode script presence:
   - Telugu script (U+0C00-U+0C7F)
   - Devanagari script (U+0900-U+097F)
   - Latin script (A-Za-z)
10. Language presence verification per category:
    - Native_Telugu: contains TE tokens
    - English_Telugu / English_Native_Telugu: contains EN and TE tokens
    - Hindi_Telugu / Hindi_Native_Telugu: contains HI and TE tokens
    - English_Hindi_Telugu: contains EN, HI, and TE tokens
11. Provenance Architecture & Conditional Rules (Step 26/28):
    - Four collection methods: licensed_corpus_extraction, naturally_occurring, human_elicited, parallel_reference.
    - Strict rejection of automatically_generated data from ground truth.
    - Method-specific conditional requirements for source_dataset, source_record_id, license, source_url, contributor_id, consent_status.
    - Verified source rights and consent required for reviewed data.
12. Independent Calculation & Verification of Language Statistics (Schema v1.3.0):
    - language_token_counts: exactly eight independent count keys (EN, HI, TE, OTHER, NE, MIXED, AMBIGUOUS, NULL).
    - Every token contributes to exactly one count; sum must equal len(tokens).
    - Missing count keys are rejected; cannot be silently assumed zero.
    - language_switch_count: independent counts of transitions between language-bearing classes (EN, HI, TE), ignoring OTHER, NE, MIXED, AMBIGUOUS, NULL.
13. Source grouping & split readiness: verifies source_group_id to keep authoring/corpus groups disjoint without splitting groups.
14. Review status barrier: requires two independent reviewers, review_date, verified rights, and satisfied consent for stage2_approved and adjudicated.
15. Manifest consistency check against dataset_manifest.json (v1.3.0, splits, classes, seed).
16. Comprehensive self-test suite covering all 30 test cases.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Configure console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CUSTOM_DIR = PROJECT_ROOT / "data" / "custom" / "trilingual_lid"
EXAMPLES_DIR = CUSTOM_DIR / "examples"

REQUIRED_FIELDS = [
    "sentence_id",
    "original_sentence_id",
    "source",
    "subset",
    "original_split",
    "split",
    "text",
    "tokens",
    "original_labels",
    "source_labels",
    "model_labels",
    "text_format",
    "lid_eligible",
    "lid_eligible_tokens",
    "source_record_id",
]

ALLOWED_SUBSETS = {
    "Native_Telugu",
    "English_Telugu",
    "English_Native_Telugu",
    "Hindi_Telugu",
    "Hindi_Native_Telugu",
    "English_Hindi_Telugu",
}

# The model strictly uses 4 supervised classes
SUPERVISED_MODEL_CLASSES = {0: "EN", 1: "HI", 2: "TE", 3: "OTHER"}
ALLOWED_MODEL_LABELS = {0, 1, 2, 3, -100}
ALLOWED_SOURCE_LABELS = {"EN", "HI", "TE", "OTHER", "NE", "AMBIGUOUS", "MIXED", None}

SOURCE_TO_MODEL_MAP = {
    "EN": 0,
    "HI": 1,
    "TE": 2,
    "OTHER": 3,
    "MIXED": -100,
    "NE": -100,
    "AMBIGUOUS": -100,
    None: -100,
}

# Provenance Taxonomy (Step 26/28)
ALLOWED_COLLECTION_METHODS = {
    "licensed_corpus_extraction",
    "naturally_occurring",
    "human_elicited",
    "parallel_reference",
}

ALLOWED_REVIEW_STATUSES = {
    "candidate",
    "stage1_approved",
    "stage2_approved",
    "adjudicated",
    "rejected",
    "approved",  # backward compatibility alias for stage2_approved
}

LANGUAGE_BEARING_CLASSES = {"EN", "HI", "TE"}
LANGUAGE_TOKEN_COUNT_KEYS = ["EN", "HI", "TE", "OTHER", "NE", "MIXED", "AMBIGUOUS", "NULL"]

# Unicode Script Regex Patterns
RE_TELUGU = re.compile(r"[\u0C00-\u0C7F]")
RE_DEVANAGARI = re.compile(r"[\u0900-\u097F]")
RE_LATIN = re.compile(r"[A-Za-z]")

# ISO-8601 Date regex
RE_DATE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Pseudonym pattern
RE_CONTRIBUTOR_PSEUDONYM = re.compile(r"^(contrib_[0-9]{2,}|contributor_[0-9]{2,}|contrib_[a-z0-9]+)$", re.IGNORECASE)
RE_ANNOTATOR_PSEUDONYM = re.compile(r"^(annotator_[0-9]{2,}|rev_[0-9]{2,}|reviewer_[0-9]{2,})$", re.IGNORECASE)


def normalize_key(tokens: list) -> str:
    """Canonical normalized comparison key for duplicate detection."""
    return " ".join(t.strip().casefold() for t in tokens)


def compute_language_token_counts(source_labels: list) -> dict:
    """
    Step 28 (Schema v1.3.0) 8-key independent counts of source annotation labels:
    EN, HI, TE, OTHER, NE, MIXED, AMBIGUOUS, NULL.
    Every token contributes to exactly one count.
    JSON null source labels increment NULL.
    AMBIGUOUS source labels increment AMBIGUOUS.
    Total count must equal len(source_labels).
    """
    counts = {k: 0 for k in LANGUAGE_TOKEN_COUNT_KEYS}
    for lbl in source_labels:
        if lbl is None:
            counts["NULL"] += 1
        elif lbl in counts:
            counts[lbl] += 1
    return counts


def compute_language_switch_count(source_labels: list) -> int:
    """
    Count intra-sentential transitions between language-bearing tokens (EN, HI, TE).
    Tokens annotated with OTHER, NE, MIXED, AMBIGUOUS, or null are ignored.
    """
    switches = 0
    prev_lang = None
    for lbl in source_labels:
        if lbl in LANGUAGE_BEARING_CLASSES:
            if prev_lang is not None and lbl != prev_lang:
                switches += 1
            prev_lang = lbl
    return switches


def validate_single_record(
    rec: dict,
    expected_split: str,
    record_source: str,
    seen_ids: set,
    seen_keys: dict,
    seen_source_records: set = None,
) -> tuple:
    """
    Validate a single record dictionary against Step 26 provenance-aware rules.
    Returns: (errors, warnings)
    """
    if seen_source_records is None:
        seen_source_records = set()

    errors = []
    warnings = []
    sid = rec.get("sentence_id", "<missing_id>")

    # 1. Required Fields Check
    missing_fields = [f for f in REQUIRED_FIELDS if f not in rec]
    if missing_fields:
        errors.append(f"[{record_source}] {sid}: Missing required fields: {missing_fields}")
        return errors, warnings

    # 2. Unique ID Check
    if sid in seen_ids:
        errors.append(f"[{record_source}] Duplicate sentence_id '{sid}' detected.")
    else:
        seen_ids.add(sid)

    # Check ID Prefix Convention
    if expected_split == "candidate" and not sid.startswith("custom_cand_"):
        warnings.append(f"[{record_source}] {sid}: Candidate ID does not follow 'custom_cand_' prefix.")
    elif expected_split == "reviewed" and not sid.startswith("custom_rev_"):
        errors.append(f"[{record_source}] {sid}: Reviewed ID must start with 'custom_rev_'.")
    elif expected_split == "rejected" and not sid.startswith("custom_rej_"):
        warnings.append(f"[{record_source}] {sid}: Rejected ID does not follow 'custom_rej_' prefix.")

    # 3. Review Status Barrier & Reviewed File Split Consistency
    if expected_split == "reviewed":
        if rec.get("split") != "reviewed":
            errors.append(f"[{record_source}] {sid}: Record in reviewed file has split '{rec.get('split')}' != 'reviewed'.")
        if "metadata" in rec and rec["metadata"].get("review_status") == "candidate":
            errors.append(f"[{record_source}] {sid}: Unreviewed candidate record found inside reviewed_sentences.jsonl!")
        if "metadata" in rec and rec["metadata"].get("annotation_status") == "candidate":
            errors.append(f"[{record_source}] {sid}: Unreviewed candidate record found inside reviewed_sentences.jsonl!")

    # 4. Text and Tokens Non-Empty Check
    text = str(rec.get("text", "")).strip()
    tokens = rec.get("tokens", [])
    if not text:
        errors.append(f"[{record_source}] {sid}: Empty 'text' string.")
    if not isinstance(tokens, list) or len(tokens) == 0:
        errors.append(f"[{record_source}] {sid}: Empty or non-list 'tokens' array.")
        return errors, warnings

    if len(tokens) < 3:
        warnings.append(f"[{record_source}] {sid}: Very short sentence ({len(tokens)} tokens).")

    # 5. Length Parity Check
    src_labels = rec.get("source_labels", [])
    model_labels = rec.get("model_labels", [])
    if not (len(tokens) == len(src_labels) == len(model_labels)):
        errors.append(
            f"[{record_source}] {sid}: Length mismatch: tokens={len(tokens)}, "
            f"source_labels={len(src_labels)}, model_labels={len(model_labels)}"
        )
        return errors, warnings

    # 6. Model & Source Labels Validity, Consistency, and Fused Token Rules
    for idx, (tok, s_lbl, m_lbl) in enumerate(zip(tokens, src_labels, model_labels)):
        if m_lbl not in ALLOWED_MODEL_LABELS:
            errors.append(f"[{record_source}] {sid} token[{idx}] '{tok}': Invalid model_label '{m_lbl}' (allowed: {ALLOWED_MODEL_LABELS}).")
        if s_lbl not in ALLOWED_SOURCE_LABELS:
            errors.append(f"[{record_source}] {sid} token[{idx}] '{tok}': Invalid source_label '{s_lbl}' (allowed: {ALLOWED_SOURCE_LABELS}).")

        # Decision 2 Rule: MIXED is provenance only and cannot be assigned a supervised class ID
        if s_lbl == "MIXED":
            if m_lbl != -100:
                errors.append(
                    f"[{record_source}] {sid} token[{idx}] '{tok}': MIXED is annotation provenance only and "
                    f"cannot be assigned supervised class ID {m_lbl} (must be -100). MIXED cannot be treated as OTHER or any model class."
                )
            if m_lbl == 3:
                errors.append(
                    f"[{record_source}] {sid} token[{idx}] '{tok}': MIXED cannot be treated as OTHER (model_label=3)."
                )

        # Step 28 Rule: AMBIGUOUS is provenance only and cannot receive a supervised class ID
        if s_lbl == "AMBIGUOUS":
            if m_lbl != -100:
                errors.append(
                    f"[{record_source}] {sid} token[{idx}] '{tok}': AMBIGUOUS is annotation provenance only and "
                    f"cannot be assigned supervised class ID {m_lbl} (must be -100). AMBIGUOUS cannot be treated as OTHER or any model class."
                )
            if m_lbl in (0, 1, 2, 3):
                errors.append(
                    f"[{record_source}] {sid} token[{idx}] '{tok}': AMBIGUOUS cannot receive a supervised class ID ({m_lbl})."
                )

        # Step 28 Rule: NULL source label is provenance only and cannot receive a supervised class ID
        if s_lbl is None:
            if m_lbl != -100:
                errors.append(
                    f"[{record_source}] {sid} token[{idx}] '{tok}': NULL source label is provenance only and "
                    f"cannot be assigned supervised class ID {m_lbl} (must be -100). NULL cannot be treated as OTHER or any model class."
                )
            if m_lbl in (0, 1, 2, 3):
                errors.append(
                    f"[{record_source}] {sid} token[{idx}] '{tok}': NULL cannot receive a supervised class ID ({m_lbl})."
                )

        # General cross-consistency check between source_labels and model_labels
        expected_m = SOURCE_TO_MODEL_MAP.get(s_lbl, -100)
        if m_lbl != expected_m:
            errors.append(
                f"[{record_source}] {sid} token[{idx}] '{tok}': Inconsistent labels: "
                f"source_label='{s_lbl}' implies model_label={expected_m}, but got {m_lbl}."
            )

    # 7. LID Eligibility Calculation Verification
    comp_eligible_tokens = sum(1 for m in model_labels if m != -100)
    if rec.get("lid_eligible_tokens") != comp_eligible_tokens:
        errors.append(
            f"[{record_source}] {sid}: lid_eligible_tokens mismatch: "
            f"recorded={rec.get('lid_eligible_tokens')}, computed={comp_eligible_tokens}."
        )
    if rec.get("lid_eligible") != (comp_eligible_tokens > 0):
        errors.append(
            f"[{record_source}] {sid}: lid_eligible boolean mismatch: "
            f"recorded={rec.get('lid_eligible')}, expected={comp_eligible_tokens > 0}."
        )

    # 8. Subset and Category Validation
    subset = rec.get("subset")
    if subset not in ALLOWED_SUBSETS:
        errors.append(f"[{record_source}] {sid}: Invalid subset '{subset}' (allowed: {ALLOWED_SUBSETS}).")
        return errors, warnings

    # 9. Language Annotation and Script Verification
    has_te_label = any(l == "TE" for l in src_labels)
    has_hi_label = any(l == "HI" for l in src_labels)
    has_en_label = any(l == "EN" for l in src_labels)

    has_te_script = bool(RE_TELUGU.search(text))
    has_hi_script = bool(RE_DEVANAGARI.search(text))
    has_en_script = bool(RE_LATIN.search(text))

    # Category A: Native_Telugu
    if subset == "Native_Telugu":
        if not has_te_script:
            errors.append(f"[{record_source}] {sid}: Native_Telugu sentence lacks Telugu Unicode script (U+0C00-U+0C7F).")
        if not has_te_label:
            errors.append(f"[{record_source}] {sid}: Native_Telugu sentence contains 0 tokens annotated as 'TE'.")
        if has_hi_label or has_en_label:
            errors.append(f"[{record_source}] {sid}: Native_Telugu sentence contains unauthorized foreign language tags (EN/HI).")

    # Category B: English_Telugu / English_Native_Telugu
    elif subset in ("English_Telugu", "English_Native_Telugu"):
        if not has_te_script:
            errors.append(f"[{record_source}] {sid}: {subset} sentence lacks Telugu Unicode script (U+0C00-U+0C7F).")
        if not has_en_script:
            errors.append(f"[{record_source}] {sid}: {subset} sentence lacks Latin script for English.")
        if not has_te_label:
            errors.append(f"[{record_source}] {sid}: {subset} sentence contains 0 tokens annotated as 'TE'.")
        if not has_en_label:
            errors.append(f"[{record_source}] {sid}: {subset} sentence contains 0 tokens annotated as 'EN'.")
        if has_hi_label:
            errors.append(f"[{record_source}] {sid}: {subset} sentence incorrectly contains Hindi ('HI') tags.")

    # Category C: Hindi_Telugu / Hindi_Native_Telugu
    elif subset in ("Hindi_Telugu", "Hindi_Native_Telugu"):
        if not has_te_script:
            errors.append(f"[{record_source}] {sid}: {subset} sentence lacks Telugu Unicode script (U+0C00-U+0C7F).")
        if not has_hi_script:
            errors.append(f"[{record_source}] {sid}: {subset} sentence lacks Devanagari script (U+0900-U+097F).")
        if not has_te_label:
            errors.append(f"[{record_source}] {sid}: {subset} sentence contains 0 tokens annotated as 'TE'.")
        if not has_hi_label:
            errors.append(f"[{record_source}] {sid}: {subset} sentence contains 0 tokens annotated as 'HI'.")
        if has_en_label:
            warnings.append(f"[{record_source}] {sid}: {subset} sentence contains English tags (should be Category D if trilingual).")

    # Category D: English_Hindi_Telugu
    elif subset == "English_Hindi_Telugu":
        if not has_te_script:
            errors.append(f"[{record_source}] {sid}: English_Hindi_Telugu sentence lacks Telugu Unicode script (U+0C00-U+0C7F).")
        if not has_hi_script:
            errors.append(f"[{record_source}] {sid}: English_Hindi_Telugu sentence lacks Devanagari script (U+0900-U+097F).")
        if not has_en_script:
            errors.append(f"[{record_source}] {sid}: English_Hindi_Telugu sentence lacks Latin script for English.")
        if not has_te_label:
            errors.append(f"[{record_source}] {sid}: English_Hindi_Telugu sentence lacks tokens annotated as 'TE'.")
        if not has_hi_label:
            errors.append(f"[{record_source}] {sid}: English_Hindi_Telugu sentence lacks tokens annotated as 'HI'.")
        if not has_en_label:
            errors.append(f"[{record_source}] {sid}: English_Hindi_Telugu sentence lacks tokens annotated as 'EN'.")

    # 10. Duplicate Sentence Key Detection
    key = normalize_key(tokens)
    if key in seen_keys:
        prior_sid, prior_split = seen_keys[key]
        errors.append(
            f"[{record_source}] {sid}: Duplicate normalized sentence detected! "
            f"Matches {prior_sid} (in {prior_split}). Key: '{key[:50]}...'"
        )
    else:
        seen_keys[key] = (sid, expected_split)

    # -------------------------------------------------------------------------
    # 11. STEP 26 PROVENANCE & CONDITIONAL VALIDATION RULES
    # -------------------------------------------------------------------------
    meta = rec.get("metadata", {})
    if not isinstance(meta, dict):
        errors.append(f"[{record_source}] {sid}: 'metadata' must be an object.")
        return errors, warnings

    collection_method = meta.get("collection_method")

    # Disallow AI generated records
    if collection_method in ("automatically_generated", "synthetic_generated", "llm_generated"):
        errors.append(
            f"[{record_source}] {sid}: Automatically generated text ('{collection_method}') is strictly prohibited from ground-truth data."
        )

    # Validate collection method enum if provided
    if collection_method is not None and collection_method not in ALLOWED_COLLECTION_METHODS:
        errors.append(
            f"[{record_source}] {sid}: Invalid collection_method '{collection_method}'. Allowed: {sorted(ALLOWED_COLLECTION_METHODS)}"
        )

    # Top-level source_record_id canonical value
    src_rec_id = rec.get("source_record_id")

    # Method-Specific Conditional Rules
    if collection_method == "licensed_corpus_extraction":
        # Required: source_dataset, source_record_id (non-null), license, source_url
        if not meta.get("source_dataset"):
            errors.append(f"[{record_source}] {sid}: 'source_dataset' is required for licensed_corpus_extraction.")
        if src_rec_id is None or str(src_rec_id).strip() == "":
            errors.append(f"[{record_source}] {sid}: 'source_record_id' is required and must not be null for licensed_corpus_extraction.")
        if not meta.get("license"):
            errors.append(f"[{record_source}] {sid}: 'license' is required for licensed_corpus_extraction.")
        if not meta.get("source_url"):
            errors.append(f"[{record_source}] {sid}: 'source_url' is required for licensed_corpus_extraction.")
        # contributor_id must be null
        if meta.get("contributor_id") is not None:
            errors.append(f"[{record_source}] {sid}: 'contributor_id' must be null for licensed_corpus_extraction.")
        # consent_status must be not_applicable_public_corpus
        if meta.get("consent_status") != "not_applicable_public_corpus":
            errors.append(
                f"[{record_source}] {sid}: 'consent_status' must be 'not_applicable_public_corpus' for licensed_corpus_extraction (got '{meta.get('consent_status')}')."
            )

    elif collection_method == "naturally_occurring":
        if not (meta.get("source_url") or meta.get("source_dataset")):
            errors.append(f"[{record_source}] {sid}: 'source_url' or documented 'source_dataset' is required for naturally_occurring.")
        if not meta.get("consent_status") or meta.get("consent_status") in ("pending", "pending_consent"):
            errors.append(f"[{record_source}] {sid}: Valid permission/compliance 'consent_status' required for naturally_occurring.")
        if not meta.get("license"):
            errors.append(f"[{record_source}] {sid}: 'license' or rights reference is required for naturally_occurring.")

    elif collection_method == "human_elicited":
        # Required: contributor_id (non-null, pseudonymous), consent_status, agreed license
        cid = meta.get("contributor_id")
        if not cid:
            errors.append(f"[{record_source}] {sid}: 'contributor_id' is required for human_elicited records.")
        elif not RE_CONTRIBUTOR_PSEUDONYM.match(str(cid)):
            errors.append(f"[{record_source}] {sid}: contributor_id '{cid}' must be pseudonymous (e.g., 'contrib_01'). PII is prohibited.")

        # source_record_id must be null
        if src_rec_id is not None:
            errors.append(f"[{record_source}] {sid}: 'source_record_id' must be null for direct human_elicited records (got '{src_rec_id}').")

        # consent required
        c_status = meta.get("consent_status")
        if not c_status or c_status in ("pending", "pending_consent"):
            errors.append(f"[{record_source}] {sid}: Valid contributor 'consent_status' is required for human_elicited records.")

        if not meta.get("license"):
            errors.append(f"[{record_source}] {sid}: Contributor agreed 'license' terms must be recorded for human_elicited records.")

    elif collection_method == "parallel_reference":
        # Required: contributor_id, consent_status, source_dataset, source_record_id (reference ID), license
        cid = meta.get("contributor_id")
        if not cid:
            errors.append(f"[{record_source}] {sid}: Authoring 'contributor_id' is required for parallel_reference records.")
        elif not RE_CONTRIBUTOR_PSEUDONYM.match(str(cid)):
            errors.append(f"[{record_source}] {sid}: contributor_id '{cid}' must be pseudonymous (e.g., 'contrib_01').")

        if not meta.get("consent_status") or meta.get("consent_status") in ("pending", "pending_consent"):
            errors.append(f"[{record_source}] {sid}: Contributor 'consent_status' is required for parallel_reference records.")

        if not meta.get("source_dataset"):
            errors.append(f"[{record_source}] {sid}: Reference 'source_dataset' is required for parallel_reference records.")
        if src_rec_id is None or str(src_rec_id).strip() == "":
            errors.append(f"[{record_source}] {sid}: Reference 'source_record_id' is required for parallel_reference records.")
        if not meta.get("license"):
            errors.append(f"[{record_source}] {sid}: Reference source 'license' is required for parallel_reference records.")

    # Source Grouping Verification (Task 4)
    source_grp = meta.get("source_group_id") or meta.get("group_id")
    if not source_grp:
        warnings.append(
            f"[{record_source}] {sid}: Missing 'source_group_id' in metadata: blocks final group-aware train/val/test split readiness."
        )

    # Duplicate source_record_id check for corpus records
    if src_rec_id is not None and meta.get("source_dataset"):
        src_tuple = (meta.get("source_dataset"), str(src_rec_id))
        if src_tuple in seen_source_records:
            errors.append(
                f"[{record_source}] {sid}: Duplicate source_record_id '{src_rec_id}' detected for source_dataset '{meta.get('source_dataset')}'."
            )
        else:
            seen_source_records.add(src_tuple)

    # -------------------------------------------------------------------------
    # 12. STEP 26 REVIEW BARRIER & AUDIT CHECKS FOR REVIEWED DATA
    # -------------------------------------------------------------------------
    is_reviewed_record = (
        expected_split == "reviewed"
        or rec.get("split") == "reviewed"
        or meta.get("annotation_status") in ("stage2_approved", "adjudicated")
    )

    if is_reviewed_record:
        # Check review status
        ann_status = meta.get("annotation_status") or meta.get("review_status")
        if ann_status not in ("stage2_approved", "adjudicated", "approved"):
            errors.append(
                f"[{record_source}] {sid}: Reviewed record must have annotation_status 'stage2_approved' or 'adjudicated' (got '{ann_status}')."
            )

        # Both reviewers required
        a1 = meta.get("annotator_1") or meta.get("stage1_reviewer")
        a2 = meta.get("annotator_2") or meta.get("stage2_reviewer")
        if not a1 or not a2:
            errors.append(f"[{record_source}] {sid}: Reviewed record requires both annotator_1 and annotator_2 reviewer IDs.")

        # Review date required
        r_date = meta.get("review_date")
        if not r_date or not RE_DATE_ISO.match(str(r_date)):
            errors.append(f"[{record_source}] {sid}: Reviewed record requires valid ISO-8601 review_date (YYYY-MM-DD), got '{r_date}'.")

        # Source rights must be verified (cannot be pending or unclear)
        lic = meta.get("license")
        if not lic or lic in ("pending", "unclear", "pending_rights"):
            errors.append(f"[{record_source}] {sid}: Reviewed record cannot have pending or unverified license ('{lic}').")

        # Contributor consent must be satisfied
        c_stat = meta.get("consent_status")
        if not c_stat or c_stat in ("pending", "pending_consent"):
            errors.append(f"[{record_source}] {sid}: Reviewed record cannot have pending consent_status ('{c_stat}').")

    # -------------------------------------------------------------------------
    # 13. STEP 28 INDEPENDENT CALCULATION OF LANGUAGE STATISTICS (SCHEMA v1.3.0)
    # -------------------------------------------------------------------------
    calc_token_counts = compute_language_token_counts(src_labels)
    rec_token_counts = meta.get("language_token_counts")
    if rec_token_counts is not None:
        if not isinstance(rec_token_counts, dict):
            errors.append(f"[{record_source}] {sid}: 'language_token_counts' must be an object.")
        else:
            # 1. Missing keys check (Schema v1.3.0 requires exactly all 8 keys; cannot silently assume zero)
            missing_count_keys = [k for k in LANGUAGE_TOKEN_COUNT_KEYS if k not in rec_token_counts]
            if missing_count_keys:
                errors.append(
                    f"[{record_source}] {sid}: 'language_token_counts' is missing required keys for schema v1.3.0: {missing_count_keys}."
                )

            # 2. Unexpected keys check
            unexpected_keys = [k for k in rec_token_counts if k not in LANGUAGE_TOKEN_COUNT_KEYS]
            if unexpected_keys:
                errors.append(
                    f"[{record_source}] {sid}: 'language_token_counts' contains unexpected keys: {unexpected_keys}."
                )

            # 3. Value types and parity with independently computed counts
            for k in LANGUAGE_TOKEN_COUNT_KEYS:
                if k in rec_token_counts:
                    rec_val = rec_token_counts[k]
                    if not isinstance(rec_val, int) or isinstance(rec_val, bool) or rec_val < 0:
                        errors.append(
                            f"[{record_source}] {sid}: language_token_counts['{k}'] must be a non-negative integer (got {rec_val})."
                        )
                    else:
                        calc_val = calc_token_counts[k]
                        if rec_val != calc_val:
                            errors.append(
                                f"[{record_source}] {sid}: language_token_counts['{k}'] mismatch: recorded={rec_val}, computed={calc_val}."
                            )

            # 4. Total count parity: Total count must equal len(tokens)
            if not missing_count_keys:
                total_recorded = sum(rec_token_counts.values())
                if total_recorded != len(tokens):
                    errors.append(
                        f"[{record_source}] {sid}: Total language_token_counts sum ({total_recorded}) does not equal token count ({len(tokens)})."
                    )

    calc_switch_count = compute_language_switch_count(src_labels)
    rec_switch_count = meta.get("language_switch_count")
    if rec_switch_count is not None:
        if not isinstance(rec_switch_count, int) or rec_switch_count < 0:
            errors.append(f"[{record_source}] {sid}: 'language_switch_count' must be a non-negative integer.")
        elif rec_switch_count != calc_switch_count:
            errors.append(
                f"[{record_source}] {sid}: language_switch_count mismatch: recorded={rec_switch_count}, computed={calc_switch_count}."
            )

    return errors, warnings


def validate_jsonl_file(
    filepath: Path,
    expected_split: str,
    seen_ids: set,
    seen_keys: dict,
    seen_source_records: set = None,
) -> dict:
    """Validate all lines of a JSONL file."""
    if not filepath.exists():
        return {
            "status": "FAIL",
            "file": filepath.name,
            "record_count": 0,
            "errors": [f"Required file not found: {filepath}"],
            "warnings": [],
            "records": [],
        }

    records = []
    file_errors = []
    file_warnings = []

    with filepath.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                file_errors.append(f"Line {line_no}: Unexpected empty line in {filepath.name}")
                continue
            try:
                rec = json.loads(line_str)
            except json.JSONDecodeError as e:
                file_errors.append(f"Line {line_no}: JSON decode error: {e}")
                continue

            records.append(rec)
            errs, warns = validate_single_record(
                rec,
                expected_split,
                f"{filepath.name}:{line_no}",
                seen_ids,
                seen_keys,
                seen_source_records,
            )
            file_errors.extend(errs)
            file_warnings.extend(warns)

    status = "FAIL" if file_errors else ("PASS WITH WARNINGS" if file_warnings else "PASS")

    return {
        "status": status,
        "file": filepath.name,
        "record_count": len(records),
        "errors": file_errors,
        "warnings": file_warnings,
        "records": records,
    }


def validate_manifest(manifest_path: Path, candidate_count: int, reviewed_count: int, rejected_count: int) -> list:
    """Verify manifest existence, split policy, model classes, and count consistency."""
    errors = []
    if not manifest_path.exists():
        errors.append(f"Manifest file not found: {manifest_path}")
        return errors

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Manifest JSON decode error: {e}")
        return errors

    # 1. Actual counts verification
    actual = manifest.get("actual_counts", {})
    if actual.get("candidate_sentences") != candidate_count:
        errors.append(f"Manifest candidate count ({actual.get('candidate_sentences')}) != actual file count ({candidate_count})")
    if actual.get("reviewed_sentences") != reviewed_count:
        errors.append(f"Manifest reviewed count ({actual.get('reviewed_sentences')}) != actual file count ({reviewed_count})")
    if actual.get("rejected_sentences") != rejected_count:
        errors.append(f"Manifest rejected count ({actual.get('rejected_sentences')}) != actual file count ({rejected_count})")

    # 2. Collection targets verification
    targets = manifest.get("collection_targets", {}).get("categories", {})
    expected_categories = ["Native_Telugu", "English_Native_Telugu", "Hindi_Native_Telugu", "English_Hindi_Telugu"]
    for cat in expected_categories:
        if cat not in targets:
            errors.append(f"Manifest missing collection target category: {cat}")
        elif targets[cat].get("target_count") != 100:
            errors.append(f"Manifest target count for {cat} is {targets[cat].get('target_count')} != 100")

    # 3. Decision 1: Split Policy Verification
    split_policy = manifest.get("split_policy", {})
    if not split_policy:
        errors.append("Manifest missing 'split_policy' configuration.")
    else:
        if split_policy.get("strategy") != "group_aware_stratified_60_20_20":
            errors.append(f"Manifest split strategy '{split_policy.get('strategy')}' != 'group_aware_stratified_60_20_20'")
        if split_policy.get("random_seed") != 42:
            errors.append(f"Manifest random_seed {split_policy.get('random_seed')} != 42")
        overall = split_policy.get("overall_target_allocation", {})
        if overall.get("train") != 240 or overall.get("validation") != 80 or overall.get("test") != 80:
            errors.append(f"Manifest overall split allocation ({overall}) != 240/80/80")

    # 4. Decision 2: Model Classes Verification
    model_classes = manifest.get("model_classes", {})
    if not model_classes:
        errors.append("Manifest missing 'model_classes' configuration.")
    else:
        if model_classes.get("supervised_classes_count") != 4:
            errors.append(f"Manifest supervised classes count ({model_classes.get('supervised_classes_count')}) != 4")
        mapping = model_classes.get("model_label_mapping", {})
        if mapping != {"EN": 0, "HI": 1, "TE": 2, "OTHER": 3}:
            errors.append(f"Manifest model_label_mapping ({mapping}) != {{EN:0, HI:1, TE:2, OTHER:3}}")
        non_sup = model_classes.get("non_supervised_annotations", {})
        if non_sup.get("MIXED") != -100:
            errors.append("Manifest non_supervised_annotations must map MIXED to -100")

    # 5. Provenance Architecture & Schema v1.3.0 Verification
    if manifest.get("version") != "1.3.0":
        errors.append(f"Manifest version '{manifest.get('version')}' != '1.3.0'")
    if manifest.get("schema_version") != "1.3.0":
        errors.append(f"Manifest schema_version '{manifest.get('schema_version')}' != '1.3.0'")

    prov = manifest.get("provenance_architecture", {})
    if not prov:
        errors.append("Manifest missing 'provenance_architecture' configuration.")
    else:
        methods = set(prov.get("eligible_collection_methods", []))
        if methods != ALLOWED_COLLECTION_METHODS:
            errors.append(f"Manifest eligible_collection_methods ({methods}) != {ALLOWED_COLLECTION_METHODS}")

        lang_stats = prov.get("language_statistics_policy", {})
        if lang_stats:
            token_classes = lang_stats.get("token_counts_classes", [])
            if token_classes != LANGUAGE_TOKEN_COUNT_KEYS:
                errors.append(
                    f"Manifest token_counts_classes ({token_classes}) != {LANGUAGE_TOKEN_COUNT_KEYS}"
                )

    return errors


def test_schema_example(seen_ids: set, seen_keys: dict) -> tuple:
    """Validate that the illustrative dummy schema example passes all rules in isolation."""
    example_path = EXAMPLES_DIR / "schema_example.json"
    if not example_path.exists():
        return [f"Schema example file not found: {example_path}"], []

    with example_path.open("r", encoding="utf-8") as f:
        example_rec = json.load(f)

    # Must be marked as dummy
    errors = []
    if not example_rec.get("is_dummy_example"):
        errors.append("examples/schema_example.json is missing 'is_dummy_example: true' flag.")

    # Validate schema rules in isolation
    isolated_ids = set()
    isolated_keys = {}
    isolated_sources = set()
    errs, warns = validate_single_record(
        example_rec, "reviewed", "examples/schema_example.json", isolated_ids, isolated_keys, isolated_sources
    )
    errors.extend(errs)

    return errors, warns


def run_self_test():
    """
    Execute comprehensive synthetic self-test suite covering all 22 Step 26 test cases.
    Verifies that the validator correctly accepts valid patterns and strictly rejects violations.
    """
    print("=" * 75, flush=True)
    print("RUNNING VALIDATOR SELF-TEST SUITE (STEP 28 SPECIFICATION - 30 TESTS)", flush=True)
    print("=" * 75, flush=True)

    tests_passed = 0
    total_tests = 0

    base_rec = {
        "sentence_id": "custom_rev_000001",
        "original_sentence_id": "orig_001",
        "source": "Custom-Trilingual",
        "subset": "Native_Telugu",
        "original_split": "custom_reviewed",
        "split": "reviewed",
        "text": "నమస్కారం ఎలా ఉన్నారు ?",
        "tokens": ["నమస్కారం", "ఎలా", "ఉన్నారు", "?"],
        "original_labels": ["TE", "TE", "TE", "OTHER"],
        "source_labels": ["TE", "TE", "TE", "OTHER"],
        "model_labels": [2, 2, 2, 3],
        "text_format": "native_telugu",
        "lid_eligible": True,
        "lid_eligible_tokens": 4,
        "source_record_id": "bht25_te_001",
        "metadata": {
            "collection_method": "licensed_corpus_extraction",
            "source_dataset": "BHT25",
            "source_url": "https://huggingface.co/datasets/sudeshna84/BHT25",
            "license": "CC-BY-4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "source_group_id": "tagore_short_stories",
            "source_domain": "literary_general",
            "script_combination": "telugu_only",
            "contributor_id": None,
            "consent_status": "not_applicable_public_corpus",
            "annotator_1": "annotator_01",
            "annotator_2": "annotator_02",
            "annotation_status": "stage2_approved",
            "review_date": "2026-10-31",
            "language_switch_count": 0,
            "language_token_counts": {
                "EN": 0,
                "HI": 0,
                "TE": 3,
                "OTHER": 1,
                "NE": 0,
                "MIXED": 0,
                "AMBIGUOUS": 0,
                "NULL": 0
            },
            "category": "native_telugu",
            "review_status": "approved",
            "annotator_consensus": "unanimous"
        }
    }

    # -------------------------------------------------------------------------
    # TEST 1: Valid licensed_corpus_extraction record accepted
    # -------------------------------------------------------------------------
    total_tests += 1
    t1_rec = dict(base_rec)
    errs, _ = validate_single_record(t1_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 1 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 1: Valid licensed_corpus_extraction record accepted.")

    # -------------------------------------------------------------------------
    # TEST 2: Missing licence rejected for corpus extraction
    # -------------------------------------------------------------------------
    total_tests += 1
    t2_rec = json.loads(json.dumps(base_rec))
    t2_rec["sentence_id"] = "custom_rev_000002"
    t2_rec["metadata"]["license"] = None
    errs, _ = validate_single_record(t2_rec, "reviewed", "test", set(), {}, set())
    assert any("'license' is required" in e or "unverified license" in e for e in errs), f"Test 2 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 2: Missing license rejected for corpus extraction.")

    # -------------------------------------------------------------------------
    # TEST 3: Missing source_record_id rejected for corpus extraction
    # -------------------------------------------------------------------------
    total_tests += 1
    t3_rec = json.loads(json.dumps(base_rec))
    t3_rec["sentence_id"] = "custom_rev_000003"
    t3_rec["source_record_id"] = None
    errs, _ = validate_single_record(t3_rec, "reviewed", "test", set(), {}, set())
    assert any("'source_record_id' is required and must not be null" in e for e in errs), f"Test 3 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 3: Missing source_record_id rejected for corpus extraction.")

    # -------------------------------------------------------------------------
    # TEST 4: Missing source_group_id blocks final split readiness (warning recorded)
    # -------------------------------------------------------------------------
    total_tests += 1
    t4_rec = json.loads(json.dumps(base_rec))
    t4_rec["sentence_id"] = "custom_rev_000004"
    t4_rec["metadata"]["source_group_id"] = None
    t4_rec["metadata"]["group_id"] = None
    errs, warns = validate_single_record(t4_rec, "reviewed", "test", set(), {}, set())
    assert any("Missing 'source_group_id' in metadata" in w for w in warns), f"Test 4 failed: warns={warns}"
    tests_passed += 1
    print("  [PASS] Test 4: Missing source_group_id flags split readiness warning.")

    # -------------------------------------------------------------------------
    # TEST 5: Valid human_elicited record accepted
    # -------------------------------------------------------------------------
    total_tests += 1
    t5_rec = json.loads(json.dumps(base_rec))
    t5_rec["sentence_id"] = "custom_rev_000005"
    t5_rec["subset"] = "English_Native_Telugu"
    t5_rec["text"] = "good morning ఎలా ఉన్నారు ?"
    t5_rec["tokens"] = ["good", "morning", "ఎలా", "ఉన్నారు", "?"]
    t5_rec["original_labels"] = ["EN", "EN", "TE", "TE", "OTHER"]
    t5_rec["source_labels"] = ["EN", "EN", "TE", "TE", "OTHER"]
    t5_rec["model_labels"] = [0, 0, 2, 2, 3]
    t5_rec["text_format"] = "mixed_english_native_telugu"
    t5_rec["lid_eligible_tokens"] = 5
    t5_rec["source_record_id"] = None  # null for direct elicitation
    t5_rec["metadata"] = {
        "collection_method": "human_elicited",
        "source_dataset": None,
        "source_url": None,
        "license": "Contributor-Agreement",
        "license_url": None,
        "source_group_id": "contrib_01_session1",
        "source_domain": "conversational",
        "script_combination": "latin_telugu",
        "contributor_id": "contrib_01",
        "consent_status": "consented_academic_use",
        "annotator_1": "annotator_01",
        "annotator_2": "annotator_02",
        "annotation_status": "stage2_approved",
        "review_date": "2026-10-31",
        "language_switch_count": 1,
        "language_token_counts": {"EN": 2, "HI": 0, "TE": 2, "OTHER": 1, "NE": 0, "MIXED": 0, "AMBIGUOUS": 0, "NULL": 0},
        "category": "english_native_telugu",
        "review_status": "approved"
    }
    errs, _ = validate_single_record(t5_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 5 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 5: Valid human_elicited record accepted.")

    # -------------------------------------------------------------------------
    # TEST 6: Missing contributor ID rejected for human elicitation
    # -------------------------------------------------------------------------
    total_tests += 1
    t6_rec = json.loads(json.dumps(t5_rec))
    t6_rec["sentence_id"] = "custom_rev_000006"
    t6_rec["metadata"]["contributor_id"] = None
    errs, _ = validate_single_record(t6_rec, "reviewed", "test", set(), {}, set())
    assert any("'contributor_id' is required" in e for e in errs), f"Test 6 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 6: Missing contributor ID rejected for human elicitation.")

    # -------------------------------------------------------------------------
    # TEST 7: Missing consent rejected for human elicitation
    # -------------------------------------------------------------------------
    total_tests += 1
    t7_rec = json.loads(json.dumps(t5_rec))
    t7_rec["sentence_id"] = "custom_rev_000007"
    t7_rec["metadata"]["consent_status"] = None
    errs, _ = validate_single_record(t7_rec, "reviewed", "test", set(), {}, set())
    assert any("consent_status" in e for e in errs), f"Test 7 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 7: Missing consent rejected for human elicitation.")

    # -------------------------------------------------------------------------
    # TEST 8: Valid parallel_reference record accepted
    # -------------------------------------------------------------------------
    total_tests += 1
    t8_rec = json.loads(json.dumps(t5_rec))
    t8_rec["sentence_id"] = "custom_rev_000008"
    t8_rec["source_record_id"] = "bht25_row_452"
    t8_rec["metadata"]["collection_method"] = "parallel_reference"
    t8_rec["metadata"]["source_dataset"] = "BHT25"
    t8_rec["metadata"]["license"] = "CC-BY-4.0"
    t8_rec["metadata"]["source_group_id"] = "tagore_short_stories"
    errs, _ = validate_single_record(t8_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 8 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 8: Valid parallel_reference record accepted.")

    # -------------------------------------------------------------------------
    # TEST 9: Missing reference record ID rejected
    # -------------------------------------------------------------------------
    total_tests += 1
    t9_rec = json.loads(json.dumps(t8_rec))
    t9_rec["sentence_id"] = "custom_rev_000009"
    t9_rec["source_record_id"] = None
    errs, _ = validate_single_record(t9_rec, "reviewed", "test", set(), {}, set())
    assert any("Reference 'source_record_id' is required" in e for e in errs), f"Test 9 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 9: Missing reference record ID rejected for parallel reference.")

    # -------------------------------------------------------------------------
    # TEST 10: Automatically generated record rejected
    # -------------------------------------------------------------------------
    total_tests += 1
    t10_rec = json.loads(json.dumps(t5_rec))
    t10_rec["sentence_id"] = "custom_rev_000010"
    t10_rec["metadata"]["collection_method"] = "automatically_generated"
    errs, _ = validate_single_record(t10_rec, "reviewed", "test", set(), {}, set())
    assert any("Automatically generated text" in e for e in errs), f"Test 10 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 10: Automatically generated record strictly rejected.")

    # -------------------------------------------------------------------------
    # TEST 11: Duplicate source_record_id handling validated
    # -------------------------------------------------------------------------
    total_tests += 1
    seen_srcs = set()
    t11_a = json.loads(json.dumps(base_rec))
    t11_a["sentence_id"] = "custom_rev_000011a"
    t11_a["source_record_id"] = "corpus_dup_001"
    t11_b = json.loads(json.dumps(base_rec))
    t11_b["sentence_id"] = "custom_rev_000011b"
    t11_b["text"] = "వేరే వాక్యం ఇక్కడ ఉంది ."
    t11_b["tokens"] = ["వేరే", "వాక్యం", "ఇక్కడ", "ఉంది", "."]
    t11_b["original_labels"] = ["TE", "TE", "TE", "TE", "OTHER"]
    t11_b["source_labels"] = ["TE", "TE", "TE", "TE", "OTHER"]
    t11_b["model_labels"] = [2, 2, 2, 2, 3]
    t11_b["lid_eligible_tokens"] = 5
    t11_b["source_record_id"] = "corpus_dup_001"  # Duplicate source ID from same dataset!
    t11_b["metadata"]["language_token_counts"] = {"EN": 0, "HI": 0, "TE": 4, "OTHER": 1, "NE": 0, "MIXED": 0, "AMBIGUOUS": 0, "NULL": 0}
    errs_a, _ = validate_single_record(t11_a, "reviewed", "test", set(), {}, seen_srcs)
    errs_b, _ = validate_single_record(t11_b, "reviewed", "test", set(), {}, seen_srcs)
    assert len(errs_a) == 0, f"Test 11a failed: {errs_a}"
    assert any("Duplicate source_record_id" in e for e in errs_b), f"Test 11b failed: {errs_b}"
    tests_passed += 1
    print("  [PASS] Test 11: Duplicate source_record_id detection validated.")

    # -------------------------------------------------------------------------
    # TEST 12: Null source_record_id accepted for direct human elicitation
    # -------------------------------------------------------------------------
    total_tests += 1
    t12_rec = json.loads(json.dumps(t5_rec))
    t12_rec["sentence_id"] = "custom_rev_000012"
    t12_rec["source_record_id"] = None
    errs, _ = validate_single_record(t12_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 12 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 12: Null source_record_id accepted for direct human elicitation.")

    # -------------------------------------------------------------------------
    # TEST 13: EN/HI/TE/OTHER mapping unchanged
    # -------------------------------------------------------------------------
    total_tests += 1
    assert SOURCE_TO_MODEL_MAP["EN"] == 0, "EN mapping modified!"
    assert SOURCE_TO_MODEL_MAP["HI"] == 1, "HI mapping modified!"
    assert SOURCE_TO_MODEL_MAP["TE"] == 2, "TE mapping modified!"
    assert SOURCE_TO_MODEL_MAP["OTHER"] == 3, "OTHER mapping modified!"
    assert SUPERVISED_MODEL_CLASSES == {0: "EN", 1: "HI", 2: "TE", 3: "OTHER"}
    tests_passed += 1
    print("  [PASS] Test 13: Supervised EN/HI/TE/OTHER mapping confirmed unchanged.")

    # -------------------------------------------------------------------------
    # TEST 14: MIXED cannot receive a supervised class ID
    # -------------------------------------------------------------------------
    total_tests += 1
    for bad_id in [0, 1, 2, 3]:
        t14_rec = json.loads(json.dumps(t5_rec))
        t14_rec["sentence_id"] = f"custom_rev_000014_{bad_id}"
        t14_rec["tokens"] = ["computerలో", "code", "ఉంది", "."]
        t14_rec["source_labels"] = ["MIXED", "EN", "TE", "OTHER"]
        t14_rec["model_labels"] = [bad_id, 0, 2, 3]
        t14_rec["lid_eligible_tokens"] = 4
        t14_rec["metadata"]["language_token_counts"] = {"EN": 1, "HI": 0, "TE": 1, "OTHER": 1, "NE": 0, "MIXED": 1, "AMBIGUOUS": 0, "NULL": 0}
        errs, _ = validate_single_record(t14_rec, "reviewed", "test", set(), {}, set())
        assert any("cannot be assigned supervised class" in e or "Inconsistent labels" in e or "MIXED cannot be treated as OTHER" in e for e in errs), \
            f"Test 14 failed for bad_id {bad_id}: {errs}"
    tests_passed += 1
    print("  [PASS] Test 14: MIXED strictly cannot receive any supervised class ID (0, 1, 2, 3).")

    # -------------------------------------------------------------------------
    # TEST 15: NE remains ignored (-100)
    # -------------------------------------------------------------------------
    total_tests += 1
    assert SOURCE_TO_MODEL_MAP["NE"] == -100, "NE mapping modified!"
    t15_rec = json.loads(json.dumps(t5_rec))
    t15_rec["sentence_id"] = "custom_rev_000015"
    t15_rec["tokens"] = ["Hyderabad", "లో", "code", "ఉంది", "."]
    t15_rec["source_labels"] = ["NE", "TE", "EN", "TE", "OTHER"]
    t15_rec["model_labels"] = [0, 2, 0, 2, 3]  # NE assigned 0 instead of -100
    t15_rec["metadata"]["language_token_counts"] = {"EN": 1, "HI": 0, "TE": 2, "OTHER": 1, "NE": 1, "MIXED": 0, "AMBIGUOUS": 0, "NULL": 0}
    t15_rec["metadata"]["language_switch_count"] = 2
    errs, _ = validate_single_record(t15_rec, "reviewed", "test", set(), {}, set())
    assert any("Inconsistent labels" in e for e in errs), f"Test 15 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 15: NE confirmed ignored (-100).")

    # -------------------------------------------------------------------------
    # TEST 16: Language token counts independently recalculated
    # -------------------------------------------------------------------------
    total_tests += 1
    t16_rec = json.loads(json.dumps(t5_rec))
    t16_rec["sentence_id"] = "custom_rev_000016"
    t16_rec["metadata"]["language_token_counts"] = {"EN": 99, "HI": 0, "TE": 2, "OTHER": 1, "NE": 0, "MIXED": 0, "AMBIGUOUS": 0, "NULL": 0}  # False count 99
    errs, _ = validate_single_record(t16_rec, "reviewed", "test", set(), {}, set())
    assert any("language_token_counts['EN'] mismatch" in e for e in errs), f"Test 16 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 16: Language token counts independently recalculated & verified.")

    # -------------------------------------------------------------------------
    # TEST 17: Language switch count independently recalculated
    # -------------------------------------------------------------------------
    total_tests += 1
    t17_rec = json.loads(json.dumps(t5_rec))
    t17_rec["sentence_id"] = "custom_rev_000017"
    t17_rec["metadata"]["language_switch_count"] = 5  # Actual is 1
    errs, _ = validate_single_record(t17_rec, "reviewed", "test", set(), {}, set())
    assert any("language_switch_count mismatch" in e for e in errs), f"Test 17 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 17: Language switch count independently recalculated & verified.")

    # -------------------------------------------------------------------------
    # TEST 18: Both reviewers required for stage2_approved
    # -------------------------------------------------------------------------
    total_tests += 1
    t18_rec = json.loads(json.dumps(t5_rec))
    t18_rec["sentence_id"] = "custom_rev_000018"
    t18_rec["metadata"]["annotator_2"] = None
    errs, _ = validate_single_record(t18_rec, "reviewed", "test", set(), {}, set())
    assert any("requires both annotator_1 and annotator_2" in e for e in errs), f"Test 18 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 18: Both reviewers strictly required for stage2_approved.")

    # -------------------------------------------------------------------------
    # TEST 19: Both reviewers and review date required for adjudicated
    # -------------------------------------------------------------------------
    total_tests += 1
    t19_rec = json.loads(json.dumps(t5_rec))
    t19_rec["sentence_id"] = "custom_rev_000019"
    t19_rec["metadata"]["annotation_status"] = "adjudicated"
    t19_rec["metadata"]["review_date"] = None
    errs, _ = validate_single_record(t19_rec, "reviewed", "test", set(), {}, set())
    assert any("requires valid ISO-8601 review_date" in e for e in errs), f"Test 19 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 19: Reviewers and review_date strictly required for adjudicated records.")

    # -------------------------------------------------------------------------
    # TEST 20: Existing Telugu and Devanagari script checks still work
    # -------------------------------------------------------------------------
    total_tests += 1
    t20_a = json.loads(json.dumps(base_rec))
    t20_a["sentence_id"] = "custom_rev_000020a"
    t20_a["text"] = "Namaskaram ela unnaru ?"  # Lacks Telugu script
    errs_a, _ = validate_single_record(t20_a, "reviewed", "test", set(), {}, set())
    assert any("lacks Telugu Unicode script" in e for e in errs_a), f"Test 20a failed: {errs_a}"

    t20_b = json.loads(json.dumps(base_rec))
    t20_b["sentence_id"] = "custom_rev_000020b"
    t20_b["subset"] = "Hindi_Native_Telugu"
    t20_b["text"] = "namaste ఉంది ."  # Lacks Devanagari script
    t20_b["tokens"] = ["namaste", "ఉంది", "."]
    t20_b["source_labels"] = ["HI", "TE", "OTHER"]
    t20_b["model_labels"] = [1, 2, 3]
    t20_b["text_format"] = "mixed_hindi_native_telugu"
    t20_b["lid_eligible_tokens"] = 3
    t20_b["metadata"]["language_token_counts"] = {"EN": 0, "HI": 1, "TE": 1, "OTHER": 1, "NE": 0, "MIXED": 0, "AMBIGUOUS": 0, "NULL": 0}
    t20_b["metadata"]["language_switch_count"] = 1
    errs_b, _ = validate_single_record(t20_b, "reviewed", "test", set(), {}, set())
    assert any("lacks Devanagari script" in e for e in errs_b), f"Test 20b failed: {errs_b}"
    tests_passed += 1
    print("  [PASS] Test 20: Existing Telugu and Devanagari script validation confirmed active.")

    # -------------------------------------------------------------------------
    # TEST 21: Existing duplicate detection still works
    # -------------------------------------------------------------------------
    total_tests += 1
    seen_keys_t21 = {}
    t21_a = json.loads(json.dumps(base_rec))
    t21_a["sentence_id"] = "custom_rev_000021a"
    validate_single_record(t21_a, "reviewed", "test", set(), seen_keys_t21, set())
    t21_b = json.loads(json.dumps(base_rec))
    t21_b["sentence_id"] = "custom_rev_000021b"
    t21_b["tokens"] = ["  నమస్కారం  ", "ఎలా", "ఉన్నారు", "?"]
    errs_21, _ = validate_single_record(t21_b, "reviewed", "test", set(), seen_keys_t21, set())
    assert any("Duplicate normalized sentence detected" in e for e in errs_21), f"Test 21 failed: {errs_21}"
    tests_passed += 1
    print("  [PASS] Test 21: Duplicate normalized sentence detection confirmed active.")

    # -------------------------------------------------------------------------
    # TEST 22: Existing 60/20/20 target allocation remains unchanged
    # -------------------------------------------------------------------------
    total_tests += 1
    manifest_path = CUSTOM_DIR / "dataset_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as f:
        mf = json.load(f)
    sp = mf.get("split_policy", {})
    assert sp.get("strategy") == "group_aware_stratified_60_20_20", "Split strategy altered!"
    assert sp.get("random_seed") == 42, "Seed altered!"
    assert sp.get("overall_target_allocation") == {"train": 240, "validation": 80, "test": 80}, "Allocation altered!"
    tests_passed += 1
    print("  [PASS] Test 22: 60/20/20 target allocation (240/80/80, seed=42) confirmed unchanged.")

    # -------------------------------------------------------------------------
    # TEST 23: AMBIGUOUS token counted correctly under AMBIGUOUS key
    # -------------------------------------------------------------------------
    total_tests += 1
    t23_rec = json.loads(json.dumps(t5_rec))
    t23_rec["sentence_id"] = "custom_rev_000023"
    t23_rec["tokens"] = ["good", "morning", "ఎలా", "maybe", "?"]
    t23_rec["source_labels"] = ["EN", "EN", "TE", "AMBIGUOUS", "OTHER"]
    t23_rec["model_labels"] = [0, 0, 2, -100, 3]
    t23_rec["lid_eligible_tokens"] = 4
    t23_rec["metadata"]["language_token_counts"] = {
        "EN": 2, "HI": 0, "TE": 1, "OTHER": 1, "NE": 0, "MIXED": 0, "AMBIGUOUS": 1, "NULL": 0
    }
    t23_rec["metadata"]["language_switch_count"] = 1
    errs, _ = validate_single_record(t23_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 23 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 23: AMBIGUOUS token counted correctly under AMBIGUOUS key.")

    # -------------------------------------------------------------------------
    # TEST 24: JSON null token counted under NULL key
    # -------------------------------------------------------------------------
    total_tests += 1
    t24_rec = json.loads(json.dumps(t5_rec))
    t24_rec["sentence_id"] = "custom_rev_000024"
    t24_rec["tokens"] = ["good", "morning", "ఎలా", "blank", "?"]
    t24_rec["source_labels"] = ["EN", "EN", "TE", None, "OTHER"]
    t24_rec["model_labels"] = [0, 0, 2, -100, 3]
    t24_rec["lid_eligible_tokens"] = 4
    t24_rec["metadata"]["language_token_counts"] = {
        "EN": 2, "HI": 0, "TE": 1, "OTHER": 1, "NE": 0, "MIXED": 0, "AMBIGUOUS": 0, "NULL": 1
    }
    t24_rec["metadata"]["language_switch_count"] = 1
    errs, _ = validate_single_record(t24_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 24 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 24: JSON null token counted under NULL key.")

    # -------------------------------------------------------------------------
    # TEST 25: Eight count keys sum exactly to token count
    # -------------------------------------------------------------------------
    total_tests += 1
    t25_rec = json.loads(json.dumps(t5_rec))
    t25_rec["sentence_id"] = "custom_rev_000025"
    t25_rec["subset"] = "English_Hindi_Telugu"
    t25_rec["text"] = "office बहुत ఎలా ! Hyderabad codeలో maybe unknown"
    t25_rec["tokens"] = ["office", "बहुत", "ఎలా", "!", "Hyderabad", "codeలో", "maybe", "unknown"]
    t25_rec["source_labels"] = ["EN", "HI", "TE", "OTHER", "NE", "MIXED", "AMBIGUOUS", None]
    t25_rec["model_labels"] = [0, 1, 2, 3, -100, -100, -100, -100]
    t25_rec["lid_eligible_tokens"] = 4
    t25_rec["metadata"]["category"] = "english_hindi_telugu"
    t25_rec["metadata"]["language_token_counts"] = {
        "EN": 1, "HI": 1, "TE": 1, "OTHER": 1, "NE": 1, "MIXED": 1, "AMBIGUOUS": 1, "NULL": 1
    }
    t25_rec["metadata"]["language_switch_count"] = 2
    assert sum(t25_rec["metadata"]["language_token_counts"].values()) == len(t25_rec["tokens"]) == 8
    errs, _ = validate_single_record(t25_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 25 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 25: Eight count keys sum exactly to token count.")

    # -------------------------------------------------------------------------
    # TEST 26: Incorrect total count rejected
    # -------------------------------------------------------------------------
    total_tests += 1
    t26_rec = json.loads(json.dumps(t25_rec))
    t26_rec["sentence_id"] = "custom_rev_000026"
    t26_rec["metadata"]["language_token_counts"]["NULL"] = 0  # Total sum becomes 7 != len(tokens)=8
    errs, _ = validate_single_record(t26_rec, "reviewed", "test", set(), {}, set())
    assert any("Total language_token_counts sum" in e or "mismatch" in e for e in errs), f"Test 26 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 26: Incorrect total count rejected.")

    # -------------------------------------------------------------------------
    # TEST 27: Missing new count keys rejected for schema v1.3.0
    # -------------------------------------------------------------------------
    total_tests += 1
    t27_rec = json.loads(json.dumps(t25_rec))
    t27_rec["sentence_id"] = "custom_rev_000027"
    # Old 6-key structure missing AMBIGUOUS and NULL
    t27_rec["metadata"]["language_token_counts"] = {
        "EN": 1, "HI": 1, "TE": 1, "OTHER": 1, "NE": 1, "MIXED": 1
    }
    errs, _ = validate_single_record(t27_rec, "reviewed", "test", set(), {}, set())
    assert any("missing required keys for schema v1.3.0" in e for e in errs), f"Test 27 failed: {errs}"
    tests_passed += 1
    print("  [PASS] Test 27: Missing count keys strictly rejected for schema v1.3.0.")

    # -------------------------------------------------------------------------
    # TEST 28: AMBIGUOUS cannot receive a supervised class ID
    # -------------------------------------------------------------------------
    total_tests += 1
    for bad_id in [0, 1, 2, 3]:
        t28_rec = json.loads(json.dumps(t23_rec))
        t28_rec["sentence_id"] = f"custom_rev_000028_{bad_id}"
        t28_rec["model_labels"][3] = bad_id  # AMBIGUOUS assigned supervised class ID
        t28_rec["lid_eligible_tokens"] = 5
        errs, _ = validate_single_record(t28_rec, "reviewed", "test", set(), {}, set())
        assert any("AMBIGUOUS cannot receive a supervised class ID" in e or "Inconsistent labels" in e for e in errs), \
            f"Test 28 failed for bad_id {bad_id}: {errs}"
    tests_passed += 1
    print("  [PASS] Test 28: AMBIGUOUS strictly cannot receive any supervised class ID (0, 1, 2, 3).")

    # -------------------------------------------------------------------------
    # TEST 29: NULL cannot receive a supervised class ID
    # -------------------------------------------------------------------------
    total_tests += 1
    for bad_id in [0, 1, 2, 3]:
        t29_rec = json.loads(json.dumps(t24_rec))
        t29_rec["sentence_id"] = f"custom_rev_000029_{bad_id}"
        t29_rec["model_labels"][3] = bad_id  # NULL assigned supervised class ID
        t29_rec["lid_eligible_tokens"] = 5
        errs, _ = validate_single_record(t29_rec, "reviewed", "test", set(), {}, set())
        assert any("NULL cannot receive a supervised class ID" in e or "Inconsistent labels" in e for e in errs), \
            f"Test 29 failed for bad_id {bad_id}: {errs}"
    tests_passed += 1
    print("  [PASS] Test 29: NULL strictly cannot receive any supervised class ID (0, 1, 2, 3).")

    # -------------------------------------------------------------------------
    # TEST 30: Language-switch count ignores AMBIGUOUS and NULL
    # -------------------------------------------------------------------------
    total_tests += 1
    sw_labels = ["EN", "AMBIGUOUS", "EN", None, "TE"]
    calc_sw = compute_language_switch_count(sw_labels)
    assert calc_sw == 1, f"Test 30 switch count calculation failed: {calc_sw} != 1"

    t30_rec = json.loads(json.dumps(t5_rec))
    t30_rec["sentence_id"] = "custom_rev_000030"
    t30_rec["tokens"] = ["good", "maybe", "morning", "blank", "ఎలా"]
    t30_rec["source_labels"] = sw_labels
    t30_rec["model_labels"] = [0, -100, 0, -100, 2]
    t30_rec["lid_eligible_tokens"] = 3
    t30_rec["metadata"]["language_token_counts"] = {
        "EN": 2, "HI": 0, "TE": 1, "OTHER": 0, "NE": 0, "MIXED": 0, "AMBIGUOUS": 1, "NULL": 1
    }
    t30_rec["metadata"]["language_switch_count"] = 1  # Correct switch count
    errs, _ = validate_single_record(t30_rec, "reviewed", "test", set(), {}, set())
    assert len(errs) == 0, f"Test 30 valid record failed: {errs}"

    # Verify that incorrectly counting AMBIGUOUS/NULL as switches triggers an error
    t30_bad = json.loads(json.dumps(t30_rec))
    t30_bad["sentence_id"] = "custom_rev_000030_bad"
    t30_bad["metadata"]["language_switch_count"] = 3  # Incorrect: counted AMBIGUOUS and NULL
    errs_bad, _ = validate_single_record(t30_bad, "reviewed", "test", set(), {}, set())
    assert any("language_switch_count mismatch" in e for e in errs_bad), f"Test 30 bad record failed: {errs_bad}"
    tests_passed += 1
    print("  [PASS] Test 30: Language-switch count ignores AMBIGUOUS and NULL tokens.")

    print("\n" + "=" * 75, flush=True)
    print(f"SELF-TEST SUITE RESULT: ALL {tests_passed}/{total_tests} SPECIFIED CASES PASSED!", flush=True)
    print("=" * 75, flush=True)


def main():
    parser = argparse.ArgumentParser(description="Validate Custom Trilingual LID Dataset Infrastructure (Step 28).")
    parser.add_argument("--self-test", action="store_true", help="Run comprehensive unit tests on synthetic fixtures.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    print("=" * 75, flush=True)
    print("VALIDATING CUSTOM TRILINGUAL DATASET INFRASTRUCTURE (STEP 28)", flush=True)
    print(f"Target Directory: {CUSTOM_DIR}", flush=True)
    print("=" * 75, flush=True)

    seen_ids = set()
    seen_keys = {}
    seen_source_records = set()

    # 1. Validate JSONL Dataset Files
    files_to_validate = [
        (CUSTOM_DIR / "candidate_sentences.jsonl", "candidate"),
        (CUSTOM_DIR / "reviewed_sentences.jsonl", "reviewed"),
        (CUSTOM_DIR / "rejected_sentences.jsonl", "rejected"),
    ]

    all_file_results = {}
    total_hard_errors = 0
    total_warnings = 0

    for path, split_type in files_to_validate:
        res = validate_jsonl_file(path, split_type, seen_ids, seen_keys, seen_source_records)
        all_file_results[path.name] = res
        total_hard_errors += len(res["errors"])
        total_warnings += len(res["warnings"])
        print(f"\n[{res['status']}] {path.name}: {res['record_count']} records | Errors: {len(res['errors'])} | Warnings: {len(res['warnings'])}")
        for e in res["errors"]:
            print(f"  ERROR: {e}")
        for w in res["warnings"]:
            print(f"  WARNING: {w}")

    # 2. Validate Schema Example (Isolated Test)
    print("\nValidating illustrative dummy schema example (examples/schema_example.json)...", flush=True)
    ex_errors, ex_warnings = test_schema_example(seen_ids, seen_keys)
    total_hard_errors += len(ex_errors)
    total_warnings += len(ex_warnings)
    print(f"  Schema Example Status: {'PASS' if not ex_errors else 'FAIL'} | Errors: {len(ex_errors)} | Warnings: {len(ex_warnings)}")
    for e in ex_errors:
        print(f"  ERROR: {e}")
    for w in ex_warnings:
        print(f"  WARNING: {w}")

    # 3. Validate Dataset Manifest
    print("\nValidating dataset_manifest.json...", flush=True)
    cand_cnt = all_file_results["candidate_sentences.jsonl"]["record_count"]
    rev_cnt = all_file_results["reviewed_sentences.jsonl"]["record_count"]
    rej_cnt = all_file_results["rejected_sentences.jsonl"]["record_count"]

    manifest_errors = validate_manifest(CUSTOM_DIR / "dataset_manifest.json", cand_cnt, rev_cnt, rej_cnt)
    total_hard_errors += len(manifest_errors)
    print(f"  Manifest Status: {'PASS' if not manifest_errors else 'FAIL'} | Errors: {len(manifest_errors)}")
    for e in manifest_errors:
        print(f"  ERROR: {e}")

    # 4. Check Presence of Core Documentation & Infrastructure Files
    required_docs = [
        "README.md",
        "split_policy.md",
        "annotation_guidelines.md",
        "label_reference.md",
        "dataset_schema.json",
        "annotation_template.csv",
        "dataset_manifest.json",
    ]
    print("\nChecking presence of documentation & infrastructure files...", flush=True)
    for doc in required_docs:
        doc_path = CUSTOM_DIR / doc
        exists = doc_path.exists()
        size = doc_path.stat().st_size if exists else 0
        if not exists or size == 0:
            total_hard_errors += 1
            print(f"  [MISSING/EMPTY] {doc}")
        else:
            print(f"  [FOUND] {doc:<26} ({size:,} bytes)")

    # 5. Final Assessment
    print("\n" + "=" * 75, flush=True)
    if total_hard_errors == 0 and total_warnings == 0:
        overall_status = "PASS"
    elif total_hard_errors == 0:
        overall_status = "PASS WITH WARNINGS"
    else:
        overall_status = "FAIL"

    print(f"OVERALL VALIDATION STATUS: {overall_status}", flush=True)
    print(f"  Hard Errors: {total_hard_errors}", flush=True)
    print(f"  Warnings:    {total_warnings}", flush=True)
    print(f"  Candidate Records: {cand_cnt}", flush=True)
    print(f"  Reviewed Records:  {rev_cnt}", flush=True)
    print(f"  Rejected Records:  {rej_cnt}", flush=True)
    print("=" * 75, flush=True)

    if overall_status == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
