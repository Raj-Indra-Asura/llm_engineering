from __future__ import annotations

import shutil
from pathlib import Path

from gridlens.rag.answer import retrieve_context
from gridlens.rag.ingest import ingest_knowledge_base


def test_ingest_creates_db(knowledge_dir: Path) -> None:
    db_path = Path(__file__).resolve().parents[1] / "data" / "rag_ingest_test_db"
    if db_path.exists():
        shutil.rmtree(db_path)
    result = ingest_knowledge_base(knowledge_dir, db_path)

    assert result["n_chunks"] > 0


def test_retrieve_returns_results(rag_db_path: Path) -> None:
    results = retrieve_context("battery efficiency", rag_db_path)
    assert len(results) >= 1


def test_retrieve_threshold(rag_db_path: Path) -> None:
    results = retrieve_context("xyzzy quux blorb snth", rag_db_path, similarity_threshold=0.9999)
    assert results == []


def test_keyword_fallback(rag_db_path: Path) -> None:
    results = retrieve_context("locational pricing", rag_db_path, similarity_threshold=0.9999)
    assert len(results) >= 1
    assert any(result.doc_id == "07_system_limitations" for result in results)
