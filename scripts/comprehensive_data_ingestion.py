"""
Comprehensive Data Ingestion Script
====================================
Ingests all data from:
1. Web scrapers (cached JSON files)
2. PDF documents from data/docs/
3. Stores everything properly in the data warehouse

Run: python scripts/comprehensive_data_ingestion.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from core.database import get_db, SessionLocal
from core.models import Service, Procedure, Document, FAQ, ContentChunk, RawContent
from core.repositories import ServiceRepository
from data.processing.document_parser import DocumentParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


BASE_SERVICES = [
    {
        'name': 'Passport Services',
        'category': 'passport',
        'description': 'Passport application, renewal, and related services',
        'ministry': 'Ministry of External Affairs'
    },
    {
        'name': 'Aadhaar Services',
        'category': 'aadhaar',
        'description': 'Aadhaar enrollment, updates, and verification',
        'ministry': 'UIDAI'
    },
    {
        'name': 'PAN Card Services',
        'category': 'pan',
        'description': 'PAN card application, correction, and verification',
        'ministry': 'Income Tax Department'
    },
    {
        'name': 'EPFO Services',
        'category': 'epfo',
        'description': 'EPF balance, passbook, and withdrawal services',
        'ministry': 'Ministry of Labour and Employment'
    },
    {
        'name': 'Driving License Services',
        'category': 'parivahan',
        'description': 'Driving license application, renewal, and verification',
        'ministry': 'Ministry of Road Transport and Highways'
    },
    {
        'name': 'Education Services',
        'category': 'education',
        'description': 'Scholarships, educational certificates, and related services',
        'ministry': 'Ministry of Education'
    },
    {
        'name': 'Railway Services',
        'category': 'railways',
        'description': 'Railway tickets, reservations, and travel information',
        'ministry': 'Ministry of Railways'
    },
    {
        'name': 'RBI Services',
        'category': 'rbi',
        'description': 'Banking, forex, and financial services',
        'ministry': 'Reserve Bank of India'
    },
]

CATEGORY_MAP = {
    'passport': 'passport',
    'aadhaar': 'aadhaar',
    'pan': 'pan',
    'epfo': 'epfo',
    'parivahan': 'parivahan',
    'education': 'education',
    'railways': 'railways',
    'rbi': 'rbi',
    'other': None,
}


class ComprehensiveDataIngestion:
    """Handles all data ingestion into the warehouse"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.service_repo = ServiceRepository(self.db)
        self.doc_parser = DocumentParser()
        self.stats = {
            'scraped_files': 0,
            'pdf_files': 0,
            'services_created': 0,
            'procedures_created': 0,
            'documents_created': 0,
            'faqs_created': 0,
            'chunks_created': 0,
            'raw_content_created': 0,
            'errors': []
        }
    
    def ingest_all(self):
        """Main ingestion orchestrator"""
        logger.info("🚀 Starting comprehensive data ingestion...")
        
        try:
            # Step 1: Ensure base services exist
            self._ensure_base_services()
            
            # Step 2: Ingest scraped web content
            self._ingest_scraped_data()
            
            # Step 3: Ingest PDF documents
            self._ingest_pdf_documents()
            
            # Step 4: Print summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Fatal error during ingestion: {e}", exc_info=True)
            self.stats['errors'].append(str(e))
        finally:
            self.db.close()
    
    def _ensure_base_services(self):
        """Create base government services if they don't exist"""
        logger.info("📋 Ensuring base services exist...")
        
        for service_data in BASE_SERVICES:
            # Check if service exists
            existing = self.db.query(Service).filter(
                Service.category == service_data['category']
            ).first()
            
            if not existing:
                service = Service(**service_data)
                self.db.add(service)
                self.stats['services_created'] += 1
                logger.info(f"✅ Created service: {service_data['name']}")
        
        self.db.commit()
    
    def _ingest_scraped_data(self):
        """Ingest data from web scrapers cache"""
        logger.info("🕷️  Ingesting scraped web content...")
        
        cache_dir = project_root / 'data' / 'cache' / 'scrapers'
        if not cache_dir.exists():
            logger.warning(f"Scraper cache directory not found: {cache_dir}")
            return
        
        for json_file in cache_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Store as raw content
                raw_content = RawContent(
                    source_type='scraping',
                    source_url=cache_data.get('url', ''),
                    source_name=f"Scraped: {cache_data.get('url', 'Unknown')}",
                    title=f"Cache: {json_file.name}",
                    content=json.dumps(cache_data),
                    content_type='json',
                    metadata_json=cache_data,
                    is_processed=True,
                    processing_status='completed'
                )
                
                self.db.add(raw_content)
                self.stats['scraped_files'] += 1
                self.stats['raw_content_created'] += 1
                
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
                self.stats['errors'].append(f"Scraper {json_file.name}: {str(e)}")
        
        self.db.commit()
        logger.info(f"✅ Ingested {self.stats['scraped_files']} scraped files")
    
    def _ingest_pdf_documents(self):
        """Ingest PDF documents from data/docs/"""
        logger.info("📄 Ingesting PDF documents...")
        
        docs_dir = project_root / 'data' / 'docs'
        if not docs_dir.exists():
            logger.warning(f"Docs directory not found: {docs_dir}")
            return
        
        for category_dir, category in CATEGORY_MAP.items():
            dir_path = docs_dir / category_dir
            if not dir_path.exists():
                continue
            
            # Get service for this category
            service = None
            if category:
                service = self.db.query(Service).filter(
                    Service.category == category
                ).first()
            
            # Process all PDFs in this directory
            for pdf_file in dir_path.glob('*.pdf'):
                try:
                    self._process_pdf_file(pdf_file, service)
                except Exception as e:
                    logger.error(f"Error processing {pdf_file}: {e}")
                    self.stats['errors'].append(f"PDF {pdf_file.name}: {str(e)}")
        
        self.db.commit()
        logger.info(f"✅ Ingested {self.stats['pdf_files']} PDF files")
    
    def _process_pdf_file(self, pdf_path: Path, service: Service = None):
        """Process a single PDF file"""
        logger.info(f"Processing: {pdf_path.name}")
        
        # Extract text
        text_chunks = self.doc_parser.parse_pdf(str(pdf_path))
        
        if not text_chunks:
            logger.warning(f"No text extracted from {pdf_path.name}")
            return
        
        text_content = '\n\n'.join(text_chunks)
        
        # Store as raw content
        raw_content = RawContent(
            source_type='pdf',
            source_url=str(pdf_path),
            source_name=pdf_path.name,
            title=pdf_path.stem.replace('-', ' ').title(),
            content=text_content,
            content_type='pdf',
            language='en',
            file_path=str(pdf_path),
            file_size_bytes=pdf_path.stat().st_size,
            is_processed=True,
            processing_status='completed',
            metadata_json={'chunks': len(text_chunks)}
        )
        
        self.db.add(raw_content)
        self.db.flush()  # Get the ID
        self.stats['raw_content_created'] += 1
        
        # Create document entry if we have a service
        if service:
            document = Document(
                service_id=service.service_id,
                name=pdf_path.stem.replace('-', ' ').title(),
                description=f"Document extracted from {pdf_path.name}",
                document_type='pdf',
                is_mandatory=False,
                raw_content=text_content[:10000],  # First 10k chars
                is_processed=True
            )
            
            self.db.add(document)
            self.stats['documents_created'] += 1
        
        # Create content chunks (for search)
        self._store_chunks(text_content, service)
        
        self.stats['pdf_files'] += 1
    
    def _create_chunks(self, text: str, service: Service = None, chunk_size: int = 500) -> list:
        """Split text into chunks for better search"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:  # Only add meaningful chunks
                chunks.append(chunk)
        
        return chunks

    def _store_chunks(self, text: str, service: Service = None) -> None:
        for chunk_text in self._create_chunks(text, service):
            self.db.add(
                ContentChunk(
                    content_text=chunk_text,
                    service_id=service.service_id if service else None,
                    category=service.category if service else 'general',
                )
            )
            self.stats['chunks_created'] += 1
    
    def _print_summary(self):
        """Print ingestion summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 DATA INGESTION SUMMARY")
        logger.info("="*60)
        for k in [
            'services_created','scraped_files','pdf_files','documents_created','chunks_created','raw_content_created'
        ]:
            logger.info(f"{k.replace('_',' ').title():<24} {self.stats[k]}")
        logger.info(f"{'Total errors':<24} {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            logger.info("\n⚠️  ERRORS:")
            for error in self.stats['errors'][:10]:  # Show first 10
                logger.info(f"  - {error}")
            if len(self.stats['errors']) > 10:
                logger.info(f"  ... and {len(self.stats['errors']) - 10} more")
        
        logger.info("="*60)


if __name__ == "__main__":
    ingestion = ComprehensiveDataIngestion()
    ingestion.ingest_all()
    print("\n✅ Data ingestion complete! Run 'python scripts/view_warehouse_data.py' to inspect the data.")

