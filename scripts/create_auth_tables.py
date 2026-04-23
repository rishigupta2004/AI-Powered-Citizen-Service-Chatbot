"""
Create authentication tables in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, SessionLocal
from core.auth_models import Base

def create_auth_tables():
    """Create all authentication tables"""
    try:
        print("Creating authentication tables...")
        
        # Create all tables defined in auth_models
        Base.metadata.create_all(bind=engine)
        
        print("✅ Authentication tables created successfully!")
        
        # Verify tables were created
        db = SessionLocal()
        try:
            # Check if tables exist by querying metadata
            inspector = db.get_bind().dialect.inspector(db.get_bind())
            tables = inspector.get_table_names()
            
            auth_tables = [
                'users', 'user_auth_methods', 'user_sessions', 
                'otp_attempts', 'password_resets', 'login_attempts'
            ]
            
            print("\n📊 Table Status:")
            for table in auth_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - Missing!")
            
            print(f"\nTotal tables in database: {len(tables)}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating authentication tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_auth_tables()
    if success:
        print("\n🎉 Authentication system ready!")
        print("You can now use the authentication endpoints.")
    else:
        print("\n💥 Failed to create authentication tables.")
        sys.exit(1)
