from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from gridlens.app.config import Settings
from gridlens.app.logging_config import get_logger
from gridlens.app.routers import compare, explain, health, scenarios

settings = Settings()
logger = get_logger(__name__)

app = FastAPI(title=settings.app_name, version=settings.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
        logger.exception(
            "request_failed",
            extra={
                "request_id": getattr(request.state, "request_id", ""),
                "operation": f"{request.method} {request.url.path}",
                "duration_ms": duration_ms,
                "error_category": "unhandled_exception",
            },
        )
        raise

    duration_ms = round((time.perf_counter() - started_at) * 1000, 3)
    logger.info(
        "request_completed",
        extra={
            "request_id": getattr(request.state, "request_id", ""),
            "operation": f"{request.method} {request.url.path}",
            "duration_ms": duration_ms,
        },
    )
    return response


app.include_router(health.router)
app.include_router(scenarios.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(explain.router, prefix="/api")
