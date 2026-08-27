from __future__ import annotations

import shutil
from pathlib import Path

import httpx
import pytest

from gridlens.app.main import app
from gridlens.domain.models import ScenarioRequest
from gridlens.rag.ingest import ingest_knowledge_base


@pytest.fixture
def default_request() -> ScenarioRequest:
    return ScenarioRequest()


@pytest.fixture(scope="session")
def knowledge_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "knowledge"


@pytest.fixture(scope="session")
def rag_db_path(knowledge_dir: Path) -> Path:
    db_path = Path(__file__).resolve().parents[1] / "data" / "chroma_db_test"
    if db_path.exists():
        shutil.rmtree(db_path)
    ingest_knowledge_base(knowledge_dir, db_path)
    return db_path


@pytest.fixture
async def async_client() -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
