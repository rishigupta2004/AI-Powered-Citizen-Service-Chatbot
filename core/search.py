"""
Streamlined Search Engine — semantic search with text fallback.

Search priority:
  1. Vector semantic search (HF API embeddings) — best results
  2. PostgreSQL text search (ILIKE fallback) — always works
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import os
from .repositories import (
    ServiceRepository,
    DocumentRepository,
    FAQRepository,
    ContentChunkRepository,
)
from .embeddings import get_embedding_engine


class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
        self.embeddings_enabled = os.getenv("EMBEDDING_ENABLED", "true").lower() in (
            "1", "true", "yes",
        )
        self.embedding_model = None
        self.service_repo = ServiceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.faq_repo = FAQRepository(db)
        self.chunk_repo = ContentChunkRepository(db)

    def search(
        self, query: str, service_id: Optional[int] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Hybrid search across all content types.
        Tries vector search first; falls back to text search if embedding is empty.
        """
        try:
            # Generate query embedding (returns [] if HF API unavailable)
            query_embedding = (
                self._generate_embedding(query) if self.embeddings_enabled else []
            )

            results = []

            # ── Documents ────────────────────────────────────────────────
            docs = []
            if self.embeddings_enabled and query_embedding:
                docs = self.document_repo.search_semantic(query_embedding, limit)
            if not docs:
                # Text fallback
                docs = self.document_repo.search_text(query, limit)

            for doc in docs:
                if not service_id or doc.service_id == service_id:
                    results.append({
                        "type": "document",
                        "content": doc.raw_content or doc.name,
                        "similarity": self._calculate_similarity(
                            query_embedding, doc.embedding
                        ) if query_embedding else 0.5,
                        "service_id": doc.service_id,
                        "source": "document",
                        "source_name": doc.name,
                    })

            # ── FAQs ─────────────────────────────────────────────────────
            faqs = []
            if self.embeddings_enabled and query_embedding:
                faqs = self.faq_repo.search_semantic(query_embedding, limit)
            if not faqs:
                faqs = self.faq_repo.search_text(query, limit)

            for faq in faqs:
                if not service_id or faq.service_id == service_id:
                    results.append({
                        "type": "faq",
                        "content": f"Q: {faq.question}\nA: {faq.answer}",
                        "similarity": self._calculate_similarity(
                            query_embedding, faq.question_embedding
                        ) if query_embedding else 0.5,
                        "service_id": faq.service_id,
                        "source": "faq",
                        "source_name": faq.question[:80] if faq.question else "",
                    })

            # ── Content Chunks ───────────────────────────────────────────
            chunks = []
            if self.embeddings_enabled and query_embedding:
                chunks = self.chunk_repo.search_semantic(query_embedding, limit)
            if not chunks:
                # Text fallback — always returns results if data exists
                chunks = self.chunk_repo.search_text(query, limit)

            for chunk in chunks:
                if not service_id or chunk.service_id == service_id:
                    results.append({
                        "type": "content_chunk",
                        "content": chunk.chunk_text,
                        "similarity": self._calculate_similarity(
                            query_embedding, chunk.embedding
                        ) if query_embedding else 0.5,
                        "service_id": chunk.service_id,
                        "source": "content_chunk",
                        "source_name": f"chunk_{chunk.chunk_id}",
                    })

            # Sort by similarity score descending
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

            return {
                "query": query,
                "total_results": len(results),
                "results": results[:limit],
                "search_mode": "semantic" if query_embedding else "text",
            }

        except Exception as e:
            return {
                "query": query,
                "total_results": 0,
                "results": [],
                "error": str(e),
            }

    def get_model_name(self) -> str:
        return self.model_name

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding via HF API. Returns [] if unavailable."""
        try:
            engine = get_embedding_engine()
            if not engine.is_loaded():
                return []
            return engine.embed_text(text, is_query=True)
        except Exception:
            return []

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: Any
    ) -> float:
        """Cosine similarity between two embedding vectors."""
        try:
            if not embedding1 or embedding2 is None:
                return 0.0

            # Handle pgvector returning numpy array or list
            if hasattr(embedding2, 'tolist'):
                embedding2 = embedding2.tolist()
            if not embedding2:
                return 0.0

            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))
        except Exception:
            return 0.0