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
import httpx
import asyncio
from .repositories import (
    ServiceRepository,
    DocumentRepository,
    FAQRepository,
    ContentChunkRepository,
)
from .embeddings import get_embedding_engine
from .config import EMBEDDING_DIM


class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
        self.embeddings_enabled = os.getenv("EMBEDDING_ENABLED", "true").lower() in (
            "1",
            "true",
            "yes",
        )
        self.embedding_model = None
        self.rerank_enabled = os.getenv("RERANK_ENABLED", "false").lower() in (
            "1",
            "true",
            "yes",
        )
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
            # Generate query embedding with timeout protection
            query_embedding = []
            if self.embeddings_enabled:
                try:
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=1
                    ) as executor:
                        future = executor.submit(self._generate_embedding, query)
                        query_embedding = future.result(timeout=10)
                except Exception:
                    query_embedding = []

            # Expand query for multilingual recall
            expanded_queries = self._expand_query(query)
            lookup_queries = list(dict.fromkeys([query] + expanded_queries))
            results = []

            # ── Documents ────────────────────────────────────────────────
            docs = []
            if self.embeddings_enabled and query_embedding:
                try:
                    docs = self.document_repo.search_semantic(query_embedding, limit)
                except Exception:
                    docs = []
            if not docs:
                # Text fallback
                for lookup_q in lookup_queries[:2]:
                    docs.extend(self.document_repo.search_text(lookup_q, limit))

            for doc in docs:
                if not service_id or doc.service_id == service_id:
                    base_similarity = (
                        self._calculate_similarity(query_embedding, doc.embedding)
                        if query_embedding
                        else 0.45
                    )
                    keyword_boost = self._keyword_overlap_score(
                        query,
                        f"{doc.name or ''} {doc.description or ''} {doc.raw_content or ''}",
                    )
                    results.append(
                        {
                            "type": "document",
                            "content": doc.raw_content or doc.name,
                            "similarity": min(1.0, base_similarity + keyword_boost),
                            "service_id": doc.service_id,
                            "source": "document",
                            "source_name": doc.name,
                        }
                    )

            # ── FAQs ─────────────────────────────────────────────────────
            faqs = []
            if self.embeddings_enabled and query_embedding:
                try:
                    faqs = self.faq_repo.search_semantic(query_embedding, limit)
                except Exception:
                    faqs = []
            if not faqs:
                for lookup_q in lookup_queries[:2]:
                    faqs.extend(self.faq_repo.search_text(lookup_q, limit))

            for faq in faqs:
                if not service_id or faq.service_id == service_id:
                    base_similarity = (
                        self._calculate_similarity(
                            query_embedding, faq.question_embedding
                        )
                        if query_embedding
                        else 0.5
                    )
                    keyword_boost = self._keyword_overlap_score(
                        query, f"{faq.question or ''} {faq.answer or ''}"
                    )
                    results.append(
                        {
                            "type": "faq",
                            "content": f"Q: {faq.question}\nA: {faq.answer}",
                            "similarity": min(1.0, base_similarity + keyword_boost),
                            "service_id": faq.service_id,
                            "source": "faq",
                            "source_name": faq.question[:80] if faq.question else "",
                        }
                    )

            # ── Content Chunks ───────────────────────────────────────────
            chunks = []
            if self.embeddings_enabled and query_embedding:
                try:
                    chunks = self.chunk_repo.search_semantic(query_embedding, limit)
                except Exception:
                    chunks = []
            if not chunks:
                # Text fallback — always returns results if data exists
                for lookup_q in lookup_queries[:2]:
                    chunks.extend(self.chunk_repo.search_text(lookup_q, limit))

            for chunk in chunks:
                if not service_id or chunk.service_id == service_id:
                    base_similarity = (
                        self._calculate_similarity(query_embedding, chunk.embedding)
                        if query_embedding
                        else 0.45
                    )
                    keyword_boost = self._keyword_overlap_score(
                        query, chunk.chunk_text or ""
                    )
                    results.append(
                        {
                            "type": "content_chunk",
                            "content": chunk.chunk_text,
                            "similarity": min(1.0, base_similarity + keyword_boost),
                            "service_id": chunk.service_id,
                            "source": "content_chunk",
                            "source_name": f"chunk_{chunk.chunk_id}",
                        }
                    )

            # De-duplicate near-identical content snippets.
            deduped: list[dict[str, Any]] = []
            seen_fingerprints: set[str] = set()
            for item in results:
                fp = self._fingerprint(item.get("content", ""))
                if fp in seen_fingerprints:
                    continue
                seen_fingerprints.add(fp)
                deduped.append(item)
            results = deduped

            # Sort by similarity score descending
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)

            # Async reranking — only if we have semantic results
            if self.rerank_enabled and query_embedding and results:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        import concurrent.futures

                        with concurrent.futures.ThreadPoolExecutor() as pool:
                            results = pool.submit(
                                asyncio.run, self._rerank_via_hf(query, results, limit)
                            ).result(timeout=20)
                    else:
                        results = asyncio.run(
                            self._rerank_via_hf(query, results, limit)
                        )
                except Exception:
                    pass  # Keep original sort order

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
            vector = engine.embed_text(text, is_query=True)
            if not vector:
                return []
            if len(vector) != EMBEDDING_DIM:
                return []
            return vector
        except Exception:
            return []

    def _expand_query(self, query: str) -> list[str]:
        """Return [original_query, english_translation] for non-English queries."""
        queries = [query]
        try:
            if any(ord(c) > 127 for c in query):
                sarvam_key = os.getenv("SARVAM_API_KEY", "")
                if sarvam_key:
                    import httpx, asyncio

                    async def translate():
                        async with httpx.AsyncClient(timeout=10) as c:
                            r = await c.post(
                                "https://api.sarvam.ai/translate",
                                headers={"api-subscription-key": sarvam_key},
                                json={
                                    "input": query,
                                    "source_language_code": "auto",
                                    "target_language_code": "en-IN",
                                    "mode": "formal",
                                },
                            )
                            if r.status_code == 200:
                                return r.json().get("translated_text", "")
                            return ""

                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            import concurrent.futures

                            with concurrent.futures.ThreadPoolExecutor() as pool:
                                translated = pool.submit(
                                    asyncio.run, translate()
                                ).result(timeout=12)
                        else:
                            translated = asyncio.run(translate())
                        if translated and translated != query:
                            queries.append(translated)
                    except Exception:
                        pass
        except Exception:
            pass
        return queries

    def _fingerprint(self, text: str) -> str:
        return " ".join((text or "").lower().split())[:240]

    def _keyword_overlap_score(self, query: str, text: str) -> float:
        q_tokens = {tok for tok in query.lower().split() if len(tok) >= 3}
        if not q_tokens:
            return 0.0
        lowered = (text or "").lower()
        overlap = sum(1 for tok in q_tokens if tok in lowered)
        if overlap <= 0:
            return 0.0
        return min(0.25, overlap * 0.05)

    async def _rerank_via_hf(self, query: str, results: list, top_k: int = 5) -> list:
        """Rerank results using HF cross-encoder. Falls back to original order if API fails."""
        if not results or len(results) <= 1:
            return results
        try:
            hf_token = os.getenv("HF_TOKEN", "")
            url = "https://router.huggingface.co/hf-inference/models/cross-encoder/ms-marco-MiniLM-L-6-v2"
            pairs = [[query, r.get("content", "")[:512]] for r in results]
            async with httpx.AsyncClient(timeout=15) as c:
                resp = await c.post(
                    url,
                    headers={"Authorization": f"Bearer {hf_token}"},
                    json={"inputs": pairs},
                )
                if resp.status_code == 200:
                    scores = resp.json()
                    for i, r in enumerate(results):
                        r["rerank_score"] = scores[i] if isinstance(scores, list) else 0
                    results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        except Exception as e:
            print(f"Reranker skipped: {e}")
        return results[:top_k]

    def _calculate_similarity(self, embedding1: List[float], embedding2: Any) -> float:
        """Cosine similarity between two embedding vectors."""
        try:
            if not embedding1 or embedding2 is None:
                return 0.0

            # Handle pgvector returning numpy array or list
            if hasattr(embedding2, "tolist"):
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
