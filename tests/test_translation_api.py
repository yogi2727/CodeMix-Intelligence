"""
CodeMix Intelligence - Step 2E
Integration and Unit Tests for FastAPI Model 2 Translation API.

Covers:
1. POST /api/translate with a valid request
2. Correct response schema validation
3. Whitespace-only input returns 400 Bad Request
4. Empty input returns 422 Unprocessable Entity (Pydantic schema validation)
5. Over-1000-character input returns 422 Unprocessable Entity
6. Missing model artifacts return 503 Service Unavailable
7. Translator runtime failure returns 500 Internal Server Error (without stack trace leak)
8. Repeated requests reuse a single translator instance (singleton pattern)
9. Concurrent initialization does not create multiple translator instances
10. GET /api/health preserves existing Model 1 keys and taxonomy
11. GET /api/health does not trigger mT5 model loading
12. Health status changes correctly after mT5 loads

Uses mocked translator instances to prevent repeated 1.2 GB model loading in unit tests.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from starlette.testclient import TestClient
import torch

import backend.main as backend_module
from backend.main import app, check_translation_assets_available


class TestTranslationAPI(unittest.TestCase):
    """Test suite for Translation API endpoints and health reporting."""

    @classmethod
    def setUpClass(cls):
        """Initialize TestClient once in lifespan context for the entire suite."""
        cls.client_ctx = TestClient(app)
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        """Tear down TestClient lifespan context."""
        cls.client_ctx.__exit__(None, None, None)

    def setUp(self):
        """Reset global and app state translator holders before each test."""
        backend_module.translator = None
        app.state.translator = None

    def tearDown(self):
        """Clean up translator state after each test."""
        backend_module.translator = None
        app.state.translator = None

    def test_01_valid_translation_request(self):
        """Test POST /api/translate returns 200 and expected translation for valid input."""
        mock_trans = MagicMock()
        mock_trans.translate.return_value = "i did not ever show cased my ego."
        mock_trans.model_name = "google/mt5-small"
        mock_trans.task = "Romanized Hinglish to English translation"
        mock_trans.NUM_BEAMS = 4

        with patch("backend.main.HinglishTranslator", return_value=mock_trans):
            payload = {"text": "bas kabhi ghamand nahi kiya."}
            response = self.client.post("/api/translate", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["source_text"], "bas kabhi ghamand nahi kiya.")
            self.assertEqual(data["translated_text"], "i did not ever show cased my ego.")
            mock_trans.translate.assert_called_once_with("bas kabhi ghamand nahi kiya.")

    def test_02_correct_response_schema(self):
        """Test response conforms strictly to TranslateResponse schema."""
        mock_trans = MagicMock()
        mock_trans.translate.return_value = "hello friend"
        mock_trans.model_name = "google/mt5-small"
        mock_trans.task = "Romanized Hinglish to English translation"
        mock_trans.NUM_BEAMS = 4

        with patch("backend.main.HinglishTranslator", return_value=mock_trans):
            response = self.client.post("/api/translate", json={"text": "hello dost"})
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("source_text", data)
            self.assertIn("translated_text", data)
            self.assertIn("model", data)
            self.assertIn("task", data)
            self.assertIn("num_beams", data)
            self.assertIsInstance(data["source_text"], str)
            self.assertIsInstance(data["translated_text"], str)
            self.assertIsInstance(data["model"], str)
            self.assertIsInstance(data["task"], str)
            self.assertIsInstance(data["num_beams"], int)

    def test_03_whitespace_only_input_returns_400(self):
        """Test whitespace-only input returns HTTP 400 Bad Request."""
        response = self.client.post("/api/translate", json={"text": "     "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty or whitespace only", response.json()["detail"])

    def test_04_empty_input_returns_422(self):
        """Test empty string returns HTTP 422 Unprocessable Entity from Pydantic schema validation."""
        response = self.client.post("/api/translate", json={"text": ""})
        self.assertEqual(response.status_code, 422)

    def test_05_oversized_input_returns_422(self):
        """Test input > 1000 characters returns HTTP 422 from Pydantic schema validation."""
        oversized = "a" * 1001
        response = self.client.post("/api/translate", json={"text": oversized})
        self.assertEqual(response.status_code, 422)

    def test_06_missing_model_artifacts_returns_503(self):
        """Test that missing model files raise HTTP 503 with non-sensitive error message."""
        mock_trans_cls = MagicMock()
        mock_trans_instance = MagicMock()
        mock_trans_instance.verify_model_assets.side_effect = FileNotFoundError("Missing model.safetensors")
        mock_trans_cls.return_value = mock_trans_instance

        with patch("backend.main.HinglishTranslator", mock_trans_cls):
            response = self.client.post("/api/translate", json={"text": "test sentence"})
            self.assertEqual(response.status_code, 503)
            self.assertIn("missing or not extracted", response.json()["detail"])

    def test_07_translator_runtime_failure_returns_500(self):
        """Test translation runtime error returns HTTP 500 without leaking stack traces."""
        mock_trans = MagicMock()
        mock_trans.translate.side_effect = RuntimeError("Internal CUDA execution error")
        mock_trans.model_name = "google/mt5-small"
        mock_trans.task = "Romanized Hinglish to English translation"

        with patch("backend.main.HinglishTranslator", return_value=mock_trans):
            response = self.client.post("/api/translate", json={"text": "test sentence"})
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()["detail"], "Translation execution failed.")

    def test_08_repeated_requests_reuse_single_instance(self):
        """Verify repeated calls to /api/translate reuse the same singleton translator instance."""
        mock_trans = MagicMock()
        mock_trans.translate.return_value = "translated output"
        mock_trans.model_name = "google/mt5-small"
        mock_trans.task = "Romanized Hinglish to English translation"

        with patch("backend.main.HinglishTranslator", return_value=mock_trans) as mock_cls:
            for _ in range(4):
                res = self.client.post("/api/translate", json={"text": "sentence"})
                self.assertEqual(res.status_code, 200)

            # Class constructor should only have been called exactly once
            mock_cls.assert_called_once()
            self.assertEqual(mock_trans.translate.call_count, 4)

    def test_09_concurrent_initialization_creates_single_instance(self):
        """Verify concurrent first requests do not instantiate multiple translator instances."""
        mock_trans = MagicMock()
        mock_trans.translate.return_value = "concurrent result"
        mock_trans.model_name = "google/mt5-small"
        mock_trans.task = "Romanized Hinglish to English translation"

        with patch("backend.main.HinglishTranslator", return_value=mock_trans) as mock_cls:
            def make_request():
                return self.client.post("/api/translate", json={"text": "concurrent request"})

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                responses = [f.result() for f in futures]

            for res in responses:
                self.assertEqual(res.status_code, 200)

            # Singleton guarantee: constructor called exactly once despite 5 concurrent threads
            self.assertEqual(mock_cls.call_count, 1)

    def test_10_api_health_preserves_model1_keys(self):
        """Verify GET /api/health preserves all existing Model 1 keys and values."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Model 1 keys
        self.assertEqual(data["application"], "CodeMix Intelligence - Token-Level Language Identification")
        self.assertEqual(data["model"], "google/muril-base-cased")
        self.assertTrue(data["model_loaded"])
        self.assertEqual(data["device"], "cpu")
        self.assertEqual(data["supported_labels"], ["EN", "HI", "TE", "OTHER"])
        self.assertEqual(data["label_mapping"], {"EN": 0, "HI": 1, "TE": 2, "OTHER": 3})
        self.assertEqual(data["status"], "ready")

    def test_11_api_health_does_not_load_mt5(self):
        """Verify GET /api/health reports translation availability without loading model weights."""
        with patch("backend.main.HinglishTranslator") as mock_cls:
            response = self.client.get("/api/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()

            # Model must NOT be instantiated
            mock_cls.assert_not_called()
            self.assertIsNone(app.state.translator)
            self.assertIsNone(backend_module.translator)

            # Translation health section
            self.assertIn("translation", data)
            trans_info = data["translation"]
            self.assertEqual(trans_info["model"], "google/mt5-small")
            self.assertEqual(trans_info["task"], "Romanized Hinglish to English translation")
            self.assertTrue(trans_info["available"])
            self.assertFalse(trans_info["loaded"])
            self.assertIsNone(trans_info["device"])
            self.assertEqual(trans_info["precision"], "FP32")

    def test_12_health_status_changes_after_mt5_loads(self):
        """Verify health endpoint accurately reflects loaded state and device after mT5 is loaded."""
        mock_trans = MagicMock()
        mock_trans.model_loaded = True
        mock_trans.device = torch.device("cpu")
        app.state.translator = mock_trans
        backend_module.translator = mock_trans

        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        trans_info = data["translation"]
        self.assertTrue(trans_info["available"])
        self.assertTrue(trans_info["loaded"])
        self.assertEqual(trans_info["device"], "cpu")
        self.assertEqual(trans_info["precision"], "FP32")


if __name__ == "__main__":
    unittest.main(verbosity=2)
