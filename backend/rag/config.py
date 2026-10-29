import os
from pathlib import Path

RAG_DIR = Path(os.getenv("RAG_STORAGE_DIR", "data/rag_store"))
RAG_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = RAG_DIR / "faiss.index"
CHUNKS_PATH = RAG_DIR / "chunks.json"

EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
CHAT_MODEL = os.getenv(
    "RAG_CHAT_MODEL",
    "llama-3.3-70b-versatile",
)

CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
