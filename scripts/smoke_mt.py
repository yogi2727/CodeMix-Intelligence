"""
CodeMix Intelligence - Smoke Test for MT Pipeline API
Verifies POST http://127.0.0.1:8000/api/mt/translate with:
1. Telugu sentence (strategy=full)
2. Hindi sentence (strategy=full)
3. Mixed sentence (strategy=clause)

Prints status code, translation, and total time for each.
Exits with code 0 on success, or non-zero (1) on failure.
"""

import sys
import time
import requests

API_URL = "http://127.0.0.1:8000/api/mt/translate"

TEST_CASES = [
    {
        "name": "Telugu Sentence",
        "payload": {
            "text": "Nenu repu college ki vastanu, but assignment complete cheyyaledu",
            "strategy": "full",
            "gloss": True,
            "src_hint": "TE"
        }
    },
    {
        "name": "Hindi Sentence",
        "payload": {
            "text": "Kal meeting hai please slides bhej dena",
            "strategy": "full",
            "gloss": True,
            "src_hint": "HI"
        }
    },
    {
        "name": "Mixed Hindi+Telugu Sentence",
        "payload": {
            "text": "Nenu repu college ki vastanu, tum bhi aao na",
            "strategy": "clause",
            "gloss": True
        }
    }
]


def run_smoke_test():
    print(f"Running MT Pipeline Smoke Test against {API_URL}...\n")
    all_passed = True

    for i, test in enumerate(TEST_CASES, 1):
        name = test["name"]
        payload = test["payload"]
        print(f"[{i}/3] Testing: {name}")
        print(f"      Input: \"{payload['text']}\"")
        print(f"      Strategy: {payload['strategy']}")

        start_time = time.perf_counter()
        try:
            resp = requests.post(API_URL, json=payload, timeout=120)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            status_code = resp.status_code
            print(f"      Status Code: {status_code}")
            print(f"      Total Time:  {elapsed_ms:.1f} ms")

            if status_code == 200:
                data = resp.json()
                translation = data.get("translation", "")
                print(f"      Translation: \"{translation}\"")
                if not translation or not translation.strip():
                    print("      FAILED: Returned empty translation.")
                    all_passed = False
                else:
                    print("      PASSED")
            else:
                print(f"      FAILED with HTTP {status_code}: {resp.text}")
                all_passed = False

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            print(f"      Status Code: ERROR")
            print(f"      Total Time:  {elapsed_ms:.1f} ms")
            print(f"      FAILED: Exception occurred: {e}")
            all_passed = False

        print()

    if not all_passed:
        print("Smoke test FAILED: One or more requests did not succeed.")
        sys.exit(1)
    else:
        print("Smoke test PASSED: All 3 translation requests completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    run_smoke_test()

