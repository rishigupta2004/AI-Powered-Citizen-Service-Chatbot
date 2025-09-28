"""
Streamlined Document Processor - Essential functionality only
"""
import os
import re
import hashlib
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import PyPDF2
import pdfplumber
import fitz
from .models import Service, Document, ContentChunk
from .repositories import ServiceRepository, DocumentRepository, ContentChunkRepository

class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.service_repo = ServiceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.chunk_repo = ContentChunkRepository(db)
    
    def process_document(self, file_path: str, service_id: int) -> Dict[str, Any]:
        """Process a single document"""
        try:
            # Extract text content
            text_content = self._extract_text(file_path)
            if not text_content.strip():
                return {'status': 'error', 'error': 'No text content extracted'}
            
            # Generate embedding
            embedding = self._generate_embedding(text_content)
            
            # Create document record
            document = self.document_repo.create(
                service_id=service_id,
                name=os.path.basename(file_path),
                description=f"Processed document from {file_path}",
                document_type='pdf',
                raw_content=text_content,
                embedding=embedding,
                is_processed=True
            )
            
            # Create content chunks
            chunks = self._create_chunks(text_content, service_id)
            
            return {
                'status': 'success',
                'document_id': document.doc_id,
                'chunks_created': len(chunks)
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try PyMuPDF first
            with fitz.open(file_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                if text.strip():
                    return text
            
            # Fallback to pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
                return text
                
        except Exception as e:
            print(f"Text extraction failed: {e}")
            return ""
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            embedding = self.embedding_model.encode(text[:512])  # Limit text length
            return embedding.tolist()
        except Exception:
            return [0.0] * 384
    
    def _create_chunks(self, text: str, service_id: int) -> List[ContentChunk]:
        """Create content chunks for vector search"""
        chunks = []
        sentences = re.split(r'[.!?]+', text)
        
        # Group sentences into chunks
        chunk_size = 3
        for i in range(0, len(sentences), chunk_size):
            chunk_text = " ".join(sentences[i:i + chunk_size])
            if len(chunk_text.strip()) < 50:
                continue
            
            embedding = self._generate_embedding(chunk_text)
            
            chunk = self.chunk_repo.create(
                content_text=chunk_text,
                service_id=service_id,
                embedding=embedding
            )
            chunks.append(chunk)
        
        return chunks
