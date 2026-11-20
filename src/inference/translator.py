"""
CodeMix Intelligence - Step 2C
Hinglish to English Translation Engine using fine-tuned google/mt5-small.

Implements HinglishTranslator:
- Resolves model directory from explicit path, MT5_MODEL_DIR env var, or default project path
- Enforces presence of all required local model artifacts before loading
- Strictly loads local files only (never downloads from Hugging Face Hub)
- Loads FP32 weights on CUDA (if available) or CPU with use_cache=True and eval() mode
- Uses exact prompt prefix: "translate Hinglish to English: "
- Uses deterministic beam search generation: num_beams=4, max_length=128, do_sample=False
- Validates input text (non-empty string, <= 1000 characters)
- Thread-safe model generation via threading.Lock
"""

from __future__ import annotations

import os
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class HinglishTranslator:
    """
    Production-ready local inference engine for Romanized Hinglish to English translation
    using fine-tuned google/mt5-small.
    """

    # Default relative path from project repository root
    DEFAULT_MODEL_REL_PATH = Path("artifacts/models/mt5_hinglish_translation")
    ENV_MODEL_DIR_KEY = "MT5_MODEL_DIR"
    MODEL_NAME = "google/mt5-small"
    TASK = "Romanized Hinglish to English translation"

    # Generation and tokenization parameters matching Colab training configuration
    PREFIX = "translate Hinglish to English: "
    MAX_SOURCE_LENGTH = 128
    MAX_GENERATION_LENGTH = 128
    NUM_BEAMS = 4
    DO_SAMPLE = False
    MAX_INPUT_CHARS = 1000

    # Required local artifacts inside model directory
    REQUIRED_FILES = [
        "model.safetensors",
        "config.json",
        "generation_config.json",
        "tokenizer_config.json",
        "tokenizer.json"
    ]

    def __init__(
        self,
        model_dir: Optional[Path | str] = None,
        device: Optional[str] = None,
        lazy: bool = False
    ) -> None:
        """
        Initialize the translator.

        Args:
            model_dir: Optional explicit path to extracted model directory.
                       If None, checks MT5_MODEL_DIR env var or defaults to
                       artifacts/models/mt5_hinglish_translation relative to project root.
            device: Optional compute device string ('cpu', 'cuda', etc.).
                    If None, automatically selects CUDA when available, otherwise CPU.
            lazy: If True, defer model weight and tokenizer loading until load_model()
                  or first translate() call. Defaults to False (eager loading).
        """
        self.model_dir = self.resolve_model_dir(model_dir)
        self._requested_device = device
        if device is not None:
            self._device = torch.device(device)
        else:
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._lock = threading.Lock()
        self._model_loaded = False
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModelForSeq2SeqLM] = None

        if not lazy:
            self.load_model()

    @staticmethod
    def _find_repo_root() -> Path:
        """Locate project repository root by searching parent hierarchy for markers."""
        current = Path(__file__).resolve().parent
        for parent in [current] + list(current.parents):
            if (parent / "artifacts").exists() and (parent / "data").exists():
                return parent
        return Path.cwd()

    @classmethod
    def resolve_model_dir(cls, model_dir: Optional[Path | str] = None) -> Path:
        """
        Resolve model directory from explicit argument, MT5_MODEL_DIR environment
        variable, or default project root relative path.
        """
        if model_dir is not None:
            return Path(model_dir).resolve()

        env_path = os.getenv(cls.ENV_MODEL_DIR_KEY)
        if env_path:
            return Path(env_path).resolve()

        repo_root = cls._find_repo_root()
        return (repo_root / cls.DEFAULT_MODEL_REL_PATH).resolve()

    def verify_model_assets(self) -> None:
        """
        Validate that model directory exists and contains all required artifacts.

        Raises:
            FileNotFoundError: If the directory or any required file is missing.
            NotADirectoryError: If the path exists but is not a directory.
        """
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Model directory does not exist: {self.model_dir}\n"
                f"Ensure Model 2 release artifacts are extracted into {self.DEFAULT_MODEL_REL_PATH}."
            )
        if not self.model_dir.is_dir():
            raise NotADirectoryError(
                f"Model path exists but is not a directory: {self.model_dir}"
            )

        missing_files = []
        for req_file in self.REQUIRED_FILES:
            file_path = self.model_dir / req_file
            if not file_path.is_file():
                missing_files.append(req_file)

        if missing_files:
            raise FileNotFoundError(
                f"Missing required model artifact(s) in {self.model_dir}: {', '.join(missing_files)}"
            )

    def load_model(self) -> None:
        """
        Load tokenizer and model weights from local files into memory.

        Raises:
            FileNotFoundError: If required files are missing.
            RuntimeError: If tokenizer or model loading fails.
        """
        with self._lock:
            if self._model_loaded:
                return

            self.verify_model_assets()

            # Load Fast Tokenizer (local_files_only=True ensures no remote requests)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    str(self.model_dir),
                    local_files_only=True,
                    use_fast=True
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load tokenizer from {self.model_dir}: {e}"
                ) from e

            # Load Model Weights in FP32
            try:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    str(self.model_dir),
                    local_files_only=True
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load model weights from {self.model_dir}: {e}"
                ) from e

            # Target device, FP32 precision, caching and evaluation mode
            self.model.to(device=self._device, dtype=torch.float32)
            self.model.config.use_cache = True
            self.model.eval()

            self._model_loaded = True

    def translate(self, text: str) -> str:
        """
        Translate a Romanized Hinglish sentence to English.

        Args:
            text: Non-empty Romanized Hinglish sentence (up to 1,000 characters).

        Returns:
            Clean translated English string.

        Raises:
            ValueError: If input is not a string, is empty/whitespace, or exceeds length limit.
            RuntimeError: If model is not loaded or generation fails.
        """
        if not isinstance(text, str):
            raise ValueError("Input text must be a string.")

        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Input text must not be empty or whitespace only.")

        if len(cleaned) > self.MAX_INPUT_CHARS:
            raise ValueError(
                f"Input text exceeds maximum allowed length of {self.MAX_INPUT_CHARS} characters "
                f"(received {len(cleaned)})."
            )

        # Lazy loading safeguard
        if not self._model_loaded:
            self.load_model()

        if self.tokenizer is None or self.model is None:
            raise RuntimeError("Model or tokenizer is not properly initialized.")

        # Prepend training prefix
        prompt = self.PREFIX + cleaned

        encoded = self.tokenizer(
            prompt,
            max_length=self.MAX_SOURCE_LENGTH,
            truncation=True,
            return_tensors="pt"
        )

        input_ids = encoded["input_ids"].to(self._device)
        attention_mask = encoded["attention_mask"].to(self._device)

        # Thread-safe generation
        with self._lock:
            with torch.inference_mode():
                try:
                    generated_ids = self.model.generate(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        max_length=self.MAX_GENERATION_LENGTH,
                        num_beams=self.NUM_BEAMS,
                        do_sample=self.DO_SAMPLE
                    )
                except Exception as e:
                    raise RuntimeError(f"Translation generation failed: {e}") from e

        translated_text = self.tokenizer.decode(
            generated_ids[0],
            skip_special_tokens=True
        ).strip()

        return translated_text

    def translate_batch(self, texts: List[str], batch_size: int = 32) -> List[str]:
        """
        Translate a list of Romanized Hinglish sentences to English in batches.

        Args:
            texts: List of Romanized Hinglish sentences.
            batch_size: Number of sentences to process per batch (default 32).

        Returns:
            List of translated English strings.
        """
        if not texts:
            return []

        if not self._model_loaded:
            self.load_model()

        if self.tokenizer is None or self.model is None:
            raise RuntimeError("Model or tokenizer is not properly initialized.")

        results: List[str] = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            cleaned_batch = [t.strip() if isinstance(t, str) and t.strip() else "" for t in batch_texts]
            prompts = [self.PREFIX + t if t else self.PREFIX for t in cleaned_batch]

            encoded = self.tokenizer(
                prompts,
                max_length=self.MAX_SOURCE_LENGTH,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            input_ids = encoded["input_ids"].to(self._device)
            attention_mask = encoded["attention_mask"].to(self._device)

            with self._lock:
                with torch.inference_mode():
                    generated_ids = self.model.generate(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        max_length=self.MAX_GENERATION_LENGTH,
                        num_beams=self.NUM_BEAMS,
                        do_sample=self.DO_SAMPLE
                    )

            batch_decoded = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )
            results.extend([d.strip() for d in batch_decoded])

        return results

    @property
    def device(self) -> torch.device:
        """Compute device currently configured for inference."""
        return self._device

    @property
    def model_name(self) -> str:
        """Base model name."""
        return self.MODEL_NAME

    @property
    def task(self) -> str:
        """Task description."""
        return self.TASK

    @property
    def model_loaded(self) -> bool:
        """Boolean indicator of whether model weights are loaded."""
        return self._model_loaded

    @property
    def model_directory(self) -> Path:
        """Resolved directory containing model artifacts."""
        return self.model_dir

