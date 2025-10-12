#!/usr/bin/env python3
"""Export warehouse verification CSVs and print counts."""
import argparse
import csv
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.append(ROOT)
from core.database import SessionLocal
from core.models import Service, Document, FAQ, ContentChunk, RawContent


def write_csv(path, rows, headers):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", default="artifacts")
    args = ap.parse_args()

    db = SessionLocal()
    try:
        services = db.query(Service).all()
        documents = db.query(Document).all()
        faqs = db.query(FAQ).all()
        chunks = db.query(ContentChunk).all()
        raw = db.query(RawContent).all()

        write_csv(f"{args.export_dir}/table_sizes.csv", [
            ("services", len(services)),
            ("documents", len(documents)),
            ("faqs", len(faqs)),
            ("content_chunks", len(chunks)),
            ("raw_content", len(raw)),
        ], ["table", "records"])

        write_csv(f"{args.export_dir}/records_counts.csv", [
            ("services", len(services)),
            ("documents", len(documents)),
            ("faqs", len(faqs)),
            ("content_chunks", len(chunks)),
            ("raw_content", len(raw)),
        ], ["table", "count"])

        # docs by service (best-effort)
        svc_map = {s.service_id: s.name for s in services}
        by_service = {}
        for d in documents:
            by_service.setdefault(svc_map.get(d.service_id, "Unknown"), 0)
            by_service[svc_map.get(d.service_id, "Unknown")] += 1
        write_csv(f"{args.export_dir}/docs_by_service.csv", sorted(by_service.items()), ["service", "documents"])

        # chunks by category
        by_cat = {}
        for c in chunks:
            by_cat.setdefault(c.category or "None", 0)
            by_cat[c.category or "None"] += 1
        write_csv(f"{args.export_dir}/chunks_by_category.csv", sorted(by_cat.items()), ["category", "chunks"])

        # sample faqs
        write_csv(f"{args.export_dir}/faqs_sample.csv", [
            (f.faq_id, f.service_id, (f.question or "")[:120], (f.answer or "")[:120]) for f in faqs[:50]
        ], ["faq_id", "service_id", "question", "answer"])

        print("Exported warehouse verification CSVs to:", args.export_dir)
    finally:
        db.close()


if __name__ == "__main__":
    main()


