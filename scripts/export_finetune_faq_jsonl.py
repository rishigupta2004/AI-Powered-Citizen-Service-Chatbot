"""
Export FAQs to JSONL for fine-tuning: {"prompt","completion"}

Run: python scripts/export_finetune_faq_jsonl.py --out data/exports/faqs.jsonl
"""
import sys, json, argparse
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from core.models import FAQ

def normalize(text: str) -> str:
    return ' '.join((text or '').split())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(project_root / 'data' / 'exports' / 'faqs.jsonl'))
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
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
    finally:
        db.close()

if __name__ == '__main__':
    main()

