from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False)   # e.g., "passport pdf", "uidai doc"
    file_name = Column(String(255))
    language = Column(String(50))
    doc_type = Column(String(50))                  # e.g., "pdf", "word", "image"
    created_at = Column(DateTime, server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    section = Column(String(255))
    content = Column(Text, nullable=False)
    language = Column(String(50))

    document = relationship("Document", back_populates="chunks")
