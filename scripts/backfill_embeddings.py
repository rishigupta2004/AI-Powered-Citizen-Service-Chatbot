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
from core.database import SessionLocal
from core.models import Document, FAQ, ContentChunk
from core.embeddings import get_embedding_engine
from core.config import EMBEDDING_DIM


def load_model():
    engine = get_embedding_engine()
    if engine.is_loaded():
        return engine
    return None


def encode(engine, text: str, is_query: bool = False) -> List[float]:
    try:
        if not engine:
            return []
        emb = engine.embed_text(text, is_query=is_query)
        if len(emb) != EMBEDDING_DIM:
            return []
        return emb
    except Exception:
        return []


def column_exists(inspector, table_name: str, column: str) -> bool:
    try:
        cols = [c["name"] for c in inspector.get_columns(table_name)]
        return column in cols
    except Exception:
        return False


def main():
    db = SessionLocal()
    insp = inspect(db.bind)
    engine = load_model()
    updated = {"documents": 0, "faqs": 0, "chunks": 0}
    try:
        if engine is None:
            print("ℹ️ Embeddings disabled or model unavailable; skipping backfill.")
            print(f"✅ No changes made. Current counts: {updated}")
            db.close()
            return

        print(
            f"Using model: {os.getenv('EMBEDDING_MODEL', 'intfloat/multilingual-e5-small')}"
        )

        # Documents (Passages)
        if column_exists(insp, "documents", "embedding"):
            print("Backfilling documents...")
            docs = (
                db.query(Document)
                .filter(Document.embedding.is_(None))
                .limit(1000)
                .all()
            )
            for d in docs:
                text_val = str(getattr(d, "raw_content", "") or getattr(d, "name", ""))
                emb = encode(engine, text_val, is_query=False)
                if emb:
                    setattr(d, "embedding", emb)
                    updated["documents"] += 1
            db.commit()

        # FAQs (Passages)
        faq_q_col = column_exists(insp, "faqs", "question_embedding")
        if faq_q_col:
            print("Backfilling FAQs...")
            faqs = (
                db.query(FAQ)
                .filter(
                    (FAQ.question_embedding.is_(None))
                    | (FAQ.answer_embedding.is_(None))
                )
                .limit(2000)
                .all()
            )
            for f in faqs:
                q_emb = encode(engine, str(getattr(f, "question", "")), is_query=False)
                a_emb = encode(engine, str(getattr(f, "answer", "")), is_query=False)
                if q_emb:
                    setattr(f, "question_embedding", q_emb)
                if a_emb:
                    setattr(f, "answer_embedding", a_emb)
                if q_emb or a_emb:
                    updated["faqs"] += 1
            db.commit()

        # Content Chunks (Passages)
        chunk_col = column_exists(insp, "content_chunks", "embedding")
        if chunk_col:
            print("Backfilling content chunks...")
            # Re-embed all chunks
            chunks = db.query(ContentChunk).limit(5000).all()
            chunks = (
                db.query(ContentChunk)
                .filter(ContentChunk.embedding.is_(None))
                .limit(10000)
                .all()
            )

            # Process in batches
            batch_size = 50
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]
                texts = [str(getattr(c, "chunk_text", "")) for c in batch]
                embeddings = engine.embed_batch(texts, is_query=False)

                for j, chunk in enumerate(batch):
                    if j < len(embeddings) and len(embeddings[j]) == EMBEDDING_DIM:
                        setattr(chunk, "embedding", embeddings[j])
                        updated["chunks"] += 1

                db.commit()
                print(f"Processed chunks {i} to {i + len(batch)} of {len(chunks)}")

        print(f"✅ Backfill complete: {updated}")
    except Exception as e:
        db.rollback()
        print(f"❌ Backfill failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
