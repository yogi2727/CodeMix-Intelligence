"""
CodeMix Intelligence - Step 33B
FastAPI Backend for Token-Level Language Identification

Endpoints:
- GET /health: Basic service status
- GET /api/health: Detailed application and model status
- POST /api/predict: Token-level language identification prediction
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.inference.predictor import MuRILLIDPredictor

# Global predictor holder for lifespan
predictor: MuRILLIDPredictor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model once at application startup."""
    global predictor
    print("Loading MuRIL LID Predictor on application startup...")
    predictor = MuRILLIDPredictor()
    app.state.predictor = predictor
    print(f"MuRIL LID Predictor loaded successfully on device: {predictor.device}")
    yield
    print("Shutting down MuRIL LID Predictor...")
    predictor = None


app = FastAPI(
    title="CodeMix Intelligence LID API",
    description="Token-Level Language Identification for English, Hindi, and Telugu Code-Mixed Text",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Pydantic Schemas
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
# API Endpoints
# ==============================================================================

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, str]:
    """Basic service health check."""
    return {"status": "healthy"}


@app.get("/api/health", status_code=status.HTTP_200_OK)
def api_health(request: Request) -> Dict[str, Any]:
    """Detailed model and environment health check."""
    pred: MuRILLIDPredictor = getattr(request.app.state, "predictor", predictor)
    if pred is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MuRIL model is not initialized or still loading."
        )

    return {
        "application": "CodeMix Intelligence - Token-Level Language Identification",
        "model": "google/muril-base-cased",
        "model_loaded": True,
        "device": str(pred.device),
        "supported_labels": list(pred.LABEL2ID.keys()),
        "label_mapping": pred.LABEL2ID,
        "status": "ready"
    }


@app.post(
    "/api/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK
)
def predict_tokens(payload: PredictRequest, request: Request) -> Dict[str, Any]:
    """
    Predict token-level language identification tags for a given code-mixed text.
    """
    cleaned_text = payload.text.strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input text must not be empty or whitespace only."
        )

    pred: MuRILLIDPredictor = getattr(request.app.state, "predictor", predictor)
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
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )
