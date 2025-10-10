"""
Phase 4 Warehouse Validation (Local)

Runs structural and content checks against the warehouse tables:
- services, procedures, documents, faqs, content_chunks, raw_content

Usage:
  python3 scripts/db_validate_phase4.py

Environment:
  DATABASE_URL must point to your Postgres instance.
"""
import os
from typing import List, Dict
from sqlalchemy import create_engine, text


TABLES: List[str] = [
    "services",
    "procedures",
    "documents",
    "faqs",
    "content_chunks",
    "raw_content",
]


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL is not set. Export it before running.")
        return

    engine = create_engine(db_url)
    with engine.connect() as conn:
        print_header("Phase 4 Warehouse Validation")
        # Show database information
        try:
            ver = conn.execute(text("SELECT version();")).scalar()
            print(f"Database: {ver}")
        except Exception:
            pass

        for table in TABLES:
            print_header(f"Table: {table}")
            # Columns
            cols = conn.execute(text(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = :table
                ORDER BY ordinal_position
                """
            ), {"table": table}).mappings().all()

            if cols:
                print("Columns:")
                for c in cols:
                    print(f"- {c['column_name']} ({c['data_type']}, nullable={c['is_nullable']})")
            else:
                print("(No columns found; table may not exist)")

            # Indexes
            try:
                idx = conn.execute(text(
                    """
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = :table
                    ORDER BY indexname
                    """
                ), {"table": table}).mappings().all()
                if idx:
                    print("Indexes:")
                    for i in idx:
                        print(f"- {i['indexname']}: {i['indexdef']}")
            except Exception:
                pass

            # Counts
            try:
                cnt = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                print(f"Row count: {cnt}")
            except Exception as e:
                print(f"Row count: error ({e})")

            # Sample rows
            try:
                sample = conn.execute(text(f"SELECT * FROM {table} ORDER BY 1 DESC LIMIT 10;")).mappings().all()
                if sample:
                    print("Sample rows (up to 10):")
                    for r in sample:
                        # Print a compact dict
                        dr: Dict[str, str] = {k: (str(v)[:200] if v is not None else None) for k, v in dict(r).items()}
                        print(dr)
                else:
                    print("(No rows)")
            except Exception as e:
                print(f"Sample rows: error ({e})")

        print_header("Validation Complete")


if __name__ == "__main__":
    main()