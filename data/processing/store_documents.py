import os
try:
    # Prefer core models/session to avoid missing data.db in this streamlined repo
    from core.models import Document, ContentChunk as DocumentChunk
    from core.database import SessionLocal
except Exception:
    # Fallback to legacy data.db for external environments
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from data.db.models import Base, Document, DocumentChunk
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://username:password@localhost/citizen_services_dev")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

from data.processing.document_parser import DocumentParser
from data.processing.classifier import classify_document

class DocumentPipeline:
    def __init__(self):
        self.parser = DocumentParser()

    def ingest(self, file_path: str, source: str):
        session = SessionLocal()
        ext = file_path.split(".")[-1].lower()

        # Parse based on file type
        if ext == "pdf":
            chunks = self.parser.parse_pdf(file_path)
            doc_type = "pdf"
        elif ext in ["doc", "docx"]:
            chunks = self.parser.parse_word(file_path)
            doc_type = "word"
        elif ext in ["png", "jpg", "jpeg"]:
            chunks = self.parser.parse_image(file_path)
            doc_type = "image"
        else:
            raise ValueError("Unsupported file type")

        # Create document record
        document = Document(
            source=source,
            file_name=file_path,
            doc_type=doc_type,
            language=self.parser.detect_language(" ".join(chunks[:2])) if chunks else "unknown"
        )
        session.add(document)
        session.flush()

        # Add chunks
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            lang = self.parser.detect_language(chunk)
            section = classify_document(chunk)
            session.add(DocumentChunk(
                document_id=document.id,
                section=section,
                content=chunk,
                language=lang
            ))

        session.commit()
        session.close()
        print(f"✅ Ingested {len(chunks)} chunks from {file_path}")


class DocumentStore:
    """Lightweight wrapper used by tests to validate storage imports."""
    def __init__(self, db):
        self.db = db
