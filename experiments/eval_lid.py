"""Token-level LID metrics. Input: TSV, one 'token<TAB>label' per line, blank line between sentences."""
import argparse
from collections import Counter
from backend.mt.lid import LABELS


def read_conll(path):
    sents, cur = [], []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            if cur:
                sents.append(cur); cur = []
        else:
            tok, lab = line.split("\t")
            cur.append((tok, lab.upper()))
    if cur:
        sents.append(cur)
    return sents


def prf(gold, pred, labels=LABELS):
    out = {}
    for l in labels:
        tp = sum(g == l and p == l for g, p in zip(gold, pred))
        fp = sum(g != l and p == l for g, p in zip(gold, pred))
        fn = sum(g == l and p != l for g, p in zip(gold, pred))
        P = tp / (tp + fp) if tp + fp else 0.0
        R = tp / (tp + fn) if tp + fn else 0.0
        out[l] = {"P": round(P, 3), "R": round(R, 3), "F1": round(2 * P * R / (P + R), 3) if P + R else 0.0}
    out["macro_F1"] = round(sum(out[l]["F1"] for l in labels) / len(labels), 3)
    out["confusions"] = Counter((g, p) for g, p in zip(gold, pred) if g != p).most_common(8)
    return out


def evaluate_lid(lid, sents):
    gold, pred = [], []
    for s in sents:
        toks = [t for t, _ in s]
        labs, _ = lid.predict(toks)
        gold += [l for _, l in s]; pred += labs
    return prf(gold, pred)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tsv", required=True)
    from backend.mt.lid import MurilLID
    print(evaluate_lid(MurilLID(), read_conll(ap.parse_args().tsv)))
