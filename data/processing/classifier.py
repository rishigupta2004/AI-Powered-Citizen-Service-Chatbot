def classify_document(text: str) -> str:
    """
    Simple rule-based classifier.
    Extendable with ML models later (BERT/SVM).
    """
    text_l = text.lower()
    if "passport" in text_l:
        return "passport"
    elif "aadhaar" in text_l:
        return "aadhaar"
    elif "pan" in text_l:
        return "pan"
    elif "epf" in text_l:
        return "epfo"
    elif "driving license" in text_l or "parivahan" in text_l:
        return "parivahan"
    return "general"
