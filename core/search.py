"""
Streamlined Search Engine - Embeddings optional and lazily loaded
"""
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import os
from .repositories import ServiceRepository, DocumentRepository, FAQRepository, ContentChunkRepository

class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.embeddings_enabled = os.getenv('EMBEDDING_ENABLED', 'true').lower() in ('1', 'true', 'yes')
        self.embedding_model = None
        self.service_repo = ServiceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.faq_repo = FAQRepository(db)
        self.chunk_repo = ContentChunkRepository(db)
    
    def search(self, query: str, service_id: Optional[int] = None, limit: int = 10) -> Dict[str, Any]:
        """Perform hybrid search across all content types"""
        try:
            # Generate query embedding if enabled
            query_embedding = self._generate_embedding(query) if self.embeddings_enabled else []
            
            # Search different content types
            results = []
            
            # Search documents
            docs = self.document_repo.search_semantic(query_embedding, limit) if self.embeddings_enabled else []
            for doc in docs:
                if not service_id or doc.service_id == service_id:
                    results.append({
                        'type': 'document',
                        'content': doc.raw_content or doc.name,
                        'similarity': self._calculate_similarity(query_embedding, doc.embedding),
                        'service_id': doc.service_id,
                        'source': 'document'
                    })
            
            # Search FAQs
            faqs = self.faq_repo.search_semantic(query_embedding, limit) if self.embeddings_enabled else []
            for faq in faqs:
                if not service_id or faq.service_id == service_id:
                    results.append({
                        'type': 'faq',
                        'content': f"Q: {faq.question}\nA: {faq.answer}",
                        'similarity': self._calculate_similarity(query_embedding, faq.question_embedding),
                        'service_id': faq.service_id,
                        'source': 'faq'
                    })
            
            # Search content chunks
            chunks = self.chunk_repo.search_semantic(query_embedding, limit) if self.embeddings_enabled else []
            for chunk in chunks:
                if not service_id or chunk.service_id == service_id:
                    results.append({
                        'type': 'content_chunk',
                        'content': chunk.content_text,
                        'similarity': self._calculate_similarity(query_embedding, chunk.embedding),
                        'service_id': chunk.service_id,
                        'source': 'content_chunk'
                    })
            
            # Sort by similarity
            results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return {
                'query': query,
                'total_results': len(results),
                'results': results[:limit]
            }
            
        except Exception as e:
            return {
                'query': query,
                'total_results': 0,
                'results': [],
                'error': str(e)
            }

    def get_model_name(self) -> str:
        """Return the currently configured embedding model name."""
        return self.model_name
    
    def _ensure_model(self):
        if self.embedding_model is None and self.embeddings_enabled:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(self.model_name)
            except Exception:
                self.embedding_model = None

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text if enabled; otherwise return empty list."""
        try:
            self._ensure_model()
            if self.embedding_model is None:
                return []
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception:
            return []
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception:
            return 0.0
