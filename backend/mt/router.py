"""Plug into your existing FastAPI app:
    from backend.mt.router import router      # or `from mt.router import router` if you run uvicorn inside backend/
    app.include_router(router)
Adds POST /api/mt/translate and GET /api/mt/translate/health."""
import os
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .pipeline import CodeMixPipeline, build_pipeline

router = APIRouter()
_pipe = None


def set_pipeline(p: CodeMixPipeline):  # used by tests
    global _pipe
    _pipe = p


def get_pipeline():
    global _pipe
    if _pipe is None:
        _pipe = build_pipeline(translit_backend=os.getenv("TRANSLIT_BACKEND", "auto"))
    return _pipe


class TranslateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    strategy: Literal["direct", "lid_only", "full", "clause"] = "full"
    gloss: bool = False
    src_hint: Literal["TE", "HI"] = "TE"   # only used by the "direct" baseline (it has no LID)


@router.get("/api/mt/translate/health")
def health():
    return {"status": "ok", "loaded": _pipe is not None}


@router.post("/api/mt/translate")
def translate(req: TranslateRequest):
    try:
        return get_pipeline().run(req.text, strategy=req.strategy, src_hint=req.src_hint, gloss=req.gloss)
    except Exception as e:  # surface model-loading problems clearly in the UI
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
