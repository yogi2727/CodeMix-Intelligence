import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.mt.normalizer import normalize, tokenize
from backend.mt.pipeline import CodeMixPipeline, dominant_language
from backend.mt.lid import rule_label
from backend.mt import router as R
from experiments.eval_lid import prf

TE = {"nenu", "repu", "ki", "vastanu", "cheyyaledu"}

class StubLID:
    def predict(self, toks):
        labs = [rule_label(t) or ("TE" if t.lower() in TE else "EN") for t in toks]
        return labs, [0.9] * len(toks)

class StubTranslator:
    def translate(self, sents, lang):
        return [f"[{lang}] {s}" for s in sents]

class StubXlit:
    def __call__(self, w, lang): return f"<{w}>"

def pipe():
    return CodeMixPipeline(StubLID(), StubTranslator(), StubXlit())

def test_normalizer():
    assert normalize("heyyyy plz come") == "hey please come" and normalize("heyyy") == "heyy"
    assert tokenize("cheyyaledu 😀 @sam #fun") == ["cheyyaledu", "😀", "@sam", "#fun"]
    assert normalize("Hello , world !") == "Hello, world!"
    assert tokenize("నేను repu వస్తాను") == ["నేను", "repu", "వస్తాను"]  # matras not split

def test_rules():
    assert rule_label("నేను") == "TE" and rule_label("मैं") == "HI"
    assert rule_label("😀") == "OTHER" and rule_label("college") is None

def test_full_pipeline():
    r = pipe().run("Nenu repu college ki vastanu, but assignment complete cheyyaledu")
    langs = {t["text"]: t["lang"] for t in r["tokens"]}
    assert langs["Nenu"] == "TE" and langs["college"] == "EN" and langs[","] == "OTHER"
    assert r["dominant_lang"] == "TE" and r["translation"].startswith("[TE] <Nenu>")
    assert "college" in r["translation"] and "<college>" not in r["translation"]  # English untouched

def test_lid_only_has_no_transliteration():
    r = pipe().run("Nenu repu vastanu", strategy="lid_only")
    assert "<" not in r["translation"]

def test_english_skips_mt():
    r = pipe().run("see you at the library")
    assert r["dominant_lang"] is None and r["translation"] == "see you at the library"

def test_direct_uses_hint():
    assert pipe().run("anything", strategy="direct", src_hint="HI")["translation"] == "[HI] anything"

def test_gloss():
    r = pipe().run("Nenu repu college", gloss=True)
    assert "Nenu" in r["glosses"] and "college" not in r["glosses"]

def test_dominant():
    assert dominant_language(["HI", "TE", "TE", "EN"], [1, .5, .6, 1]) == "TE"
    assert dominant_language(["EN", "OTHER"], [1, 1]) is None

def test_api():
    app = FastAPI(); app.include_router(R.router); R.set_pipeline(pipe())
    c = TestClient(app)
    assert c.get("/api/mt/translate/health").json()["status"] == "ok"
    j = c.post("/api/mt/translate", json={"text": "Nenu repu college", "gloss": True}).json()
    assert j["dominant_lang"] == "TE" and j["timings_ms"]
    assert c.post("/api/mt/translate", json={"text": ""}).status_code == 422

def test_prf():
    m = prf(["EN", "TE", "TE"], ["EN", "TE", "EN"])
    assert m["TE"]["P"] == 1.0 and m["TE"]["R"] == 0.5


def test_caps_and_elongation():
    assert normalize("NENU REPU college ki vastanuuuu plz") == "nenu repu college ki vastanu please"
    assert normalize("soooo good") == "so good"

def test_hinglish_lexicon():
    from backend.mt.transliterate import HinglishTransliterator
    h = HinglishTransliterator()
    assert h("kya", "HI") == "क्या" and h("Bhej", "HI") == "भेज" and h("hoon", "HI") == "हूँ"
    assert h("college", "EN") == "college"


def test_more_noise():
    assert normalize("bilkullll nahi plzz") == "bilkul nahi please"
    assert tokenize("cheyyaledu")[0] == "cheyyaledu" and normalize("cheyyaledu") == "cheyyaledu"


def test_punct_cap():
    assert normalize("kya..... hai!!!!!!") == "kya... hai!!!"
    assert normalize("wait... ok") == "wait... ok"


class StubLID2:
    HI = {"tum", "bhi", "aao"}
    def predict(self, toks):
        labs = [rule_label(t) or ("TE" if t.lower() in TE else "HI" if t.lower() in self.HI else "EN") for t in toks]
        return labs, [0.9] * len(toks)

def test_clause_strategy():
    p = CodeMixPipeline(StubLID2(), StubTranslator(), StubXlit())
    r = p.run("Nenu repu vastanu, tum bhi aao", strategy="clause")
    assert [c["lang"] for c in r["clauses"]] == ["TE", "HI"]
    assert r["translation"] == "[TE] <Nenu> <repu> <vastanu>, [HI] <tum> <bhi> <aao>"

def test_split_clauses_merges_tiny_pieces():
    from backend.mt.pipeline import split_clauses
    assert split_clauses(["a", "b", ",", "c", "d", "e"]) == [[0, 1, 2], [3, 4, 5]]
    assert split_clauses(["a", "b", "c", ",", "ok", "."]) == [[0, 1, 2, 3, 4, 5]]

def test_te_lexicon_file():
    from backend.mt.transliterate import load_lexicon, TE_LEXICON_PATH
    assert load_lexicon(TE_LEXICON_PATH)["veldam"] == "వెళ్దాం"
