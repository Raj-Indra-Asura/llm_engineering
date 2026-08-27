from __future__ import annotations

from fastapi import FastAPI

from gridlens.app.routers import health, scenarios

app = FastAPI(title="GridLens API", version="1.0.0")
app.include_router(health.router)
app.include_router(scenarios.router, prefix="/api")
