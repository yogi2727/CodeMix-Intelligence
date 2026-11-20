import glob, json, os, re, time
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

ROOT = os.path.join("artifacts", "models", "mt5_hinglish_translation")
TEST = os.path.join("data", "processed", "translation", "phinc_hinglish_splits", "phinc_test.jsonl")
OUT = os.path.join("results", "mt5_phinc_test_predictions.csv")
PREFIX = "translate Hinglish to English: "
BATCH = 16

cfgs = glob.glob(os.path.join(ROOT, "**", "config.json"), recursive=True)
assert cfgs, "No config.json found under " + ROOT
cfgs.sort(key=lambda p: (0 if re.search("best|final", p, re.I) else 1, len(p)))
model_dir = os.path.dirname(cfgs[0])
print("model folder:", model_dir, "| other candidates:", [os.path.dirname(c) for c in cfgs[1:4]])
tok = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSeq2SeqLM.from_pretrained(model_dir).eval()
torch.set_num_threads(max(1, os.cpu_count() or 1))

df = pd.DataFrame([json.loads(l) for l in open(TEST, encoding="utf-8") if l.strip()])
if "quality_status" in df:
    df = df[df.quality_status == "retained"]
df = df.reset_index(drop=True)
print(len(df), "test sentences")
os.makedirs("results", exist_ok=True)
done = {}
if os.path.exists(OUT):
    old = pd.read_csv(OUT).fillna("")
    done = dict(zip(old.example_id, old.mt5_prediction))
    print("resuming:", len(done), "already done")
todo = [i for i in range(len(df)) if df.example_id[i] not in done]
todo.sort(key=lambda i: len(str(df.source_text[i])))
t0 = time.time()
for b in range(0, len(todo), BATCH):
    idx = todo[b:b + BATCH]
    enc = tok([PREFIX + str(df.source_text[i]) for i in idx], max_length=128, truncation=True, padding=True, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**enc, num_beams=4, max_new_tokens=128)
    for i, text in zip(idx, tok.batch_decode(out, skip_special_tokens=True)):
        done[df.example_id[i]] = text
    pd.DataFrame({"example_id": df.example_id, "source_text": df.source_text, "target_text": df.target_text,
                  "mt5_prediction": [done.get(e, "") for e in df.example_id]}).to_csv(OUT, index=False)
    n = b + len(idx)
    el = time.time() - t0
    print(f"{n}/{len(todo)} done, {el/60:.1f} min elapsed, about {(el/n)*(len(todo)-n)/60:.1f} min left", flush=True)
print("saved", OUT)
