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
from core.embeddings import get_embedding_engine


def load_model():
    engine = get_embedding_engine()
    if engine.is_loaded():
        return engine
    return None


def encode(engine, text: str, is_query: bool = False) -> List[float]:
    try:
        if not engine:
            return []
        return engine.embed_text(text, is_query=is_query)
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
                d.embedding = encode(engine, d.raw_content or d.name, is_query=False)
                updated["documents"] += 1
            db.commit()

        # FAQs (Passages)
        faq_q_col = column_exists(insp, "faqs", "question_embedding")
        if faq_q_col:
            print("Backfilling FAQs...")
            # We want to re-embed all FAQs to use the new multilingual model
            # So we don't filter by is_(None)
            faqs = db.query(FAQ).limit(1000).all()
            for f in faqs:
                f.question_embedding = encode(engine, f.question, is_query=False)
                f.answer_embedding = encode(engine, f.answer, is_query=False)
                updated["faqs"] += 1
            db.commit()

        # Content Chunks (Passages)
        chunk_col = column_exists(insp, "content_chunks", "embedding")
        if chunk_col:
            print("Backfilling content chunks...")
            # Re-embed all chunks
            chunks = (
                db.query(ContentChunk)
                .options(
                    load_only(
                        ContentChunk.chunk_id,
                        ContentChunk.chunk_text,
                        ContentChunk.embedding,
                    )
                )
                .limit(5000)
                .all()
            )

            # Process in batches
            batch_size = 50
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i : i + batch_size]
                texts = [c.chunk_text for c in batch]
                embeddings = engine.embed_batch(texts, is_query=False)

                for j, chunk in enumerate(batch):
                    if j < len(embeddings) and len(embeddings[j]) > 0:
                        chunk.embedding = embeddings[j]
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
