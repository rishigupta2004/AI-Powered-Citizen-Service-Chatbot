from langdetect import detect
import re

GOV_KEYWORDS = [
    "passport", "aadhaar", "pan", "epfo", "parivahan",
    "ministry", "service", "procedure", "verification"
]

class NLPToolkit:
    """Lightweight multilingual NLP utilities for Phase 4 tasks."""

    def language_detection(self, text: str) -> str:
        try:
            return detect(text)
        except Exception:
            return "unknown"

    def entity_extraction(self, text: str) -> list:
        t = text.lower()
        entities = [kw for kw in GOV_KEYWORDS if kw in t]
        return list(sorted(set(entities)))

    def content_classification(self, text: str) -> str:
        # Leverage existing classifier
        try:
            from data.processing.classifier import DocumentClassifier
            return DocumentClassifier().classify(text)
        except Exception:
            return "general"

    def relationship_extraction(self, text: str) -> list:
        t = text.lower()
        relations = []
        if "passport" in t:
            relations.append({"from": "passport", "to": "ministry of external affairs", "type": "belongs_to"})
        if "aadhaar" in t:
            relations.append({"from": "aadhaar", "to": "uidai", "type": "managed_by"})
        if "pan" in t:
            relations.append({"from": "pan", "to": "income tax department", "type": "managed_by"})
        return relations

    def summarization(self, text: str) -> str:
        # Simple sentence-based summarization
        sentences = [s.strip() for s in re.split(r"[\.!?]+", text) if s.strip()]
        return " ".join(sentences[:2])