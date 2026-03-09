"""
Re-embed all chunks/FAQs with BAAI/bge-small-en-v1.5
Run once: python scripts/reembed_chunks.py
"""
import os, sys, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
os.environ['EMBEDDING_MODEL'] = 'BAAI/bge-small-en-v1.5'

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import SessionLocal
from core.models import ContentChunk, FAQ
from core.embeddings import get_embedding_engine

db = SessionLocal()
engine = get_embedding_engine()

# Re-embed chunks
chunks = db.query(ContentChunk).filter(ContentChunk.chunk_text.isnot(None)).all()
print(f"Re-embedding {len(chunks)} chunks...")
for i, chunk in enumerate(chunks):
    vec = engine.embed_text(chunk.chunk_text, is_query=False)
    if vec:
        chunk.embedding = vec
    if (i+1) % 50 == 0:
        db.commit()
        print(f"  {i+1}/{len(chunks)} done")
    time.sleep(0.05)  # rate limit
db.commit()
print("✅ Chunks done")

# Re-embed FAQs
faqs = db.query(FAQ).all()
print(f"Re-embedding {len(faqs)} FAQs...")
for i, faq in enumerate(faqs):
    if faq.question:
        faq.question_embedding = engine.embed_text(faq.question, is_query=False)
    if faq.answer:
        faq.answer_embedding = engine.embed_text(faq.answer, is_query=False)
    if (i+1) % 20 == 0:
        db.commit()
        print(f"  {i+1}/{len(faqs)} done")
    time.sleep(0.05)
db.commit()
print("✅ FAQs done")
db.close()
print("\n✅ All embeddings updated to bge-small-en-v1.5")
