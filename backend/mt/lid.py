"""Step 2: token-level language ID. Rules for scripts/punctuation, fine-tuned MuRIL for Latin-script words."""
import os
import re

LABELS = ("EN", "HI", "TE", "OTHER")
_DEV = re.compile(r"[\u0900-\u097F]")
_TEL = re.compile(r"[\u0C00-\u0C7F]")


def rule_label(tok: str):
    """Return a label if the token is decidable without a model, else None."""
    if _TEL.search(tok):
        return "TE"
    if _DEV.search(tok):
        return "HI"
    if tok.lower().startswith(("http", "www", "@", "#")) or not any(c.isalpha() for c in tok):
        return "OTHER"
    return None


def is_native_script(tok: str) -> bool:
    return bool(_TEL.search(tok) or _DEV.search(tok))


class RuleLID:
    """Fallback with no model: script rules only, Latin words default to EN."""
    def predict(self, tokens):
        labels, confs = [], []
        for t in tokens:
            r = rule_label(t)
            labels.append(r or "EN")
            confs.append(1.0 if r else 0.5)
        return labels, confs


class MurilLID:
    def __init__(self, model_dir=None, device=None, max_len=256):
        import torch
        from transformers import AutoModelForTokenClassification, AutoTokenizer
        model_dir = model_dir or os.getenv("LID_MODEL_DIR", "models/muril-lid")
        self.torch, self.max_len = torch, max_len
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForTokenClassification.from_pretrained(model_dir).to(self.device).eval()
        self.id2label = {int(i): re.sub(r"^[BI]-", "", l).upper() for i, l in self.model.config.id2label.items()}

    def predict(self, tokens):
        if not tokens:
            return [], []
        torch = self.torch
        enc = self.tok(tokens, is_split_into_words=True, return_tensors="pt",
                       truncation=True, max_length=self.max_len)
        word_ids = enc.word_ids()
        with torch.no_grad():
            logits = self.model(**{k: v.to(self.device) for k, v in enc.items()}).logits[0]
        probs = logits.softmax(-1).cpu()
        labels, confs = ["EN"] * len(tokens), [0.0] * len(tokens)
        seen = set()
        for pos, wid in enumerate(word_ids):
            if wid is None or wid in seen:
                continue
            seen.add(wid)  # first sub-token represents the word
            p, i = probs[pos].max(-1)
            labels[wid], confs[wid] = self.id2label[int(i)], float(p)
        for k, t in enumerate(tokens):  # rules override the model where they are certain
            r = rule_label(t)
            if r:
                labels[k], confs[k] = r, 1.0
        return labels, confs
