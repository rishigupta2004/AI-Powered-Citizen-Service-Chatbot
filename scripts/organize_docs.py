#!/usr/bin/env python3
"""
scripts/organize_docs.py

Usage:
    python -m scripts.organize_docs data/docs
"""
import sys
from pathlib import Path
from slugify import slugify
import csv

def normalize_folder(root: Path):
    root = root.resolve()
    rows = []
    for sub in root.iterdir():
        if not sub.is_dir():
            continue
        dept = sub.name
        for file in sub.iterdir():
            if not file.is_file():
                continue
            # sanitize
            new_name = slugify(file.stem)[:160] + file.suffix.lower()
            new_path = file.parent / new_name
            if file != new_path:
                file.rename(new_path)
            rows.append({"department": dept, "filename": new_name, "filepath": str(new_path)})
    # manifest
    manifest = root / "organize_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["department","filename","filepath"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Organized files. Manifest: {manifest}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.organize_docs <docs_root>")
        sys.exit(1)
    normalize_folder(Path(sys.argv[1]))
