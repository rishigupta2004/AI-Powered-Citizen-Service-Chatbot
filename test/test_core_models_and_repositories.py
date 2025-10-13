"""
Simple test script - tests core functionality without AI/ML dependencies
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_core_imports():
    """Test core database and model imports"""
    try:
        from core.database import get_db, Base, engine, SessionLocal
        from core.models import Service, Procedure, Document, FAQ, ContentChunk
        from core.repositories import ServiceRepository, DocumentRepository, FAQRepository
        print("✅ Core imports successful")
        return True
    except Exception as e:
        print(f"❌ Core import failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        from core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models_creation():
    """Test that models can be created"""
    try:
        from core.models import Service
        from core.database import SessionLocal
        from core.repositories import ServiceRepository
        
        db = SessionLocal()
        service_repo = ServiceRepository(db)
        
        # Test creating a service
        service = service_repo.create(
            name="Test Service",
            category="test",
            description="Test description",
            ministry="Test Ministry"
        )
        
        print(f"✅ Model creation successful - Service ID: {service.service_id}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def main():
    """Run basic tests"""
    print("🧪 Testing simplified system functionality...")
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Database Connection", test_database_connection),
        ("Model Creation", test_models_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Simplified system tests passed! Core functionality is working.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
