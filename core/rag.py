from typing import List, Dict, Any
from .database import SessionLocal
from .search import SearchEngine
from .nlp import NLPToolkit
import os

class RAGPipeline:
    """Minimal RAG pipeline for government queries with citations and scoring."""
    def __init__(self, db=None):
        self.db = db or SessionLocal()
        self.search = SearchEngine(self.db)
        self.nlp = NLPToolkit()
        # Gate any generative behavior behind env flag (disabled by default)
        self.generative_enabled = os.getenv('GENERATIVE_ENABLED', 'false').lower() in ('1', 'true', 'yes')

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        res = self.search.search(query, limit=top_k)
        return res.get("results", [])

    def generate_response(self, query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Non-LLM synthesis from contexts (always available)
        content_parts = [c.get("content", "")[:200] for c in contexts if c.get("content")]
        summary = " ".join(content_parts)[:800]
        lang = self.nlp.language_detection(query)
        citations = [{"source": c.get("source"), "service_id": c.get("service_id")} for c in contexts]
        answer = f"Answer ({lang}): {summary}" if summary else "No context available."
        return {"answer": answer, "citations": citations}

    def score_answer(self, query: str, result: Dict[str, Any]) -> float:
        score = 0.5
        if result.get("citations"):
            score += 0.3
        if len(result.get("answer", "")) > 50:
            score += 0.2
        return min(score, 1.0)

    def ask(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        ctx = self.retrieve_context(query, top_k)
        resp = self.generate_response(query, ctx)
        resp["score"] = self.score_answer(query, resp)
        return resp