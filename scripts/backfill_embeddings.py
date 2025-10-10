"""
Backfill embeddings for Documents, FAQs, and Content Chunks.
Skips items that already have embeddings. Safe to re-run.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import os
from typing import List
from sqlalchemy import inspect
from sqlalchemy.orm import load_only
from core.database import SessionLocal
from core.models import Document, FAQ, ContentChunk

def load_model():
    enabled = os.getenv('EMBEDDING_ENABLED', 'true').lower() in ('1', 'true', 'yes')
    if not enabled:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        return SentenceTransformer(model_name)
    except Exception:
        return None

def encode(model, text: str) -> List[float]:
    try:
        if not model:
            return []
        vec = model.encode(text or "")
        return vec.tolist()
    except Exception:
        return []

def column_exists(inspector, table_name: str, column: str) -> bool:
    try:
        cols = [c['name'] for c in inspector.get_columns(table_name)]
        return column in cols
    except Exception:
        return False

def main():
    db = SessionLocal()
    insp = inspect(db.bind)
    model = load_model()
    updated = {"documents": 0, "faqs": 0, "chunks": 0}
    try:
        if model is None:
            print("ℹ️ Embeddings disabled or model unavailable; skipping backfill.")
            print(f"✅ No changes made. Current counts: {updated}")
            db.close()
            return
        # Documents
        if column_exists(insp, 'documents', 'embedding'):
            docs = db.query(Document).filter(Document.embedding.is_(None)).limit(200).all()
            for d in docs:
                d.embedding = encode(model, d.raw_content or d.name)
                updated["documents"] += 1

        # FAQs
        faq_q_col = column_exists(insp, 'faqs', 'question_embedding')
        if faq_q_col:
            faqs = db.query(FAQ).filter(FAQ.question_embedding.is_(None)).limit(200).all()
            for f in faqs:
                f.question_embedding = encode(model, f.question)
                updated["faqs"] += 1
        # Content Chunks
        chunk_col = column_exists(insp, 'content_chunks', 'embedding')
        if chunk_col:
            chunks = (
                db.query(ContentChunk)
                .options(load_only(ContentChunk.chunk_id, ContentChunk.content_text, ContentChunk.embedding))
                .filter(ContentChunk.embedding.is_(None))
                .limit(200)
                .all()
            )
            for c in chunks:
                c.embedding = encode(model, c.content_text)
                updated["chunks"] += 1

        db.commit()
        print(f"✅ Backfill complete: {updated}")
    except Exception as e:
        db.rollback()
        print(f"❌ Backfill failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()