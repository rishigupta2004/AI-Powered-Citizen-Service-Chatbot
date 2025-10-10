"""
Idempotent migration: add `category` column to `content_chunks` if missing.

Usage:
  python3 scripts/apply_migration.py
"""
import sys
from sqlalchemy import create_engine, text
import os


def main():
    try:
        from core.database import DATABASE_URL
    except Exception:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not set and core.database unavailable")
            sys.exit(1)

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Add column if it does not exist
            conn.execute(text("ALTER TABLE IF EXISTS content_chunks ADD COLUMN IF NOT EXISTS category VARCHAR(100);"))
            # Optional helpful index
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chunks_category ON content_chunks(category);"))
            conn.commit()
            print("✅ Migration applied: content_chunks.category added (if missing)")
        except Exception as e:
            print("❌ Migration failed:", e)
            conn.rollback()
            sys.exit(1)


if __name__ == "__main__":
    main()