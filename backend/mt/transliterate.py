"""Step 3: Romanized Hindi/Telugu word -> native script, so the MT model sees a script it knows."""
import csv
import os
import re


class NoTransliterator:
    name = "none"
    def __call__(self, word, lang):
        return word


# Common Hinglish words (lexicon first, because schwa deletion / spelling variation defeats pure rules).
HI_LEXICON = {
    # pronouns / verbs be
    "main": "मैं", "mai": "मैं", "hum": "हम", "ham": "हम", "tum": "तुम", "aap": "आप", "tu": "तू",
    "woh": "वो", "wo": "वो", "vo": "वो", "yeh": "यह", "ye": "ये", "is": "इस", "us": "उस",
    "mujhe": "मुझे", "tumhe": "तुम्हें", "hume": "हमें", "humein": "हमें", "usse": "उससे", "mujhse": "मुझसे",
    "mera": "मेरा", "meri": "मेरी", "mere": "मेरे", "tera": "तेरा", "tumhara": "तुम्हारा", "tumhari": "तुम्हारी",
    "hamara": "हमारा", "uska": "उसका", "uski": "उसकी", "tumne": "तुमने", "usne": "उसने", "maine": "मैंने",
    "hoon": "हूँ", "hu": "हूँ", "huu": "हूँ", "hai": "है", "hain": "हैं", "ho": "हो", "tha": "था", "thi": "थी", "the": "थे",
    "hoga": "होगा", "hogi": "होगी", "hui": "हुई", "hua": "हुआ", "hue": "हुए", "gaya": "गया", "gayi": "गई", "gaye": "गए",
    # question words
    "kya": "क्या", "kab": "कब", "kahan": "कहाँ", "kaise": "कैसे", "kyun": "क्यों", "kyu": "क्यों", "kaun": "कौन",
    "kitna": "कितना", "kitne": "कितने", "kitni": "कितनी", "kaha": "कहाँ", "kidhar": "किधर",
    # quantity / quality
    "kuch": "कुछ", "koi": "कोई", "sab": "सब", "bahut": "बहुत", "bohot": "बहुत", "thoda": "थोड़ा", "thodi": "थोड़ी",
    "zyada": "ज़्यादा", "jyada": "ज़्यादा", "kam": "कम", "accha": "अच्छा", "acha": "अच्छा", "achha": "अच्छा",
    "bura": "बुरा", "bilkul": "बिल्कुल", "sach": "सच", "theek": "ठीक", "thik": "ठीक", "sahi": "सही",
    "zaroor": "ज़रूर", "jaldi": "जल्दी", "mast": "मस्त", "kharab": "खराब", "naraz": "नाराज़",
    # particles / postpositions
    "nahi": "नहीं", "nahin": "नहीं", "na": "ना", "mat": "मत", "aur": "और", "ya": "या", "lekin": "लेकिन",
    "par": "पर", "pe": "पे", "magar": "मगर", "toh": "तो", "to": "तो", "bhi": "भी", "hi": "ही", "se": "से",
    "ko": "को", "ka": "का", "ki": "की", "ke": "के", "mein": "में", "me": "में", "tak": "तक", "liye": "लिए",
    "saath": "साथ", "baad": "बाद", "pehle": "पहले", "paas": "पास", "isliye": "इसलिए", "kyunki": "क्योंकि",
    "agar": "अगर", "phir": "फिर", "fir": "फिर", "ab": "अब", "tab": "तब", "jab": "जब", "wala": "वाला",
    "wali": "वाली", "wale": "वाले", "aisa": "ऐसा", "waisa": "वैसा", "jaisa": "जैसा",
    # time / place
    "abhi": "अभी", "aaj": "आज", "kal": "कल", "parso": "परसों", "subah": "सुबह", "shaam": "शाम", "raat": "रात",
    "din": "दिन", "der": "देर", "hafte": "हफ्ते", "hafta": "हफ्ता", "saal": "साल", "mahina": "महीना",
    "yahan": "यहाँ", "wahan": "वहाँ", "idhar": "इधर", "udhar": "उधर", "ghar": "घर", "bahar": "बाहर", "andar": "अंदर",
    "raste": "रास्ते", "wapas": "वापस",
    # verbs
    "aao": "आओ", "aaoge": "आओगे", "aana": "आना", "aaunga": "आऊँगा", "aa": "आ", "jao": "जाओ", "jaana": "जाना",
    "ja": "जा", "jaunga": "जाऊँगा", "raha": "रहा", "rahi": "रही", "rahe": "रहे", "chal": "चल", "chalo": "चलो",
    "chalte": "चलते", "chalo": "चलो", "karo": "करो", "karna": "करना", "kar": "कर", "karta": "करता", "kiya": "किया", "karunga": "करूँगा",
    "karenge": "करेंगे", "bol": "बोल", "bolo": "बोलो", "bata": "बता", "batao": "बताओ", "dekh": "देख", "dekho": "देखो",
    "dekhi": "देखी", "suno": "सुनो", "samajh": "समझ", "samjha": "समझा", "pata": "पता", "padhna": "पढ़ना",
    "bhej": "भेज", "dena": "देना", "do": "दो", "de": "दे", "dijiye": "दीजिए", "lena": "लेना", "le": "ले", "lo": "लो",
    "milna": "मिलना", "mila": "मिला", "milte": "मिलते", "milega": "मिलेगा", "khana": "खाना", "khaya": "खाया",
    "peena": "पीना", "sona": "सोना", "uthna": "उठना", "chahiye": "चाहिए", "chahta": "चाहता", "chahti": "चाहती",
    "sakta": "सकता", "sakti": "सकती", "sakte": "सकते", "pahunch": "पहुँच", "chhod": "छोड़", "banaun": "बनाऊँ",
    "maza": "मज़ा", "samay": "समय", "pila": "पिला",
    # nouns
    "kaam": "काम", "paisa": "पैसा", "paise": "पैसे", "dost": "दोस्त", "yaar": "यार", "bhai": "भाई", "padhai": "पढ़ाई",
    "dimaag": "दिमाग", "chai": "चाय", "khana": "खाना", "bhookh": "भूख", "pyaas": "प्यास", "thand": "ठंड",
    # numbers
    "ek": "एक", "teen": "तीन", "char": "चार", "paanch": "पाँच", "dus": "दस",
}


def _hinglish_to_itrans(w):
    w = w.lower().replace("w", "v").replace("z", "j").replace("q", "k").replace("x", "ksh").replace("f", "ph")
    w = w.replace("ch", "\u0001")
    w = re.sub(r"c(?=[ei])", "s", w).replace("c", "k").replace("\u0001", "ch")
    if len(w) > 2 and re.search(r"[^aeiou]a$", w):  # Hinglish final 'a' is long: kya -> kyaa
        w += "a"
    return w


class HinglishTransliterator:
    """Lexicon of common Hinglish words, then ITRANS-with-heuristics fallback for unseen words."""
    name = "hinglish_rule"
    def __init__(self):
        self.s = None

    def __call__(self, word, lang="HI"):
        if lang != "HI":
            return word
        w = word.lower()
        if w in HI_LEXICON:
            return HI_LEXICON[w]
        try:
            if self.s is None:
                from indic_transliteration import sanscript
                self.s = sanscript
            return self.s.transliterate(_hinglish_to_itrans(w), self.s.ITRANS, self.s.DEVANAGARI)
        except Exception:
            return word


def load_lexicon(path):
    """CSV with header roman,native -> {roman: native}. Missing file = empty lexicon."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {r["roman"].strip().lower(): r["native"].strip() for r in csv.DictReader(f) if r.get("native", "").strip()}


TE_LEXICON_PATH = os.path.join(os.path.dirname(__file__), "te_lexicon.csv")


class RuleTransliterator:
    """Fallback without a neural model. Telugu: ITRANS -> Telugu. Hindi: Hinglish lexicon + heuristics."""
    name = "rule"
    def __init__(self):
        from indic_transliteration import sanscript
        self.s = sanscript
        self.hi = HinglishTransliterator()
        self.te_lex = load_lexicon(TE_LEXICON_PATH)  # curated Telugu spellings override the ITRANS rules

    def __call__(self, word, lang):
        if lang == "HI":
            return self.hi(word, lang)
        if lang != "TE":
            return word
        w = word.lower()
        if w in self.te_lex:
            return self.te_lex[w]
        return self.s.transliterate(w.replace("w", "v"), self.s.ITRANS, self.s.TELUGU)


class IndicXlitTransliterator:
    """Best option: AI4Bharat IndicXlit (pip install ai4bharat-transliteration)."""
    name = "indicxlit"
    def __init__(self):
        from ai4bharat.transliteration import XlitEngine
        self._Engine, self.engines = XlitEngine, {}

    def __call__(self, word, lang):
        code = {"HI": "hi", "TE": "te"}.get(lang)
        if code is None:
            return word
        if code not in self.engines:
            self.engines[code] = self._Engine(code, beam_width=10, src_script_type="en")
        out = self.engines[code].translit_word(word, topk=1)
        return out[code][0] if out.get(code) else word


def build_transliterator(backend="auto"):
    if backend == "none":
        return NoTransliterator()
    if backend in ("auto", "indicxlit"):
        try:
            return IndicXlitTransliterator()
        except Exception:
            if backend == "indicxlit":
                raise
    return RuleTransliterator()
