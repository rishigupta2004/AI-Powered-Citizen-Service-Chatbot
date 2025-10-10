"""
Seed demo Procedures, FAQs, and Content Chunks for core services.
Safe re-run: skips insert if records already exist.
"""
import sys
from pathlib import Path
from typing import List

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import SessionLocal
from core.models import Service, Procedure, FAQ, ContentChunk
from sqlalchemy import func

def ensure_entities(db, service_id: int, service_key: str):
    # Procedures
    existing_proc = db.query(func.count(Procedure.procedure_id)).filter(Procedure.service_id == service_id).scalar() or 0
    if existing_proc == 0:
        proc_titles = [
            f"{service_key.title()} Application",
            f"{service_key.title()} Renewal",
            f"{service_key.title()} Update"
        ]
        for t in proc_titles:
            db.add(Procedure(
                service_id=service_id,
                title=t,
                description=f"Steps for {t.lower()}",
                procedure_type="standard",
                steps={"steps": ["Fill form", "Upload documents", "Submit"]},
                estimated_time="15 min",
                processing_time="3-5 days",
                language="en",
            ))
    
    # FAQs
    existing_faq = db.query(func.count(FAQ.faq_id)).filter(FAQ.service_id == service_id).scalar() or 0
    if existing_faq == 0:
        faqs = [
            (f"How to apply for {service_key}?", f"Use the {service_key} portal and submit required documents."),
            (f"How long does {service_key} take?", "Typically 3-5 business days."),
            (f"Can I update my {service_key}?", f"Yes, use the {service_key} update service.")
        ]
        for q, a in faqs:
            db.add(FAQ(
                service_id=service_id,
                question=q,
                answer=a,
                short_answer=a[:120],
                category=service_key,
                language="en",
            ))
    
    # Content Chunks
    # Use safe count on primary key to avoid selecting optional columns
    existing_chunks = db.query(func.count(ContentChunk.chunk_id)).filter(ContentChunk.service_id == service_id).scalar() or 0
    if existing_chunks == 0:
        chunks: List[str] = [
            f"{service_key.title()} overview and requirements.",
            f"{service_key.title()} step-by-step process.",
            f"{service_key.title()} fees and timelines."
        ]
        for text in chunks:
            # Insert with only existing columns to avoid mismatched schema issues
            db.execute(ContentChunk.__table__.insert().values(
                content_text=text,
                service_id=service_id,
            ))

def main():
    db = SessionLocal()
    try:
        # Expect at least these services to exist
        services = db.query(Service).all()
        by_name = {s.name.lower(): s for s in services}
        pairs = [
            (by_name.get("passport services"), "passport"),
            (by_name.get("aadhaar services"), "aadhaar"),
            (by_name.get("pan card services"), "pan"),
        ]
        for svc, key in pairs:
            if svc:
                ensure_entities(db, svc.service_id, key)
        db.commit()
        print("✅ Seeded Procedures, FAQs, and Content Chunks (where missing)")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()