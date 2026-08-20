# RAG Module — Retrieval-Augmented Generation
# Pipeline: Query → Embed → ChromaDB Search → Context → LLM

from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import torch

# ─── Config (match embed_data.py) ─────────────────────────
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "project_global"
EMBED_MODEL = "BAAI/bge-m3"
USE_FP16 = True
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─── Lazy-loaded Embedding Model ──────────────────────────
_embed_model = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(EMBED_MODEL, trust_remote_code=True, device=DEVICE)
        if USE_FP16 and DEVICE == "cuda":
            _embed_model.half()
    return _embed_model


def embed_text(text: str) -> List[float]:
    """Generate embedding for a single query text."""
    model = _get_embed_model()
    emb = model.encode([text], normalize_embeddings=True, convert_to_tensor=True, device=DEVICE, show_progress_bar=False)
    return emb.cpu().float().numpy()[0].tolist()


# ─── ChromaDB Client ──────────────────────────────────────
_client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
_collection = _client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


# ─── Public API ───────────────────────────────────────────

def query_similar(query: str, n_results: int = 5, source_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve top-k similar documents for a query. Optionally filter by source_file."""
    query_embedding = embed_text(query)
    where = {"source_file": source_file} if source_file else None
    results = _collection.query(query_embeddings=[query_embedding], n_results=n_results, include=["documents", "metadatas", "distances"], where=where)
    if not results["documents"] or not results["documents"][0]:
        return []
    return [{"document": doc, "metadata": meta, "distance": dist} for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])]


def build_context(query: str, n_results: int = 5, source_file: Optional[str] = None) -> str:
    """Build context string from retrieved documents. Optionally filter by source_file."""
    results = query_similar(query, n_results, source_file)
    if not results:
        return ""
    parts = []
    for i, r in enumerate(results, 1):
        meta = r["metadata"]
        title = meta.get("title", meta.get("source_file", "Unknown"))
        parts.append(f"[Source {i}: {title}]\n{r['document']}")
    return "\n\n---\n\n".join(parts)


def get_collection_stats() -> Dict[str, Any]:
    return {"document_count": _collection.count(), "collection_name": COLLECTION_NAME}


def clear_collection() -> None:
    _client.delete_collection(COLLECTION_NAME)
    global _collection
    _collection = _client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})