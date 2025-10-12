#!/usr/bin/env python3
"""
Process pending raw_content entries: extract normalized text, persist documents/chunks,
and mark as completed or log per-item failure reasons.
"""
import argparse
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.append(ROOT)
from sqlalchemy.orm import Session
import csv
from core.database import SessionLocal
from core.models import RawContent, Document, ContentChunk, Service
from core.nlp import NLPToolkit
from data.processing.document_parser import DocumentParser


def chunk_text(text: str, max_len: int = 800) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_len])
        start += max_len
    return chunks


CATEGORY_TO_SERVICE = {
    "passport": "Passport Services",
    "aadhaar": "Aadhaar Services",
    "pan": "PAN Card Services",
    "epfo": "EPFO Services",
    "parivahan": "Driving License Services",
    "driving": "Driving License Services",
    "railways": "Railway Services",
    "education": "Education Services",
    "rbi": "RBI Services",
}

def resolve_service_id(db: Session, category: str | None, title: str | None) -> int:
    """Map category/name to an existing Service, or create a General fallback."""
    target = None
    if category:
        key = category.lower()
        target = CATEGORY_TO_SERVICE.get(key, None)
    # Try by category exact match first
    svc = None
    if category:
        svc = db.query(Service).filter(Service.category.ilike(f"%{category}%")).first()
    # Try by mapped service name
    if not svc and target:
        svc = db.query(Service).filter(Service.name.ilike(f"%{target}%")).first()
    # Try by title keywords
    name_lc = (title or "").lower()
    if not svc:
        for key, svcname in CATEGORY_TO_SERVICE.items():
            if key in name_lc or svcname.split()[0].lower() in name_lc:
                svc = db.query(Service).filter(Service.name.ilike(f"%{svcname}%")).first()
                if svc:
                    break
    if svc:
        return svc.service_id
    # Fallback: create General service once
    general = db.query(Service).filter(Service.name == "General").first()
    if not general:
        general = Service(name="General", category="general", description="Catch-all for unclassified content", ministry=None, is_active=True)
        db.add(general)
        db.commit()
        db.refresh(general)
    return general.service_id


def process_pending(db: Session, resume: bool = True, failures_csv: str = "artifacts/processing_failures.csv") -> dict:
    nlp = NLPToolkit()
    parser = DocumentParser()
    q = db.query(RawContent).filter(RawContent.is_processed == False)
    pending = q.all()
    summary = {"pending": len(pending), "processed": 0, "errors": 0}

    # open failure log
    os.makedirs(os.path.dirname(failures_csv), exist_ok=True)
    failures_f = open(failures_csv, "w", newline="")
    failures_w = csv.writer(failures_f)
    failures_w.writerow(["content_id", "source_type", "source_url", "status", "error"])

    for rc in pending:
        try:
            # Normalize text; if HTML/JSON etc., use parser.normalize
            normalized = rc.content
            if rc.content_type in ("html", "json") or (not normalized):
                normalized = parser.normalize(rc.content or "")

            # Derive simple tags
            lang = nlp.language_detection(normalized or "")
            ents = nlp.entity_extraction(normalized or "")
            category = ents[0] if ents else None

            # Resolve service id
            svc_id = resolve_service_id(db, category, rc.title or rc.source_name)

            # Create document record
            doc = Document(
                service_id=svc_id,
                name=rc.title or rc.source_name or (rc.source_url or "raw-content"),
                description=rc.source_url or rc.source_name,
                document_type=rc.content_type,
                is_mandatory=False,
                language=lang,
                is_processed=True,
                raw_content=normalized,
            )
            db.add(doc)
            db.flush()

            # Create content chunks
            for ch in chunk_text(normalized):
                db.add(ContentChunk(
                    service_id=None,
                    content_text=ch,
                    category=category,
                ))

            # Mark RC as processed
            rc.is_processed = True
            rc.processing_status = "completed"
            db.commit()
            summary["processed"] += 1
        except Exception as e:
            db.rollback()
            rc.processing_status = "error"
            rc.processing_errors = str(e)
            db.commit()
            summary["errors"] += 1
            failures_w.writerow([
                rc.content_id,
                rc.source_type,
                rc.source_url or "",
                rc.processing_status,
                str(e)
            ])

    failures_f.close()

    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", type=int, default=1)
    args = ap.parse_args()
    db = SessionLocal()
    try:
        s = process_pending(db, resume=bool(args.resume))
        print("Processed pending raw_content:", s)
    finally:
        db.close()


if __name__ == "__main__":
    main()


