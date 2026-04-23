"""Core DB subpackage

Provides convenient re-exports for database engine, session, models,
and repositories without changing existing import paths.
"""

from ..database import engine, SessionLocal, get_db  # type: ignore
from ..models import Service, Document, FAQ, ContentChunk, RawContent  # type: ignore
from ..repositories import (  # type: ignore
    ServiceRepository,
    DocumentRepository,
    FAQRepository,
    ContentChunkRepository,
    RawContentRepository,
)

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "Service",
    "Document",
    "FAQ",
    "ContentChunk",
    "RawContent",
    "ServiceRepository",
    "DocumentRepository",
    "FAQRepository",
    "ContentChunkRepository",
    "RawContentRepository",
]