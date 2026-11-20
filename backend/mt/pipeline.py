"""Chains normalize -> LID -> transliterate -> translate. Three strategies for the ablation:
  direct   : raw text straight into the MT model (baseline, needs a source-language hint)
  lid_only : normalize + LID picks the source-language tag, no transliteration
  full     : normalize + LID + transliterate Romanized Indic words + translate (proposed)
  clause   : like full, but every clause (split at , ; . ! ? :) gets its own source-language tag.
             For sentences that mix Hindi and Telugu. Uses `lid_mixed` if one was provided."""
import time
from .lid import is_native_script
from .normalizer import detokenize, normalize_tokens
from .transliterate import NoTransliterator, HI_LEXICON

STRATEGIES = ("direct", "lid_only", "full", "clause")
INDIC = ("HI", "TE")
BREAK = {",", ";", ".", "!", "?", ":"}

# Lexicon overrides LID for words that appear in the curated Hindi lexicon.
# The MuRIL model sometimes misclassifies common Hinglish words (mai, kal, karta, huu)
# as Telugu when they appear in mixed sentences. The lexicon is authoritative for these.
_HI_LEX_KEYS = set(HI_LEXICON.keys())


def split_clauses(tokens):
    """Index lists per clause; pieces of <=2 tokens stay with the previous clause."""
    segs, cur = [], []
    for i, t in enumerate(tokens):
        cur.append(i)
        if t in BREAK:
            segs.append(cur); cur = []
    if cur:
        segs.append(cur)
    merged = []
    for sg in segs:
        if merged and len(sg) <= 2:
            merged[-1] += sg
        else:
            merged.append(sg)
    return merged


def dominant_language(labels, confs):
    # Majority vote by token count, not sum of confidences.
    # Summing confidences lets a few high-confidence Telugu tokens outvote many
    # lower-confidence Hindi tokens in mixed sentences, which transliterates Hindi
    # words into Telugu script and produces garbage translations.
    score = {l: sum(1 for lab in labels if lab == l) for l in INDIC}
    if max(score.values()) == 0:
        return None
    return max(score, key=score.get)


class CodeMixPipeline:
    def __init__(self, lid, translator, translit=None, lid_mixed=None):
        self.lid, self.translator, self.lid_mixed = lid, translator, lid_mixed
        self.translit = translit or NoTransliterator()

    def run(self, text, strategy="full", src_hint="TE", gloss=False):
        if strategy not in STRATEGIES:
            raise ValueError(f"strategy must be one of {STRATEGIES}")
        tm = {}
        t0 = time.perf_counter()
        if strategy == "direct":
            tr = self.translator.translate([text], src_hint)[0]
            tm["translate"] = _ms(t0)
            return {"original": text, "normalized": text, "tokens": [], "dominant_lang": src_hint,
                    "translation": tr, "strategy": strategy, "glosses": {}, "timings_ms": tm}

        tokens = normalize_tokens(text)
        tm["normalize"] = _ms(t0); t0 = time.perf_counter()
        lid = self.lid_mixed if (strategy == "clause" and self.lid_mixed is not None) else self.lid
        labels, confs = lid.predict(tokens)
        tm["lid"] = _ms(t0); t0 = time.perf_counter()

        # Authority Check: The Hindi lexicon is more reliable for common Hinglish words
        # than the MuRIL model when appearing in mixed Hindi+Telugu sentences.
        for i, tok in enumerate(tokens):
            low = tok.lower()
            if low in _HI_LEX_KEYS and labels[i] == "TE":
                labels[i] = "HI"
                confs[i] = 1.0  # boost confidence to override dominant language if needed

        # Token-level native script mapping
        natives = list(tokens)
        if strategy in ("full", "clause"):
            for i, (tok, lab) in enumerate(zip(tokens, labels)):
                if lab in INDIC and not is_native_script(tok):
                    # We use the token's individual label for transliteration
                    # This handles mixed Hindi + Telugu within a single sentence
                    natives[i] = self.translit(tok, lab)
        tm["transliterate"] = _ms(t0); t0 = time.perf_counter()

        normalized = detokenize(tokens)
        dom = dominant_language(labels, confs)
        clauses = None
        if dom is None:  # nothing Indic: already English, skip MT
            translation = normalized
        elif strategy == "clause":
            translation, clauses = self._translate_clauses(tokens, natives, labels, confs)
        else:
            # Full strategy: use token-level native script, but MT still needs a source tag.
            # We use the majority vote dominant language for the source tag.
            translation = self.translator.translate([detokenize(natives)], dom)[0]
        tm["translate"] = _ms(t0)

        glosses = self._gloss(tokens, natives, labels) if (gloss and dom) else {}
        return {
            "original": text, "normalized": normalized, "dominant_lang": dom, "strategy": strategy,
            "tokens": [{"text": t, "lang": l, "conf": round(c, 3), "native": n if n != t else None}
                       for t, l, c, n in zip(tokens, labels, confs, natives)],
            "translation": translation, "glosses": glosses, "timings_ms": tm,
            **({"clauses": clauses} if clauses is not None else {}),
        }

    def _translate_clauses(self, tokens, natives, labels, confs):
        parts = []
        for idx in split_clauses(tokens):
            dom = dominant_language([labels[i] for i in idx], [confs[i] for i in idx])
            parts.append({"text": detokenize([natives[i] for i in idx]), "lang": dom})
        for lang in INDIC:  # one MT call per language
            todo = [p for p in parts if p["lang"] == lang]
            if todo:
                for p, out in zip(todo, self.translator.translate([p["text"] for p in todo], lang)):
                    p["translation"] = out
        for p in parts:
            p.setdefault("translation", p["text"])  # clause without Indic words stays as it is
        return " ".join(p["translation"] for p in parts), parts

    def _gloss(self, tokens, natives, labels, cap=40):
        """Approximate per-word meaning (word-level MT is noisy; show it as a hint, not truth)."""
        out = {}
        for lang in INDIC:
            words = list(dict.fromkeys(n for n, l in zip(natives, labels) if l == lang))[:cap]
            if words:
                for w, g in zip(words, self.translator.translate(words, lang)):
                    out[w] = g
        return {t: out[n] for t, n, l in zip(tokens, natives, labels) if l in INDIC and n in out}


def _ms(t0):
    return round((time.perf_counter() - t0) * 1000, 1)


def build_pipeline(lid_dir=None, translit_backend="auto"):
    """Real models (needs torch/transformers + the fine-tuned MuRIL folder)."""
    import os
    from .lid import MurilLID
    from .transliterate import build_transliterator
    from .translator import IndicTrans2Translator
    mixed_dir = os.getenv("LID_V2_DIR")  # optional second LID model trained on mixed HI+TE sentences
    return CodeMixPipeline(MurilLID(lid_dir), IndicTrans2Translator(), build_transliterator(translit_backend),
                           lid_mixed=MurilLID(mixed_dir) if mixed_dir else None)
