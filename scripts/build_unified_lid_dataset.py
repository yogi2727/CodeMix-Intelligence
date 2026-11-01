"""
Build the Unified Trilingual Language Identification Dataset for CodeMix Intelligence.

Ingests:
- COMI-LINGUA (comi_lid_train.jsonl, comi_lid_test.jsonl)
- Telugu-English (Blog and Twitter train/test JSONL files)

Applies:
- Common schema mapping with strict label normalization.
- Ineligible sentence exclusion (all-NE sentences).
- Cross-split leakage prevention (removing train records matching any test sentence).
- Duplicate resolution (retaining canonical, quarantining conflicts).
- Deterministic 90/10 train/validation split by unique sentence groups using seed 42.
- Dedicated test split files by domain (COMI-LINGUA, Blog, Twitter) and unified test.
- MuRIL tokenizer sequence length profiling (p50, p90, p95, p99).
- Saves complete dataset manifest with full provenance and accounting.
"""

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from transformers import AutoTokenizer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_DIR = PROJECT_ROOT / "data" / "processed" / "normalized"
COMI_DIR = NORMALIZED_DIR / "comi_lingua"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "language_identification"

RANDOM_SEED = 42
MODEL_ID = "google/muril-base-cased"

INPUT_FILES = [
    ("comi_lid_train", COMI_DIR / "comi_lid_train.jsonl", "COMI-LINGUA", "COMI-LINGUA", "train", "mixed_script_hindi_english"),
    ("comi_lid_test", COMI_DIR / "comi_lid_test.jsonl", "COMI-LINGUA", "COMI-LINGUA", "test", "mixed_script_hindi_english"),
    ("tenglish_blog_train", NORMALIZED_DIR / "tenglish_blog_train.jsonl", "Telugu-English", "Blog", "train", "romanized_telugu_english"),
    ("tenglish_blog_test", NORMALIZED_DIR / "tenglish_blog_test.jsonl", "Telugu-English", "Blog", "test", "romanized_telugu_english"),
    ("tenglish_twitter_train", NORMALIZED_DIR / "tenglish_twitter_train.jsonl", "Telugu-English", "Twitter", "train", "romanized_telugu_english"),
    ("tenglish_twitter_test", NORMALIZED_DIR / "tenglish_twitter_test.jsonl", "Telugu-English", "Twitter", "test", "romanized_telugu_english"),
]

LABEL_TO_ID = {
    "EN": 0,
    "HI": 1,
    "TE": 2,
    "OTHER": 3,
}

IGNORE_LABEL_ID = -100


def normalize_comparison_key(tokens: list) -> str:
    """Documented comparison key: token text, case-folded, stripped."""
    return " ".join(t.strip().casefold() for t in tokens)


def extract_raw_records():
    """Load all records from the six aligned files and extract initial metadata."""
    raw_train = []
    raw_test = []

    for fid, path, source, subset, split, text_format in INPUT_FILES:
        print(f"Loading {fid} from {path.name}...", flush=True)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                rec = json.loads(line)
                tokens = rec["tokens"]
                norm_key = normalize_comparison_key(tokens)

                if source == "Telugu-English":
                    orig_labels = rec["original_labels"]
                    orig_annotators = None
                    src_labels = rec["labels"]
                    model_labels = [IGNORE_LABEL_ID if l == "NE" else LABEL_TO_ID[l] for l in src_labels]
                else:  # COMI-LINGUA
                    orig_annotators = rec["original_labels_by_annotator"]
                    orig_labels = rec["labels"]  # consensus original
                    src_labels = rec["labels"]
                    model_labels = [IGNORE_LABEL_ID if l is None else LABEL_TO_ID[l] for l in src_labels]

                lid_eligible_tokens = sum(1 for m in model_labels if m != IGNORE_LABEL_ID)
                lid_eligible = lid_eligible_tokens > 0

                item = {
                    "source_record_id": f"{fid}_{idx:06d}",
                    "original_sentence_id": rec["sentence_id"],
                    "source": source,
                    "subset": subset,
                    "original_split": split,
                    "text": rec["text"],
                    "tokens": tokens,
                    "original_labels": orig_labels,
                    "original_labels_by_annotator": orig_annotators,
                    "source_labels": src_labels,
                    "model_labels": model_labels,
                    "text_format": text_format,
                    "lid_eligible": lid_eligible,
                    "lid_eligible_tokens": lid_eligible_tokens,
                    "norm_key": norm_key,
                }

                if split == "train":
                    raw_train.append(item)
                else:
                    raw_test.append(item)

    return raw_train, raw_test


def process_test_data(raw_test: list):
    """
    Process test records:
    - Exclude ineligible (all-NE) records.
    - Resolve duplicates: retain canonical when agreeing, quarantine when conflicting.
    """
    print("\nProcessing Test split records...", flush=True)
    excluded = []
    quarantined = []
    eligible_test = []

    for r in raw_test:
        if not r["lid_eligible"]:
            r["exclusion_reason"] = "all_tokens_ignored_ne"
            r["exclusion_details"] = "All tokens have label NE (-100); no target language labels exist in sentence."
            excluded.append(r)
        else:
            eligible_test.append(r)

    # Group eligible by normalized key
    test_groups = defaultdict(list)
    for r in eligible_test:
        test_groups[r["norm_key"]].append(r)

    canonical_test = []

    for nk, items in test_groups.items():
        label_seqs = set(tuple(it["model_labels"]) for it in items)
        if len(label_seqs) > 1:
            for it in items:
                it["quarantine_reason"] = "test_label_conflict"
                it["quarantine_details"] = f"Conflicting label sequences in test duplicate group for key: '{nk[:50]}'"
                quarantined.append(it)
        else:
            canonical_test.append(items[0])
            for it in items[1:]:
                it["quarantine_reason"] = "test_exact_duplicate_deduped"
                it["quarantine_details"] = f"Duplicate identical record in test for key: '{nk[:50]}'"
                quarantined.append(it)

    return canonical_test, excluded, quarantined


def process_train_data(raw_train: list, all_test_keys: set):
    """
    Process training records:
    - Exclude ineligible (all-NE) records.
    - Cross-split leakage prevention: remove training records matching test keys.
    - Resolve duplicates: retain canonical when agreeing, quarantine when conflicting.
    """
    print("\nProcessing Train split records...", flush=True)
    excluded = []
    quarantined = []
    eligible_train = []

    for r in raw_train:
        if not r["lid_eligible"]:
            r["exclusion_reason"] = "all_tokens_ignored_ne"
            r["exclusion_details"] = "All tokens have label NE (-100); no target language labels exist in sentence."
            excluded.append(r)
        else:
            eligible_train.append(r)

    # Cross-split test leakage prevention
    train_non_test = []
    for r in eligible_train:
        if r["norm_key"] in all_test_keys:
            r["quarantine_reason"] = "cross_split_test_leakage_prevented"
            r["quarantine_details"] = f"Sentence text occurs in test set; removed from training to prevent data leakage."
            quarantined.append(r)
        else:
            train_non_test.append(r)

    # Group remaining by normalized key
    train_groups = defaultdict(list)
    for r in train_non_test:
        train_groups[r["norm_key"]].append(r)

    canonical_train = []

    for nk, items in train_groups.items():
        label_seqs = set(tuple(it["model_labels"]) for it in items)
        if len(label_seqs) > 1:
            for it in items:
                it["quarantine_reason"] = "train_label_conflict"
                it["quarantine_details"] = f"Conflicting label sequences in train duplicate group for key: '{nk[:50]}'"
                quarantined.append(it)
        else:
            canonical_train.append(items[0])
            for it in items[1:]:
                it["quarantine_reason"] = "train_exact_duplicate_deduped"
                it["quarantine_details"] = f"Duplicate identical record in train for key: '{nk[:50]}'"
                quarantined.append(it)

    return canonical_train, excluded, quarantined


def create_train_validation_splits(canonical_train: list, seed: int = 42):
    """
    Deterministically split canonical training records into 90% train and 10% validation.
    Stratified by subset to preserve domain proportions.
    """
    print("\nCreating deterministic 90% train / 10% validation split (seed=42)...", flush=True)
    by_subset = defaultdict(list)
    for r in canonical_train:
        by_subset[r["subset"]].append(r)

    train_records = []
    val_records = []

    rng = random.Random(seed)

    for subset, records in sorted(by_subset.items()):
        # Sort deterministically by norm_key then source_record_id before shuffling
        records_sorted = sorted(records, key=lambda x: (x["norm_key"], x["source_record_id"]))
        rng.shuffle(records_sorted)

        n_total = len(records_sorted)
        n_train = round(n_total * 0.90)

        sub_train = records_sorted[:n_train]
        sub_val = records_sorted[n_train:]

        train_records.extend(sub_train)
        val_records.extend(sub_val)

        print(f"  {subset:<12}: Total={n_total:,} | Train={len(sub_train):,} ({len(sub_train)/n_total*100:.2f}%) | Val={len(sub_val):,} ({len(sub_val)/n_total*100:.2f}%)")

    # Final deterministic sort by sentence_id assignment order
    train_records = sorted(train_records, key=lambda x: (x["subset"], x["norm_key"]))
    val_records = sorted(val_records, key=lambda x: (x["subset"], x["norm_key"]))

    return train_records, val_records


def format_record(item: dict, split: str, idx: int) -> dict:
    """Format an item to the unified JSON schema."""
    sentence_id = f"lid_{split}_{idx:06d}"
    rec = {
        "sentence_id": sentence_id,
        "original_sentence_id": item["original_sentence_id"],
        "source": item["source"],
        "subset": item["subset"],
        "original_split": item["original_split"],
        "split": split,
        "text": item["text"],
        "tokens": item["tokens"],
        "original_labels": item["original_labels"],
        "original_labels_by_annotator": item["original_labels_by_annotator"],
        "source_labels": item["source_labels"],
        "model_labels": item["model_labels"],
        "text_format": item["text_format"],
        "lid_eligible": item["lid_eligible"],
        "lid_eligible_tokens": item["lid_eligible_tokens"],
        "source_record_id": item["source_record_id"],
    }
    if "exclusion_reason" in item:
        rec["exclusion_reason"] = item["exclusion_reason"]
        rec["exclusion_details"] = item["exclusion_details"]
    if "quarantine_reason" in item:
        rec["quarantine_reason"] = item["quarantine_reason"]
        rec["quarantine_details"] = item["quarantine_details"]

    return rec


def write_jsonl(filepath: Path, records: list):
    with filepath.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def profile_muril_lengths(records: list, tokenizer, sample_limit: int = 5000):
    """Measure subword sequence lengths using MuRIL tokenizer."""
    print(f"\nProfiling MuRIL subword sequence lengths on {min(len(records), sample_limit):,} sample records...", flush=True)
    lengths = []
    unk_count = 0
    total_subwords = 0

    sample = records[:sample_limit]
    for r in sample:
        subwords = ["[CLS]"]
        for w in r["tokens"]:
            pieces = tokenizer.tokenize(str(w))
            if not pieces:
                pieces = [tokenizer.unk_token]
            for p in pieces:
                subwords.append(p)
                if p == tokenizer.unk_token:
                    unk_count += 1
        subwords.append("[SEP]")
        lengths.append(len(subwords))
        total_subwords += len(subwords)

    lengths.sort()
    n = len(lengths)

    def percentile(p):
        k = (n - 1) * p
        f = int(k)
        c = f + 1
        if c < n:
            return round(lengths[f] + (k - f) * (lengths[c] - lengths[f]), 1)
        return float(lengths[f])

    p50 = percentile(0.50)
    p90 = percentile(0.90)
    p95 = percentile(0.95)
    p99 = percentile(0.99)
    max_len = max(lengths)
    min_len = min(lengths)

    print(f"  Subword length distribution: min={min_len}, p50={p50}, p90={p90}, p95={p95}, p99={p99}, max={max_len}")
    print(f"  Unknown ([UNK]) token rate: {unk_count}/{total_subwords} ({unk_count/total_subwords*100:.3f}%)")

    # Recommendation
    if p99 <= 128:
        rec_max_len = 128
    elif p99 <= 256:
        rec_max_len = 256
    else:
        rec_max_len = 512

    return {
        "sample_size": n,
        "min_subwords": min_len,
        "p50_subwords": p50,
        "p90_subwords": p90,
        "p95_subwords": p95,
        "p99_subwords": p99,
        "max_subwords": max_len,
        "unknown_tokens": unk_count,
        "unknown_token_rate_pct": round(unk_count / total_subwords * 100, 3) if total_subwords else 0,
        "recommended_max_length": rec_max_len,
        "recommendation_rationale": f"p99 is {p99} subwords; max_length={rec_max_len} covers >99% of sequences without truncation.",
    }


def compute_label_distribution(records: list):
    counts = Counter()
    for r in records:
        for lbl in r["model_labels"]:
            counts[lbl] += 1
    return {
        "EN (0)": counts[0],
        "HI (1)": counts[1],
        "TE (2)": counts[2],
        "OTHER (3)": counts[3],
        "IGNORED (-100)": counts[-100],
        "total_tokens": sum(counts.values()),
        "usable_tokens": sum(counts[k] for k in [0, 1, 2, 3]),
    }


def main():
    print("=" * 70, flush=True)
    print("BUILDING UNIFIED LANGUAGE IDENTIFICATION DATASET", flush=True)
    print("=" * 70, flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Raw
    raw_train, raw_test = extract_raw_records()
    total_raw = len(raw_train) + len(raw_test)
    print(f"Total raw input records: {total_raw:,} (Train: {len(raw_train):,}, Test: {len(raw_test):,})", flush=True)

    # 2. Process Test Data
    canonical_test, test_excluded, test_quarantined = process_test_data(raw_test)
    print(f"Test split: Canonical={len(canonical_test):,}, Excluded={len(test_excluded):,}, Quarantined={len(test_quarantined):,}", flush=True)

    # 3. Process Train Data (with test leakage prevention)
    all_test_keys = set(r["norm_key"] for r in raw_test)
    canonical_train, train_excluded, train_quarantined = process_train_data(raw_train, all_test_keys)
    print(f"Train split: Canonical={len(canonical_train):,}, Excluded={len(train_excluded):,}, Quarantined={len(train_quarantined):,}", flush=True)

    # 4. Train / Validation Split
    train_canonical, val_canonical = create_train_validation_splits(canonical_train, seed=RANDOM_SEED)

    # Format all records
    formatted_train = [format_record(r, "train", i) for i, r in enumerate(train_canonical, start=1)]
    formatted_val = [format_record(r, "validation", i) for i, r in enumerate(val_canonical, start=1)]
    formatted_test = [format_record(r, "test", i) for i, r in enumerate(canonical_test, start=1)]

    all_excluded = test_excluded + train_excluded
    formatted_excluded = [format_record(r, "excluded", i) for i, r in enumerate(all_excluded, start=1)]

    all_quarantined = test_quarantined + train_quarantined
    formatted_quarantined = [format_record(r, "quarantined", i) for i, r in enumerate(all_quarantined, start=1)]

    # Subsets of test
    test_comi = [r for r in formatted_test if r["subset"] == "COMI-LINGUA"]
    test_blog = [r for r in formatted_test if r["subset"] == "Blog"]
    test_twitter = [r for r in formatted_test if r["subset"] == "Twitter"]

    # Verify Accounting
    primary_total = len(formatted_train) + len(formatted_val) + len(formatted_test) + len(formatted_excluded) + len(formatted_quarantined)
    print(f"\nFinal Accounting Check:")
    print(f"  Train:        {len(formatted_train):,}")
    print(f"  Validation:   {len(formatted_val):,}")
    print(f"  Test:         {len(formatted_test):,}")
    print(f"    - COMI:     {len(test_comi):,}")
    print(f"    - Blog:     {len(test_blog):,}")
    print(f"    - Twitter:  {len(test_twitter):,}")
    print(f"  Excluded:     {len(formatted_excluded):,}")
    print(f"  Quarantined:  {len(formatted_quarantined):,}")
    print(f"  Total:        {primary_total:,} / {total_raw:,} -> {'EXACT MATCH' if primary_total == total_raw else 'MISMATCH'}")

    assert primary_total == total_raw, "Record loss detected!"

    # 5. Write Files
    print("\nWriting JSONL dataset files...", flush=True)
    write_jsonl(OUTPUT_DIR / "train.jsonl", formatted_train)
    write_jsonl(OUTPUT_DIR / "validation.jsonl", formatted_val)
    write_jsonl(OUTPUT_DIR / "test.jsonl", formatted_test)
    write_jsonl(OUTPUT_DIR / "test_comi_lingua.jsonl", test_comi)
    write_jsonl(OUTPUT_DIR / "test_tenglish_blog.jsonl", test_blog)
    write_jsonl(OUTPUT_DIR / "test_tenglish_twitter.jsonl", test_twitter)
    write_jsonl(OUTPUT_DIR / "excluded_records.jsonl", formatted_excluded)
    write_jsonl(OUTPUT_DIR / "quarantined_duplicates.jsonl", formatted_quarantined)

    # 6. Profile MuRIL Tokenizer Lengths
    print("\nLoading MuRIL tokenizer for subword length profiling...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=False)
    subword_stats = profile_muril_lengths(formatted_train + formatted_val, tokenizer)

    # 7. Compute Distributions & Manifest
    manifest = {
        "dataset_name": "CodeMix Intelligence Unified LID Dataset",
        "task": "Token-Level Trilingual Language Identification",
        "target_languages": ["English (EN)", "Hindi (HI)", "Telugu (TE)", "Universal/Symbols (OTHER)"],
        "model_id": MODEL_ID,
        "model_label_mapping": LABEL_TO_ID,
        "ignore_label_id": IGNORE_LABEL_ID,
        "random_seed": RANDOM_SEED,
        "splits_summary": {
            "train": {
                "records": len(formatted_train),
                "tokens": sum(len(r["tokens"]) for r in formatted_train),
                "subsets": dict(Counter(r["subset"] for r in formatted_train)),
                "label_distribution": compute_label_distribution(formatted_train),
            },
            "validation": {
                "records": len(formatted_val),
                "tokens": sum(len(r["tokens"]) for r in formatted_val),
                "subsets": dict(Counter(r["subset"] for r in formatted_val)),
                "label_distribution": compute_label_distribution(formatted_val),
            },
            "test": {
                "records": len(formatted_test),
                "tokens": sum(len(r["tokens"]) for r in formatted_test),
                "subsets": dict(Counter(r["subset"] for r in formatted_test)),
                "label_distribution": compute_label_distribution(formatted_test),
            },
            "excluded": {
                "records": len(formatted_excluded),
                "reasons": dict(Counter(r.get("exclusion_reason") for r in formatted_excluded)),
            },
            "quarantined": {
                "records": len(formatted_quarantined),
                "reasons": dict(Counter(r.get("quarantine_reason") for r in formatted_quarantined)),
            },
        },
        "muril_subword_profiling": subword_stats,
        "total_raw_records_accounted": total_raw,
    }

    manifest_path = OUTPUT_DIR / "dataset_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)

    print(f"\nManifest saved to: {manifest_path.relative_to(PROJECT_ROOT)}")
    print("Unified Dataset Construction Complete!", flush=True)


if __name__ == "__main__":
    main()
