"""
Export content chunks to JSONL for instruction-style fine-tuning
Record: {"instruction","input","output","meta"}

Run: python scripts/export_finetune_chunks_jsonl.py --out data/exports/chunks.jsonl
"""
import sys, json, argparse
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from core.models import ContentChunk, Service

def normalize(text: str) -> str:
    return ' '.join((text or '').split())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(project_root / 'data' / 'exports' / 'chunks.jsonl'))
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        chunks = db.query(ContentChunk).all()
        with out_path.open('w', encoding='utf-8') as f:
            for ch in chunks:
                text = normalize(ch.content_text)
                if len(text) < 80:
                    continue
                service = db.query(Service).get(ch.service_id) if ch.service_id else None
                instruction = "Summarize the government service content concisely."
                record = {
                    "instruction": instruction,
                    "input": text[:1000],
                    "output": "",  # placeholder; can be filled with gold summaries later
                    "meta": {"chunk_id": ch.chunk_id, "service": service.name if service else None, "category": ch.category}
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Wrote {out_path}")
    finally:
        db.close()

if __name__ == '__main__':
    main()

