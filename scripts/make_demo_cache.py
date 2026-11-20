import json
import os
import requests

BASE = os.getenv("MT_BASE", "http://127.0.0.1:8000")
EXAMPLES = [
    ("Nenu repu college ki vastanu, but assignment complete cheyyaledu", "TE"),
    ("Meeru ee project deadline gurinchi manager tho matladara?", "TE"),
    ("Kal meeting hai please slides bhej dena", "HI"),
    ("Tum kab tak college aaoge?", "HI"),
    ("NENU REPU college ki vastanuuuu plz", "TE"),
    ("Nenu repu college ki vastanu, tum bhi aao na", "TE"),
]
STRATEGIES = [
    ("direct", lambda hint: {"strategy": "direct", "src_hint": hint}),
    ("lid_only", lambda hint: {"strategy": "lid_only"}),
    ("full", lambda hint: {"strategy": "full", "gloss": True}),
    ("clause", lambda hint: {"strategy": "clause"}),
]

cache = {}
for text, hint in EXAMPLES:
    entry = {}
    for name, body in STRATEGIES:
        try:
            r = requests.post(BASE + "/api/mt/translate", json={"text": text, **body(hint)}, timeout=900)
            if r.status_code == 200:
                entry[name] = r.json()
                print("ok  ", name, "->", entry[name]["translation"][:70])
            else:
                print("skip", name, "status", r.status_code, r.text[:120])
        except Exception as e:
            print("fail", name, type(e).__name__, e)
    cache[text] = entry

os.makedirs("frontend", exist_ok=True)
with open("frontend/demo_cache.json", "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=1)
print("saved frontend/demo_cache.json with", len(cache), "examples")
