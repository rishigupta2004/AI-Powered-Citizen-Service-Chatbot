"""
Test Document Processing Pipeline
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_pdf_processing():
    """Test PDF processing with sample documents"""
    try:
        from core.processor import DocumentProcessor
        from core.database import SessionLocal
        from core.repositories import ServiceRepository
        
        db = SessionLocal()
        processor = DocumentProcessor(db)
        service_repo = ServiceRepository(db)
        
        # Get or create a test service
        service = service_repo.get_by_category("passport")
        if not service:
            service = service_repo.create(
                name="Passport Services",
                category="passport",
                description="Test passport service",
                ministry="Ministry of External Affairs"
            )
        
        # Test with a real sample PDF from repo if available
        # Use repository PDF path directly
        sample_pdf = "data/docs/passport/passport-applicationforminstructionbooklet-v3-0-pdf-27.pdf"
        if os.path.exists(sample_pdf):
            result = processor.process_document(sample_pdf, service[0].service_id)
            print(f"✅ PDF processing successful: {result}")
        else:
            print("⚠️  Sample PDF not found, testing with dummy content")
            # Create a test document
            from core.models import Document
            doc = Document(
                service_id=service[0].service_id,
                name="Test Document",
                description="Test document for processing",
                document_type="pdf",
                raw_content="This is test content for passport application process.",
                is_processed=True
            )
            db.add(doc)
            db.commit()
            print("✅ Test document created successfully")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ PDF processing failed: {e}")
        return False

def test_document_classification():
    """Test document classification"""
    try:
        from data.processing.classifier import DocumentClassifier
        
        classifier = DocumentClassifier()
        
        # Test classification
        test_text = "Passport application form for Indian citizens"
        category = classifier.classify_document(test_text)
        print(f"✅ Document classification successful: {category}")
        return True
    except Exception as e:
        print(f"❌ Document classification failed: {e}")
        return False

def test_document_parser():
    """Test document parser"""
    try:
        from data.processing.document_parser import DocumentParser
        
        parser = DocumentParser()
        
        # Test parsing
        test_content = "This is a test document with some content."
        parsed = parser.parse_content(test_content)
        print(f"✅ Document parsing successful: {len(parsed)} characters parsed")
        return True
    except Exception as e:
        print(f"❌ Document parsing failed: {e}")
        return False

def test_document_storage():
    """Test document storage"""
    try:
        from data.processing.store_documents import DocumentStore
        from core.database import SessionLocal
        
        db = SessionLocal()
        store = DocumentStore(db)
        
        print("✅ Document storage module imported successfully")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Document storage failed: {e}")
        return False

def main():
    """Run document processing tests"""
    print("🧪 Testing document processing pipeline...")
    
    tests = [
        ("Document Parser", test_document_parser),
        ("Document Classifier", test_document_classification),
        ("Document Storage", test_document_storage),
        ("PDF Processing", test_pdf_processing)
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
        print("🎉 Document processing pipeline is working!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
