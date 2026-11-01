"""
CodeMix Intelligence - Step 33B
Live Backend Service Verification Script

Starts uvicorn on http://127.0.0.1:8000, validates:
1. GET /health
2. GET /api/health
3. POST /api/predict with smoke-test sentence
Captures responses, latency, and shuts down server cleanly.
"""

import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
HOST = "127.0.0.1"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"

def http_get(url: str):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def http_post(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def main():
    print(f"Starting Uvicorn server on {BASE_URL}...")
    start_time = time.time()
    
    server_process = subprocess.Popen(
        [
            str(PYTHON_EXE),
            "-m", "uvicorn",
            "backend.main:app",
            "--host", HOST,
            "--port", str(PORT)
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Poll until server is ready
        ready = False
        health_res = None
        for attempt in range(30):
            time.sleep(1.0)
            try:
                status_code, data = http_get(f"{BASE_URL}/health")
                if status_code == 200:
                    ready = True
                    health_res = data
                    break
            except Exception:
                continue

        startup_duration = time.time() - start_time
        if not ready:
            print("ERROR: Server failed to start within 30 seconds.")
            stderr_out = server_process.stderr.read()
            print("Server stderr:", stderr_out)
            sys.exit(1)

        print(f"Server is LIVE (Startup time: {startup_duration:.2f}s)")
        print("\n--- 1. Testing GET /health ---")
        print(f"Status: 200 OK")
        print(f"Response: {json.dumps(health_res, indent=2)}")

        print("\n--- 2. Testing GET /api/health ---")
        api_health_status, api_health_data = http_get(f"{BASE_URL}/api/health")
        print(f"Status: {api_health_status} OK")
        print(f"Response: {json.dumps(api_health_data, indent=2)}")

        print("\n--- 3. Testing POST /api/predict (Smoke Test) ---")
        smoke_payload = {
            "text": "Hello dost nenu repu office ki vastanu"
        }
        t0 = time.time()
        predict_status, predict_data = http_post(f"{BASE_URL}/api/predict", smoke_payload)
        inference_latency = (time.time() - t0) * 1000
        print(f"Status: {predict_status} OK")
        print(f"Inference Latency: {inference_latency:.1f}ms")
        print(f"Request: {json.dumps(smoke_payload, indent=2)}")
        print(f"Response: {json.dumps(predict_data, indent=2)}")

        # Save results for reports
        verification_report = {
            "startup_time_seconds": round(startup_duration, 2),
            "inference_latency_ms": round(inference_latency, 1),
            "health_endpoint": {
                "url": f"{BASE_URL}/health",
                "status": health_res
            },
            "api_health_endpoint": {
                "url": f"{BASE_URL}/api/health",
                "status": api_health_data
            },
            "smoke_test": {
                "request": smoke_payload,
                "response": predict_data
            }
        }

        output_path = REPO_ROOT / "outputs" / "reports" / "step33B_live_verification.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(verification_report, f, indent=2, ensure_ascii=False)
        print(f"\nVerification results saved to {output_path}")

    finally:
        print("\nStopping server process...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("Server process stopped successfully.")

if __name__ == "__main__":
    main()
