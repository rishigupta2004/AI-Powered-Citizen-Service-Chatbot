"""Single source of truth for runtime configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv


def _first_non_empty(*keys: str, default: str = "") -> str:
    for key in keys:
        value = os.getenv(key)
        if value is not None and value.strip():
            return value.strip()
    return default


# Resolve project root regardless of CWD
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local", override=True)

# -- Embeddings ----------------------------------------------------------------
# 384  -> all-MiniLM-L6-v2 (default, fast)
# 1024 -> intfloat/multilingual-e5-large-instruct (production, set in .env)
EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "384"))

# -- Database ------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/citizen_services_dev",
)

# -- Auth ----------------------------------------------------------------------
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")

# -- Clerk ---------------------------------------------------------------------
CLERK_SECRET_KEY: str = _first_non_empty("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY: str = _first_non_empty(
    "CLERK_PUBLISHABLE_KEY",
    "CLERK_PUBLIC_KEY",
    "CLERK_PUBLIC_KE",
)
CLERK_FRONTEND_API_URL: str = _first_non_empty(
    "CLERK_FRONTEND_API_URL",
    "CLERK_Frontend_API_URL",
)
CLERK_BACKEND_API_URL: str = _first_non_empty(
    "CLERK_BACKEND_API_URL",
    "CLERK_Backend_API_URL",
    default="https://api.clerk.com",
)
CLERK_DOMAIN: str = _first_non_empty(
    "CLERK_DOMAIN",
    "CLERK_FRONTEND_API_URL",
    "CLERK_Frontend_API_URL",
)
_default_clerk_jwks_url = (
    f"{CLERK_DOMAIN.rstrip('/')}/.well-known/jwks.json"
    if CLERK_DOMAIN
    else "https://api.clerk.dev/.well-known/jwks.json"
)
CLERK_JWKS_URL: str = _first_non_empty(
    "CLERK_JWKS_URL",
    "JWKS_URL",
    default=_default_clerk_jwks_url,
)
JWKS_PUBLIC_KEY: str = _first_non_empty("JWKS_PUBLIC_KEY", "JWKS_Public_Key")

# -- Sarvam --------------------------------------------------------------------
SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")

# -- Frontend / CORS -----------------------------------------------------------
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "")
CORS_ORIGIN_REGEX: str = os.getenv("CORS_ORIGIN_REGEX", r"https?://.*")
