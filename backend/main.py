"""
CodeMix Intelligence - Step 2E
FastAPI Backend for Code-Mixed Intelligence:
- Model 1: Token-Level Language Identification (MuRIL)
- Model 2: Romanized Hinglish-to-English Translation (mT5-small)

Endpoints:
- GET /health: Basic service status
- GET /api/health: Detailed application and multi-model status
- POST /api/predict: Token-level language identification prediction (MuRIL)
- POST /api/translate: Romanized Hinglish-to-English translation (mT5-small)
"""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

from backend.mt.router import get_pipeline, router as mt_router

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.inference.predictor import MuRILLIDPredictor
from src.inference.translator import HinglishTranslator

logger = logging.getLogger(__name__)

# Global model holders
predictor: Optional[MuRILLIDPredictor] = None
translator: Optional[HinglishTranslator] = None
_translator_init_lock = threading.Lock()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load MuRIL LID Predictor on application startup.
    HinglishTranslator is initialized lazily upon first translation request.
    Start a background daemon thread to warm up the MT pipeline (IndicTrans2 + transliteration).
    """
    global predictor, translator
    print("Loading MuRIL LID Predictor on application startup...")
    predictor = MuRILLIDPredictor()
    app.state.predictor = predictor
    app.state.translator = None
    translator = None
    print(f"MuRIL LID Predictor loaded successfully on device: {predictor.device}")

    # Warm up MT pipeline in background daemon thread (server still starts if loading fails)
    def _warmup_mt_pipeline():
        try:
            logger.info("Warming up CodeMix MT Pipeline in background thread...")
            print("Warming up CodeMix MT Pipeline in background thread...")
            get_pipeline()
            logger.info("CodeMix MT Pipeline warmed up successfully.")
            print("CodeMix MT Pipeline warmed up successfully.")
        except Exception as e:
            logger.error("CodeMix MT Pipeline warm-up failed on startup: %s", e, exc_info=True)
            print(f"CodeMix MT Pipeline warm-up failed on startup: {e}")

    warmup_thread = threading.Thread(target=_warmup_mt_pipeline, daemon=True, name="mt-pipeline-warmup")
    warmup_thread.start()

    yield

    print("Shutting down models...")
    predictor = None
    translator = None
    app.state.predictor = None
    app.state.translator = None


app = FastAPI(
    title="CodeMix Intelligence API",
    description="Token-Level Language Identification (MuRIL) and Hinglish-to-English Translation (mT5)",
    version="1.1.0",
    lifespan=lifespan
)
app.include_router(mt_router)

# CORS Middleware for frontend integration
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Schemas - Model 1 (LID)
# ==============================================================================

class PredictRequest(BaseModel):
    text: str = Field(
        ...,
        description="The code-mixed sentence to analyze for token-level language identification.",
        examples=["Hello nenu school ki vellanu"]
    )


class TokenPrediction(BaseModel):
    token_index: int
    token: str
    predicted_label: str
    predicted_label_id: int
    confidence: float


class PredictResponse(BaseModel):
    text: str
    tokens: List[TokenPrediction]
    chunked: bool
    chunk_count: int
    model: str


# ==============================================================================
# Pydantic Schemas - Model 2 (Translation)
# ==============================================================================

class TranslateRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Romanized Hinglish text to translate into English.",
        examples=["bas kabhi ghamand nahi kiya."]
    )


class TranslateResponse(BaseModel):
    source_text: str
    translated_text: str
    model: str = "google/mt5-small"
    task: str = "Romanized Hinglish to English translation"
    num_beams: int = 4


# ==============================================================================
# Helper Functions
# ==============================================================================

def check_translation_assets_available() -> bool:
    """Check if required translation model assets exist on disk without loading."""
    try:
        model_dir = HinglishTranslator.resolve_model_dir()
        if not model_dir.is_dir():
            return False
        for req in HinglishTranslator.REQUIRED_FILES:
            if not (model_dir / req).is_file():
                return False
        return True
    except Exception:
        return False


def get_translator(app_instance: FastAPI) -> HinglishTranslator:
    """
    Thread-safe lazy singleton getter for HinglishTranslator.
    Guarantees that concurrent requests cannot instantiate multiple copies of the model.
    """
    global translator

    # Fast path: instance already created on app.state or global
    trans = getattr(app_instance.state, "translator", None) or translator
    if trans is not None:
        return trans

    with _translator_init_lock:
        # Double-checked locking
        trans = getattr(app_instance.state, "translator", None) or translator
        if trans is not None:
            return trans

        logger.info("Initializing HinglishTranslator on first translation request...")
        try:
            new_translator = HinglishTranslator(lazy=True)
            new_translator.verify_model_assets()
        except FileNotFoundError as e:
            logger.error("Translation model assets missing: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Translation model artifacts are missing or not extracted."
            ) from e
        except Exception as e:
            logger.error("Failed to initialize translator: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Translation service is temporarily unavailable."
            ) from e

        translator = new_translator
        app_instance.state.translator = new_translator
        return new_translator


# ==============================================================================
# API Endpoints
# ==============================================================================

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    """Basic service health check."""
    return {"status": "healthy"}


@app.get("/api/health", status_code=status.HTTP_200_OK)
def api_health(request: Request) -> Dict[str, Any]:
    """
    Detailed model and environment health check.
    Preserves all existing Model 1 keys while adding translation capability status.
    Never triggers translation model loading.
    """
    pred: Optional[MuRILLIDPredictor] = getattr(request.app.state, "predictor", predictor)
    if pred is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MuRIL model is not initialized or still loading."
        )

    # Translation model status (passive check, does NOT load weights)
    trans: Optional[HinglishTranslator] = getattr(request.app.state, "translator", None) or translator
    is_loaded = bool(trans.model_loaded) if trans is not None else False
    trans_device = str(trans.device) if (trans is not None and is_loaded) else None
    is_available = True if is_loaded else check_translation_assets_available()

    return {
        "application": "CodeMix Intelligence - Token-Level Language Identification",
        "model": "google/muril-base-cased",
        "model_loaded": True,
        "device": str(pred.device),
        "supported_labels": list(pred.LABEL2ID.keys()),
        "label_mapping": pred.LABEL2ID,
        "status": "ready",
        "translation": {
            "model": "google/mt5-small",
            "task": "Romanized Hinglish to English translation",
            "available": is_available,
            "loaded": is_loaded,
            "device": trans_device,
            "precision": "FP32"
        }
    }


@app.post(
    "/api/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK
)
def predict_tokens(payload: PredictRequest, request: Request) -> Dict[str, Any]:
    """
    Predict token-level language identification tags for a given code-mixed text using MuRIL.
    """
    cleaned_text = payload.text.strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text must not be empty or whitespace only."
        )

    pred: Optional[MuRILLIDPredictor] = getattr(request.app.state, "predictor", predictor)
    if pred is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictor is not loaded."
        )

    try:
        result = pred.predict(cleaned_text)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error("MuRIL inference error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


@app.post(
    "/api/translate",
    response_model=TranslateResponse,
    status_code=status.HTTP_200_OK
)
def translate_text(payload: TranslateRequest, request: Request) -> Dict[str, Any]:
    """
    Translate Romanized Hinglish text to English using fine-tuned mT5-small.
    """
    cleaned_text = payload.text.strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text must not be empty or whitespace only."
        )

    trans = get_translator(request.app)

    try:
        translated = trans.translate(cleaned_text)
        return {
            "source_text": cleaned_text,
            "translated_text": translated,
            "model": trans.model_name,
            "task": trans.task,
            "num_beams": getattr(trans, "NUM_BEAMS", 4)
        }
    except FileNotFoundError as e:
        logger.error("Translation model artifact missing during inference: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation model artifacts are missing."
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e
    except RuntimeError as e:
        err_msg = str(e)
        logger.error("Translation runtime error: %s", e, exc_info=True)
        if "Failed to load" in err_msg or "Model directory does not exist" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Translation model failed to load."
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation execution failed."
        ) from e
    except Exception as e:
        logger.error("Unexpected translation exception: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation execution failed."
        ) from e
