import os
from sqlalchemy.orm import Session
from backend.app.db import SessionLocal, engine
from backend.app import models

models.Base.metadata.create_all(bind=engine)

def seed():
    db: Session = SessionLocal()

    # Sample services
    passport = models.Service(name="Passport Seva", description="Passport application and renewal service", category="Identity")
    license = models.Service(name="Driving License", description="Issuance and renewal of DL", category="Transport")

    db.add_all([passport, license])
    db.commit()

    # Sample FAQs
    faq1 = models.FAQ(service_id=passport.service_id, question="How long does it take to get a passport?", answer="Typically 7-14 working days.")
    faq2 = models.FAQ(service_id=license.service_id, question="What documents are needed for DL?", answer="Address proof, ID proof, and recent photographs.")

    db.add_all([faq1, faq2])
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
    print("✅ Seed data inserted")

