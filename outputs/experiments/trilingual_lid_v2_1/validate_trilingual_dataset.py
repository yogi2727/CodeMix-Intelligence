#!/usr/bin/env python3
"""
CodeMix Intelligence V2.1 - Trilingual Dataset Validator
Validates token-level CSV and sentence-level JSONL trilingual code-mixed datasets.

Enforces:
1. Valid language labels (EN, HI, TE, OTHER, AMBIGUOUS, NE, MIXED).
2. Model label mappings (EN->0, HI->1, TE->2, OTHER->3, AMBIGUOUS/NE/MIXED->-100).
3. Token and character-offset consistency: text[char_start:char_end] == token.
4. Multi-level group leakage prevention (speaker_id, session_id, prompt_group_id, source_group_id, text).
5. Consent scope legality (public_cc_by_4_0, academic_research_only, internal_pilot).
6. Workflow status validity (annotation_status, adjudication_status).
7. Invalid Unicode codepoints (control chars, unpaired surrogates).
8. Class distribution and language co-occurrence tracking.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


VALID_LABELS = {"EN", "HI", "TE", "OTHER", "AMBIGUOUS", "NE", "MIXED"}
MODEL_LABEL_MAP = {
    "EN": 0,
    "HI": 1,
    "TE": 2,
    "OTHER": 3,
    "AMBIGUOUS": -100,
    "NE": -100,
    "MIXED": -100
}
VALID_WRITING_SYSTEMS = {
    "latin_romanized",
    "devanagari",
    "telugu_script",
    "numeric_symbol",
    "mixed_script"
}
VALID_CONSENT_SCOPES = {
    "public_cc_by_4_0",
    "academic_research_only",
    "internal_pilot"
}
VALID_ANNOTATION_STATUSES = {
    "raw",
    "annotated_pass1",
    "annotated_pass2",
    "adjudicated",
    "verified"
}
VALID_ADJUDICATION_STATUSES = {
    "unadjudicated",
    "agreed",
    "adjudicated_resolved",
    "adjudicated_disputed"
}


def normalize_whitespace(text: str) -> str:
    """Normalize internal and external whitespace for duplicate checking."""
    return re.sub(r"\s+", " ", text.strip()).lower()


def detect_unicode_anomalies(text: str) -> List[str]:
    """Identify invalid control characters or non-printable codepoints."""
    anomalies = []
    for idx, ch in enumerate(text):
        cat = unicodedata.category(ch)
        if cat in ("Cc", "Cs") and ch not in ("\n", "\r", "\t"):
            anomalies.append(f"Char '{ch}' (U+{ord(ch):04X}, category {cat}) at index {idx}")
    return anomalies


def detect_script(text: str) -> str:
    """Determine dominant script of a token or sentence."""
    has_devanagari = any("\u0900" <= ch <= "\u097F" for ch in text)
    has_telugu = any("\u0C00" <= ch <= "\u0C7F" for ch in text)
    has_latin = any(("a" <= ch <= "z") or ("A" <= ch <= "Z") for ch in text)

    scripts_present = sum([has_devanagari, has_telugu, has_latin])
    if scripts_present > 1:
        return "mixed_script"
    if has_devanagari:
        return "devanagari"
    if has_telugu:
        return "telugu_script"
    if has_latin:
        return "latin_romanized"
    return "numeric_symbol"


class TrilingualDatasetValidator:
    """Validator for CodeMix Intelligence V2.1 Trilingual Datasets."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.sentences: Dict[str, Dict[str, Any]] = {}
        self.normalized_text_to_ids: Dict[str, List[str]] = defaultdict(list)
        self.speaker_to_sentences: Dict[str, Set[str]] = defaultdict(set)
        self.session_to_sentences: Dict[str, Set[str]] = defaultdict(set)
        self.prompt_group_to_sentences: Dict[str, Set[str]] = defaultdict(set)
        self.group_to_sentences: Dict[str, Set[str]] = defaultdict(set)
        self.token_class_counts: Counter[str] = Counter()
        self.script_counts: Counter[str] = Counter()
        self.co_occurrence_counts: Counter[str] = Counter()
        self.consent_counts: Counter[str] = Counter()
        self.adjudication_counts: Counter[str] = Counter()

    def validate_csv_records(self, csv_path: Path) -> bool:
        """Validate a token-level CSV file conforming to DATASET_SCHEMA.md."""
        if not csv_path.exists():
            self.errors.append(f"CSV file not found: {csv_path}")
            return False

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required_cols = {
                "sentence_id", "sentence_text", "token_index", "token",
                "char_start", "char_end", "language_label"
            }
            if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
                missing = required_cols - set(reader.fieldnames or [])
                self.errors.append(f"Missing required CSV columns in {csv_path}: {missing}")
                return False

            raw_sentences: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            for row_num, row in enumerate(reader, start=2):
                sid = (row.get("sentence_id") or "").strip()
                if not sid:
                    self.errors.append(f"Row {row_num}: Missing sentence_id")
                    continue
                raw_sentences[sid].append({"row_num": row_num, **row})

        # Process assembled sentences
        for sid, rows in raw_sentences.items():
            first_row = rows[0]
            sentence_text = first_row.get("sentence_text", "")
            speaker_id = (first_row.get("speaker_id") or "spk_default").strip()
            session_id = (first_row.get("session_id") or "sess_default").strip()
            prompt_group_id = (first_row.get("prompt_group_id") or "prompt_grp_default").strip()
            group_id = (first_row.get("source_group_id") or prompt_group_id).strip()
            consent_scope = (first_row.get("consent_scope") or "public_cc_by_4_0").strip()
            annotation_status = (first_row.get("annotation_status") or "verified").strip()
            adjudication_status = (first_row.get("adjudication_status") or "agreed").strip()

            if consent_scope not in VALID_CONSENT_SCOPES:
                self.errors.append(f"Sentence {sid}: Invalid consent_scope '{consent_scope}'")
            if annotation_status not in VALID_ANNOTATION_STATUSES:
                self.warnings.append(f"Sentence {sid}: Unknown annotation_status '{annotation_status}'")
            if adjudication_status not in VALID_ADJUDICATION_STATUSES:
                self.warnings.append(f"Sentence {sid}: Unknown adjudication_status '{adjudication_status}'")

            # Check text consistency across tokens of same sentence
            for r in rows:
                if r.get("sentence_text") != sentence_text:
                    self.errors.append(
                        f"Sentence {sid}: Inconsistent sentence_text at row {r['row_num']}"
                    )

            # Check Unicode anomalies
            u_issues = detect_unicode_anomalies(sentence_text)
            if u_issues:
                self.errors.append(f"Sentence {sid}: Invalid Unicode detected: {u_issues[:3]}")

            # Sort tokens by token_index
            try:
                rows.sort(key=lambda x: int(x["token_index"]))
            except ValueError:
                self.errors.append(f"Sentence {sid}: Non-integer token_index detected")
                continue

            tokens = []
            char_offsets = []
            labels = []
            writing_systems = []

            for expected_idx, r in enumerate(rows):
                actual_idx = int(r["token_index"])
                if actual_idx != expected_idx:
                    self.errors.append(
                        f"Sentence {sid}: Token index gap or out of order at row {r['row_num']}. "
                        f"Expected {expected_idx}, got {actual_idx}"
                    )

                token = r.get("token", "")
                try:
                    c_start = int(r["char_start"])
                    c_end = int(r["char_end"])
                except (ValueError, TypeError):
                    self.errors.append(
                        f"Sentence {sid}, Token {expected_idx}: Non-integer character offsets"
                    )
                    continue

                # Offset consistency check
                slice_text = sentence_text[c_start:c_end]
                if slice_text != token:
                    self.errors.append(
                        f"Sentence {sid}, Token {expected_idx} ('{token}'): Offset mismatch. "
                        f"sentence_text[{c_start}:{c_end}] yielded '{slice_text}'"
                    )

                label = (r.get("language_label") or "").strip().upper()
                if label not in VALID_LABELS:
                    self.errors.append(
                        f"Sentence {sid}, Token {expected_idx}: Invalid language_label '{label}'"
                    )

                ws = (r.get("writing_system") or "").strip() or detect_script(token)
                tokens.append(token)
                char_offsets.append([c_start, c_end])
                labels.append(label)
                writing_systems.append(ws)
                self.token_class_counts[label] += 1
                self.script_counts[ws] += 1

            self.consent_counts[consent_scope] += 1
            self.adjudication_counts[adjudication_status] += 1
            self._register_sentence(
                sid=sid,
                text=sentence_text,
                speaker_id=speaker_id,
                session_id=session_id,
                prompt_group_id=prompt_group_id,
                group_id=group_id,
                labels=labels
            )

        return len(self.errors) == 0

    def validate_jsonl_file(self, jsonl_path: Path) -> bool:
        """Validate a sentence-level JSONL file conforming to DATASET_SCHEMA.md."""
        if not jsonl_path.exists():
            self.errors.append(f"JSONL file not found: {jsonl_path}")
            return False

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    record = json.loads(line_str)
                except json.JSONDecodeError as e:
                    self.errors.append(f"Line {line_num}: JSON decode error: {e}")
                    continue

                sid = record.get("sentence_id")
                if not sid:
                    self.errors.append(f"Line {line_num}: Missing 'sentence_id'")
                    continue

                text = record.get("text", "")
                if not text:
                    self.errors.append(f"Sentence {sid}: Empty 'text'")

                u_issues = detect_unicode_anomalies(text)
                if u_issues:
                    self.errors.append(f"Sentence {sid}: Invalid Unicode: {u_issues[:3]}")

                tokens = record.get("tokens", [])
                offsets = record.get("char_offsets", [])
                labels = record.get("labels", [])
                model_labels = record.get("model_labels", [])
                writing_systems = record.get("writing_systems", [])

                n = len(tokens)
                if not (len(offsets) == n and len(labels) == n and len(model_labels) == n):
                    self.errors.append(
                        f"Sentence {sid}: Array length mismatch: tokens={n}, offsets={len(offsets)}, "
                        f"labels={len(labels)}, model_labels={len(model_labels)}"
                    )

                for idx in range(n):
                    tok = tokens[idx]
                    off = offsets[idx]
                    lbl = labels[idx]
                    mlbl = model_labels[idx]

                    if lbl not in VALID_LABELS:
                        self.errors.append(f"Sentence {sid}, Token {idx}: Invalid label '{lbl}'")

                    expected_mlbl = MODEL_LABEL_MAP.get(lbl, -100)
                    if mlbl != expected_mlbl:
                        self.errors.append(
                            f"Sentence {sid}, Token {idx} ('{tok}'): model_label {mlbl} does not "
                            f"match expected {expected_mlbl} for label '{lbl}'"
                        )

                    c_start, c_end = off[0], off[1]
                    slice_str = text[c_start:c_end]
                    if slice_str != tok:
                        self.errors.append(
                            f"Sentence {sid}, Token {idx}: Offset mismatch. text[{c_start}:{c_end}] "
                            f"is '{slice_str}', token is '{tok}'"
                        )

                    ws = writing_systems[idx] if idx < len(writing_systems) else detect_script(tok)
                    self.token_class_counts[lbl] += 1
                    self.script_counts[ws] += 1

                meta = record.get("metadata", {})
                speaker_id = meta.get("speaker_id", "spk_default")
                session_id = meta.get("session_id", "sess_default")
                prompt_group_id = meta.get("prompt_group_id", "prompt_grp_default")
                group_id = meta.get("source_group_id", prompt_group_id)
                consent_scope = meta.get("consent_scope", "public_cc_by_4_0")
                adjudication_status = meta.get("adjudication_status", "agreed")

                self.consent_counts[consent_scope] += 1
                self.adjudication_counts[adjudication_status] += 1

                self._register_sentence(
                    sid=sid,
                    text=text,
                    speaker_id=speaker_id,
                    session_id=session_id,
                    prompt_group_id=prompt_group_id,
                    group_id=group_id,
                    labels=labels
                )

        return len(self.errors) == 0

    def _register_sentence(
        self,
        sid: str,
        text: str,
        speaker_id: str,
        session_id: str,
        prompt_group_id: str,
        group_id: str,
        labels: List[str]
    ) -> None:
        """Track duplicates, groups, and co-occurrence patterns."""
        if sid in self.sentences:
            self.errors.append(f"Duplicate sentence_id detected: '{sid}'")
        self.sentences[sid] = {
            "text": text,
            "speaker_id": speaker_id,
            "session_id": session_id,
            "prompt_group_id": prompt_group_id,
            "group_id": group_id,
            "labels": labels
        }

        norm_text = normalize_whitespace(text)
        self.normalized_text_to_ids[norm_text].append(sid)
        self.speaker_to_sentences[speaker_id].add(sid)
        self.session_to_sentences[session_id].add(sid)
        self.prompt_group_to_sentences[prompt_group_id].add(sid)
        self.group_to_sentences[group_id].add(sid)

        # Categorize language co-occurrence
        has_en = "EN" in labels
        has_hi = "HI" in labels
        has_te = "TE" in labels

        if has_en and has_hi and has_te:
            self.co_occurrence_counts["EN_HI_TE_trilingual"] += 1
        elif has_hi and has_te:
            self.co_occurrence_counts["HI_TE_bilingual"] += 1
        elif has_en and has_hi:
            self.co_occurrence_counts["EN_HI_bilingual"] += 1
        elif has_en and has_te:
            self.co_occurrence_counts["EN_TE_bilingual"] += 1
        elif has_en:
            self.co_occurrence_counts["EN_monolingual"] += 1
        elif has_hi:
            self.co_occurrence_counts["HI_monolingual"] += 1
        elif has_te:
            self.co_occurrence_counts["TE_monolingual"] += 1
        else:
            self.co_occurrence_counts["OTHER_only"] += 1

    def check_cross_split_leakage(
        self,
        other_validator: TrilingualDatasetValidator,
        split_name_a: str,
        split_name_b: str
    ) -> List[str]:
        """Verify zero text, speaker, session, or prompt group overlap between two splits."""
        leakage_errors = []
        # Check text overlaps
        texts_a = set(self.normalized_text_to_ids.keys())
        texts_b = set(other_validator.normalized_text_to_ids.keys())
        overlap_texts = texts_a.intersection(texts_b)
        if overlap_texts:
            leakage_errors.append(
                f"Split text leakage: {len(overlap_texts)} identical sentence string(s) found between "
                f"'{split_name_a}' and '{split_name_b}'"
            )

        # Check speaker overlaps
        speakers_a = set(self.speaker_to_sentences.keys()) - {"spk_default"}
        speakers_b = set(other_validator.speaker_to_sentences.keys()) - {"spk_default"}
        overlap_speakers = speakers_a.intersection(speakers_b)
        if overlap_speakers:
            leakage_errors.append(
                f"Speaker leakage: {len(overlap_speakers)} speaker_id(s) shared between "
                f"'{split_name_a}' and '{split_name_b}': {list(overlap_speakers)[:5]}"
            )

        # Check session overlaps
        sess_a = set(self.session_to_sentences.keys()) - {"sess_default"}
        sess_b = set(other_validator.session_to_sentences.keys()) - {"sess_default"}
        overlap_sess = sess_a.intersection(sess_b)
        if overlap_sess:
            leakage_errors.append(
                f"Session leakage: {len(overlap_sess)} session_id(s) shared between "
                f"'{split_name_a}' and '{split_name_b}': {list(overlap_sess)[:5]}"
            )

        # Check prompt group overlaps
        pg_a = set(self.prompt_group_to_sentences.keys()) - {"prompt_grp_default"}
        pg_b = set(other_validator.prompt_group_to_sentences.keys()) - {"prompt_grp_default"}
        overlap_pg = pg_a.intersection(pg_b)
        if overlap_pg:
            leakage_errors.append(
                f"Prompt group leakage: {len(overlap_pg)} prompt_group_id(s) shared between "
                f"'{split_name_a}' and '{split_name_b}': {list(overlap_pg)[:5]}"
            )

        # Check legacy group overlaps
        groups_a = set(self.group_to_sentences.keys()) - {"default_group", "prompt_grp_default"}
        groups_b = set(other_validator.group_to_sentences.keys()) - {"default_group", "prompt_grp_default"}
        overlap_groups = groups_a.intersection(groups_b)
        if overlap_groups:
            leakage_errors.append(
                f"Source group leakage: {len(overlap_groups)} source_group_id(s) shared between "
                f"'{split_name_a}' and '{split_name_b}': {list(overlap_groups)[:5]}"
            )

        return leakage_errors

    def generate_report(self) -> Dict[str, Any]:
        """Compile complete audit report dictionary."""
        # Check duplicate sentences within this split
        duplicate_texts = {t: ids for t, ids in self.normalized_text_to_ids.items() if len(ids) > 1}
        if duplicate_texts:
            for t, ids in list(duplicate_texts.items())[:5]:
                self.warnings.append(
                    f"Duplicate text detected ({len(ids)} copies): '{t[:40]}...' across IDs: {ids}"
                )

        total_tokens = sum(self.token_class_counts.values())
        class_pcts = {
            k: round((v / total_tokens * 100), 2) if total_tokens else 0.0
            for k, v in self.token_class_counts.items()
        }

        return {
            "is_valid": len(self.errors) == 0,
            "total_sentences": len(self.sentences),
            "total_tokens": total_tokens,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors[:50],
            "warnings": self.warnings[:50],
            "token_class_distribution": dict(self.token_class_counts),
            "token_class_percentages": class_pcts,
            "script_distribution": dict(self.script_counts),
            "language_co_occurrence": dict(self.co_occurrence_counts),
            "consent_distribution": dict(self.consent_counts),
            "adjudication_distribution": dict(self.adjudication_counts),
            "speaker_count": len(self.speaker_to_sentences),
            "session_count": len(self.session_to_sentences),
            "prompt_group_count": len(self.prompt_group_to_sentences),
            "group_count": len(self.group_to_sentences)
        }


def run_self_tests() -> bool:
    """Run built-in verification suite on synthetic valid and invalid examples."""
    print("Running TrilingualDatasetValidator self-tests...")
    import tempfile

    header = (
        "sentence_id,sentence_text,token_index,token,char_start,char_end,language_label,"
        "writing_system,speaker_id,session_id,prompt_group_id,source_group_id,consent_scope,"
        "source_provenance,annotation_status,adjudication_status,annotator_id,notes\n"
    )

    # Test 1: Valid CSV sentence conforming to new schema
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        csv_file = Path(f.name)
        f.write(header)
        f.write("tri_v21_000001,mai kal school ku jaaunga,0,mai,0,3,HI,latin_romanized,spk_0001,sess_0001,prompt_grp_001,grp_01,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")
        f.write("tri_v21_000001,mai kal school ku jaaunga,1,kal,4,7,HI,latin_romanized,spk_0001,sess_0001,prompt_grp_001,grp_01,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")
        f.write("tri_v21_000001,mai kal school ku jaaunga,2,school,8,14,EN,latin_romanized,spk_0001,sess_0001,prompt_grp_001,grp_01,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")
        f.write("tri_v21_000001,mai kal school ku jaaunga,3,ku,15,17,TE,latin_romanized,spk_0001,sess_0001,prompt_grp_001,grp_01,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")
        f.write("tri_v21_000001,mai kal school ku jaaunga,4,jaaunga,18,25,HI,latin_romanized,spk_0001,sess_0001,prompt_grp_001,grp_01,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")

    val1 = TrilingualDatasetValidator()
    ok1 = val1.validate_csv_records(csv_file)
    csv_file.unlink()
    assert ok1, f"Self-test 1 failed: {val1.errors}"
    assert val1.token_class_counts["HI"] == 3
    assert val1.token_class_counts["EN"] == 1
    assert val1.token_class_counts["TE"] == 1
    assert val1.co_occurrence_counts["EN_HI_TE_trilingual"] == 1
    assert val1.consent_counts["public_cc_by_4_0"] == 1

    # Test 2: Character offset mismatch detection
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        csv_bad = Path(f.name)
        f.write(header)
        # Offset 0..4 for 'mai' (which is 3 chars) is wrong
        f.write("tri_v21_000002,mai kal,0,mai,0,4,HI,latin_romanized,spk_0002,sess_0002,prompt_grp_002,grp_02,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")

    val2 = TrilingualDatasetValidator()
    val2.validate_csv_records(csv_bad)
    csv_bad.unlink()
    assert len(val2.errors) > 0, "Self-test 2 failed: expected offset error"

    # Test 3: Speaker leakage detection across splits
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        csv_split_a = Path(f.name)
        f.write(header)
        f.write("tri_v21_000003,namaste dost,0,namaste,0,7,HI,latin_romanized,spk_0009,sess_0009,prompt_grp_009,grp_09,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")
        f.write("tri_v21_000003,namaste dost,1,dost,8,12,HI,latin_romanized,spk_0009,sess_0009,prompt_grp_009,grp_09,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")

    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        csv_split_b = Path(f.name)
        f.write(header)
        # Same speaker spk_0009 in split B with different sentence
        f.write("tri_v21_000004,shubhodhayam mitrama,0,shubhodhayam,0,12,TE,latin_romanized,spk_0009,sess_0010,prompt_grp_010,grp_10,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")
        f.write("tri_v21_000004,shubhodhayam mitrama,1,mitrama,13,20,TE,latin_romanized,spk_0009,sess_0010,prompt_grp_010,grp_10,public_cc_by_4_0,human_elicitation_hyd,verified,agreed,annotator_01,\n")

    val_a = TrilingualDatasetValidator()
    val_a.validate_csv_records(csv_split_a)
    val_b = TrilingualDatasetValidator()
    val_b.validate_csv_records(csv_split_b)
    csv_split_a.unlink()
    csv_split_b.unlink()

    leakage_errors = val_a.check_cross_split_leakage(val_b, "split_a", "split_b")
    assert any("Speaker leakage" in err for err in leakage_errors), f"Self-test 3 failed: expected speaker leakage error, got {leakage_errors}"

    print("All validator self-tests PASSED successfully!")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CodeMix Intelligence Trilingual Datasets")
    parser.add_argument("--csv", type=str, help="Path to token-level CSV dataset")
    parser.add_argument("--jsonl", type=str, help="Path to sentence-level JSONL dataset")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-tests")
    args = parser.parse_args()

    if args.self_test:
        return 0 if run_self_tests() else 1

    if not args.csv and not args.jsonl:
        parser.print_help()
        return 1

    validator = TrilingualDatasetValidator()
    if args.csv:
        validator.validate_csv_records(Path(args.csv))
    if args.jsonl:
        validator.validate_jsonl_file(Path(args.jsonl))

    report = validator.generate_report()
    print(json.dumps(report, indent=2))
    return 0 if report["is_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
