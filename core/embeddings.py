"""
Embedding engine — HuggingFace API for semantic search.
Falls back gracefully to text search if API unavailable.

Architecture:
  - Query embedding: HuggingFace API (free tier)
  - Fallback: PostgreSQL ILIKE text search (always works)
  - Zero RAM on Fly.io — no local model loaded
"""

import os
import httpx
import asyncio
import concurrent.futures
from typing import List, Dict, Any
from sqlalchemy import text
from .database import SessionLocal


def get_model_name() -> str:
    return os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")


async def _embed_via_hf_api(text_input: str, is_query: bool = False) -> List[float]:
    """
    Call HuggingFace Inference API to embed a single text.
    Returns [] on any error — caller uses text search fallback.
    """
    model = get_model_name()

    # Apply e5 prefix — same format used when chunks were originally embedded
    if "e5" in model.lower():
        prefix = "query: " if is_query else "passage: "
        text_input = prefix + text_input.strip()

    # Try feature-extraction URL first, fall back to original if 404
    urls_to_try = [
        f"https://router.huggingface.co/hf-inference/models/{model}/feature-extraction",
        f"https://router.huggingface.co/hf-inference/models/{model}",
    ]

    hf_token = os.getenv("HF_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        for url in urls_to_try:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    json={"inputs": text_input, "options": {"wait_for_model": True}},
                )

                if response.status_code == 200:
                    result = response.json()
                    break
                elif response.status_code == 404:
                    # Try next URL
                    continue
                else:
                    print(
                        f"⚠️  HF API error {response.status_code}: {response.text[:200]}"
                    )
                    return []
            except Exception as e:
                print(f"⚠️  HF API error: {e}")
                continue
        else:
            # All URLs failed
            print("⚠️  All HF router URLs failed - falling back to text search")
            return []

        # Unwrap nested lists: [[[ ]]] → [[]] → [] → [float, ...]
        while (
            isinstance(result, list) and len(result) > 0 and isinstance(result[0], list)
        ):
            result = result[0]

        if (
            isinstance(result, list)
            and len(result) > 0
            and isinstance(result[0], float)
        ):
            return result

        print(f"⚠️  HF API unexpected shape: {str(result)[:100]}")
        return []


class EmbeddingEngine:
    """
    Embedding engine — calls HuggingFace API for vector search.
    is_loaded() always True so text fallback is never blocked.
    """

    def __init__(self):
        self.model = None  # Never loaded locally — zero RAM
        self._hf_available = bool(os.getenv("HF_TOKEN", ""))
        if self._hf_available:
            print(f"✅ Embedding engine ready (HuggingFace API): {get_model_name()}")
        else:
            print("⚠️  HF_TOKEN not set — text search fallback active")

    def is_loaded(self) -> bool:
        """
        Always True — text fallback works even without HF API.
        Returning False would block all search in SearchEngine._generate_embedding().
        """
        return True

    def has_semantic(self) -> bool:
        """True only if HF API token is configured."""
        return self._hf_available

    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        """
        Generate embedding via HF API.
        Returns [] if API fails — SearchEngine uses text fallback.
        """
        if not self._hf_available or not text:
            return []

        try:
            # Run in thread pool to avoid blocking the event loop
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, _embed_via_hf_api(text, is_query))
                return future.result(timeout=30)
        except Exception as e:
            print(f"⚠️  embed_text error: {e}")
            return []

    def embed_batch(
        self, texts: List[str], is_query: bool = False
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts sequentially."""
        if not self._hf_available or not texts:
            return [[] for _ in texts]
        return [self.embed_text(t, is_query=is_query) for t in texts]


# ── Global singleton ──────────────────────────────────────────────────────────

_embedding_engine = None


def get_embedding_engine() -> EmbeddingEngine:
    """Get or create the global embedding engine instance."""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = EmbeddingEngine()
    return _embedding_engine


def get_transformer():
    """Legacy compatibility shim."""
    return get_embedding_engine()


# ── Utility functions ─────────────────────────────────────────────────────────


def configure_pgvector() -> bool:
    db = SessionLocal()
    try:
        conn = db.connection()
        res = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname='vector'")
        ).fetchone()
        db.close()
        return bool(res)
    except Exception:
        db.close()
        return False


def embedding_generation_pipeline(
    texts: List[str], is_query: bool = False
) -> List[List[float]]:
    engine = get_embedding_engine()
    return engine.embed_batch(texts, is_query=is_query)


def vector_similarity_search(db, query: str, limit: int = 5) -> Dict[str, Any]:
    from .search import SearchEngine

    return SearchEngine(db).search(query, limit=limit)


def optimize_vector_indexing() -> bool:
    db = SessionLocal()
    try:
        conn = db.connection()
        res = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname='vector'")
        )
        if res.fetchone():
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_documents_embedding "
                    "ON documents USING ivfflat (embedding vector_cosine_ops);"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_chunks_embedding "
                    "ON content_chunks USING ivfflat (embedding vector_cosine_ops);"
                )
            )
            db.commit()
        db.close()
        return True
    except Exception:
        db.close()
        return False


def ensure_multilingual_model() -> str:
    return get_model_name()
