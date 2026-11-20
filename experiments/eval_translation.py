"""Ablation: direct vs lid_only vs full on a CSV with columns lang(te|hi), src, ref."""
import argparse
import time
import pandas as pd
import sacrebleu
from backend.mt.pipeline import STRATEGIES


def evaluate(pipe, df, strategies=STRATEGIES):
    rows, outputs = [], {}
    refs = df["ref"].tolist()
    for s in strategies:
        t0, hyps = time.perf_counter(), []
        for r in df.itertuples():
            hyps.append(pipe.run(r.src, strategy=s, src_hint=r.lang.upper())["translation"])
        ms = (time.perf_counter() - t0) * 1000 / len(df)
        rows.append({"strategy": s,
                     "chrF": round(sacrebleu.corpus_chrf(hyps, [refs]).score, 2),
                     "BLEU": round(sacrebleu.corpus_bleu(hyps, [refs]).score, 2),
                     "ms/sentence": round(ms, 1)})
        outputs[s] = hyps
    table = pd.DataFrame(rows).set_index("strategy")
    detail = df.copy()
    for s, h in outputs.items():
        detail[s] = h
        detail[f"chrF_{s}"] = [round(sacrebleu.sentence_chrf(x, [y]).score, 1) for x, y in zip(h, refs)]
    return table, detail


def per_language(df_detail, strategies=STRATEGIES):
    return df_detail.groupby("lang")[[f"chrF_{s}" for s in strategies]].mean().round(2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/test_sanity.csv")
    ap.add_argument("--out", default="results_translation.csv")
    a = ap.parse_args()
    from backend.mt.pipeline import build_pipeline
    table, detail = evaluate(build_pipeline(), pd.read_csv(a.csv))
    print(table, "\n", per_language(detail))
    detail.to_csv(a.out, index=False)
