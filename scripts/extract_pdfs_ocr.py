#!/usr/bin/env python3
"""
Extract text from all PDFs under data/docs using parser + OCR fallback.
Write artifacts/extract.log and artifacts/pdf_failures.csv with per-file/page issues.
Optionally upsert normalized text into RawContent for downstream processing.
"""
import os
import sys
import csv
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.append(ROOT)

from core.database import SessionLocal
from core.models import RawContent
from data.processing.document_parser import DocumentParser
from data.ingestion.scrapers.base_scraper import canonicalize_url

ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def upsert_pdf_text(db, pdf_path: Path, chunks: list[str]):
    # Use file path as source_url with file:// scheme for traceability
    url = f"file://{pdf_path.resolve()}"
    canon = canonicalize_url(url)
    text = "\n\n".join(chunks or [])
    existing = db.query(RawContent).filter(RawContent.source_url == canon).first()
    if existing:
        existing.content = text
        existing.content_type = "text"
        existing.source_name = pdf_path.name
        existing.is_processed = False
        existing.processing_status = "pending"
        db.commit()
        return existing.content_id
    rc = RawContent(
        source_type="pdf",
        source_url=canon,
        source_name=pdf_path.name,
        title=pdf_path.stem,
        content=text,
        content_type="text",
        is_processed=False,
        processing_status="pending",
        file_path=str(pdf_path),
    )
    db.add(rc)
    db.commit()
    db.refresh(rc)
    return rc.content_id


def main():
    db = SessionLocal()
    parser = DocumentParser()
    failures = open(ARTIFACTS / "pdf_failures.csv", "w", newline="")
    w = csv.writer(failures)
    w.writerow(["file", "page", "error"])
    try:
        base = Path("data/docs")
        pdfs = sorted(base.rglob("*.pdf"))
        for pdf in pdfs:
            try:
                chunks = parser.parse_pdf(str(pdf))
                upsert_pdf_text(db, pdf, chunks)
            except Exception as e:
                # Unknown page; log file-level error
                w.writerow([str(pdf), "*", str(e)])
                continue
        print(f"Processed {len(pdfs)} PDFs; failures logged to artifacts/pdf_failures.csv")
    finally:
        failures.close()
        db.close()


if __name__ == "__main__":
    main()


