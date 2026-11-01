"""
Preprocess COMI-LINGUA dataset for Trilingual Code-Mixed Language Identification.

Dataset: LingoIITGN/COMI-LINGUA (Config: LID)
Splits: train (30,487), test (5,000)

Applies:
- Robust multi-structure annotation parsing (dicts, pairs, indices).
- Source label normalization (hi/h -> HI, en/e -> EN, ot/u -> OTHER).
- Strict 3-annotator alignment (token count, token string, index checks).
- Majority-vote consensus (unanimous, 2/3 majority, or null for tie/no majority).
- Preservation of original Sentences text, original annotation votes, and quarantined rejects.
"""

import ast
import json
import sys
from collections import Counter
from pathlib import Path
from datasets import load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "normalized" / "comi_lingua"
CONFIG_PATH = PROJECT_ROOT / "configs" / "label_mapping.json"

DATASET_ID = "LingoIITGN/COMI-LINGUA"
DATASET_CONFIG = "LID"

ANNOTATOR_FIELDS = [
    "Annotated by: Annotator 1",
    "Annotated by: Annotator 2",
    "Annotated by: Annotator 3",
]

# Load label mapping from config
with CONFIG_PATH.open("r", encoding="utf-8") as f:
    config_data = json.load(f)

SOURCE_LABEL_MAP = config_data["source_mappings"]["COMI-LINGUA"]


def parse_single_annotation(raw_annotation):
    """
    Parse a single annotator's string representation.
    Supports dictionary items with optional index, or 2-element lists/tuples.
    """
    if not isinstance(raw_annotation, str):
        raise ValueError(f"Annotation is not a string: {type(raw_annotation)}")

    parsed = ast.literal_eval(raw_annotation)
    if not isinstance(parsed, list):
        raise ValueError(f"Annotation parsed into non-list: {type(parsed)}")

    normalized_tokens = []
    for pos, item in enumerate(parsed):
        orig_index = None
        if isinstance(item, dict):
            if "key" not in item or "value" not in item:
                raise ValueError(f"Dictionary item missing 'key' or 'value' at pos {pos}: {item}")
            token = item["key"]
            orig_val = item["value"]
            orig_index = item.get("index")
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            token, orig_val = item
        else:
            raise ValueError(f"Unsupported annotation item structure at pos {pos}: {item}")

        token_str = str(token)
        orig_label_str = str(orig_val).strip().lower()

        if orig_label_str not in SOURCE_LABEL_MAP:
            raise ValueError(f"Unknown source label '{orig_val}' at pos {pos}")

        norm_label = SOURCE_LABEL_MAP[orig_label_str]

        normalized_tokens.append({
            "token": token_str,
            "original_label": orig_val,
            "normalized_label": norm_label,
            "original_index": orig_index,
            "position": pos,
        })

    return normalized_tokens


def align_and_build_consensus(annotations):
    """
    Verify alignment across the three annotators and compute token consensus.
    Returns (is_aligned, rejection_reason, rejection_details, aligned_data)
    """
    lengths = [len(ann) for ann in annotations]
    if len(set(lengths)) != 1:
        return (
            False,
            "token_count_mismatch",
            f"Token counts differ among annotators: {lengths}",
            None,
        )

    seq_len = lengths[0]
    tokens = []
    original_labels_by_ann = {
        "annotator_1": [],
        "annotator_2": [],
        "annotator_3": [],
    }
    consensus_labels = []
    token_agreements = []

    ann1, ann2, ann3 = annotations

    for pos in range(seq_len):
        t1, t2, t3 = ann1[pos]["token"], ann2[pos]["token"], ann3[pos]["token"]
        if not (t1 == t2 == t3):
            return (
                False,
                "token_string_mismatch",
                f"Token strings mismatch at pos {pos}: ['{t1}', '{t2}', '{t3}']",
                None,
            )

        indices = [
            str(ann[pos]["original_index"])
            for ann in annotations
            if ann[pos]["original_index"] is not None
        ]
        if len(set(indices)) > 1:
            return (
                False,
                "token_index_conflict",
                f"Conflicting index values at pos {pos}: {indices}",
                None,
            )

        token = t1
        tokens.append(token)

        original_labels_by_ann["annotator_1"].append(ann1[pos]["original_label"])
        original_labels_by_ann["annotator_2"].append(ann2[pos]["original_label"])
        original_labels_by_ann["annotator_3"].append(ann3[pos]["original_label"])

        norm_votes = [
            ann1[pos]["normalized_label"],
            ann2[pos]["normalized_label"],
            ann3[pos]["normalized_label"],
        ]
        vote_counts = Counter(norm_votes)

        if len(vote_counts) == 1:
            final_label = norm_votes[0]
            agreement_type = "unanimous"
        elif max(vote_counts.values()) == 2:
            final_label = vote_counts.most_common(1)[0][0]
            agreement_type = "majority"
        else:
            final_label = None  # No majority agreement (all 3 different)
            agreement_type = "no_majority"

        consensus_labels.append(final_label)
        token_agreements.append(agreement_type)

    ignored_tokens = sum(1 for l in consensus_labels if l is None)
    lid_eligible_tokens = sum(1 for l in consensus_labels if l is not None)

    aligned_data = {
        "tokens": tokens,
        "original_labels_by_annotator": original_labels_by_ann,
        "labels": consensus_labels,
        "token_agreements": token_agreements,
        "ignored_token_count": ignored_tokens,
        "lid_eligible_tokens": lid_eligible_tokens,
        "lid_eligible": lid_eligible_tokens > 0,
    }
    return (True, None, None, aligned_data)


def process_split(split_name: str) -> dict:
    print("\n" + "=" * 70, flush=True)
    print(f"PROCESSING COMI-LINGUA SPLIT: {split_name.upper()}", flush=True)
    print("=" * 70, flush=True)

    dataset = load_dataset(
        DATASET_ID,
        DATASET_CONFIG,
        split=split_name,
        streaming=True,
    )

    aligned_output_path = OUTPUT_DIR / f"comi_lid_{split_name}.jsonl"
    rejected_output_path = OUTPUT_DIR / f"comi_lid_{split_name}_rejected.jsonl"

    aligned_count = 0
    rejected_count = 0
    total_records = 0

    rejection_reasons = Counter()
    label_distribution = Counter()
    agreement_stats = Counter()
    total_tokens = 0
    total_ignored_tokens = 0
    lid_eligible_sentences = 0
    lid_ineligible_sentences = 0

    with aligned_output_path.open("w", encoding="utf-8") as f_aligned, \
         rejected_output_path.open("w", encoding="utf-8") as f_rejected:

        for row_idx, row in enumerate(dataset, start=1):
            total_records += 1

            if row_idx % 5000 == 0:
                print(f"  Processed {row_idx:,} records (Aligned: {aligned_count:,}, Rejected: {rejected_count:,})...", flush=True)

            raw_text = row.get("Sentences", "")
            raw_ann1 = row.get("Annotated by: Annotator 1")
            raw_ann2 = row.get("Annotated by: Annotator 2")
            raw_ann3 = row.get("Annotated by: Annotator 3")

            # Parse annotations
            parsed_annotations = []
            parse_failed = False
            parse_error_msg = ""

            for ann_idx, raw_ann in enumerate([raw_ann1, raw_ann2, raw_ann3], start=1):
                try:
                    parsed_ann = parse_single_annotation(raw_ann)
                    parsed_annotations.append(parsed_ann)
                except Exception as e:
                    parse_failed = True
                    parse_error_msg = f"Annotator {ann_idx} parse failed: {str(e)}"
                    break

            if parse_failed:
                rejected_count += 1
                rejection_reasons["parse_error"] += 1
                reject_record = {
                    "original_index": row_idx,
                    "split": split_name,
                    "text": raw_text,
                    "rejection_reason": "parse_error",
                    "rejection_details": parse_error_msg,
                    "raw_annotations": {
                        "annotator_1": repr(raw_ann1[:150]) if raw_ann1 else None,
                        "annotator_2": repr(raw_ann2[:150]) if raw_ann2 else None,
                        "annotator_3": repr(raw_ann3[:150]) if raw_ann3 else None,
                    },
                }
                f_rejected.write(json.dumps(reject_record, ensure_ascii=False) + "\n")
                continue

            # Align and consensus
            is_aligned, reason, details, aligned_info = align_and_build_consensus(parsed_annotations)

            if not is_aligned:
                rejected_count += 1
                rejection_reasons[reason] += 1
                reject_record = {
                    "original_index": row_idx,
                    "split": split_name,
                    "text": raw_text,
                    "rejection_reason": reason,
                    "rejection_details": details,
                    "raw_annotations": {
                        "annotator_1": repr(raw_ann1[:150]) if raw_ann1 else None,
                        "annotator_2": repr(raw_ann2[:150]) if raw_ann2 else None,
                        "annotator_3": repr(raw_ann3[:150]) if raw_ann3 else None,
                    },
                }
                f_rejected.write(json.dumps(reject_record, ensure_ascii=False) + "\n")
                continue

            # Successfully aligned
            aligned_count += 1
            sentence_id = f"comi_lid_{split_name}_{aligned_count:06d}"

            aligned_record = {
                "sentence_id": sentence_id,
                "source": "COMI-LINGUA",
                "subset": "COMI-LINGUA",
                "split": split_name,
                "text": raw_text,
                "tokens": aligned_info["tokens"],
                "original_labels_by_annotator": aligned_info["original_labels_by_annotator"],
                "labels": aligned_info["labels"],
                "consensus_method": "majority_vote_3_annotators",
                "ignored_token_count": aligned_info["ignored_token_count"],
                "lid_eligible": aligned_info["lid_eligible"],
                "lid_eligible_tokens": aligned_info["lid_eligible_tokens"],
                "alignment_method": "exact_token_match_with_index_verification",
            }
            f_aligned.write(json.dumps(aligned_record, ensure_ascii=False) + "\n")

            # Update stats
            seq_len = len(aligned_info["tokens"])
            total_tokens += seq_len
            total_ignored_tokens += aligned_info["ignored_token_count"]

            for lbl in aligned_info["labels"]:
                label_key = "null" if lbl is None else lbl
                label_distribution[label_key] += 1

            for ag in aligned_info["token_agreements"]:
                agreement_stats[ag] += 1

            if aligned_info["lid_eligible"]:
                lid_eligible_sentences += 1
            else:
                lid_ineligible_sentences += 1

    total_agreement_tokens = sum(agreement_stats.values())
    unanimous_pct = (agreement_stats["unanimous"] / total_agreement_tokens * 100) if total_agreement_tokens else 0
    majority_pct = (agreement_stats["majority"] / total_agreement_tokens * 100) if total_agreement_tokens else 0
    no_majority_pct = (agreement_stats["no_majority"] / total_agreement_tokens * 100) if total_agreement_tokens else 0

    print(f"\n{split_name.upper()} COMPLETE:", flush=True)
    print(f"  Total Raw Records:        {total_records:,}", flush=True)
    print(f"  Successfully Aligned:     {aligned_count:,} ({aligned_count/total_records*100:.2f}%)", flush=True)
    print(f"  Quarantined / Rejected:   {rejected_count:,} ({rejected_count/total_records*100:.2f}%)", flush=True)
    print(f"  Rejection Breakdown:      {dict(rejection_reasons)}", flush=True)
    print(f"  Total Tokens:             {total_tokens:,}", flush=True)
    print(f"  Usable Consensus Tokens:  {total_tokens - total_ignored_tokens:,}", flush=True)
    print(f"  Ignored (Tie) Tokens:     {total_ignored_tokens:,} ({total_ignored_tokens/total_tokens*100:.2f}%)", flush=True)
    print(f"  Label Distribution:       {dict(label_distribution)}", flush=True)
    print(f"  Agreement Stats:          {dict(agreement_stats)}", flush=True)
    print(f"  Unanimous Agreement:      {unanimous_pct:.2f}%", flush=True)
    print(f"  LID-Eligible Sentences:   {lid_eligible_sentences:,}", flush=True)
    print(f"  LID-Ineligible Sentences: {lid_ineligible_sentences:,}", flush=True)

    return {
        "split": split_name,
        "total_records": total_records,
        "aligned_records": aligned_count,
        "rejected_records": rejected_count,
        "rejection_breakdown": dict(rejection_reasons),
        "total_tokens": total_tokens,
        "usable_tokens": total_tokens - total_ignored_tokens,
        "ignored_tokens": total_ignored_tokens,
        "label_distribution": dict(label_distribution),
        "agreement_stats": dict(agreement_stats),
        "unanimous_percentage": round(unanimous_pct, 2),
        "majority_percentage": round(majority_pct, 2),
        "no_majority_percentage": round(no_majority_pct, 2),
        "lid_eligible_sentences": lid_eligible_sentences,
        "lid_ineligible_sentences": lid_ineligible_sentences,
        "aligned_file": str(aligned_output_path.relative_to(PROJECT_ROOT)),
        "rejected_file": str(rejected_output_path.relative_to(PROJECT_ROOT)),
    }


def main():
    print("=" * 70, flush=True)
    print("COMI-LINGUA DATASET PREPROCESSING PIPELINE", flush=True)
    print(f"Source:        {DATASET_ID} ({DATASET_CONFIG})", flush=True)
    print(f"Output Target: {OUTPUT_DIR}", flush=True)
    print("=" * 70, flush=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_summary = process_split("train")
    test_summary = process_split("test")

    # Combine overall audit
    overall_tokens = train_summary["total_tokens"] + test_summary["total_tokens"]
    overall_ignored = train_summary["ignored_tokens"] + test_summary["ignored_tokens"]
    overall_aligned = train_summary["aligned_records"] + test_summary["aligned_records"]
    overall_rejected = train_summary["rejected_records"] + test_summary["rejected_records"]
    overall_records = train_summary["total_records"] + test_summary["total_records"]

    combined_labels = Counter()
    combined_labels.update(train_summary["label_distribution"])
    combined_labels.update(test_summary["label_distribution"])

    combined_agreements = Counter()
    combined_agreements.update(train_summary["agreement_stats"])
    combined_agreements.update(test_summary["agreement_stats"])

    combined_rejections = Counter()
    combined_rejections.update(train_summary["rejection_breakdown"])
    combined_rejections.update(test_summary["rejection_breakdown"])

    audit_report = {
        "dataset_name": DATASET_ID,
        "configuration": DATASET_CONFIG,
        "annotator_columns": ANNOTATOR_FIELDS,
        "normalization_mapping": SOURCE_LABEL_MAP,
        "consensus_policy": "majority_vote_3_annotators",
        "unresolved_policy": "null_token_ignored",
        "splits": {
            "train": train_summary,
            "test": test_summary,
        },
        "overall_summary": {
            "total_records": overall_records,
            "aligned_records": overall_aligned,
            "rejected_records": overall_rejected,
            "rejection_breakdown": dict(combined_rejections),
            "total_tokens": overall_tokens,
            "usable_tokens": overall_tokens - overall_ignored,
            "ignored_tokens": overall_ignored,
            "label_distribution": dict(combined_labels),
            "agreement_stats": dict(combined_agreements),
            "unanimous_percentage": round(combined_agreements["unanimous"] / overall_tokens * 100, 2) if overall_tokens else 0,
        },
    }

    audit_path = OUTPUT_DIR / "comi_lid_audit.json"
    with audit_path.open("w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 70, flush=True)
    print("ALL PROCESSING COMPLETED SUCCESSFULLY", flush=True)
    print(f"Audit report saved: {audit_path.relative_to(PROJECT_ROOT)}", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    main()
