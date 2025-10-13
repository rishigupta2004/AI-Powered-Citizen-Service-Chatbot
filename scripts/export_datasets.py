#!/usr/bin/env python3
"""
Unified export script: chunks, faqs, rag corpus.
Usage:
  python scripts/export_datasets.py --format chunks --out data/exports/chunks.jsonl
  python scripts/export_datasets.py --format faqs --out data/exports/faqs.jsonl
  python scripts/export_datasets.py --format rag --out data/exports/rag.json
"""
import sys, json, argparse
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from core.models import ContentChunk, FAQ, Service, Document

def normalize(text: str) -> str:
    return ' '.join((text or '').split())

def export_chunks(db, out_path):
    chunks = db.query(ContentChunk).all()
    with out_path.open('w', encoding='utf-8') as f:
        for ch in chunks:
            text = normalize(ch.content_text)
            if len(text) < 80:
                continue
            service = db.get(Service, ch.service_id) if ch.service_id else None
            record = {
                "instruction": "Summarize the government service content concisely.",
                "input": text[:1000],
                "output": "",
                "meta": {"chunk_id": ch.chunk_id, "service": service.name if service else None, "category": ch.category}
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path}")

def export_faqs(db, out_path):
    faqs = db.query(FAQ).all()
    with out_path.open('w', encoding='utf-8') as f:
        for faq in faqs:
            q = normalize(faq.question)
            a = normalize(faq.answer)
            if len(q) < 5 or len(a) < 5:
                continue
            rec = {
                "prompt": q,
                "completion": a,
                "meta": {"faq_id": faq.faq_id, "service_id": faq.service_id, "lang": faq.language}
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path}")

def export_rag(db, out_path):
    docs = db.query(Document).limit(100).all()
    corpus = []
    for doc in docs:
        service = db.get(Service, doc.service_id) if doc.service_id else None
        corpus.append({
            "doc_id": doc.doc_id,
            "name": doc.name,
            "content": (doc.raw_content or "")[:2000],
            "service": service.name if service else None,
        })
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(corpus, ensure_ascii=False, indent=2))
    print(f"Wrote {out_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--format', choices=['chunks', 'faqs', 'rag'], required=True)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    
    if not args.out:
        args.out = str(project_root / 'data' / 'exports' / f'{args.format}.jsonl' if args.format != 'rag' else f'{args.format}.json')
    
    out_path = Path(args.out)
    db = SessionLocal()
    try:
        if args.format == 'chunks':
            export_chunks(db, out_path)
        elif args.format == 'faqs':
            export_faqs(db, out_path)
        elif args.format == 'rag':
            export_rag(db, out_path)
    finally:
        db.close()

if __name__ == '__main__':
    main()

