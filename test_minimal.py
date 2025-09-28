"""
Minimal test script - tests only database connection
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_database_connection():
    """Test database connection"""
    try:
        from sqlalchemy import create_engine, text
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/citizen_services_dev")
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_sqlalchemy_imports():
    """Test SQLAlchemy imports"""
    try:
        from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func
        from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
        from sqlalchemy.orm import sessionmaker, declarative_base
        print("✅ SQLAlchemy imports successful")
        return True
    except Exception as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False

def test_fastapi_imports():
    """Test FastAPI imports"""
    try:
        from fastapi import FastAPI, Depends, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ FastAPI imports successful")
        return True
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("🧪 Testing minimal system functionality...")
    
    tests = [
        ("SQLAlchemy Imports", test_sqlalchemy_imports),
        ("FastAPI Imports", test_fastapi_imports),
        ("Database Connection", test_database_connection)
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
        print("🎉 Minimal system tests passed! Basic dependencies are working.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
