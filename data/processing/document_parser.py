import pdfplumber, docx, pytesseract, cv2
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
        doc = docx.Document(path)
        return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    def parse_image(self, path: str) -> list[str]:
        """OCR from image."""
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(Image.fromarray(gray))
        return [text.strip()]

    def detect_language(self, text: str) -> str:
        try:
            return detect(text)
        except:
            return "unknown"
