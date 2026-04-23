"""
Core module for Government Services Data Warehouse
Streamlined and efficient implementation
"""

from .database import get_db, Base, engine, SessionLocal
from .models import Service, Procedure, Document, FAQ, ContentChunk
from .repositories import ServiceRepository, DocumentRepository, FAQRepository, ContentChunkRepository

# Optional AI/ML imports - only import if available
try:
    from .search import SearchEngine
    from .processor import DocumentProcessor
    __all__ = [
        'get_db', 'Base', 'engine', 'SessionLocal',
        'Service', 'Procedure', 'Document', 'FAQ', 'ContentChunk',
        'ServiceRepository', 'DocumentRepository', 'FAQRepository', 'ContentChunkRepository',
        'SearchEngine', 'DocumentProcessor'
    ]
except ImportError:
    # AI/ML dependencies not available
    __all__ = [
        'get_db', 'Base', 'engine', 'SessionLocal',
        'Service', 'Procedure', 'Document', 'FAQ', 'ContentChunk',
        'ServiceRepository', 'DocumentRepository', 'FAQRepository', 'ContentChunkRepository'
    ]
