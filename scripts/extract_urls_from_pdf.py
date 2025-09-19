import sys
from pathlib import Path
import re
from PyPDF2 import PdfReader

def extract_urls_from_pdf(pdf_path: Path) -> set[str]:
    urls = set()
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        text = page.extract_text() or ""
        found = re.findall(r"https?://[^\s\)\]\}\'\"<>]+", text)
        for u in found:
            # strip trailing punctuation
            u = u.rstrip('.,;:')
            urls.add(u)
    return urls

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.extract_urls_from_pdf <pdf_path> [out_file]")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    out_file = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/docs/urls.txt")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    urls = extract_urls_from_pdf(pdf_path)
    with out_file.open("w", encoding="utf-8") as f:
        for u in sorted(urls):
            f.write(u + "\n")
    print(f"Extracted {len(urls)} unique URLs -> {out_file}")

if __name__ == "__main__":
    main()
