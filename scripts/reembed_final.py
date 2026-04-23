"""Re-embed all chunks+FAQs using raw SQL — no SQLAlchemy ORM hang."""

import os, sys, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extras import execute_values
from core.embeddings import get_embedding_engine
from core.config import EMBEDDING_DIM

DB_URL = os.environ["DATABASE_URL"].replace("postgresql+psycopg2://", "postgresql://")
conn = psycopg2.connect(DB_URL)
conn.autocommit = False
cur = conn.cursor()

eng = get_embedding_engine()

# -- Preflight: verify embedding model output matches declared dimension -------
_test_vec = eng.embed_text("preflight check", is_query=False)
if _test_vec is not None and len(_test_vec) != EMBEDDING_DIM:
    raise RuntimeError(
        f"Embedding dimension mismatch: model outputs {len(_test_vec)} dims "
        f"but EMBEDDING_DIM={EMBEDDING_DIM}. "
        f"Set EMBEDDING_DIM={len(_test_vec)} in .env and re-run init_db.py "
        f"to ALTER the vector column before re-embedding."
    )
print(f"✅ Embedding preflight OK - {EMBEDDING_DIM} dims")

# ── Chunks ────────────────────────────────────────────────────────────────────
cur.execute(
    "SELECT chunk_id, chunk_text FROM content_chunks WHERE chunk_text IS NOT NULL"
)
chunks = cur.fetchall()
print(f"Re-embedding {len(chunks)} chunks...")

for i, (cid, text) in enumerate(chunks):
    vec = eng.embed_text(text[:512], is_query=False)
    if vec:
        cur.execute(
            "UPDATE content_chunks SET embedding = %s::vector WHERE chunk_id = %s",
            (str(vec), cid),
        )
    if (i + 1) % 50 == 0:
        conn.commit()
        print(f"  {i + 1}/{len(chunks)} ✓")
    time.sleep(0.05)

conn.commit()
print("✅ Chunks done")

# ── FAQs ──────────────────────────────────────────────────────────────────────
cur.execute("SELECT faq_id, question, answer FROM faqs")
faqs = cur.fetchall()
print(f"Re-embedding {len(faqs)} FAQs...")

for i, (fid, q, a) in enumerate(faqs):
    if q:
        qvec = eng.embed_text(q[:512], is_query=False)
        if qvec:
            cur.execute(
                "UPDATE faqs SET question_embedding = %s::vector WHERE faq_id = %s",
                (str(qvec), fid),
            )
    if a:
        avec = eng.embed_text(a[:512], is_query=False)
        if avec:
            cur.execute(
                "UPDATE faqs SET answer_embedding = %s::vector WHERE faq_id = %s",
                (str(avec), fid),
            )
    if (i + 1) % 20 == 0:
        conn.commit()
        print(f"  {i + 1}/{len(faqs)} ✓")
    time.sleep(0.05)

conn.commit()
conn.close()
print("\n✅ ALL DONE — multilingual-e5-large-instruct 1024-dim vectors stored")
