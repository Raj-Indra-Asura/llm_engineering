from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache
from pathlib import Path


def _chunk_text(text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return [normalized]

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + max_chars)
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = max(0, end - overlap)
    return chunks


@lru_cache(maxsize=8)
def _get_collection(db_path: Path):
    import chromadb

    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(name="gridlens_knowledge", metadata={"hnsw:space": "cosine"})


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    try:
        return SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception:
        return _HashingSentenceTransformer()


class _HashingSentenceTransformer:
    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def encode(self, texts, normalize_embeddings: bool = True):
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                index = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16) % self.dimensions
                vector[index] += 1.0
            if normalize_embeddings:
                magnitude = math.sqrt(sum(value * value for value in vector))
                if magnitude:
                    vector = [value / magnitude for value in vector]
            vectors.append(vector)

        class _Encoded(list):
            def tolist(self):
                return list(self)

        return _Encoded(vectors)


def ingest_knowledge_base(knowledge_dir: Path, db_path: Path) -> dict:
    collection = _get_collection(db_path)
    model = _get_model()

    n_files_ingested = 0
    n_files_skipped = 0
    n_chunks = 0

    for file_path in sorted(knowledge_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()
        doc_id = file_path.stem
        title_line = content.splitlines()[0].strip() if content else doc_id
        title = title_line.lstrip("# ").strip() or doc_id
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        existing = collection.get(where={"doc_id": doc_id}, include=["metadatas"])
        existing_hash = None
        if existing["metadatas"]:
            existing_hash = existing["metadatas"][0].get("content_hash")
        if existing_hash == content_hash:
            n_files_skipped += 1
            n_chunks += len(existing["ids"])
            continue

        if existing["ids"]:
            collection.delete(ids=existing["ids"])

        chunks = _chunk_text(content)
        embeddings = model.encode(chunks, normalize_embeddings=True).tolist()
        ids = [f"{doc_id}:{index}:{content_hash[:12]}" for index in range(len(chunks))]
        metadatas = [
            {
                "doc_id": doc_id,
                "title": title,
                "chunk_index": index,
                "file_path": str(file_path),
                "content_hash": content_hash,
            }
            for index in range(len(chunks))
        ]
        collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
        n_files_ingested += 1
        n_chunks += len(chunks)

    return {
        "n_files_total": len(list(knowledge_dir.glob("*.md"))),
        "n_files_ingested": n_files_ingested,
        "n_files_skipped": n_files_skipped,
        "n_chunks": n_chunks,
        "db_path": str(db_path),
    }


if __name__ == "__main__":
    knowledge_dir = Path(__file__).parent.parent / "data" / "knowledge"
    db_path = Path(__file__).parent.parent / "data" / "chroma_db"
    result = ingest_knowledge_base(knowledge_dir, db_path)
    print(f"Ingested: {result}")
