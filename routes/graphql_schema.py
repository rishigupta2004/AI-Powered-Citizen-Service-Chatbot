"""Optional GraphQL schema scaffolding.

If `strawberry` is available, exposes a minimal schema for health checks.
Otherwise, provides helpers that indicate GraphQL is not configured.
"""

from typing import Any, List, Optional
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.models import Service, Procedure

try:
    import strawberry
    from strawberry.fastapi import GraphQLRouter

    # Simple per-request loader (sync) to avoid repeated DB hits for nested fields
    class ProcedureLoader:
        def __init__(self):
            self._cache = {}

        def load_many(self, service_ids: List[int]) -> dict:
            missing = [sid for sid in service_ids if sid not in self._cache]
            if missing:
                db = get_session()
                try:
                    rows = db.query(Procedure).filter(Procedure.service_id.in_(missing)).all()
                    by_service = {}
                    for r in rows:
                        by_service.setdefault(r.service_id, []).append(r)
                    for sid in missing:
                        self._cache[sid] = by_service.get(sid, [])
                finally:
                    db.close()
            return {sid: self._cache.get(sid, []) for sid in service_ids}

    @strawberry.type
    class ServiceType:
        service_id: int
        name: str
        category: str
        ministry: Optional[str]

        @strawberry.field
        def procedures(self, info, limit: int = 50, offset: int = 0) -> List["ProcedureType"]:
            loader: ProcedureLoader = info.context.get("procedure_loader") or ProcedureLoader()
            info.context["procedure_loader"] = loader
            data = loader.load_many([self.service_id]).get(self.service_id, [])
            sliced = data[offset: offset + limit]
            return [ProcedureType(procedure_id=r.procedure_id, service_id=r.service_id, title=r.title, description=r.description) for r in sliced]

    @strawberry.type
    class ProcedureType:
        procedure_id: int
        service_id: int
        title: str
        description: Optional[str]

    @strawberry.type
    class DocumentType:
        doc_id: int
        service_id: int
        name: str
        document_type: Optional[str]

    @strawberry.type
    class FAQType:
        faq_id: int
        service_id: int
        question: str
        answer: str

    def get_session() -> Session:
        return SessionLocal()

    @strawberry.type
    class Query:
        @strawberry.field
        def status(self) -> str:
            return "ok"

        @strawberry.field
        def services(self, info, limit: int = 50, offset: int = 0) -> List[ServiceType]:
            db = get_session()
            try:
                rows = db.query(Service).offset(offset).limit(limit).all()
                return [ServiceType(service_id=r.service_id, name=r.name, category=r.category, ministry=r.ministry) for r in rows]
            finally:
                db.close()

        @strawberry.field
        def procedures_by_service(self, info, service_id: int, limit: int = 100, offset: int = 0) -> List[ProcedureType]:
            db = get_session()
            try:
                rows = db.query(Procedure).filter(Procedure.service_id == service_id).offset(offset).limit(limit).all()
                return [ProcedureType(procedure_id=r.procedure_id, service_id=r.service_id, title=r.title, description=r.description) for r in rows]
            finally:
                db.close()

    schema = strawberry.Schema(query=Query)

    def get_graphql_router() -> Any:
        return GraphQLRouter(schema, context_getter=lambda request: {})
except Exception:
    schema = None

    def get_graphql_router() -> Any:
        return None