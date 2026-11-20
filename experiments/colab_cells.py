# Paste these into your ONE existing Colab notebook, one block per cell (the "# %%" lines mark cells).

# %% Cell 1 - install
# !pip -q install transformers sentencepiece sacrebleu indic-transliteration
# !pip -q install git+https://github.com/VarunGumma/IndicTransToolkit.git
# Optional (better transliteration, heavy): !pip -q install ai4bharat-transliteration

# %% Cell 2 - paths (unzip codemix-translate.zip into Drive first, point LID_MODEL_DIR to your fine-tuned MuRIL folder)
import os, sys
from google.colab import drive
drive.mount('/content/drive')
PROJECT = "/content/drive/MyDrive/codemix-translate"          # <- change
os.environ["LID_MODEL_DIR"] = "/content/drive/MyDrive/muril-lid"  # <- change
sys.path.insert(0, PROJECT); os.chdir(PROJECT)

# %% Cell 3 - build pipeline (downloads IndicTrans2 the first time)
from backend.mt.pipeline import build_pipeline
pipe = build_pipeline()
print("transliterator:", pipe.translit.name)

# %% Cell 4 - demo
import json
r = pipe.run("Nenu repu college ki vastanu, but assignment complete cheyyaledu", gloss=True)
print(r["translation"]); print(json.dumps(r["tokens"], ensure_ascii=False, indent=1)[:800]); print(r["timings_ms"])

# %% Cell 5 - ablation: direct vs lid_only vs full
import pandas as pd
from experiments.eval_translation import evaluate, per_language
df = pd.read_csv("data/test_sanity.csv")        # swap in a bigger CSV (lang,src,ref) when you have one
table, detail = evaluate(pipe, df)
display(table); display(per_language(detail))
detail.to_csv("results_translation.csv", index=False)

# %% Cell 6 - error analysis: where does 'full' lose to 'direct' (and the reverse)?
detail["gain_full_vs_direct"] = detail["chrF_full"] - detail["chrF_direct"]
display(detail.sort_values("gain_full_vs_direct")[["src","ref","direct","full","gain_full_vs_direct"]].head(5))
display(detail.sort_values("gain_full_vs_direct")[["src","ref","direct","full","gain_full_vs_direct"]].tail(5))

# %% Cell 7 - LID metrics (needs a TSV: token<TAB>label, blank line between sentences; use your held-out test split)
from experiments.eval_lid import read_conll, evaluate_lid
print(evaluate_lid(pipe.lid, read_conll("data/lid_test.tsv")))

# %% Cell 8 - robustness: does noisy chat text hurt? (elongation, caps, slang)
noisy = ["NENU REPU college ki vastanuuuu plz", "kal meeting hai pls slides bhej dena asap"]
for s in noisy:
    print(s, "->", pipe.run(s)["translation"])
