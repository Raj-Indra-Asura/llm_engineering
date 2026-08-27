from __future__ import annotations

from pathlib import Path
import re

from gridlens.domain.models import SourceReference
from gridlens.rag.ingest import _get_collection, _get_model


def _keyword_fallback(query: str, db_path: Path, n_results: int) -> list[SourceReference]:
    collection = _get_collection(db_path)
    payload = collection.get(include=["documents", "metadatas"])
    tokens = [token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2]
    if not tokens:
        return []

    ranked: list[tuple[int, str, dict]] = []
    for document, metadata in zip(payload["documents"], payload["metadatas"], strict=False):
        score = sum(token in document.lower() for token in tokens)
        if score:
            ranked.append((score, document, metadata))
    ranked.sort(key=lambda item: item[0], reverse=True)

    return [
        SourceReference(
            doc_id=metadata["doc_id"],
            title=metadata["title"],
            chunk_index=int(metadata["chunk_index"]),
            similarity_score=float(score) / max(len(tokens), 1),
            excerpt=document[:280],
            metadata=metadata,
        )
        for score, document, metadata in ranked[:n_results]
    ]


def retrieve_context(
    query: str,
    db_path: Path,
    n_results: int = 5,
    similarity_threshold: float = 0.3,
) -> list[SourceReference]:
    collection = _get_collection(db_path)
    if collection.count() == 0:
        return []

    model = _get_model()
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()[0]
    response = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    matches: list[SourceReference] = []
    for document, metadata, distance in zip(
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
        strict=False,
    ):
        similarity = max(0.0, 1.0 - float(distance))
        if similarity < similarity_threshold:
            continue
        matches.append(
            SourceReference(
                doc_id=metadata["doc_id"],
                title=metadata["title"],
                chunk_index=int(metadata["chunk_index"]),
                similarity_score=similarity,
                excerpt=document[:280],
                metadata=metadata,
            )
        )

    return matches or _keyword_fallback(query, db_path, n_results)
