"""Step 1: chat-text normalizer + tokenizer (keeps Indic scripts, URLs, @mentions, #tags intact)."""
import re
import unicodedata

TOKEN_RE = re.compile(
    r"https?://\S+|www\.\S+|@\w+|#\w+"
    r"|[\w\u0900-\u097F\u0C00-\u0C7F]+(?:'[A-Za-z]+)?"
    r"|[^\w\s]",
    re.UNICODE,
)
# English chat slang only (never Hindi/Telugu words, to avoid damaging them)
SLANG = {
    "plz": "please", "pls": "please", "asap": "as soon as possible", "thx": "thanks",
    "u": "you", "ur": "your", "btw": "by the way", "idk": "I don't know",
    "tmrw": "tomorrow", "msg": "message", "bcoz": "because", "coz": "because",
    "gm": "good morning", "gn": "good night",
}
_ELONG = re.compile(r"(.)\1{2,}")
_LONG_RUN = re.compile(r"(.)\1{3,}")   # 4+ repeats are always chat elongation: "bilkullll" -> "bilkul"
_COLLAPSE = re.compile(r"(.)\1+")
_TRAIL_VOWEL = re.compile(r"([aeiouAEIOU])\1{2,}$")
_PROTECTED = ("http", "www", "@", "#")


def tokenize(text: str):
    return TOKEN_RE.findall(unicodedata.normalize("NFC", text))


def _cap_punct_runs(tokens, k=3):
    """"kya....." / "!!!!!!" / emoji spam: keep at most k identical punctuation tokens in a row.
    Long dot runs make the MT model degenerate into endless repetition."""
    out, run = [], 0
    for t in tokens:
        if out and t == out[-1] and len(t) == 1 and not t.isalnum():
            run += 1
            if run >= k:
                continue
        else:
            run = 0
        out.append(t)
    return out


def normalize_tokens(text: str):
    out = []
    for tok in tokenize(text):
        if tok.lower().startswith(_PROTECTED):
            out.append(tok)
            continue
        if len(tok) > 1 and tok.isascii() and tok.isalpha() and tok.isupper():
            tok = tok.lower()  # "NENU REPU" -> "nenu repu" so LID/transliteration see normal words
        if tok.isascii():
            tok = _TRAIL_VOWEL.sub(r"\1", tok)  # "vastanuuuu" -> "vastanu", "soooo" -> "so"
        if tok.isascii():
            tok = _LONG_RUN.sub(r"\1", tok)
        tok = _ELONG.sub(r"\1\1", tok)  # "heyyy" -> "heyy" (keeps legit "yy" in "cheyyaledu")
        low = tok.lower()
        exp = SLANG.get(low) or (SLANG.get(_COLLAPSE.sub(r"\1", low)) if tok.isascii() else None)  # "plzz" -> "please"
        out.extend(exp.split() if exp else [tok])
    return _cap_punct_runs(out)


def detokenize(tokens):
    s = " ".join(tokens)
    s = re.sub(r"\s+([,.!?;:%)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s.strip()


def normalize(text: str) -> str:
    return detokenize(normalize_tokens(text))
