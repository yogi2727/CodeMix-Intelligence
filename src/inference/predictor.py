"""
CodeMix Intelligence - Step 33B
MuRIL Token-Level Language Identification Predictor

Implements MuRILLIDPredictor:
- Loads fine-tuned google/muril-base-cased model from artifacts/models/muril_lid_baseline/best_model/
- Uses BertTokenizer with use_fast=False
- Exact word-by-word WordPiece first-subword alignment
- Preserves original whitespace tokens and token order
- Long-input chunking at original whitespace token boundaries (max 254 WordPieces)
- Model evaluation mode with torch.inference_mode()
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer


class MuRILLIDPredictor:
    """Token-level Language Identification Predictor using fine-tuned MuRIL."""

    # Default relative model path from repository root
    DEFAULT_MODEL_REL_PATH = Path("artifacts/models/muril_lid_baseline/best_model")

    # Canonical label taxonomy
    ID2LABEL: Dict[int, str] = {0: "EN", 1: "HI", 2: "TE", 3: "OTHER"}
    LABEL2ID: Dict[str, int] = {"EN": 0, "HI": 1, "TE": 2, "OTHER": 3}

    REQUIRED_FILES = [
        "config.json",
        "model.safetensors",
        "vocab.txt",
        "tokenizer_config.json",
        "special_tokens_map.json"
    ]

    # Model architecture limits: 256 total subwords, 2 reserved for [CLS] and [SEP]
    MAX_SEQUENCE_LENGTH = 256
    MAX_CONTENT_SUBWORDS = 254

    def __init__(
        self,
        model_dir: Optional[Path | str] = None,
        device: Optional[str] = None
    ) -> None:
        """Initialize predictor, verify artifacts, and load tokenizer and model."""
        self.repo_root = self._find_repo_root()
        if model_dir is None:
            self.model_dir = (self.repo_root / self.DEFAULT_MODEL_REL_PATH).resolve()
        else:
            self.model_dir = Path(model_dir).resolve()

        self._verify_model_directory()

        # Hardware selection
        if device is not None:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load Tokenizer (use_fast=False for deterministic slow BertTokenizer)
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(self.model_dir),
            use_fast=False,
            local_files_only=True
        )

        # Load Model
        self.model = AutoModelForTokenClassification.from_pretrained(
            str(self.model_dir),
            local_files_only=True
        )
        self.model.to(self.device)
        self.model.eval()

        self._verify_model_configuration()

    @staticmethod
    def _find_repo_root() -> Path:
        """Locate project root by searching upwards for artifacts or .git."""
        current = Path(__file__).resolve().parent
        for parent in [current] + list(current.parents):
            if (parent / "artifacts").exists() and (parent / "data").exists():
                return parent
        return Path.cwd()

    def _verify_model_directory(self) -> None:
        """Verify that model directory exists and contains all required artifacts."""
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Model directory does not exist: {self.model_dir}\n"
                "Ensure artifacts have been integrated in Step 33A."
            )
        for req_file in self.REQUIRED_FILES:
            file_path = self.model_dir / req_file
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required model artifact missing: {req_file} at {file_path}"
                )

    def _verify_model_configuration(self) -> None:
        """Verify model output classes and label mappings."""
        if self.model.num_labels != 4:
            raise ValueError(
                f"Model must have exactly 4 output labels, but found {self.model.num_labels}"
            )
        config_id2label = {int(k): v for k, v in self.model.config.id2label.items()}
        for idx, name in self.ID2LABEL.items():
            if config_id2label.get(idx) != name:
                raise ValueError(
                    f"Label mismatch at index {idx}: expected '{name}', got '{config_id2label.get(idx)}'"
                )

    def _tokenize_word(self, word: str) -> List[str]:
        """Tokenize a single whitespace word into WordPieces with fallback for unknown characters."""
        subwords = self.tokenizer.tokenize(word)
        if not subwords:
            # Fallback for unrecognized single characters or empty splits
            subwords = [self.tokenizer.unk_token]
        return subwords

    def _chunk_tokens(
        self,
        token_subword_pairs: List[Tuple[str, List[str]]]
    ) -> List[List[Tuple[str, List[str]]]]:
        """Split tokens into chunks preserving word boundaries such that each chunk <= MAX_CONTENT_SUBWORDS."""
        chunks: List[List[Tuple[str, List[str]]]] = []
        current_chunk: List[Tuple[str, List[str]]] = []
        current_subwords_count = 0

        for token, subwords in token_subword_pairs:
            n_subwords = len(subwords)
            if n_subwords > self.MAX_CONTENT_SUBWORDS:
                raise ValueError(
                    f"Token '{token}' generates {n_subwords} subwords, exceeding the maximum allowed "
                    f"content length of {self.MAX_CONTENT_SUBWORDS} subwords. Cannot safely process."
                )

            if current_subwords_count + n_subwords > self.MAX_CONTENT_SUBWORDS:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [(token, subwords)]
                current_subwords_count = n_subwords
            else:
                current_chunk.append((token, subwords))
                current_subwords_count += n_subwords

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Perform token-level language identification on the input text.

        Returns one prediction per original whitespace token.
        Preserves original tokens and token order.
        """
        if not isinstance(text, str):
            raise TypeError("Input text must be a string.")

        tokens = text.strip().split()
        if not tokens:
            return {
                "text": text,
                "tokens": [],
                "chunked": False,
                "chunk_count": 0,
                "model": "google/muril-base-cased"
            }

        # 1. Tokenize each whitespace word separately
        token_subword_pairs: List[Tuple[str, List[str]]] = []
        for word in tokens:
            subwords = self._tokenize_word(word)
            token_subword_pairs.append((word, subwords))

        # 2. Chunk tokens if sequence length exceeds limit
        chunks = self._chunk_tokens(token_subword_pairs)
        is_chunked = len(chunks) > 1

        all_predictions: List[Dict[str, Any]] = []
        global_token_index = 0

        # 3. Process each chunk through the model
        for chunk in chunks:
            input_ids: List[int] = [self.tokenizer.cls_token_id]
            first_subword_indices: List[int] = []

            for _, subwords in chunk:
                subword_ids = self.tokenizer.convert_tokens_to_ids(subwords)
                # First subword index for this token
                first_subword_indices.append(len(input_ids))
                input_ids.extend(subword_ids)

            input_ids.append(self.tokenizer.sep_token_id)
            input_tensor = torch.tensor([input_ids], device=self.device)

            with torch.inference_mode():
                outputs = self.model(input_ids=input_tensor)
                logits = outputs.logits[0]  # Shape: [seq_len, 4]
                probs = torch.softmax(logits, dim=-1)

            for (token, _), sub_idx in zip(chunk, first_subword_indices):
                token_probs = probs[sub_idx]
                pred_label_id = int(torch.argmax(token_probs).item())
                confidence = float(token_probs[pred_label_id].item())
                pred_label = self.ID2LABEL[pred_label_id]

                all_predictions.append({
                    "token_index": global_token_index,
                    "token": token,
                    "predicted_label": pred_label,
                    "predicted_label_id": pred_label_id,
                    "confidence": round(confidence, 4)
                })
                global_token_index += 1

        return {
            "text": text,
            "tokens": all_predictions,
            "chunked": is_chunked,
            "chunk_count": len(chunks),
            "model": "google/muril-base-cased"
        }
