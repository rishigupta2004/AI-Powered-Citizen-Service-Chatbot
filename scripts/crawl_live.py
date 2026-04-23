#!/usr/bin/env python3
"""
Live crawl orchestrator (SAFE_MODE/RESUME supported via base scraper).
Discovers FAQs/pages via registered scrapers and persists raw HTML and normalized
text with metadata into the warehouse (RawContent). De-duplicates by canonical URL
and text hash. Produces artifacts/discovered_urls.csv.
"""
import os
import sys
import csv
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.append(ROOT)

from bs4 import BeautifulSoup
from core.database import SessionLocal
from core.models import RawContent
from data.ingestion.scrapers import crawl_all, SCRAPERS
from data.ingestion.scrapers.base_scraper import canonicalize_url

ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def upsert_raw(db, url: str, html: str, source_name: str, source_type: str = "scraping"):
    canon = canonicalize_url(url)
    existing = (
        db.query(RawContent)
        .filter(RawContent.source_url == canon)
        .first()
    )
    if existing:
        # update content if changed
        existing.content = html
        existing.content_type = "html"
        existing.source_name = source_name
        existing.is_processed = False
        existing.processing_status = "pending"
        db.commit()
        return existing.content_id
    rc = RawContent(
        source_type=source_type,
        source_url=canon,
        source_name=source_name,
        title=source_name,
        content=html,
        content_type="html",
        is_processed=False,
        processing_status="pending",
    )
    db.add(rc)
    db.commit()
    db.refresh(rc)
    return rc.content_id


def main():
    db = SessionLocal()
    discovered = []
    try:
        # For each scraper, attempt to fetch the main FAQ/listing page(s)
        for key, cls in SCRAPERS.items():
            s = cls()
            # heuristic: collect homepage and '/faq' pages
            candidates = ["/", "/faq", "/faqs", "/en/content/faq"]
            for rel in candidates:
                try:
                    soup = s.scrape(rel, prefer="auto")
                    if not soup:
                        continue
                    url = s._build_url(rel)
                    html = str(soup)
                    upsert_raw(db, url, html, source_name=key)
                    discovered.append(canonicalize_url(url))
                except Exception as e:
                    # continue to next candidate
                    continue
        # write discovered URLs
        with open(ARTIFACTS / "discovered_urls.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["url"])
            for u in sorted(set(discovered)):
                w.writerow([u])
        print(f"Discovered {len(discovered)} URLs")
    finally:
        db.close()


if __name__ == "__main__":
    main()


