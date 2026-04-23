#!/usr/bin/env python3
"""Enrich existing services with official PDFs, chunks, and FAQs.

Usage:
  python scripts/enrich_existing_services.py --ingest-pdfs --embed
  python scripts/enrich_existing_services.py --ingest-pdfs --scrape-faqs --embed
"""

from __future__ import annotations

import argparse
from pathlib import Path

from core.database import SessionLocal
from core.models import Service, Document, ContentChunk, FAQ
from core.embeddings import get_embedding_engine
from data.processing.document_parser import DocumentParser
from scripts.seed_national_services import SEEDS, LAST_VERIFIED
from data.ingestion.scrapers import get_all_scrapers


ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = ROOT / "data" / "docs" / "services"


def _split_chunks(text: str, chunk_size: int = 900) -> list[str]:
    words = (text or "").split()
    chunks: list[str] = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size]).strip()
        if len(chunk) >= 120:
            chunks.append(chunk)
    return chunks


def _faq_templates(
    name: str, authority: str, url: str, mode: str
) -> list[tuple[str, str]]:
    return [
        (
            f"Where should I access {name} officially?",
            f"Use the official portal managed by {authority}: {url}. Avoid unofficial links and payment pages.",
        ),
        (
            f"Can I complete {name} fully online?",
            f"Current mode is {mode}. Check the official portal for latest online/offline steps and appointment requirements.",
        ),
        (
            f"How do I verify latest documents and fees for {name}?",
            f"Check the latest notice/forms/fee section on {url}. Last verified in corpus build: {LAST_VERIFIED}.",
        ),
    ]


def run(ingest_pdfs: bool, scrape_faqs: bool, embed: bool) -> None:
    db = SessionLocal()
    parser = DocumentParser()
    emb = get_embedding_engine() if embed else None

    stats = {
        "services_seen": 0,
        "pdf_documents_added": 0,
        "pdf_chunks_added": 0,
        "template_faqs_added": 0,
        "scraped_faqs_added": 0,
    }

    try:
        scraper_map = get_all_scrapers() if scrape_faqs else {}

        for seed in SEEDS:
            service = db.query(Service).filter(Service.name == seed.name).first()
            if not service:
                continue
            stats["services_seen"] += 1

            for question, answer in _faq_templates(
                seed.name, seed.authority, seed.url, seed.mode
            ):
                existing = (
                    db.query(FAQ)
                    .filter(
                        FAQ.service_id == service.service_id, FAQ.question == question
                    )
                    .first()
                )
                if existing:
                    continue
                faq = FAQ(
                    service_id=service.service_id,
                    question=question,
                    answer=answer,
                    short_answer=answer[:220],
                    category=(seed.category or "general")[:100],
                    language="en",
                )
                if emb:
                    faq.question_embedding = emb.embed_text(question, is_query=True)
                    faq.answer_embedding = emb.embed_text(answer, is_query=False)
                db.add(faq)
                stats["template_faqs_added"] += 1

            if ingest_pdfs:
                service_folder = DOCS_ROOT / seed.slug
                if service_folder.exists() and service_folder.is_dir():
                    for pdf in sorted(service_folder.glob("*.pdf")):
                        try:
                            text_parts = parser.parse_pdf(str(pdf))
                        except Exception:
                            continue
                        full_text = "\n\n".join(text_parts).strip()
                        if not full_text:
                            continue

                        doc_name = f"{seed.name} PDF: {pdf.stem.replace('_', ' ').replace('-', ' ').strip()}"
                        existing_doc = (
                            db.query(Document)
                            .filter(
                                Document.service_id == service.service_id,
                                Document.name == doc_name,
                            )
                            .first()
                        )
                        if not existing_doc:
                            existing_doc = Document(
                                service_id=service.service_id,
                                name=doc_name,
                                description=f"Official PDF source: {pdf.name}",
                                document_type="official_pdf",
                                is_mandatory=False,
                                language="en",
                                is_processed=True,
                            )
                            db.add(existing_doc)
                            stats["pdf_documents_added"] += 1

                        existing_doc.raw_content = full_text[:40000]
                        if emb:
                            existing_doc.embedding = emb.embed_text(
                                full_text[:1800], is_query=False
                            )

                        chunks = _split_chunks(full_text)
                        for idx, chunk_text in enumerate(chunks[:20]):
                            chunk_exists = (
                                db.query(ContentChunk)
                                .filter(
                                    ContentChunk.service_id == service.service_id,
                                    ContentChunk.chunk_type == "official_pdf",
                                    ContentChunk.chunk_index == idx,
                                    ContentChunk.chunk_text == chunk_text,
                                )
                                .first()
                            )
                            if chunk_exists:
                                continue
                            chunk = ContentChunk(
                                service_id=service.service_id,
                                chunk_text=chunk_text,
                                chunk_index=idx,
                                chunk_type="official_pdf",
                                chunk_metadata={
                                    "pdf_file": pdf.name,
                                    "service_slug": seed.slug,
                                    "official_url": seed.url,
                                    "verified_at": LAST_VERIFIED,
                                },
                            )
                            if emb:
                                chunk.embedding = emb.embed_text(
                                    chunk_text[:1200], is_query=False
                                )
                            db.add(chunk)
                            stats["pdf_chunks_added"] += 1

            if scrape_faqs:
                scraper = scraper_map.get(seed.slug.split("_", 1)[0])
                if scraper is None:
                    continue
                try:
                    scraper_instance = scraper()
                    faq_items = scraper_instance.get_faqs(headless=True)
                    for item in faq_items[:120]:
                        q = (item.get("question") or "").strip()
                        a = (item.get("answer") or "").strip()
                        if not q or not a:
                            continue
                        exists = (
                            db.query(FAQ)
                            .filter(
                                FAQ.service_id == service.service_id, FAQ.question == q
                            )
                            .first()
                        )
                        if exists:
                            continue
                        faq = FAQ(
                            service_id=service.service_id,
                            question=q,
                            answer=a,
                            short_answer=a[:220],
                            category=(seed.category or "general")[:100],
                            language="en",
                        )
                        if emb:
                            faq.question_embedding = emb.embed_text(q, is_query=True)
                            faq.answer_embedding = emb.embed_text(a, is_query=False)
                        db.add(faq)
                        stats["scraped_faqs_added"] += 1
                except Exception:
                    pass

        db.commit()
        print("Enrichment complete")
        for k, v in stats.items():
            print(f"{k}: {v}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich existing services corpus")
    parser.add_argument(
        "--ingest-pdfs", action="store_true", help="Ingest official PDFs"
    )
    parser.add_argument(
        "--scrape-faqs", action="store_true", help="Fetch FAQs from registered scrapers"
    )
    parser.add_argument(
        "--embed", action="store_true", help="Generate embeddings for new corpus"
    )
    args = parser.parse_args()

    run(ingest_pdfs=args.ingest_pdfs, scrape_faqs=args.scrape_faqs, embed=args.embed)


if __name__ == "__main__":
    main()
