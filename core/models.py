"""
Streamlined Database Models - Essential entities only
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func, DECIMAL, ARRAY, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from .database import Base

class Service(Base):
    __tablename__ = "services"
    
    service_id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    ministry = Column(String(150))
    is_active = Column(Boolean, default=True)
    languages_supported = Column(PG_ARRAY(String(10)), default=['en', 'hi'])
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    procedures = relationship("Procedure", back_populates="service", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="service", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="service", cascade="all, delete-orphan")

class Procedure(Base):
    __tablename__ = "procedures"
    
    procedure_id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    procedure_type = Column(String(50))
    steps = Column(JSONB)
    estimated_time = Column(String(50))
    is_free = Column(Boolean, default=False)
    processing_time = Column(String(100))
    language = Column(String(10), default='en')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    service = relationship("Service", back_populates="procedures")

class Document(Base):
    __tablename__ = "documents"
    
    doc_id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    procedure_id = Column(Integer, ForeignKey("procedures.procedure_id", ondelete="CASCADE"))
    name = Column(String(300), nullable=False)
    description = Column(Text)
    document_type = Column(String(50))
    is_mandatory = Column(Boolean, default=True)
    copies_required = Column(Integer, default=1)
    validity_period = Column(String(100))
    language = Column(String(10), default='en')
    is_processed = Column(Boolean, default=False)
    raw_content = Column(Text)
    embedding = Column(Vector(384))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    service = relationship("Service", back_populates="documents")

class FAQ(Base):
    __tablename__ = "faqs"
    
    faq_id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    short_answer = Column(Text)
    category = Column(String(100))
    language = Column(String(10), default='en')
    question_embedding = Column(Vector(384))
    answer_embedding = Column(Vector(384))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    service = relationship("Service", back_populates="faqs")

class ContentChunk(Base):
    __tablename__ = "content_chunks"
    
    chunk_id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    content_text = Column(Text, nullable=False)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"))
    category = Column(String(100))
    embedding = Column(Vector(384))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# Helpful indexes for common queries and filters
Index('idx_services_name', Service.name)
Index('idx_procedures_title', Procedure.title)
Index('idx_documents_name', Document.name)
Index('idx_documents_language', Document.language)
Index('idx_faq_language', FAQ.language)
Index('idx_chunks_category', ContentChunk.category)

# Full-text search index for documents (GIN over tsvector)
try:
    from sqlalchemy import text
    Index(
        'idx_documents_tsv',
        text("to_tsvector('english', coalesce(name,'') || ' ' || coalesce(description,'') || ' ' || coalesce(raw_content,''))"),
        postgresql_using='gin'
    )
except Exception:
    # Skip if dialect does not support this at model import time
    pass

# --- Phase 4: Raw scraped content storage (Data Warehouse alignment) ---
class RawContent(Base):
    __tablename__ = "raw_content"

    content_id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)

    # Source information
    source_type = Column(String(50), nullable=False)  # api, scraping, pdf, ocr
    source_url = Column(String(500))
    source_name = Column(String(200))

    # Content
    title = Column(String(500))
    content = Column(Text, nullable=False)
    content_type = Column(String(50))  # html, pdf, text, json
    language = Column(String(10), default='en')

    # Processing & metadata
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default='pending')
    processing_errors = Column(Text)
    metadata_json = Column('metadata', JSONB)
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)

    # System
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

Index('idx_raw_content_source_type', RawContent.source_type)
