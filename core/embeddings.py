import os
from typing import List, Dict, Any
from sqlalchemy import text
from .database import SessionLocal
from .search import SearchEngine

def get_model_name() -> str:
    return os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

def get_transformer():
    """Lazily import transformer only if embeddings are enabled."""
    enabled = os.getenv('EMBEDDING_ENABLED', 'true').lower() in ('1', 'true', 'yes')
    if not enabled:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(get_model_name())
    except Exception:
        return None

def configure_pgvector() -> bool:
    """Verify pgvector extension is available."""
    db = SessionLocal()
    try:
        conn = db.connection()
        res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname='vector'")).fetchone()
        db.close()
        return bool(res)
    except Exception:
        db.close()
        return False

def embedding_generation_pipeline(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts, if enabled."""
    model = get_transformer()
    if model is None:
        return [[] for _ in texts]
    try:
        return [model.encode(t or "").tolist() for t in texts]
    except Exception:
        return [[] for _ in texts]

def vector_similarity_search(db, query: str, limit: int = 5) -> Dict[str, Any]:
    """Run semantic search using the core SearchEngine wrapper."""
    return SearchEngine(db).search(query, limit=limit)

def optimize_vector_indexing() -> bool:
    """Create ivfflat indexes for vector columns if pgvector is available."""
    db = SessionLocal()
    try:
        conn = db.connection()
        res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname='vector'"))
        if res.fetchone():
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON content_chunks USING ivfflat (embedding vector_cosine_ops);"))
            db.commit()
        db.close()
        return True
    except Exception:
        db.close()
        return False

def ensure_multilingual_model() -> str:
    """Return the currently configured model; supports multilingual models via ENV."""
    return get_model_name()