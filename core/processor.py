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
from data.processing.document_parser import DocumentParser
from data.processing.classifier import DocumentClassifier

class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.embedding_model = SentenceTransformer(model_name)
        self.service_repo = ServiceRepository(db)
        self.document_repo = DocumentRepository(db)
        self.chunk_repo = ContentChunkRepository(db)
        # Week 6: lightweight parser and classifier
        self.parser = DocumentParser()
        self.classifier = DocumentClassifier()
    
    def process_document(self, file_path: str, service_id: int) -> Dict[str, Any]:
        """Process a single document"""
        try:
            # Extract text content
            text_content = self._extract_text(file_path)
            if not text_content.strip():
                return {'status': 'error', 'error': 'No text content extracted'}

            # Detect language and classify
            language = self.parser.detect_language(text_content[:500]) if text_content else 'unknown'
            classification = self.classifier.classify(text_content)

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
                is_processed=True,
                language=language
            )

            # Create content chunks
            chunks = self._create_chunks(text_content, service_id)

            return {
                'status': 'success',
                'document_id': document.doc_id,
                'chunks_created': len(chunks),
                'language': language,
                'classification': classification
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
                if text.strip():
                    return text
                # Week 6: OCR fallback if no extractable text
                # Check if OCR is enabled via environment variable
                use_ocr = os.environ.get("USE_OCR", "true").lower() in ("true", "1", "yes")
                if use_ocr:
                    try:
                        import pytesseract
                        import cv2
                        import numpy as np
                        
                        ocr_text = ""
                        for page in pdf.pages:
                            try:
                                # Convert page to image
                                img = page.to_image(resolution=300).original
                                
                                # Convert PIL image to OpenCV format
                                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                                
                                # Image preprocessing for better OCR results
                                # Convert to grayscale
                                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                                
                                # Apply thresholding to handle different lighting conditions
                                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                                
                                # Apply noise reduction
                                denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
                                
                                # OCR with improved image
                                ocr_text += pytesseract.image_to_string(denoised) + "\n"
                                
                                # If OCR text is too short, try original image
                                if len(ocr_text.strip()) < 50:
                                    ocr_text += pytesseract.image_to_string(img) + "\n"
                            except Exception as e:
                                print(f"OCR processing error on page: {e}")
                                continue
                        
                        if ocr_text.strip():
                            print(f"Successfully extracted {len(ocr_text)} characters using OCR")
                            return ocr_text
                    except ImportError as e:
                        print(f"OCR dependencies not available: {e}")
                    except Exception as e:
                        print(f"OCR processing failed: {e}")
                
                # OCR not available, disabled, or failed
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
            # Week 6 follow-up: classify each chunk
            chunk_category = self.classifier.classify(chunk_text)
            
            chunk = self.chunk_repo.create(
                content_text=chunk_text,
                service_id=service_id,
                category=chunk_category,
                embedding=embedding
            )
            chunks.append(chunk)
        
        return chunks
