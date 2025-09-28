"""
Streamlined Repository Pattern - Essential operations only
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from pgvector.sqlalchemy import Vector
from .models import Service, Procedure, Document, FAQ, ContentChunk

class BaseRepository:
    def __init__(self, db: Session, model_class):
        self.db = db
        self.model_class = model_class
    
    def create(self, **kwargs):
        obj = self.model_class(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def get_by_id(self, id: int):
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def count(self):
        return self.db.query(self.model_class).count()

class ServiceRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Service)
    
    def get_by_category(self, category: str) -> List[Service]:
        return self.db.query(Service).filter(Service.category == category).all()
    
    def get_active_services(self) -> List[Service]:
        return self.db.query(Service).filter(Service.is_active == True).all()
    
    def search_services(self, query: str) -> List[Service]:
        search_term = f"%{query}%"
        return self.db.query(Service).filter(
            and_(
                Service.is_active == True,
                or_(
                    Service.name.ilike(search_term),
                    Service.description.ilike(search_term)
                )
            )
        ).all()

class DocumentRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Document)
    
    def get_by_service(self, service_id: int) -> List[Document]:
        return self.db.query(Document).filter(Document.service_id == service_id).all()
    
    def get_mandatory_documents(self, service_id: int) -> List[Document]:
        return self.db.query(Document).filter(
            and_(
                Document.service_id == service_id,
                Document.is_mandatory == True
            )
        ).all()
    
    def search_semantic(self, query_embedding: List[float], limit: int = 10) -> List[Document]:
        return self.db.query(Document).filter(
            Document.embedding.isnot(None)
        ).order_by(
            Document.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()

class FAQRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, FAQ)
    
    def get_by_service(self, service_id: int) -> List[FAQ]:
        return self.db.query(FAQ).filter(FAQ.service_id == service_id).all()
    
    def search_semantic(self, query_embedding: List[float], limit: int = 10) -> List[FAQ]:
        return self.db.query(FAQ).filter(
            FAQ.question_embedding.isnot(None)
        ).order_by(
            FAQ.question_embedding.cosine_distance(query_embedding)
        ).limit(limit).all()

class ContentChunkRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, ContentChunk)
    
    def search_semantic(self, query_embedding: List[float], limit: int = 10) -> List[ContentChunk]:
        return self.db.query(ContentChunk).filter(
            ContentChunk.embedding.isnot(None)
        ).order_by(
            ContentChunk.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
