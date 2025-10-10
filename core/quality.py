"""
Week 7: Data Quality & Validation utilities

Includes:
- Comprehensive validation for documents and content chunks
- Content deduplication (in-memory hashing)
- Multilingual verification (basic script checks)
- Quality metrics summary
- Simple lineage logging (file-based)
"""
from __future__ import annotations

import os
import json
import hashlib
from typing import List, Dict, Any, Tuple

from sqlalchemy.orm import Session

from .repositories import DocumentRepository, ContentChunkRepository, ServiceRepository


def _normalize_text(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _content_hash(text: str) -> str:
    return hashlib.sha1(_normalize_text(text).encode("utf-8")).hexdigest()


def _contains_devanagari(text: str) -> bool:
    return any(0x0900 <= ord(ch) <= 0x097F for ch in (text or ""))


def _ascii_ratio(text: str) -> float:
    if not text:
        return 0.0
    total = len(text)
    ascii_count = sum(1 for ch in text if ord(ch) < 128)
    return ascii_count / max(total, 1)


class DataValidator:
    def __init__(self, db: Session):
        self.db = db
        self.docs = DocumentRepository(db)
        self.chunks = ContentChunkRepository(db)
        self.services = ServiceRepository(db)

    def validate_documents(self, limit: int = 1000) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        for doc in self.docs.get_all(skip=0, limit=limit):
            # Check service exists
            if not self.services.get_by_id(doc.service_id):
                issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "missing_service"})

            # Content presence and minimum length
            raw = doc.raw_content or ""
            if not raw.strip():
                issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "empty_raw_content"})
            elif len(_normalize_text(raw)) < 50:
                issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "short_raw_content"})

            # Embedding existence and shape (expect 384)
            emb = getattr(doc, "embedding", None)
            if emb is None:
                issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "missing_embedding"})
            else:
                try:
                    if len(list(emb)) != 384:
                        issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "bad_embedding_length"})
                except Exception:
                    issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "embedding_unreadable"})

            # Language tag present
            lang = (doc.language or "").strip().lower()
            if not lang:
                issues.append({"type": "document", "doc_id": doc.doc_id, "issue": "missing_language"})

        return issues

    def validate_chunks(self, limit: int = 5000) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        for chunk in self.chunks.get_all(skip=0, limit=limit):
            text = chunk.content_text or ""
            if len(_normalize_text(text)) < 20:
                issues.append({"type": "chunk", "chunk_id": chunk.chunk_id, "issue": "short_chunk"})

            emb = getattr(chunk, "embedding", None)
            if emb is None:
                issues.append({"type": "chunk", "chunk_id": chunk.chunk_id, "issue": "missing_embedding"})
            else:
                try:
                    if len(list(emb)) != 384:
                        issues.append({"type": "chunk", "chunk_id": chunk.chunk_id, "issue": "bad_embedding_length"})
                except Exception:
                    issues.append({"type": "chunk", "chunk_id": chunk.chunk_id, "issue": "embedding_unreadable"})

            # Category optional but recommended
            if not getattr(chunk, "category", None):
                issues.append({"type": "chunk", "chunk_id": chunk.chunk_id, "issue": "missing_category"})

        return issues


class Deduplicator:
    def __init__(self, db: Session):
        self.db = db
        self.docs = DocumentRepository(db)
        self.chunks = ContentChunkRepository(db)

    def find_duplicate_documents(self, limit: int = 2000) -> List[Tuple[int, List[int]]]:
        groups: Dict[str, List[int]] = {}
        for doc in self.docs.get_all(skip=0, limit=limit):
            h = _content_hash(doc.raw_content or "")
            groups.setdefault(h, []).append(doc.doc_id)
        return [(doc_ids[0], doc_ids[1:]) for doc_ids in groups.values() if len(doc_ids) > 1]

    def find_duplicate_chunks(self, limit: int = 10000) -> List[Tuple[int, List[int]]]:
        groups: Dict[str, List[int]] = {}
        for ch in self.chunks.get_all(skip=0, limit=limit):
            h = _content_hash(ch.content_text or "")
            groups.setdefault(h, []).append(ch.chunk_id)
        return [(chunk_ids[0], chunk_ids[1:]) for chunk_ids in groups.values() if len(chunk_ids) > 1]


class MultilingualVerifier:
    def verify_documents(self, db: Session, limit: int = 1000) -> List[Dict[str, Any]]:
        docs = DocumentRepository(db).get_all(skip=0, limit=limit)
        issues: List[Dict[str, Any]] = []
        for doc in docs:
            text = doc.raw_content or ""
            lang = (doc.language or "").lower()
            if lang == "hi":
                if not _contains_devanagari(text):
                    issues.append({"doc_id": doc.doc_id, "issue": "language_mismatch_hi"})
            elif lang == "en":
                if _ascii_ratio(text) < 0.7:
                    issues.append({"doc_id": doc.doc_id, "issue": "language_low_ascii_en"})
            # other languages can be added later
        return issues


class QualityMonitor:
    def summarize(self, db: Session) -> Dict[str, Any]:
        docs_repo = DocumentRepository(db)
        chunks_repo = ContentChunkRepository(db)
        total_docs = docs_repo.count()
        total_chunks = chunks_repo.count()

        # quick counts
        missing_doc_embeddings = 0
        missing_chunk_embeddings = 0
        for d in docs_repo.get_all(0, 500):
            if getattr(d, "embedding", None) is None:
                missing_doc_embeddings += 1
        for c in chunks_repo.get_all(0, 1000):
            if getattr(c, "embedding", None) is None:
                missing_chunk_embeddings += 1

        return {
            "documents": {
                "count": total_docs,
                "missing_embeddings": missing_doc_embeddings,
            },
            "chunks": {
                "count": total_chunks,
                "missing_embeddings": missing_chunk_embeddings,
            },
        }


class LineageTracker:
    def __init__(self, path: str = "gov-chatbot/data/db/lineage.log"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def log(self, event: Dict[str, Any]) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


def run_all_quality_checks(db: Session) -> Dict[str, Any]:
    validator = DataValidator(db)
    dedup = Deduplicator(db)
    mlv = MultilingualVerifier()
    monitor = QualityMonitor()

    return {
        "validation": {
            "documents": validator.validate_documents(),
            "chunks": validator.validate_chunks(),
        },
        "duplicates": {
            "documents": dedup.find_duplicate_documents(),
            "chunks": dedup.find_duplicate_chunks(),
        },
        "multilingual": mlv.verify_documents(db),
        "metrics": monitor.summarize(db),
    }