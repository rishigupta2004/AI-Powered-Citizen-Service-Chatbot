"""
Phase 4 ingestion scaffold:
- Store API endpoint definitions from CSV into warehouse (RawContent), leaving links empty
- Scrape Passport FAQs and store into FAQs table
- Process PDFs in data/docs/passport using DocumentProcessor and store Documents/ContentChunks
"""
import os
import csv
from typing import Dict, List

from core.database import SessionLocal
from core.repositories import ServiceRepository, FAQRepository, RawContentRepository
from core.processor import DocumentProcessor
from data.ingestion.scrapers.passport_scraper import PassportScraper

ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(ROOT, "Service-APIService-Endpoint.csv")


def get_or_create_service(db, name: str, category: str) -> int:
    repo = ServiceRepository(db)
    # naive lookup by name
    svc = db.query(repo.model_class).filter(repo.model_class.name == name).first()
    if svc:
        return svc.service_id
    svc = repo.create(name=name, category=category, description=f"Auto-created for {name}")
    return svc.service_id


def store_api_endpoints_from_csv(db) -> int:
    """Insert API endpoints as RawContent records with empty links."""
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found at {CSV_PATH}")
        return 0
    repo = RawContentRepository(db)
    count = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        current_service = None
        for row in reader:
            service = row.get("Service") or current_service or "Unknown"
            current_service = service if row.get("Service") else current_service
            api_service = row.get("API Service") or ""
            endpoint = row.get("Endpoint") or ""
            # Insert with empty source_url per requirement
            repo.create(
                source_type="api",
                source_url="",
                source_name=service,
                title=api_service or endpoint,
                content=f"{api_service}:{endpoint}",
                content_type="json",
                language="en",
                metadata_json={"service": service, "api_service": api_service, "endpoint": endpoint}
            )
            count += 1
    print(f"Stored {count} API endpoint definitions as RawContent")
    return count


def ingest_passport_faqs(db) -> int:
    faq_repo = FAQRepository(db)
    service_id = get_or_create_service(db, "Passport Application/Renewal (MEA)", "passport")
    scraper = PassportScraper()
    faqs = scraper.get_faqs(headless=True)
    inserted = 0
    for f in faqs:
        try:
            faq_repo.create(service_id=service_id, question=f["question"], answer=f["answer"], category="general")
            inserted += 1
        except Exception:
            continue
    print(f"Inserted {inserted} Passport FAQs")
    return inserted


def ingest_passport_pdfs(db) -> int:
    service_id = get_or_create_service(db, "Passport Application/Renewal (MEA)", "passport")
    docs_dir = os.path.join(ROOT, "data", "docs", "passport")
    if not os.path.isdir(docs_dir):
        print(f"No passport docs directory at {docs_dir}")
        return 0
    dp = DocumentProcessor(db)
    inserted = 0
    for fname in os.listdir(docs_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(docs_dir, fname)
        res = dp.process_document(path, service_id)
        if res.get("status") == "success":
            inserted += 1
    print(f"Processed {inserted} passport PDFs")
    return inserted


def main():
    db = SessionLocal()
    try:
        store_api_endpoints_from_csv(db)
        ingest_passport_faqs(db)
        ingest_passport_pdfs(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()