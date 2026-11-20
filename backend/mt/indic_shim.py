"""Pure-Python stand-in for IndicTransToolkit.IndicProcessor (no C++ compiler needed, e.g. on Windows).

What the real processor does that matters here:
  1. IndicTrans2 was trained on text where every Indic script is first mapped to Devanagari
     (Unicode block offsets, as in indic_nlp's UnicodeIndicTransliterator). Telugu input MUST be mapped,
     otherwise the model produces nonsense.
  2. It prepends the language tags: "<src_lang> <tgt_lang> <sentence>".
It does NOT protect numbers/URLs/entities with placeholders, so results can differ slightly from the toolkit
(mention this in the report)."""
import re

try:  # the real toolkit detokenizes English with Moses; sacremoses gives the same result
    from sacremoses import MosesDetokenizer
    _DETOK = MosesDetokenizer(lang="en")
except Exception:
    _DETOK = None
_CONTRACTION = re.compile(r"\s+(['\u2019](?:s|t|ll|re|ve|d|m)\b)")   # "I 'll" -> "I'll", "haven 't" -> "haven't"


def clean_english(s):
    s = re.sub(r"\s+", " ", s).strip()
    if _DETOK is not None:
        s = _DETOK.detokenize(s.split(" "))
    return _CONTRACTION.sub(r"\1", s)


_DEVA_BASE = 0x0900
_BLOCK = {"ben_Beng": 0x0980, "pan_Guru": 0x0A00, "guj_Gujr": 0x0A80, "ory_Orya": 0x0B00, "asm_Beng": 0x0980,
          "tam_Taml": 0x0B80, "tel_Telu": 0x0C00, "kan_Knda": 0x0C80, "mal_Mlym": 0x0D00}


def to_devanagari(text, lang):
    base = _BLOCK.get(lang)
    if base is None:           # Devanagari (hin_Deva, ...) or Latin: nothing to do
        return text
    return "".join(chr(_DEVA_BASE + ord(c) - base) if base <= ord(c) < base + 0x80 else c for c in text)


class IndicProcessor:
    def __init__(self, inference=True):
        self.inference = inference

    def preprocess_batch(self, batch, src_lang, tgt_lang=None, is_target=False, visualize=False):
        out = []
        for s in batch:
            s = re.sub(r"\s+", " ", s).strip()
            if is_target:
                out.append(s)
            else:
                out.append(f"{src_lang} {tgt_lang} {to_devanagari(s, src_lang)}")
        return out

    def postprocess_batch(self, sents, lang="eng_Latn"):
        return [clean_english(s) for s in sents]
