"""
Streamlined Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://rishigupta:home@localhost:5432/gov_chatbot_db"
)

# Robust engine configuration for stability and performance
_connect_timeout = min(5, int(os.getenv("DB_CONNECT_TIMEOUT", "5")))
_engine_args = {
    "pool_pre_ping": True,
    "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    "pool_recycle": 1800,
    "connect_args": {
        "connect_timeout": _connect_timeout,
        "options": "-c statement_timeout=10000",  # 10s query timeout
    },
}

# Add SSL mode for cloud databases (Supabase, Neon, etc.)
_db_url = DATABASE_URL
if not _db_url.startswith("sqlite"):
    _engine_args["connect_args"]["sslmode"] = "require"

engine = create_engine(_db_url, **_engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
