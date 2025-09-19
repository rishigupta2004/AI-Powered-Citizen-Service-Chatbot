from sqlalchemy.orm import Session
from . import models

def get_services(db: Session):
    return db.query(models.Service).all()

def create_service(db: Session, name: str, description: str, category: str = None):
    service = models.Service(name=name, description=description, category=category)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service
