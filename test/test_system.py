"""
Test script for the streamlined system
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that all core modules can be imported"""
    try:
        from core.database import get_db, Base, engine
        from core.models import Service, Procedure, Document, FAQ, ContentChunk
        from core.repositories import ServiceRepository, DocumentRepository, FAQRepository
        from core.search import SearchEngine
        from core.processor import DocumentProcessor
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
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

def test_api_imports():
    """Test that the API can be imported"""
    try:
        import app
        print("✅ API imports successful")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing streamlined system...")
    
    tests = [
        ("Import Test", test_imports),
        ("Database Connection", test_database_connection),
        ("API Import", test_api_imports)
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
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
