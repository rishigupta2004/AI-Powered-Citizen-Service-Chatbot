from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.api.deps import get_db
from backend.app.repositories.service_repository import get_services, create_service

router = APIRouter()

@router.get("/")
def list_services(db: Session = Depends(get_db)):
    services = get_services(db)
    return [{"id": s.service_id, "name": s.name, "description": s.description} for s in services]

@router.post("/")
def add_service(name: str, description: str, category: str = None, db: Session = Depends(get_db)):
    service = create_service(db, name, description, category)
    return {"id": service.service_id, "name": service.name}
