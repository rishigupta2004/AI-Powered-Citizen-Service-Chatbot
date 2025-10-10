from fastapi import APIRouter, Depends, Query, Body
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import csv
import json

from core.database import get_db, SessionLocal
from core.search import SearchEngine
from core.quality import run_all_quality_checks, QualityMonitor
from core.repositories import (
    RawContentRepository,
    ServiceRepository,
    DocumentRepository,
    FAQRepository,
)
from core.cache import ttl_cache
from core.ops.backup_restore import backup_database, restore_database
from core.recommendations import RecommendationEngine
from .graphql_schema import get_graphql_router
from .schemas import (
    EndpointResponse,
    SearchQuery,
    SuggestionQuery,
    AnalyticsEvent,
    AdminContentRequest,
    BackupRequest,
    RestoreRequest,
)


router = APIRouter(prefix="/api/v1", tags=["v1"])


# Week 12: Service-specific endpoints
@router.get("/passport/procedures", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def passport_procedures() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "passport", "endpoint": "procedures"})


@router.get("/passport/documents", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def passport_documents() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "passport", "endpoint": "documents"})


@router.get("/passport/fees", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def passport_fees() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "passport", "endpoint": "fees"})


@router.get("/passport/offices", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def passport_offices() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "passport", "endpoint": "offices"})


@router.get("/aadhaar/enrollment", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def aadhaar_enrollment() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "aadhaar", "endpoint": "enrollment"})


@router.get("/aadhaar/updates", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def aadhaar_updates() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "aadhaar", "endpoint": "updates"})


@router.get("/aadhaar/documents", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def aadhaar_documents() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "aadhaar", "endpoint": "documents"})


@router.get("/pan/application", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def pan_application() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "pan", "endpoint": "application"})


@router.get("/pan/correction", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def pan_correction() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "pan", "endpoint": "correction"})


@router.get("/pan/linking", response_model=EndpointResponse)
@ttl_cache(ttl_seconds=120)
def pan_linking() -> EndpointResponse:
    return EndpointResponse(status="not_implemented", links=[], data={"service": "pan", "endpoint": "linking"})


# Week 13: Search & discovery APIs
@router.get("/search")
def universal_search(q: str = Query(..., description="Query string"), service_id: int | None = None, limit: int = 10, db: Session = Depends(get_db)) -> Dict[str, Any]:
    engine = SearchEngine(db)
    return engine.search(q, service_id=service_id, limit=limit)


@router.get("/discovery/services")
@ttl_cache(ttl_seconds=300)
def discovery_services() -> Dict[str, Any]:
    csv_path = Path("gov-chatbot/Service-APIService-Endpoint.csv")
    services: Dict[str, List[Dict[str, str]]] = {}
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                service = (row.get("Service") or "").strip() or "Unknown"
                services.setdefault(service, []).append({
                    "api_service": (row.get("API Service") or "").strip(),
                    "endpoint": (row.get("Endpoint") or "").strip(),
                })
    return {"services": services}


@router.get("/recommendations")
@ttl_cache(ttl_seconds=120)
def recommendation_system(q: str = Query(""), db: Session = Depends(get_db)) -> Dict[str, Any]:
    engine = RecommendationEngine()
    # Use query-driven embedding recommendations when provided, otherwise fallback by document counts
    if q:
        recs = engine.recommend_by_embedding(q, top_k=10)
        return {"recommendations": recs}
    svc_repo = ServiceRepository(db)
    doc_repo = DocumentRepository(db)
    data: List[Dict[str, Any]] = []
    for svc in svc_repo.get_all(0, 50):
        count = len(doc_repo.get_by_service(getattr(svc, "id", 0)))
        data.append({"service_id": getattr(svc, "id", 0), "name": getattr(svc, "name", ""), "document_count": count})
    data.sort(key=lambda x: x["document_count"], reverse=True)
    return {"recommendations": data[:10]}


@router.get("/suggestions")
@ttl_cache(ttl_seconds=60)
def query_suggestions(q: str = Query(""), limit: int = 5) -> Dict[str, Any]:
    engine = RecommendationEngine()
    suggestions = engine.suggest_queries(q, top_k=limit) if q else []
    return {"suggestions": suggestions}


@router.post("/analytics/events")
def analytics_event(event: AnalyticsEvent = Body(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    repo = RawContentRepository(db)
    content = json.dumps(event.dict(), ensure_ascii=False)
    saved = repo.create(
        source_type="analytics_event",
        source_url="",
        source_name="analytics",
        title=event.event_type,
        content=content,
        content_type="application/json",
        language="en",
        is_processed=False,
        processing_status="unprocessed",
        metadata_json={"user_id": event.user_id},
    )
    return {"status": "accepted", "event_id": getattr(saved, "content_id", None)}


# Week 14: Admin & Management APIs
@router.post("/admin/content")
def admin_content(req: AdminContentRequest = Body(...)) -> Dict[str, Any]:
    # Placeholder content management handler
    return {"status": "not_implemented", "action": req.action, "type": req.type}


@router.get("/admin/quality")
def data_quality(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return run_all_quality_checks(db)


@router.get("/admin/analytics")
def admin_analytics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    repo = RawContentRepository(db)
    events = repo.get_by_source("analytics_event", limit=100)
    return {"events_count": len(events)}


@router.get("/admin/system-health")
def system_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Basic health summary
    try:
        svc_repo = ServiceRepository(db)
        doc_repo = DocumentRepository(db)
        faq_repo = FAQRepository(db)
        monitor = QualityMonitor()
        metrics = monitor.summarize(db)
        return {
            "status": "ok",
            "services": svc_repo.count(),
            "documents": doc_repo.count(),
            "faqs": faq_repo.count(),
            "metrics": metrics,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/admin/backup")
def backup(req: BackupRequest = Body(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Perform immediate backup to destination or default timestamped folder
    dest = req.destination or f"gov-chatbot/data/db/backups/{Path.cwd().name}-{Path('gov-chatbot').name}-{int(Path().stat().st_mtime)}"
    # Prefer a readable timestamped folder name
    ts_folder = f"gov-chatbot/data/db/backups/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    output_dir = req.destination or ts_folder
    try:
        result = backup_database(db, output_dir)
        return {"status": "completed", **result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/admin/restore")
def restore(req: RestoreRequest = Body(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        result = restore_database(db, req.source)
        return {"status": "completed", **result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Week 15: GraphQL Integration (placeholder status endpoint)
# Avoid path collision with the mounted GraphQL router at `/api/v1/graphql`
# by exposing a separate status route under `/api/v1/graphql-status`.
@router.get("/graphql-status")
def graphql_status() -> Dict[str, Any]:
    router = get_graphql_router()
    if router is None:
        return {"status": "not_configured", "message": "Install 'strawberry-graphql' to enable GraphQL."}
    return {"status": "available", "message": "GraphQL router is mounted at /api/v1/graphql"}