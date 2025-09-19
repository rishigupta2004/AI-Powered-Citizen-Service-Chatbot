from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Service(Base):
    __tablename__ = "services"
    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(80))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    procedures = relationship("Procedure", back_populates="service", cascade="all, delete")
    documents = relationship("Document", back_populates="service", cascade="all, delete")
    faqs = relationship("FAQ", back_populates="service", cascade="all, delete")

class Procedure(Base):
    __tablename__ = "procedures"
    procedure_id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"))
    title = Column(Text)
    steps = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    service = relationship("Service", back_populates="procedures")

class Document(Base):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"))
    name = Column(String(150))
    description = Column(Text)
    mandatory = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    service = relationship("Service", back_populates="documents")

class FAQ(Base):
    __tablename__ = "faqs"
    faq_id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"))
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    service = relationship("Service", back_populates="faqs")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    email = Column(String(200), unique=True, index=True)
    role = Column(String(50), default="citizen")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
