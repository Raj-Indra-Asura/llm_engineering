from pathlib import Path

from gridlens.rag.ingest import ingest_knowledge_base

if __name__ == "__main__":
    knowledge_dir = Path(__file__).parent.parent / "data" / "knowledge"
    db_path = Path(__file__).parent.parent / "data" / "chroma_db"
    result = ingest_knowledge_base(knowledge_dir, db_path)
    print(f"Ingested: {result}")
