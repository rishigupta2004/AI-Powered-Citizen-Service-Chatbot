"""
Streamlined FastAPI Application - Essential endpoints only
"""
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import os
import asyncio

from core.database import get_db
from core.models import Service, Procedure, Document, FAQ
from core.repositories import ServiceRepository, DocumentRepository, FAQRepository
from core.search import SearchEngine
from routes.api_endpoints import router as api_router
from routes.v1_endpoints import router as v1_router

app = FastAPI(
    title="Government Services API",
    description="Streamlined API for Government Services Data Warehouse",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Phase 4 CSV-derived service API endpoints (links left empty)
app.include_router(api_router)
app.include_router(v1_router)

# --- Week 3: Security & Middleware ---

# API key auth dependency (simple header-based)
API_KEY = os.getenv("API_KEY")

def require_api_key(request: Request):
    if API_KEY:
        key = request.headers.get("x-api-key")
        if key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
    # If no API_KEY set, run open mode
    return True

# Simple rate limiting (token bucket per IP)
RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "10"))
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "20"))
_buckets = {}

class Bucket:
    def __init__(self, capacity: int, refill_per_sec: int):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_per_sec = refill_per_sec
        self.last = time.time()

    def allow(self) -> bool:
        now = time.time()
        elapsed = now - self.last
        # Refill tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip for health and docs
    if request.url.path in ("/health", "/docs", "/openapi.json"):
        return await call_next(request)
    ip = request.client.host if request.client else "unknown"
    b = _buckets.get(ip)
    if b is None:
        b = Bucket(RATE_LIMIT_BURST, RATE_LIMIT_RPS)
        _buckets[ip] = b
    if not b.allow():
        return PlainTextResponse(status_code=429, content="Rate limit exceeded")
    return await call_next(request)

# Request logging (minimal)
@app.middleware("http")
async def request_logging(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    print(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response

# Structured error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "error": {
            "type": "HTTPException",
            "detail": exc.detail,
            "path": request.url.path
        }
    })

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Minimal logging; avoids leaking internals
    print(f"ERROR {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={
        "error": {
            "type": "ServerError",
            "detail": "An unexpected error occurred",
            "path": request.url.path
        }
    })

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/metrics")
async def metrics(db: Session = Depends(get_db), _auth: bool = Depends(require_api_key)):
    # Basic metrics: counts of core tables
    from core.repositories import ServiceRepository, DocumentRepository, FAQRepository, ContentChunkRepository
    s = ServiceRepository(db).count()
    d = DocumentRepository(db).count()
    f = FAQRepository(db).count()
    try:
        from core.repositories import ContentChunkRepository
        c = ContentChunkRepository(db).count()
    except Exception:
        c = 0
    return {"services": s, "documents": d, "faqs": f, "content_chunks": c}

# Search Endpoint
@app.post("/search")
async def search(
    query: str,
    service_id: Optional[int] = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_api_key)
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
    _auth: bool = Depends(require_api_key)
):
    """Get services with optional filtering"""
    service_repo = ServiceRepository(db)
    
    if category:
        services = service_repo.get_by_category(category)
    elif active_only:
        services = service_repo.get_active_services()
    else:
        services = service_repo.get_all(skip=skip, limit=limit)
    
    return [{
        'service_id': s.service_id,
        'name': s.name,
        'category': s.category,
        'description': s.description,
        'ministry': s.ministry,
        'is_active': s.is_active,
        'languages_supported': s.languages_supported
    } for s in services]

@app.get("/services/{service_id}")
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get specific service by ID"""
    service_repo = ServiceRepository(db)
    service = service_repo.get_by_id(service_id)
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return {
        'service_id': service.service_id,
        'name': service.name,
        'category': service.category,
        'description': service.description,
        'ministry': service.ministry,
        'is_active': service.is_active,
        'languages_supported': service.languages_supported
    }

# Documents Endpoints
@app.get("/documents")
async def get_documents(
    service_id: Optional[int] = None,
    mandatory_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get documents with optional filtering"""
    document_repo = DocumentRepository(db)
    
    if service_id and mandatory_only:
        documents = document_repo.get_mandatory_documents(service_id)
    elif service_id:
        documents = document_repo.get_by_service(service_id)
    else:
        documents = document_repo.get_all(skip=skip, limit=limit)
    
    return [{
        'doc_id': d.doc_id,
        'name': d.name,
        'description': d.description,
        'document_type': d.document_type,
        'is_mandatory': d.is_mandatory,
        'copies_required': d.copies_required,
        'validity_period': d.validity_period,
        'is_processed': d.is_processed
    } for d in documents]

# FAQs Endpoints
@app.get("/faqs")
async def get_faqs(
    service_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get FAQs with optional filtering"""
    faq_repo = FAQRepository(db)
    
    if service_id:
        faqs = faq_repo.get_by_service(service_id)
    else:
        faqs = faq_repo.get_all(skip=skip, limit=limit)
    
    return [{
        'faq_id': f.faq_id,
        'question': f.question,
        'answer': f.answer,
        'short_answer': f.short_answer,
        'category': f.category,
        'service_id': f.service_id
    } for f in faqs]

# Document Processing Endpoint
@app.post("/process-document")
async def process_document(
    file_path: str,
    service_id: int,
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_api_key)
):
    """Process a document and extract content"""
    from core.processor import DocumentProcessor
    
    processor = DocumentProcessor(db)
    result = processor.process_document(file_path, service_id)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
