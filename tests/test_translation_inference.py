"""
CodeMix Intelligence - Step 2D
Unit and Integration Tests for HinglishTranslator Inference Engine.

Covers:
1. Model path resolution (default and MT5_MODEL_DIR environment override)
2. Missing directory and missing asset validation
3. Input validation (empty, whitespace-only, non-string, >1000 characters)
4. Lazy model initialization (deferred weight loading)
5. Model precision, device, and evaluation mode verification
6. Real translation inference smoke tests using shared model instance
7. Thread-safe execution under concurrent calls
"""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import sys
import tempfile
import unittest

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from src.inference.translator import HinglishTranslator


class TestTranslationUnitValidation(unittest.TestCase):
    """
    Fast unit tests for path resolution, configuration, and input validation.
    These tests do NOT load the 1.2 GB model weights.
    """

    def setUp(self):
        # Create a lazy translator that has not loaded model weights
        self.lazy_translator = HinglishTranslator(lazy=True)

    def test_default_model_path_resolution(self):
        """Verify default model directory resolves to artifacts/models/mt5_hinglish_translation."""
        resolved = HinglishTranslator.resolve_model_dir()
        expected = (REPO_ROOT / "artifacts" / "models" / "mt5_hinglish_translation").resolve()
        self.assertEqual(resolved, expected)
        self.assertTrue(resolved.exists())

    def test_env_override_model_path_resolution(self):
        """Verify MT5_MODEL_DIR environment variable overrides default path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_env = os.environ.get(HinglishTranslator.ENV_MODEL_DIR_KEY)
            try:
                os.environ[HinglishTranslator.ENV_MODEL_DIR_KEY] = tmpdir
                resolved = HinglishTranslator.resolve_model_dir()
                self.assertEqual(resolved, Path(tmpdir).resolve())
            finally:
                if orig_env is not None:
                    os.environ[HinglishTranslator.ENV_MODEL_DIR_KEY] = orig_env
                else:
                    os.environ.pop(HinglishTranslator.ENV_MODEL_DIR_KEY, None)

    def test_missing_model_directory_raises(self):
        """Verify FileNotFoundError is raised when model directory does not exist."""
        non_existent = REPO_ROOT / "artifacts" / "models" / "non_existent_mt5_dir_xyz"
        translator = HinglishTranslator(model_dir=non_existent, lazy=True)
        with self.assertRaises(FileNotFoundError) as ctx:
            translator.verify_model_assets()
        self.assertIn("Model directory does not exist", str(ctx.exception))

    def test_missing_required_asset_raises(self):
        """Verify FileNotFoundError is raised when a required model artifact is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create all except model.safetensors
            for fname in ["config.json", "generation_config.json", "tokenizer_config.json", "tokenizer.json"]:
                (tmp_path / fname).touch()

            translator = HinglishTranslator(model_dir=tmp_path, lazy=True)
            with self.assertRaises(FileNotFoundError) as ctx:
                translator.verify_model_assets()
            self.assertIn("Missing required model artifact(s)", str(ctx.exception))
            self.assertIn("model.safetensors", str(ctx.exception))

    def test_lazy_initialization_state(self):
        """Verify that lazy=True defers loading and reports model_loaded=False."""
        self.assertFalse(self.lazy_translator.model_loaded)
        self.assertIsNone(self.lazy_translator.model)
        self.assertIsNone(self.lazy_translator.tokenizer)
        self.assertEqual(self.lazy_translator.model_name, "google/mt5-small")
        self.assertEqual(self.lazy_translator.task, "Romanized Hinglish to English translation")

    def test_input_validation_empty_string(self):
        """Verify empty string raises ValueError without calling model."""
        with self.assertRaises(ValueError) as ctx:
            self.lazy_translator.translate("")
        self.assertIn("empty or whitespace only", str(ctx.exception))

    def test_input_validation_whitespace(self):
        """Verify whitespace-only string raises ValueError without calling model."""
        with self.assertRaises(ValueError) as ctx:
            self.lazy_translator.translate("      ")
        self.assertIn("empty or whitespace only", str(ctx.exception))

    def test_input_validation_non_string(self):
        """Verify non-string input raises ValueError without calling model."""
        for invalid in [12345, None, ["sample"], {"text": "sample"}]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError) as ctx:
                    self.lazy_translator.translate(invalid)
                self.assertIn("must be a string", str(ctx.exception))

    def test_input_validation_oversized_text(self):
        """Verify input exceeding 1000 characters raises ValueError."""
        oversized = "a " * 501  # 1002 chars
        with self.assertRaises(ValueError) as ctx:
            self.lazy_translator.translate(oversized)
        self.assertIn("exceeds maximum allowed length of 1000 characters", str(ctx.exception))


class TestTranslationInferenceEngine(unittest.TestCase):
    """
    Integration tests with the actual fine-tuned mT5-small model.
    Loads the model once in setUpClass to test real inference.
    """

    @classmethod
    def setUpClass(cls):
        """Load model once for all integration test cases in this suite."""
        cls.translator = HinglishTranslator(lazy=True)
        cls.translator.load_model()

    def test_model_loaded_and_precision(self):
        """Verify model loaded state, device, evaluation mode, and FP32 precision."""
        self.assertTrue(self.translator.model_loaded)
        self.assertIsNotNone(self.translator.model)
        self.assertIsNotNone(self.translator.tokenizer)

        # FP32 verification
        first_param = next(self.translator.model.parameters())
        self.assertEqual(first_param.dtype, torch.float32)

        # Evaluation mode & cache
        self.assertFalse(self.translator.model.training)
        self.assertTrue(self.translator.model.config.use_cache)

    def test_properties(self):
        """Verify read-only properties reflect model details."""
        self.assertEqual(self.translator.model_name, "google/mt5-small")
        self.assertEqual(self.translator.task, "Romanized Hinglish to English translation")
        self.assertTrue(self.translator.model_directory.is_dir())
        self.assertIn(self.translator.device.type, ["cpu", "cuda"])

    def test_translation_smoke_example_1(self):
        """Smoke test Example 1: 'bas kabhi ghamand nahi kiya.'"""
        sample = "bas kabhi ghamand nahi kiya."
        output = self.translator.translate(sample)
        self.assertIsInstance(output, str)
        self.assertTrue(len(output.strip()) > 0)

    def test_translation_smoke_example_2(self):
        """Smoke test Example 2: 'Mujhe lagta hai ki train late ho sakti hai.'"""
        sample = "Mujhe lagta hai ki train late ho sakti hai."
        output = self.translator.translate(sample)
        self.assertIsInstance(output, str)
        self.assertTrue(len(output.strip()) > 0)

    def test_translation_smoke_example_3(self):
        """Smoke test Example 3: 'Kal meeting kitne baje start hogi?'"""
        sample = "Kal meeting kitne baje start hogi?"
        output = self.translator.translate(sample)
        self.assertIsInstance(output, str)
        self.assertTrue(len(output.strip()) > 0)

    def test_concurrent_translations(self):
        """Verify thread-safe translation execution under concurrent threads."""
        samples = [
            "Mujhe train ke liye wait karna padega.",
            "Meeting kab start hogi please batao."
        ]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(self.translator.translate, s) for s in samples]
            results = [f.result() for f in futures]

        for res in results:
            self.assertIsInstance(res, str)
            self.assertTrue(len(res.strip()) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

