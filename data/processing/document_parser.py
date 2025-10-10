import pdfplumber, pytesseract, cv2
try:
    import docx  # Optional dependency for Word parsing
    _HAS_DOCX = True
except Exception:
    docx = None
    _HAS_DOCX = False
from PIL import Image
from langdetect import detect
import os

class DocumentParser:
    def __init__(self):
        pass

    def parse_pdf(self, path: str) -> list[str]:
        """Extract text from a PDF (with fallback OCR)."""
        text_chunks = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_chunks.append(text.strip())
                else:
                    # OCR fallback
                    img = page.to_image(resolution=300).original
                    text_chunks.append(pytesseract.image_to_string(img))
        return text_chunks

    def parse_word(self, path: str) -> list[str]:
        """Extract text from Word document."""
        if not _HAS_DOCX:
            raise ImportError("python-docx is not installed; Word parsing unavailable.")
        doc = docx.Document(path)
        return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    def parse_image(self, path: str) -> list[str]:
        """OCR from image."""
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        return [text.strip()]

    def parse_content(self, text: str) -> list[str]:
        """Normalize raw text input into logical chunks.
        Splits by double newlines or periods to produce manageable pieces.
        """
        if not text:
            return []
        # Prefer paragraph splits; fallback to sentences
        parts = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(parts) <= 1:
            parts = [p.strip() for p in text.split(".") if p.strip()]
        return parts

    def detect_language(self, text: str) -> str:
        try:
            return detect(text)
        except:
            return "unknown"
