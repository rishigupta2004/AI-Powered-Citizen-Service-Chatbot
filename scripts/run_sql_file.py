"""
Run SQL file against the configured DATABASE_URL and print results.

Usage:
  python3 scripts/run_sql_file.py database/warehouse_inspection.sql
  python3 scripts/run_sql_file.py database/enhanced_schema.sql

The runner is tolerant: it skips comments, splits by semicolons, and
continues on errors, printing brief outputs for SELECT statements.
"""
import sys
import os
from pathlib import Path
from typing import List
from sqlalchemy import create_engine, text


def load_database_url() -> str:
    try:
        from core.database import DATABASE_URL  # type: ignore
        return DATABASE_URL
    except Exception:
        env_url = os.getenv("DATABASE_URL")
        if not env_url:
            raise RuntimeError("DATABASE_URL not set and core.database unavailable")
        return env_url


def read_sql_statements(file_path: str) -> List[str]:
    sql = Path(file_path).read_text(encoding="utf-8")
    # Remove Windows newlines
    sql = sql.replace("\r\n", "\n")
    statements: List[str] = []
    buffer: List[str] = []
    for line in sql.splitlines():
        # Skip comments
        if line.strip().startswith("--"):
            continue
        buffer.append(line)
        if ";" in line:
            joined = "\n".join(buffer)
            parts = joined.split(";")
            # All parts except last end in semicolon
            for part in parts[:-1]:
                stmt = part.strip()
                if stmt:
                    statements.append(stmt)
            buffer = [parts[-1]] if parts[-1].strip() else []
    # Remainder
    remainder = "\n".join(buffer).strip()
    if remainder:
        statements.append(remainder)
    return statements


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/run_sql_file.py <sql_file>")
        return 1
    sql_file = sys.argv[1]
    if not os.path.exists(sql_file):
        print(f"❌ SQL file not found: {sql_file}")
        return 1

    db_url = load_database_url()
    engine = create_engine(db_url, pool_pre_ping=True)
    stmts = read_sql_statements(sql_file)

    print(f"🗃️  Executing SQL file: {sql_file}")
    print(f"📌 DATABASE_URL: {db_url}")
    print(f"📑 Statements: {len(stmts)}\n")

    with engine.connect() as conn:
        for i, stmt in enumerate(stmts, 1):
            try:
                print(f"--[{i}]--\n{stmt[:200]}{'...' if len(stmt) > 200 else ''}")
                is_select = stmt.strip().lower().startswith("select")
                result = conn.execute(text(stmt))
                if is_select:
                    rows = result.mappings().fetchmany(5)
                    if rows:
                        for r in rows:
                            print(dict(r))
                    else:
                        print("(no rows)")
                else:
                    try:
                        conn.commit()
                    except Exception:
                        pass
                    print("(executed)")
            except Exception as e:
                print(f"⚠️  Error executing statement {i}: {e}")
            print("")

    print("✅ SQL execution complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())