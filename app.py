"""
Streamlined FastAPI Application - Essential endpoints only
"""

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import time
import asyncio
import logging
import re
from pathlib import Path
from urllib.parse import quote

from core.database import get_db
from core.config import FRONTEND_URL, CORS_ORIGINS, CORS_ORIGIN_REGEX

# Models imported lazily by repositories/endpoints; keep app surface minimal
from core.repositories import ServiceRepository, DocumentRepository, FAQRepository
from core.search import SearchEngine
from routes.api_endpoints import router as api_router
from routes.v1_endpoints import router as v1_router
from routes.graphql_schema import get_graphql_router
from routes.auth_endpoints import (
    router as auth_router,
    _legacy_router as auth_legacy_router,
)
from routes.clerk_sync import router as clerk_router
from routes.middleware import (
    register_middlewares,
    register_exception_handlers,
    require_api_key,
)
from routes.chat_endpoints import chat_router
from core.embeddings import get_embedding_engine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Government Services API",
    description="Streamlined API for Government Services Data Warehouse",
    version="1.0.0",
)

PROJECT_ROOT = Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / "data" / "docs"

_cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4173",
    "https://seva-sindu-portal.vercel.app",
    "https://gov-chatbot.fly.dev",
    "https://rishigupta-rg007--seva-sindhu-backend-fastapi-entrypoint.modal.run",
]
if FRONTEND_URL:
    _cors_origins.append(FRONTEND_URL.rstrip("/"))
if CORS_ORIGINS:
    _cors_origins.extend(
        origin.strip().rstrip("/")
        for origin in CORS_ORIGINS.split(",")
        if origin.strip()
    )

_cors_origins = sorted(set(_cors_origins))


def _is_allowed_browser_origin(origin: str | None) -> bool:
    if not origin:
        return False
    normalized = origin.strip().rstrip("/")
    if normalized in _cors_origins:
        return True
    if CORS_ORIGIN_REGEX:
        try:
            return re.match(CORS_ORIGIN_REGEX, normalized) is not None
        except re.error:
            return False
    return False


# Include Phase 4 CSV-derived service API endpoints (links left empty)
app.include_router(api_router)
app.include_router(v1_router)
app.include_router(auth_router)
app.include_router(auth_legacy_router)
app.include_router(clerk_router)
app.include_router(chat_router)

# Mount GraphQL router if available (optional dependency)
try:
    _graphql_router = get_graphql_router()
    if _graphql_router is not None:
        app.include_router(_graphql_router, prefix="/api/v1/graphql")
        print("✅ GraphQL router mounted at /api/v1/graphql")
    else:
        print("ℹ️ GraphQL not configured; install 'strawberry-graphql' to enable.")
except Exception:
    print("ℹ️ GraphQL not configured; install 'strawberry-graphql' to enable.")

register_middlewares(app)
register_exception_handlers(app)

if DOCS_DIR.exists():
    app.mount("/public/docs", StaticFiles(directory=DOCS_DIR), name="public-docs")


def _candidate_doc_folders(service_slug: str) -> list[str]:
    slug = (service_slug or "").lower()
    if not slug:
        return []
    mapping: list[tuple[str, str]] = [
        ("aadhaar", "aadhaar"),
        ("myaadhaar", "aadhaar"),
        ("passport", "passport"),
        ("pan", "pan"),
        ("epfo", "epfo"),
        ("parivahan", "parivahan"),
        ("sarathi", "parivahan"),
        ("vahan", "parivahan"),
        ("rail", "railways"),
        ("rbi", "rbi"),
        ("scholar", "education"),
        ("swayam", "education"),
        ("diksha", "education"),
        ("education", "education"),
        ("tax", "pan"),
        ("income_tax", "pan"),
        ("gst", "pan"),
        ("voter", "other"),
        ("rti", "other"),
        ("court", "other"),
        ("health", "other"),
        ("cowin", "other"),
        ("abha", "other"),
        ("consumer", "other"),
        ("cyber", "other"),
        ("pm", "other"),
        ("nps", "other"),
        ("grievance", "other"),
    ]
    matched: list[str] = []

    service_specific = DOCS_DIR / "services" / slug
    if service_specific.exists() and service_specific.is_dir():
        return [f"services/{slug}"]

    for token, folder in mapping:
        if token in slug and folder not in matched:
            matched.append(folder)
    return matched


@app.get("/api/v1/service-docs/{service_slug}")
async def get_service_docs(service_slug: str):
    if not DOCS_DIR.exists():
        return {"service_slug": service_slug, "documents": []}

    docs: list[dict[str, object]] = []
    seen_paths: set[str] = set()

    folders = _candidate_doc_folders(service_slug)

    for folder in folders:
        folder_path = DOCS_DIR / folder
        if not folder_path.exists() or not folder_path.is_dir():
            continue

        for file_path in sorted(folder_path.glob("*.pdf")):
            rel = file_path.relative_to(DOCS_DIR).as_posix()
            if rel in seen_paths:
                continue
            try:
                size_kb = max(1, int(file_path.stat().st_size / 1024))
            except FileNotFoundError:
                continue
            docs.append(
                {
                    "name": file_path.stem.replace("-", " ").replace("_", " ").strip(),
                    "format": "PDF",
                    "size": f"{size_kb} KB",
                    "url": f"/public/docs/{quote(rel)}",
                    "source": folder,
                }
            )
            seen_paths.add(rel)

    return {"service_slug": service_slug, "documents": docs}


@app.middleware("http")
async def explicit_browser_cors(request: Request, call_next):
    origin = request.headers.get("origin")
    preflight = request.method == "OPTIONS" and request.headers.get(
        "access-control-request-method"
    )

    if preflight:
        if not _is_allowed_browser_origin(origin):
            return Response(status_code=400, content="Disallowed CORS origin")
        response = Response(status_code=204)
    else:
        response = await call_next(request)

    if _is_allowed_browser_origin(origin):
        allowed_origin = origin.rstrip("/") if origin else ""
        response.headers["Access-Control-Allow-Origin"] = allowed_origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = request.headers.get(
            "access-control-request-headers", "content-type,authorization"
        )
    return response


def _run_embedding_warmup() -> None:
    engine = get_embedding_engine()
    engine.embed_text("passport status check", is_query=True)


@app.on_event("startup")
async def warmup_embeddings() -> None:
    """Warm embedding path to reduce first-request latency."""
    try:
        await asyncio.wait_for(asyncio.to_thread(_run_embedding_warmup), timeout=4.0)
        logger.info("Embedding warm-up completed")
    except asyncio.TimeoutError:
        logger.info("Embedding warm-up timed out; continuing startup")
    except Exception as exc:  # pragma: no cover
        logger.info("Embedding warm-up skipped: %s", exc)


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/metrics")
async def metrics(
    db: Session = Depends(get_db), _auth: bool = Depends(require_api_key)
):
    # Basic metrics: counts of core tables
    from core.repositories import (
        ServiceRepository,
        DocumentRepository,
        FAQRepository,
        ContentChunkRepository,
    )

    s = ServiceRepository(db).count()
    d = DocumentRepository(db).count()
    f = FAQRepository(db).count()
    c = ContentChunkRepository(db).count()
    return {"services": s, "documents": d, "faqs": f, "content_chunks": c}


# Search Endpoint
@app.post("/search")
async def search(
    query: str,
    service_id: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_api_key),
):
    """Search across all content types"""
    search_engine = SearchEngine(db)
    results = search_engine.search(query, service_id, limit)
    return results


# Services Endpoints
@app.get("/services")
async def get_services(
    category: Optional[str] = None,
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_api_key),
):
    """Get services with optional filtering"""
    service_repo = ServiceRepository(db)

    if category:
        services = service_repo.get_by_category(category)
    elif active_only:
        services = service_repo.get_active_services()
    else:
        services = service_repo.get_all(skip=skip, limit=limit)

    return [
        {
            "service_id": s.service_id,
            "name": s.name,
            "category": s.category,
            "description": s.description,
            "ministry": s.ministry,
            "is_active": s.is_active,
            "languages_supported": s.languages_supported,
        }
        for s in services
    ]


@app.get("/services/{service_id}")
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get specific service by ID"""
    service_repo = ServiceRepository(db)
    service = service_repo.get_by_id(service_id)

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {
        "service_id": service.service_id,
        "name": service.name,
        "category": service.category,
        "description": service.description,
        "ministry": service.ministry,
        "is_active": service.is_active,
        "languages_supported": service.languages_supported,
    }


# Documents Endpoints
@app.get("/documents")
async def get_documents(
    service_id: Optional[int] = None,
    mandatory_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get documents with optional filtering"""
    document_repo = DocumentRepository(db)

    if service_id and mandatory_only:
        documents = document_repo.get_mandatory_documents(service_id)
    elif service_id:
        documents = document_repo.get_by_service(service_id)
    else:
        documents = document_repo.get_all(skip=skip, limit=limit)

    return [
        {
            "doc_id": d.doc_id,
            "name": d.name,
            "description": d.description,
            "document_type": d.document_type,
            "is_mandatory": d.is_mandatory,
            "copies_required": d.copies_required,
            "validity_period": d.validity_period,
            "is_processed": d.is_processed,
        }
        for d in documents
    ]


# FAQs Endpoints
@app.get("/faqs")
async def get_faqs(
    service_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get FAQs with optional filtering"""
    faq_repo = FAQRepository(db)

    if service_id:
        faqs = faq_repo.get_by_service(service_id)
    else:
        faqs = faq_repo.get_all(skip=skip, limit=limit)

    return [
        {
            "faq_id": f.faq_id,
            "question": f.question,
            "answer": f.answer,
            "short_answer": f.short_answer,
            "category": f.category,
            "service_id": f.service_id,
        }
        for f in faqs
    ]


# Document Processing Endpoint
@app.post("/process-document")
async def process_document(
    file_path: str,
    service_id: int,
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_api_key),
):
    """Process a document and extract content"""
    from core.processor import DocumentProcessor

    processor = DocumentProcessor(db)
    result = processor.process_document(file_path, service_id)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
