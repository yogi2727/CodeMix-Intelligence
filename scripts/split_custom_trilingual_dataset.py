"""
Reproducible Group-Aware Stratified Splitting Script for Custom Trilingual Dataset.

Splits data/custom/trilingual_lid/reviewed_sentences.jsonl into:
- 60% Train (~240 sentences across 4 categories)
- 20% Validation (~80 sentences across 4 categories)
- 20% Test (~80 sentences across 4 categories)

Key Principles:
1. Category stratification across Native_Telugu, English_Telugu, Hindi_Telugu, English_Hindi_Telugu.
2. Group-aware splitting: prevents leakage from identical templates, shared contributors, or sources.
3. Deterministic and reproducible using seed=42.
4. Independent verification: ensures zero normalized sentence overlap between train, val, and test.
5. Safe execution guard: exits gracefully without error if reviewed_sentences.jsonl is empty.
"""

import argparse
import json
import random
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
REVIEWED_FILE = CUSTOM_DIR / "reviewed_sentences.jsonl"
SPLITS_DIR = CUSTOM_DIR / "splits"

DEFAULT_SEED = 42

CATEGORY_ALIASES = {
    "Native_Telugu": "Native_Telugu",
    "English_Telugu": "English_Telugu",
    "English_Native_Telugu": "English_Telugu",
    "Hindi_Telugu": "Hindi_Telugu",
    "Hindi_Native_Telugu": "Hindi_Telugu",
    "English_Hindi_Telugu": "English_Hindi_Telugu",
}


def normalize_key(tokens: list) -> str:
    """Canonical normalized comparison key for duplicate detection."""
    return " ".join(t.strip().casefold() for t in tokens)


def load_reviewed_records(filepath: Path) -> list:
    """Load records from reviewed_sentences.jsonl."""
    if not filepath.exists():
        print(f"Reviewed file does not exist: {filepath}")
        return []

    records = []
    with filepath.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_str = line.strip()
            if line_str:
                records.append(json.loads(line_str))
    return records


def perform_stratified_split(records: list, seed: int = DEFAULT_SEED):
    """
    Perform group-aware, category-stratified 60/20/20 split.
    """
    rng = random.Random(seed)

    # 1. Group records by canonical category
    by_category = defaultdict(list)
    for r in records:
        raw_sub = r.get("subset", "")
        canon_sub = CATEGORY_ALIASES.get(raw_sub, raw_sub)
        by_category[canon_sub].append(r)

    train_records = []
    val_records = []
    test_records = []

    split_stats = {}

    for cat, cat_records in sorted(by_category.items()):
        # 2. Form groups within category to prevent template/contributor leakage
        # Group key: metadata.source_group_id (primary), fallback to group_id, contributor_id, or template_id
        groups = defaultdict(list)
        for r in cat_records:
            meta = r.get("metadata", {})
            group_key = (
                meta.get("source_group_id")
                or meta.get("group_id")
                or meta.get("contributor_id")
                or meta.get("template_id")
                or normalize_key(r.get("tokens", []))
            )
            groups[group_key].append(r)

        # Shuffle group items deterministically
        group_keys = sorted(groups.keys())
        rng.shuffle(group_keys)

        total_cat_records = len(cat_records)
        target_train = round(total_cat_records * 0.60)
        target_val = round(total_cat_records * 0.20)
        # Target test receives remaining balance

        cat_train = []
        cat_val = []
        cat_test = []

        curr_train_cnt = 0
        curr_val_cnt = 0

        for gk in group_keys:
            items = groups[gk]
            if curr_train_cnt + len(items) <= target_train or (curr_val_cnt >= target_val and len(cat_test) >= (total_cat_records - target_train - target_val)):
                cat_train.extend(items)
                curr_train_cnt += len(items)
            elif curr_val_cnt + len(items) <= target_val:
                cat_val.extend(items)
                curr_val_cnt += len(items)
            else:
                cat_test.extend(items)

        # Safety Check: In case all items fell into train/val due to boundary logic
        if not cat_test and len(cat_train) > target_train:
            # Shift lowest-priority group
            cat_test.append(cat_train.pop())

        train_records.extend(cat_train)
        val_records.extend(cat_val)
        test_records.extend(cat_test)

        split_stats[cat] = {
            "total": total_cat_records,
            "train": len(cat_train),
            "validation": len(cat_val),
            "test": len(cat_test),
            "train_pct": round(len(cat_train) / total_cat_records * 100, 2) if total_cat_records else 0,
            "val_pct": round(len(cat_val) / total_cat_records * 100, 2) if total_cat_records else 0,
            "test_pct": round(len(cat_test) / total_cat_records * 100, 2) if total_cat_records else 0,
        }

    return train_records, val_records, test_records, split_stats


def verify_zero_leakage(train_recs: list, val_recs: list, test_recs: list):
    """Verify zero duplicate sentences across splits."""
    train_keys = {normalize_key(r["tokens"]): r["sentence_id"] for r in train_recs}
    val_keys = {normalize_key(r["tokens"]): r["sentence_id"] for r in val_recs}
    test_keys = {normalize_key(r["tokens"]): r["sentence_id"] for r in test_recs}

    train_val_overlap = set(train_keys) & set(val_keys)
    train_test_overlap = set(train_keys) & set(test_keys)
    val_test_overlap = set(val_keys) & set(test_keys)

    errors = []
    if train_val_overlap:
        errors.append(f"Train vs Validation leakage detected ({len(train_val_overlap)} duplicate sentences)!")
    if train_test_overlap:
        errors.append(f"Train vs Test leakage detected ({len(train_test_overlap)} duplicate sentences)!")
    if val_test_overlap:
        errors.append(f"Validation vs Test leakage detected ({len(val_test_overlap)} duplicate sentences)!")

    return errors


def write_split_file(filepath: Path, records: list, split_name: str):
    """Write records with updated split field."""
    with filepath.open("w", encoding="utf-8") as f:
        for r in records:
            r_copy = dict(r)
            r_copy["split"] = split_name
            f.write(json.dumps(r_copy, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Split reviewed custom trilingual dataset into train/val/test.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"Random seed (default: {DEFAULT_SEED})")
    parser.add_argument("--force", action="store_true", help="Force split even if target counts (400) are not met.")
    args = parser.parse_args()

    print("=" * 75, flush=True)
    print("CUSTOM TRILINGUAL DATASET STRATIFIED SPLIT ASSIGNMENT", flush=True)
    print(f"Target Reviewed File: {REVIEWED_FILE}", flush=True)
    print(f"Random Seed:          {args.seed}", flush=True)
    print("=" * 75, flush=True)

    records = load_reviewed_records(REVIEWED_FILE)
    print(f"\nLoaded {len(records)} reviewed records from {REVIEWED_FILE.name}.", flush=True)

    # SAFE EXECUTION GUARD:
    # If dataset has 0 records, do NOT fail with an unhandled exception; explain and exit cleanly.
    if len(records) == 0:
        print("\n[SAFE GUARD ACTIVE] reviewed_sentences.jsonl contains 0 records.")
        print("Data collection and two-stage review are currently in progress.")
        print("This split script is staged and ready. It will execute once the 400 reviewed sentences are populated.")
        print("No output files have been written.\n")
        return

    if len(records) < 400 and not args.force:
        print(f"\n[WARNING] Only {len(records)}/400 target reviewed records collected.")
        print("To proceed with a partial split, rerun with the '--force' flag.")
        return

    # Task 4 Check: Refuse to assign final splits to records without valid source_group_id
    missing_group_records = [
        r.get("sentence_id", "<unknown>")
        for r in records
        if not (r.get("metadata", {}).get("source_group_id") or r.get("metadata", {}).get("group_id"))
        and not r.get("metadata", {}).get("approved_grouping_exception")
    ]
    if missing_group_records:
        print(f"\n[CRITICAL ERROR] {len(missing_group_records)} records lack valid 'source_group_id' in metadata!")
        print("Group-aware splitting requires document/work or contributor source grouping to prevent cross-split leakage.")
        print("Refusing to assign final splits without valid source grouping. (Examples: " + ", ".join(missing_group_records[:5]) + ")")
        sys.exit(1)

    # Execute Split
    print("\nExecuting group-aware stratified 60/20/20 split...", flush=True)
    train_recs, val_recs, test_recs, split_stats = perform_stratified_split(records, seed=args.seed)

    # Verify zero leakage
    leakage_errors = verify_zero_leakage(train_recs, val_recs, test_recs)
    if leakage_errors:
        print("\n[CRITICAL ERROR] Cross-split leakage detected:")
        for e in leakage_errors:
            print(f"  {e}")
        sys.exit(1)

    # Write output splits
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    train_path = SPLITS_DIR / "train.jsonl"
    val_path = SPLITS_DIR / "validation.jsonl"
    test_path = SPLITS_DIR / "test.jsonl"
    manifest_path = SPLITS_DIR / "split_manifest.json"

    print("\nWriting split files to data/custom/trilingual_lid/splits/...", flush=True)
    write_split_file(train_path, train_recs, "train")
    write_split_file(val_path, val_recs, "validation")
    write_split_file(test_path, test_recs, "test")

    split_manifest = {
        "dataset_name": "CodeMix Intelligence Custom Trilingual Dataset Splits",
        "random_seed": args.seed,
        "source_file": "data/custom/trilingual_lid/reviewed_sentences.jsonl",
        "total_records_split": len(records),
        "split_summary": {
            "train": len(train_recs),
            "validation": len(val_recs),
            "test": len(test_recs),
        },
        "category_breakdown": split_stats,
        "leakage_verification": {
            "train_val_overlap": 0,
            "train_test_overlap": 0,
            "val_test_overlap": 0,
            "leakage_free": True,
        },
    }

    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(split_manifest, f, indent=4, ensure_ascii=False)

    print("\nSplit Assignment Summary:")
    print(f"  Train:      {len(train_recs):>4} records ({len(train_recs)/len(records)*100:.2f}%)")
    print(f"  Validation: {len(val_recs):>4} records ({len(val_recs)/len(records)*100:.2f}%)")
    print(f"  Test:       {len(test_recs):>4} records ({len(test_recs)/len(records)*100:.2f}%)")
    print("\nCategory Distribution:")
    for cat, st in split_stats.items():
        print(f"  {cat:<24}: Total={st['total']:>3} | Train={st['train']:>2} | Val={st['validation']:>2} | Test={st['test']:>2}")

    print(f"\nManifest saved to: {manifest_path}")
    print("Stratified splitting complete: 0 cross-split leakage verified!", flush=True)


if __name__ == "__main__":
    main()
