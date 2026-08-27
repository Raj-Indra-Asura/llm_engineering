from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from gridlens.app.services.explain import explain_scenario
from gridlens.domain.models import ExplainRequest
from gridlens.rag.ingest import ingest_knowledge_base

router = APIRouter()

_ROOT = Path(__file__).resolve().parents[2]
_KNOWLEDGE_DIR = _ROOT / "data" / "knowledge"
_DB_PATH = _ROOT / "data" / "chroma_db"


@router.post("/explain")
def explain_endpoint(request: ExplainRequest) -> dict:
    ingest_knowledge_base(_KNOWLEDGE_DIR, _DB_PATH)
    return explain_scenario(request.result, request.question, _DB_PATH, use_llm=False)
