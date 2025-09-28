"""
Streamlined Database Initialization
"""
import os
from sqlalchemy import create_engine, text
from core.database import Base, DATABASE_URL

def init_database():
    """Initialize the database with schema and sample data"""
    try:
        print("🚀 Initializing database...")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Enable extensions
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            conn.commit()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Insert sample data
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        from core.models import Service
        from core.repositories import ServiceRepository
        
        service_repo = ServiceRepository(db)
        
        # Check if data already exists
        if service_repo.count() > 0:
            print("ℹ️  Data already exists, skipping...")
            db.close()
            return
        
        # Insert sample services
        services_data = [
            {
                'name': 'Passport Services',
                'category': 'passport',
                'description': 'Passport application, renewal, and correction services',
                'ministry': 'Ministry of External Affairs',
                'languages_supported': ['en', 'hi']
            },
            {
                'name': 'Aadhaar Services',
                'category': 'aadhaar',
                'description': 'Aadhaar enrollment, updates, and verification',
                'ministry': 'Ministry of Electronics and IT',
                'languages_supported': ['en', 'hi']
            },
            {
                'name': 'PAN Card Services',
                'category': 'pan',
                'description': 'PAN card application and correction services',
                'ministry': 'Ministry of Finance',
                'languages_supported': ['en', 'hi']
            },
            {
                'name': 'EPFO Services',
                'category': 'epfo',
                'description': 'EPF passbook and balance inquiry services',
                'ministry': 'Ministry of Labour',
                'languages_supported': ['en', 'hi']
            },
            {
                'name': 'Driving License Services',
                'category': 'driving',
                'description': 'Driving license application and renewal services',
                'ministry': 'Ministry of Road Transport',
                'languages_supported': ['en', 'hi']
            }
        ]
        
        for service_data in services_data:
            service_repo.create(**service_data)
        
        print(f"✅ Inserted {len(services_data)} services")
        db.commit()
        db.close()
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()
