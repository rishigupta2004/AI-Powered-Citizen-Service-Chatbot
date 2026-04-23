from typing import List, Dict, Any

from .repositories import ContentChunkRepository, FAQRepository, DocumentRepository
from .search import SearchEngine


class RecommendationEngine:
    def __init__(self):
        self.chunk_repo = ContentChunkRepository()
        self.faq_repo = FAQRepository()
        self.doc_repo = DocumentRepository()
        self.search_engine = SearchEngine()

    def recommend_by_embedding(self, text: str, top_k: int = 8) -> List[Dict[str, Any]]:
        # Prefer semantic search across chunks, fallback to text search
        try:
            results = self.chunk_repo.semantic_search(text, top_k=top_k)
        except Exception:
            results = self.chunk_repo.text_search(text, top_k=top_k)
        # Normalize output
        normalized = []
        for r in results:
            normalized.append({
                "chunk_id": r.get("id") or r.get("chunk_id"),
                "document_id": r.get("document_id"),
                "score": r.get("score", None),
                "preview": r.get("content", "")[:240],
            })
        return normalized

    def suggest_queries(self, prefix: str, top_k: int = 10) -> List[str]:
        # Use search engine suggestion if available, fallback to FAQ titles
        try:
            return self.search_engine.suggest(prefix, top_k=top_k)
        except Exception:
            faqs = self.faq_repo.text_search(prefix, top_k=top_k)
            titles = [f.get("question") or f.get("title") for f in faqs]
            return [t for t in titles if t]