"""
CodeMix Intelligence - Step 33B
Unit and Integration Tests for MuRIL Inference Engine and FastAPI Backend.

Covers:
1. Model directory and file validation
2. Label mapping and class count verification
3. Empty / whitespace-only input handling
4. Token count and prediction count 1-to-1 equality
5. Valid predicted labels (EN, HI, TE, OTHER)
6. Confidence values strictly between 0 and 1
7. Long-input chunking (>254 WordPieces) and oversized token error handling
8. API health endpoints (GET /health and GET /api/health)
9. API prediction endpoint (POST /api/predict)
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from starlette.testclient import TestClient

from backend.main import app
from src.inference.predictor import MuRILLIDPredictor


class TestMuRILLIDPredictor(unittest.TestCase):
    """Unit tests for the MuRILLIDPredictor inference engine."""

    @classmethod
    def setUpClass(cls):
        """Initialize the predictor once for all tests to optimize memory and runtime."""
        cls.predictor = MuRILLIDPredictor()

    def test_model_directory_validation(self):
        """Test that invalid model directories raise appropriate FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            MuRILLIDPredictor(model_dir="non_existent_model_dir_xyz")

    def test_label_mapping(self):
        """Test that label mapping conforms to the canonical taxonomy."""
        expected_label2id = {"EN": 0, "HI": 1, "TE": 2, "OTHER": 3}
        expected_id2label = {0: "EN", 1: "HI", 2: "TE", 3: "OTHER"}

        self.assertEqual(self.predictor.LABEL2ID, expected_label2id)
        self.assertEqual(self.predictor.ID2LABEL, expected_id2label)
        self.assertEqual(self.predictor.model.num_labels, 4)

    def test_empty_input_handling(self):
        """Test engine behavior when input is empty or contains only whitespace."""
        res_empty = self.predictor.predict("")
        self.assertEqual(res_empty["tokens"], [])
        self.assertFalse(res_empty["chunked"])
        self.assertEqual(res_empty["chunk_count"], 0)

        res_spaces = self.predictor.predict("     ")
        self.assertEqual(res_spaces["tokens"], [])
        self.assertFalse(res_spaces["chunked"])
        self.assertEqual(res_spaces["chunk_count"], 0)

    def test_token_prediction_count_equality(self):
        """Test that every whitespace token gets exactly one prediction in matching order."""
        sample_text = "This is a simple test sentence for verification"
        tokens = sample_text.split()
        res = self.predictor.predict(sample_text)

        self.assertEqual(len(res["tokens"]), len(tokens))
        for i, tok in enumerate(tokens):
            pred_item = res["tokens"][i]
            self.assertEqual(pred_item["token_index"], i)
            self.assertEqual(pred_item["token"], tok)

    def test_valid_predicted_labels(self):
        """Test that all predicted labels belong to the canonical 4-class taxonomy."""
        sample_text = "Hello nenu school ki vellanu and mein khana khaya"
        res = self.predictor.predict(sample_text)
        valid_labels = {"EN", "HI", "TE", "OTHER"}

        for item in res["tokens"]:
            self.assertIn(item["predicted_label"], valid_labels)
            self.assertEqual(
                item["predicted_label_id"],
                self.predictor.LABEL2ID[item["predicted_label"]]
            )

    def test_confidence_values_in_bounds(self):
        """Test that all confidence values are between 0.0 and 1.0."""
        sample_text = "Universal testing of probability bounds"
        res = self.predictor.predict(sample_text)

        for item in res["tokens"]:
            conf = item["confidence"]
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)

    def test_long_input_chunking(self):
        """Test that inputs exceeding 254 WordPieces are safely chunked without token loss."""
        # Generate a sequence of repeated words that clearly exceeds 254 WordPieces
        words = ["namaskaram", "hello", "dost"] * 90  # 270 words; namaskaram produces 3 subwords -> >350 subwords
        long_text = " ".join(words)

        res = self.predictor.predict(long_text)
        self.assertTrue(res["chunked"])
        self.assertGreater(res["chunk_count"], 1)
        self.assertEqual(len(res["tokens"]), len(words))

        # Check token order preservation
        for i, word in enumerate(words):
            self.assertEqual(res["tokens"][i]["token"], word)
            self.assertEqual(res["tokens"][i]["token_index"], i)

    def test_oversized_single_token_error(self):
        """Test that an individual token exceeding the subword limit raises ValueError."""
        # A single whitespace-delimited token with >254 WordPieces (e.g., hyphenated compound)
        oversized_word = "-".join(["namaste"] * 150)
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict(oversized_word)
        self.assertIn("exceeding the maximum allowed content length", str(ctx.exception))


class TestFastAPIEndpoints(unittest.TestCase):
    """Integration tests for FastAPI endpoints using TestClient."""

    @classmethod
    def setUpClass(cls):
        """Use TestClient with lifespan context."""
        cls.client_ctx = TestClient(app)
        # Enter lifespan context
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_ctx.__exit__(None, None, None)

    def test_health_endpoint(self):
        """Test GET /health returns 200 OK and status healthy."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_api_health_endpoint(self):
        """Test GET /api/health returns 200 OK and detailed model status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["application"], "CodeMix Intelligence - Token-Level Language Identification")
        self.assertEqual(data["model"], "google/muril-base-cased")
        self.assertTrue(data["model_loaded"])
        self.assertIn(data["device"], ["cpu", "cuda", "cuda:0"])
        self.assertEqual(data["supported_labels"], ["EN", "HI", "TE", "OTHER"])

    def test_api_predict_endpoint_valid_input(self):
        """Test POST /api/predict with a valid code-mixed sentence."""
        payload = {"text": "Hello nenu school ki vellanu"}
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["text"], "Hello nenu school ki vellanu")
        self.assertEqual(data["model"], "google/muril-base-cased")
        self.assertFalse(data["chunked"])
        self.assertEqual(data["chunk_count"], 1)
        self.assertEqual(len(data["tokens"]), 5)

        first_token = data["tokens"][0]
        self.assertEqual(first_token["token"], "Hello")
        self.assertIn("predicted_label", first_token)
        self.assertIn("predicted_label_id", first_token)
        self.assertIn("confidence", first_token)
        self.assertGreaterEqual(first_token["confidence"], 0.0)
        self.assertLessEqual(first_token["confidence"], 1.0)

    def test_api_predict_empty_input(self):
        """Test POST /api/predict with empty string returns 400 Bad Request."""
        payload = {"text": "   "}
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Input text must not be empty", response.json()["detail"])

    def test_api_predict_oversized_token(self):
        """Test POST /api/predict with single oversized token returns 422 Unprocessable Entity."""
        oversized = "-".join(["namaste"] * 150)
        payload = {"text": oversized}
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("exceeding the maximum allowed content length", response.json()["detail"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
