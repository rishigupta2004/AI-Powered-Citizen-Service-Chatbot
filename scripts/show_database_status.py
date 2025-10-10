"""
Show Database Status: counts and samples for core entities
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import SessionLocal
from core.models import Service, Procedure, Document, FAQ, ContentChunk
from sqlalchemy import func

def count_and_samples(db, model, label: str, sample_query, to_dict_fn):
    # Safe count using primary key to avoid selecting non-existent columns
    pk = list(model.__table__.primary_key.columns)[0]
    count = db.query(func.count(pk)).scalar() or 0
    print(f"{label}: {count} records")
    items = sample_query.limit(3).all()
    for i, item in enumerate(items, 1):
        fields = to_dict_fn(item)
        print(f"  {label} sample {i}: {fields}")

def main():
    print("📚 Database Status Overview")
    db = SessionLocal()
    try:
        count_and_samples(
            db,
            Service,
            "Services",
            db.query(Service.service_id, Service.name, Service.category, Service.is_active),
            lambda r: {"service_id": r[0], "name": r[1], "category": r[2], "is_active": r[3]},
        )
        count_and_samples(
            db,
            Procedure,
            "Procedures",
            db.query(Procedure.procedure_id, Procedure.service_id, Procedure.title, Procedure.language),
            lambda r: {"procedure_id": r[0], "service_id": r[1], "title": r[2], "language": r[3]},
        )
        count_and_samples(
            db,
            Document,
            "Documents",
            db.query(Document.doc_id, Document.service_id, Document.name, Document.language, Document.is_mandatory),
            lambda r: {"doc_id": r[0], "service_id": r[1], "name": r[2], "language": r[3], "is_mandatory": r[4]},
        )
        count_and_samples(
            db,
            FAQ,
            "FAQs",
            db.query(FAQ.faq_id, FAQ.service_id, FAQ.category, FAQ.language),
            lambda r: {"faq_id": r[0], "service_id": r[1], "category": r[2], "language": r[3]},
        )
        # ContentChunk may not have 'category' in some deployments; sample only safe columns
        count_and_samples(
            db,
            ContentChunk,
            "Content Chunks",
            db.query(ContentChunk.chunk_id, ContentChunk.service_id),
            lambda r: {"chunk_id": r[0], "service_id": r[1]},
        )
    finally:
        db.close()

if __name__ == "__main__":
    main()