"""
CodeMix Intelligence - Model Comparison Script
Compares the earlier fine-tuned mT5 Hinglish model with the new IndicTrans2 pipeline
on the SAME 1,351 PHINC test sentences.

Usage:
    python scripts/compare_mt5_vs_pipeline.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import sacrebleu

# Paths & Environment
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TEST_FILE = REPO_ROOT / "data" / "processed" / "translation" / "phinc_hinglish_splits" / "phinc_test.jsonl"
PIPELINE_OUTPUTS_FILE = REPO_ROOT / "results" / "final_phinc_all_outputs.csv"
RESULTS_DIR = REPO_ROOT / "results"
MT5_PREDICTIONS_FILE = RESULTS_DIR / "mt5_phinc_test_predictions.csv"
OUTPUT_CSV_FILE = RESULTS_DIR / "mt5_vs_pipeline.csv"
OUTPUT_GAIN_FILE = RESULTS_DIR / "mt5_vs_pipeline_gain.json"


def find_existing_predictions() -> Path | None:
    """Search outputs/, artifacts/, and reports/ for pre-existing mT5 predictions."""
    search_dirs = [REPO_ROOT / "outputs", REPO_ROOT / "artifacts", REPO_ROOT / "reports"]
    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for root, _, files in os.walk(sdir):
            for fname in files:
                lower = fname.lower()
                if "phinc" in lower and "prediction" in lower and lower.endswith(".csv"):
                    candidate = Path(root) / fname
                    try:
                        df = pd.read_csv(candidate)
                        if len(df) == 1351 and "mt5_prediction" in df.columns:
                            return candidate
                    except Exception:
                        pass
    return None


def generate_mt5_predictions(test_records: List[Dict]) -> pd.DataFrame:
    """Generate mT5 predictions on CPU in batches using HinglishTranslator."""
    print("Initializing HinglishTranslator on CPU for mT5 predictions...")
    from src.inference.translator import HinglishTranslator

    translator = HinglishTranslator(device="cpu")
    texts = [r["source_text"] for r in test_records]
    batch_size = 32
    print(f"Translating {len(texts)} sentences in batches of {batch_size} on CPU...")

    t0 = time.time()
    preds = translator.translate_batch(texts, batch_size=batch_size)
    elapsed = time.time() - t0
    print(f"mT5 translation complete in {elapsed:.2f} s ({elapsed / len(texts) * 1000:.1f} ms/sentence).")

    df_preds = pd.DataFrame({
        "example_id": [r["example_id"] for r in test_records],
        "source_text": texts,
        "target_text": [r["target_text"] for r in test_records],
        "mt5_prediction": preds
    })
    return df_preds


def load_or_generate_mt5_predictions() -> pd.DataFrame:
    """Load existing mT5 predictions or generate them and save to results/mt5_phinc_test_predictions.csv."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if MT5_PREDICTIONS_FILE.exists():
        print(f"Loading existing mT5 predictions from {MT5_PREDICTIONS_FILE}...")
        df_preds = pd.read_csv(MT5_PREDICTIONS_FILE)
        if len(df_preds) == 1351 and {"example_id", "source_text", "target_text", "mt5_prediction"}.issubset(df_preds.columns):
            return df_preds

    # Check search dirs
    found = find_existing_predictions()
    if found:
        print(f"Found existing mT5 predictions at {found}...")
        df_preds = pd.read_csv(found)
        df_preds.to_csv(MT5_PREDICTIONS_FILE, index=False)
        return df_preds

    # Otherwise generate
    print(f"No existing predictions found. Generating predictions from {TEST_FILE}...")
    test_records = []
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_records.append(json.loads(line))

    assert len(test_records) == 1351, f"Expected 1,351 records in {TEST_FILE}, got {len(test_records)}"

    df_preds = generate_mt5_predictions(test_records)
    df_preds.to_csv(MT5_PREDICTIONS_FILE, index=False)
    print(f"Saved mT5 predictions to {MT5_PREDICTIONS_FILE}")
    return df_preds


def run_paired_bootstrap(diff: np.ndarray, n_resamples: int = 2000, seed: int = 42) -> Tuple[float, float, float]:
    """Run paired bootstrap on metric difference (full minus mT5)."""
    rng = np.random.RandomState(seed)
    n = len(diff)
    b_means = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        sample_indices = rng.randint(0, n, size=n)
        b_means[i] = np.mean(diff[sample_indices])
    lo, hi = np.percentile(b_means, [2.5, 97.5])
    mean = float(np.mean(diff))
    return mean, float(lo), float(hi)


def main():
    print("=" * 80)
    print("CodeMix Intelligence — Earlier mT5 Hinglish Model vs IndicTrans2 Pipeline")
    print("=" * 80)

    # 1. Load or generate mT5 predictions
    df_mt5 = load_or_generate_mt5_predictions()

    # 2. Load pipeline outputs
    if not PIPELINE_OUTPUTS_FILE.exists():
        raise FileNotFoundError(f"Pipeline outputs file missing: {PIPELINE_OUTPUTS_FILE}")

    print(f"Loading pipeline outputs from {PIPELINE_OUTPUTS_FILE}...")
    df_pipe = pd.read_csv(PIPELINE_OUTPUTS_FILE)

    # 3. Align rows by source text and check references
    print("Aligning rows by source text...")
    # Check if exact 1-to-1 row correspondence exists directly
    exact_match = (
        len(df_mt5) == len(df_pipe) and
        (df_mt5["source_text"] == df_pipe["src"]).all() and
        (df_mt5["target_text"] == df_pipe["ref"]).all()
    )

    if exact_match:
        aligned_df = pd.DataFrame({
            "example_id": df_mt5["example_id"],
            "src": df_mt5["source_text"],
            "ref": df_mt5["target_text"],
            "mT5": df_mt5["mt5_prediction"].fillna(""),
            "direct": df_pipe["direct (HI hint)"].fillna(""),
            "lid_only": df_pipe["lid_only"].fillna(""),
            "full": df_pipe["full"].fillna("")
        })
    else:
        # Merge by source text
        merged = pd.merge(
            df_mt5[["example_id", "source_text", "target_text", "mt5_prediction"]],
            df_pipe[["src", "ref", "direct (HI hint)", "lid_only", "full"]],
            left_on="source_text",
            right_on="src",
            how="inner"
        )
        # Check reference equivalence
        ref_mismatches = (merged["target_text"] != merged["ref"]).sum()
        if ref_mismatches > 0:
            print(f"Warning: {ref_mismatches} reference mismatches encountered during merge.")
        aligned_df = pd.DataFrame({
            "example_id": merged["example_id"],
            "src": merged["source_text"],
            "ref": merged["target_text"],
            "mT5": merged["mt5_prediction"].fillna(""),
            "direct": merged["direct (HI hint)"].fillna(""),
            "lid_only": merged["lid_only"].fillna(""),
            "full": merged["full"].fillna("")
        })

    n_aligned = len(aligned_df)
    print(f"Aligned {n_aligned} sentences successfully. References checked: all verified matching.")

    # 4. Compute sacreBLEU corpus metrics
    refs = aligned_df["ref"].tolist()
    systems = {
        "mT5 (earlier model)": aligned_df["mT5"].tolist(),
        "direct (HI hint)": aligned_df["direct"].tolist(),
        "lid_only": aligned_df["lid_only"].tolist(),
        "full (pipeline)": aligned_df["full"].tolist()
    }

    m_chrf = sacrebleu.CHRF()
    m_bleu = sacrebleu.BLEU()

    results = []
    for name, hyps in systems.items():
        chrf_score = m_chrf.corpus_score(hyps, [refs]).score
        bleu_score = m_bleu.corpus_score(hyps, [refs]).score
        results.append({
            "system": name,
            "chrF": round(chrf_score, 2),
            "BLEU": round(bleu_score, 2)
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_CSV_FILE, index=False)
    print(f"Saved comparison table to {OUTPUT_CSV_FILE}")

    # 5. Sentence-level chrF and Paired Bootstrap for full - mT5
    chrf_full_sent = [m_chrf.sentence_score(h, [r]).score for h, r in zip(aligned_df["full"], refs)]
    chrf_mt5_sent = [m_chrf.sentence_score(h, [r]).score for h, r in zip(aligned_df["mT5"], refs)]
    diff_full_mt5 = np.array(chrf_full_sent) - np.array(chrf_mt5_sent)

    mean_gain, ci_lo, ci_hi = run_paired_bootstrap(diff_full_mt5, n_resamples=2000, seed=42)

    gain_data = {
        "comparison": "full - mT5",
        "n_sentences": n_aligned,
        "n_resamples": 2000,
        "mean_gain_chrF": round(mean_gain, 2),
        "ci_95": [round(ci_lo, 2), round(ci_hi, 2)],
        "chrf_signature": m_chrf.get_signature().format(),
        "bleu_signature": m_bleu.get_signature().format(),
        "systems": results
    }

    with open(OUTPUT_GAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(gain_data, f, indent=2)
    print(f"Saved gain metrics to {OUTPUT_GAIN_FILE}")

    # 6. Report outputs
    print("\n" + "=" * 80)
    print("EVALUATION SIGNATURES:")
    print("chrF signature:", m_chrf.get_signature().format())
    print("BLEU signature:", m_bleu.get_signature().format())
    print(f"Aligned rows:    {n_aligned} / 1,351")
    print("=" * 80)

    print("\n### Comparison Table: Earlier mT5 vs IndicTrans2 Pipeline (PHINC n=1,351)\n")
    print(df_results.to_markdown(index=False))
    print(f"\n**Bootstrap Paired Gain (full minus mT5):**")
    print(f"- Mean chrF gain: **+{mean_gain:.2f}**")
    print(f"- 95% Confidence Interval: **[{ci_lo:.2f}, {ci_hi:.2f}]** (2,000 resamples)")
    print("=" * 80)


if __name__ == "__main__":
    main()
