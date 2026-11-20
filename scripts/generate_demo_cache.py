import json
import urllib.request
import sys
import os

sentences = [
    ("Nenu repu college ki vastanu, but assignment complete cheyyaledu", "TE"),
    ("Meeru ee project deadline gurinchi manager tho matladara?", "TE"),
    ("Kal meeting hai please slides bhej dena", "HI"),
    ("Tum kab tak college aaoge?", "HI"),
    ("NENU REPU college ki vastanuuuu plz", "TE"),
    ("Nenu repu college ki vastanu, tum bhi aao na", "TE")
]

url = "http://127.0.0.1:8000/api/mt/translate"
strategies = ["direct", "lid_only", "full", "clause"]
output_path = "frontend/demo_cache.json"

cache = {}
if os.path.exists(output_path):
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = {}

for text, hint in sentences:
    if text not in cache:
        cache[text] = {}
    print(f"Processing: {text}", flush=True)
    for strat in strategies:
        if strat in cache[text] and cache[text][strat].get("translation"):
            print(f"  [{strat}] already cached: {cache[text][strat].get('translation')}", flush=True)
            continue
        payload = {
            "text": text,
            "strategy": strat,
            "gloss": True,
            "src_hint": hint
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                cache[text][strat] = res
                print(f"  [{strat}]: {res.get('translation')}", flush=True)
        except Exception as e:
            print(f"  [{strat}] ERROR: {e}", flush=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"Successfully finished {output_path}", flush=True)
