"""
Legacy migration placeholder.

NOTE: The `content_chunks.category` column was renamed to `content_chunks.chunk_type`
in the repair pass (March 2025).

This script is intentionally a no-op on updated databases and is kept only as
historical reference.

Current migration source of truth:
  - database/enhanced_schema.sql
  - scripts/sql_runtime_alignment.sql
"""


def main() -> None:
    print("ℹ️ No migration executed.")
    print("   `category` has been replaced by `chunk_type`.")
    print("   Use scripts/sql_runtime_alignment.sql for DB alignment SQL.")


if __name__ == "__main__":
    main()
