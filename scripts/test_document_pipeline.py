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
