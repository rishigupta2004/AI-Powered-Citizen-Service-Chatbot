from data.processing.store_documents import DocumentPipeline

pipeline = DocumentPipeline()

# Example files (replace with your own dataset paths)
pipeline.ingest("data/docs/passport_services.pdf", source="passport")
pipeline.ingest("data/docs/aadhaar_update_form.pdf", source="aadhaar")
pipeline.ingest("data/docs/sample_pan_procedure.docx", source="pan")
pipeline.ingest("data/docs/epfo_notice.png", source="epfo")



"""
#!/usr/bin/env python3

scripts/test_document_pipeline.py

Walks data/docs/* and calls the DocumentPipeline.ingest for each file.

Usage:
    export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/gov_chatbot"
    python -m scripts.test_document_pipeline

import os
from pathlib import Path
from data.processing.store_documents import DocumentPipeline

def main():
    docs_root = Path("data/docs")
    pipeline = DocumentPipeline()
    total = 0
    for dept_dir in sorted(docs_root.iterdir()):
        if not dept_dir.is_dir():
            continue
        dept = dept_dir.name
        for file in sorted(dept_dir.iterdir()):
            if file.is_file():
                print(f"Ingesting {file} as source={dept} ...")
                try:
                    pipeline.ingest(str(file), source=dept)
                    total += 1
                except Exception as e:
                    print(f"Error ingesting {file}: {e}")
    print(f"Finished. Ingested {total} files.")

if __name__ == "__main__":
    main()   
"""