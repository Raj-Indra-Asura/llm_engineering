from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
