from typing import List, Dict, Any, Optional
from .database import SessionLocal
from .search import SearchEngine
from .repositories import DocumentRepository
from .nlp import NLPToolkit
from sqlalchemy.exc import SQLAlchemyError

_QUERY_LOG: List[Dict[str, Any]] = []

def hybrid_search(db, query: str, limit: int = 10) -> Dict[str, Any]:
    """Combine vector search with simple text search and merge results.
    Robust against database transaction errors by rolling back and returning graceful fallbacks.
    """
    se = SearchEngine(db)
    # Vector search with safe fallback
    try:
        vector = se.search(query, limit=limit)
        vector_results = vector.get("results", [])
    except Exception:
        # If vector search fails, fallback to no vector results
        vector_results = []

    # Text search with transaction safety
    text_results: List[Dict[str, Any]] = []
    try:
        repo = DocumentRepository(db)
        text_docs = repo.search_text(query, limit=limit)
        text_results = [
            {
                "type": "document",
                "content": d.raw_content or d.name,
                "similarity": 0.0,
                "service_id": d.service_id,
                "source": "text"
            }
            for d in text_docs
        ]
    except SQLAlchemyError:
        # Rollback aborted transaction and proceed with available results
        try:
            db.rollback()
        except Exception:
            pass
        text_results = []

    merged = vector_results + text_results
    merged.sort(key=lambda x: x.get("similarity", 0), reverse=True)
    return {"query": query, "results": merged[:limit], "total_results": len(merged)}

def query_understanding(text: str) -> Dict[str, Any]:
    nlp = NLPToolkit()
    entities = nlp.entity_extraction(text)
    intent = nlp.content_classification(text)
    lang = nlp.language_detection(text)
    return {"language": lang, "intent": intent, "entities": entities}

def multilingual_query_processing(text: str) -> Dict[str, str]:
    nlp = NLPToolkit()
    lang = nlp.language_detection(text)
    # Stub translation: return same text, mark language
    translated = text if lang == "en" else text
    return {"language": lang, "original": text, "english_text": translated}

def rank_and_filter(results: List[Dict[str, Any]], category: Optional[str] = None) -> List[Dict[str, Any]]:
    ranked = sorted(results, key=lambda x: x.get("similarity", 0), reverse=True)
    if category:
        ranked = [r for r in ranked if r.get("source") == category]
    return ranked

def log_query(query: str, meta: Optional[Dict[str, Any]] = None) -> None:
    _QUERY_LOG.append({"query": query, "meta": meta or {}})

def get_query_logs() -> List[Dict[str, Any]]:
    return list(_QUERY_LOG)