"""
Comprehensive System Test - Tests all components including ingestion and processing
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

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

def test_pgvector_extension():
    """Test pgvector extension"""
    try:
        from core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone():
                print("✅ pgvector extension is installed")
                return True
            else:
                print("❌ pgvector extension not found")
                return False
    except Exception as e:
        print(f"❌ pgvector test failed: {e}")
        return False

def test_models_creation():
    """Test that models can be created"""
    try:
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

def test_ingestion_clients():
    """Test ingestion API clients"""
    try:
        from data.ingestion.api_clients.passport import PassportAPIClient
        from data.ingestion.api_clients.aadhaar import AadhaarAPIClient
        
        print("✅ Ingestion API clients imported successfully")
        return True
    except Exception as e:
        print(f"❌ Ingestion clients import failed: {e}")
        return False

def test_scrapers():
    """Test web scrapers"""
    try:
        from data.ingestion.scrapers.passport_scraper import PassportScraper
        from data.ingestion.scrapers.aadhaar_scraper import AadhaarScraper
        
        print("✅ Web scrapers imported successfully")
        return True
    except Exception as e:
        print(f"❌ Scrapers import failed: {e}")
        return False

def test_document_processing():
    """Test document processing"""
    try:
        from data.processing.document_parser import DocumentParser
        from data.processing.classifier import DocumentClassifier
        from data.processing.store_documents import DocumentStore
        
        print("✅ Document processing modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Document processing import failed: {e}")
        return False

def test_vector_search():
    """Test vector search functionality"""
    try:
        from core.search import SearchEngine
        from core.database import SessionLocal
        
        db = SessionLocal()
        search_engine = SearchEngine(db)
        
        # Test search
        results = search_engine.search("passport application", limit=5)
        print(f"✅ Vector search working - Found {results['total_results']} results")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Vector search failed: {e}")
        return False

def test_document_processor():
    """Test document processor"""
    try:
        from core.processor import DocumentProcessor
        from core.database import SessionLocal
        
        db = SessionLocal()
        processor = DocumentProcessor(db)
        
        print("✅ Document processor imported successfully")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Document processor failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI application"""
    try:
        import app
        print("✅ FastAPI application imported successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False

def main():
    """Run comprehensive system tests"""
    print("🧪 Testing complete system functionality...")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("pgvector Extension", test_pgvector_extension),
        ("Model Creation", test_models_creation),
        ("Ingestion Clients", test_ingestion_clients),
        ("Web Scrapers", test_scrapers),
        ("Document Processing", test_document_processing),
        ("Vector Search", test_vector_search),
        ("Document Processor", test_document_processor),
        ("FastAPI App", test_fastapi_app)
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
        print("🎉 All system tests passed! The data warehouse is fully functional.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
