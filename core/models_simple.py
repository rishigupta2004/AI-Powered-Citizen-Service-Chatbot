"""
Simplified Database Models - Without vector support for basic testing
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class Service(Base):
    __tablename__ = "services"
    
    service_id = Column(Integer, primary_key=True)
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
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    service = relationship("Service", back_populates="documents")

class FAQ(Base):
    __tablename__ = "faqs"
    
    faq_id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    short_answer = Column(Text)
    category = Column(String(100))
    language = Column(String(10), default='en')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    service = relationship("Service", back_populates="faqs")

class ContentChunk(Base):
    __tablename__ = "content_chunks"
    
    chunk_id = Column(Integer, primary_key=True)
    content_text = Column(Text, nullable=False)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
