from backend.app.db import SessionLocal
from backend.app.repositories.service_repository import get_services

db = SessionLocal()
services = get_services(db)
for s in services:
    print(f"{s.service_id}: {s.name} - {s.description}")
db.close()
