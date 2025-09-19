from sqlalchemy.orm import Session
from backend.app import models

def get_services(db: Session):
    return db.query(models.Service).all()

def get_service_by_id(db: Session, service_id: int):
    return db.query(models.Service).filter(models.Service.service_id == service_id).first()

def create_service(db: Session, name: str, description: str, category: str = None):
    service = models.Service(name=name, description=description, category=category)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service
