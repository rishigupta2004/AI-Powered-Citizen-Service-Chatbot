"""
Ad-hoc test runner for Week 7 Quality & Validation

Runs:
- Validation (documents/chunks)
- Deduplication detection
- Multilingual verification
- Metrics summary
- Lineage logging sample

Optionally, verifies scraper import availability.
"""
import json
from datetime import datetime

from core.database import SessionLocal
from core.quality import (
    DataValidator,
    Deduplicator,
    MultilingualVerifier,
    QualityMonitor,
    LineageTracker,
    run_all_quality_checks,
)


def main():
    print("=== Week 7 Quality & Validation Test ===")
    db = SessionLocal()
    try:
        summary = run_all_quality_checks(db)
        print("-- Metrics --")
        print(json.dumps(summary["metrics"], indent=2))

        print("-- Validation Issues (first 10) --")
        doc_issues = summary["validation"]["documents"][:10]
        chunk_issues = summary["validation"]["chunks"][:10]
        print(json.dumps({"documents": doc_issues, "chunks": chunk_issues}, indent=2))

        print("-- Duplicates (first 10) --")
        dup_docs = summary["duplicates"]["documents"][:10]
        dup_chunks = summary["duplicates"]["chunks"][:10]
        print(json.dumps({"documents": dup_docs, "chunks": dup_chunks}, indent=2))

        print("-- Multilingual Issues (first 10) --")
        ml_issues = summary["multilingual"][:10]
        print(json.dumps(ml_issues, indent=2))

        # Lineage logging sample (if any document exists)
        tracker = LineageTracker()
        tracker.log({
            "event": "quality_test_run",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": summary["metrics"],
        })
        print("Lineage log written.")

        # Optional: scraper import availability
        try:
            import data.ingestion.scrapers.passport_scraper as ps
            print("Scraper import: OK -", ps.__name__)
        except Exception as e:
            print("Scraper import: FAIL -", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    main()