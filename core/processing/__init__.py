"""Core Processing subpackage

Aggregates processing, quality, NLP, and embeddings utilities.
"""

from ..processor import DocumentProcessor  # type: ignore
from ..quality import (  # type: ignore
    DataValidator,
    Deduplicator,
    MultilingualVerifier,
    QualityMonitor,
    LineageTracker,
)
from ..nlp import NLPUtils  # type: ignore
from ..embeddings import Embeddings  # type: ignore

__all__ = [
    "DocumentProcessor",
    "DataValidator",
    "Deduplicator",
    "MultilingualVerifier",
    "QualityMonitor",
    "LineageTracker",
    "NLPUtils",
    "Embeddings",
]