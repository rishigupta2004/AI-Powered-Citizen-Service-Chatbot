"""
Export RAG corpus from documents and content_chunks for retrieval training.
Writes compact JSON and manifest.

Run: python scripts/export_rag_corpus.py --out data/exports/rag_corpus.json
"""
import sys, json, argparse
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from core.models import Document, ContentChunk, Service

def normalize(text: str) -> str:
    return ' '.join((text or '').split())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(project_root / 'data' / 'exports' / 'rag_corpus.json'))
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        services = {s.service_id: s for s in db.query(Service).all()}
        docs = db.query(Document).all()
        chunks = db.query(ContentChunk).all()
        corpus = {
            "documents": [
                {
                    "doc_id": d.doc_id,
                    "service": services.get(d.service_id).name if d.service_id in services else None,
                    "name": d.name,
                    "content": (normalize(d.raw_content)[:4000] if d.raw_content else None),
                    "type": d.document_type,
                }
                for d in docs
            ],
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "service": services.get(c.service_id).name if c.service_id in services else None,
                    "category": c.category,
                    "text": normalize(c.content_text)[:1200],
                }
                for c in chunks if (c.content_text and len(c.content_text) > 60)
            ],
        }
        with out_path.open('w', encoding='utf-8') as f:
            json.dump(corpus, f, ensure_ascii=False)
        print(f"Wrote {out_path}")
    finally:
        db.close()

if __name__ == '__main__':
    main()

