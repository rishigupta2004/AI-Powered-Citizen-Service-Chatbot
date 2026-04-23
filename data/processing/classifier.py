def classify_document(text: str) -> str:
    """
    Simple rule-based classifier.
    Extendable with ML models later (BERT/SVM).
    """
    text_l = text.lower()
    if "passport" in text_l:
        return "passport"
    elif "aadhaar" in text_l or "uidai" in text_l:
        return "aadhaar"
    elif "pan" in text_l or "income tax" in text_l:
        return "pan"
    elif "epf" in text_l or "provident fund" in text_l:
        return "epf"
    elif "driving license" in text_l or "parivahan" in text_l or "rto" in text_l:
        return "driving_license"
    return "general"


class DocumentClassifier:
    """Class-based wrapper for classification used in Week 6 pipeline."""

    def __init__(self) -> None:
        # Placeholder for future ML models
        self._labels = [
            ("passport", ["passport", "visa"]),
            ("aadhaar", ["aadhaar", "uidai"]),
            ("pan", ["pan", "income tax"]),
            ("epf", ["epf", "provident fund", "pf"]),
            ("driving_license", ["driving license", "dl", "parivahan", "rto"]),
        ]

    def classify(self, text: str) -> str:
        t = text.lower()
        for label, keywords in self._labels:
            if any(k in t for k in keywords):
                return label
        return "general"

    # Backwards-compatible method expected by tests
    def classify_document(self, text: str) -> str:
        return self.classify(text)
