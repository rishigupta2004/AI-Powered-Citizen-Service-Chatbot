"""
Test Data Ingestion Pipeline
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_api_clients():
    """Test API clients"""
    try:
        from data.ingestion.api_clients.passport import PassportAPIClient
        from data.ingestion.api_clients.aadhaar import AadhaarAPIClient
        from data.ingestion.api_clients.pan import PANAPIClient
        
        # Test passport client
        passport_client = PassportAPIClient()
        print("✅ Passport API client created successfully")
        
        # Test aadhaar client
        aadhaar_client = AadhaarAPIClient()
        print("✅ Aadhaar API client created successfully")
        
        # Test PAN client
        pan_client = PANAPIClient()
        print("✅ PAN API client created successfully")
        
        return True
    except Exception as e:
        print(f"❌ API clients test failed: {e}")
        return False

def test_scrapers():
    """Test web scrapers"""
    try:
        from data.ingestion.scrapers.passport_scraper import PassportScraper
        from data.ingestion.scrapers.aadhaar_scraper import AadhaarScraper
        from data.ingestion.scrapers.pan_scraper import PANScraper
        
        # Test passport scraper
        passport_scraper = PassportScraper()
        print("✅ Passport scraper created successfully")
        
        # Test aadhaar scraper
        aadhaar_scraper = AadhaarScraper()
        print("✅ Aadhaar scraper created successfully")
        
        # Test PAN scraper
        pan_scraper = PANScraper()
        print("✅ PAN scraper created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Scrapers test failed: {e}")
        return False

def test_data_validation():
    """Test data validation"""
    try:
        from data.ingestion.api_clients.schemas import ServiceSchema, ProcedureSchema
        
        # Test service schema
        service_data = {
            "name": "Test Service",
            "category": "test",
            "description": "Test description",
            "ministry": "Test Ministry"
        }
        service_schema = ServiceSchema(**service_data)
        print("✅ Service schema validation successful")
        
        # Test procedure schema
        procedure_data = {
            "title": "Test Procedure",
            "description": "Test procedure description",
            "procedure_type": "application"
        }
        procedure_schema = ProcedureSchema(**procedure_data)
        print("✅ Procedure schema validation successful")
        
        return True
    except Exception as e:
        print(f"❌ Data validation test failed: {e}")
        return False

def test_database_integration():
    """Test database integration"""
    try:
        from core.database import SessionLocal
        from core.repositories import ServiceRepository, DocumentRepository
        from data.ingestion.api_clients.passport import PassportAPIClient
        
        db = SessionLocal()
        service_repo = ServiceRepository(db)
        document_repo = DocumentRepository(db)
        
        # Create test service
        service = service_repo.create(
            name="Test Passport Service",
            category="passport",
            description="Test passport service for ingestion",
            ministry="Ministry of External Affairs"
        )
        
        # Create test document
        document = document_repo.create(
            service_id=service.service_id,
            name="Test Document",
            description="Test document for ingestion",
            document_type="pdf",
            raw_content="Test content for passport application"
        )
        
        print(f"✅ Database integration successful - Service ID: {service.service_id}, Document ID: {document.doc_id}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def main():
    """Run ingestion tests"""
    print("🧪 Testing data ingestion pipeline...")
    
    tests = [
        ("API Clients", test_api_clients),
        ("Web Scrapers", test_scrapers),
        ("Data Validation", test_data_validation),
        ("Database Integration", test_database_integration)
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
        print("🎉 Data ingestion pipeline is working!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
