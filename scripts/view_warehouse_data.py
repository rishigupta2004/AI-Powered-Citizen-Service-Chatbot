"""
Data Warehouse Viewer
=====================
View all data stored in the warehouse with detailed statistics and samples

Run: python scripts/view_warehouse_data.py
Options:
  --detailed    Show detailed samples from each table
  --export      Export data to JSON files
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import argparse
from datetime import datetime
from sqlalchemy import func, text

from core.database import SessionLocal
from core.models import Service, Procedure, Document, FAQ, ContentChunk, RawContent


def _json_safe_default(o):
    try:
        import numpy as _np
        if isinstance(o, (_np.floating,)):
            return float(o)
        if isinstance(o, (_np.integer,)):
            return int(o)
        if isinstance(o, _np.ndarray):
            return o.tolist()
    except Exception:
        pass
    if hasattr(o, 'tolist'):
        try:
            return o.tolist()
        except Exception:
            pass
    return str(o)

class WarehouseViewer:
    """View and inspect data warehouse contents"""
    
    def __init__(self, detailed=False, export=False):
        self.db = SessionLocal()
        self.detailed = detailed
        self.export = export
        self.export_dir = project_root / 'data' / 'exports'
        
        if self.export:
            self.export_dir.mkdir(exist_ok=True)
    
    def view_all(self):
        """View all warehouse data"""
        print("\n" + "="*80)
        print("📊 DATA WAREHOUSE CONTENTS")
        print("="*80)
        
        self._view_services()
        self._view_procedures()
        self._view_documents()
        self._view_faqs()
        self._view_content_chunks()
        self._view_raw_content()
        self._view_database_stats()
        
        print("\n" + "="*80)
        print("✅ Warehouse inspection complete!")
        print("="*80 + "\n")
        
        self.db.close()
    
    def _view_services(self):
        """View services table"""
        print("\n" + "-"*80)
        print("🏛️  SERVICES")
        print("-"*80)
        
        services = self.db.query(Service).all()
        print(f"Total services: {len(services)}")
        
        if services:
            print("\n{:<5} {:<30} {:<15} {:<30}".format(
                "ID", "Name", "Category", "Ministry"
            ))
            print("-" * 80)
            
            for service in services:
                print("{:<5} {:<30} {:<15} {:<30}".format(
                    service.service_id,
                    service.name[:29],
                    service.category,
                    (service.ministry or 'N/A')[:29]
                ))
            
            if self.detailed:
                print("\n📋 Sample Service Details:")
                sample = services[0]
                print(f"  UUID: {sample.uuid}")
                print(f"  Name: {sample.name}")
                print(f"  Category: {sample.category}")
                print(f"  Description: {sample.description}")
                print(f"  Ministry: {sample.ministry}")
                print(f"  Active: {sample.is_active}")
                print(f"  Languages: {sample.languages_supported}")
                print(f"  Created: {sample.created_at}")
        
        if self.export:
            self._export_table_data('services', services)
    
    def _view_procedures(self):
        """View procedures table"""
        print("\n" + "-"*80)
        print("📝 PROCEDURES")
        print("-"*80)
        
        procedures = self.db.query(Procedure).all()
        print(f"Total procedures: {len(procedures)}")
        
        if procedures and self.detailed:
            print("\n{:<5} {:<40} {:<15} {:<15}".format(
                "ID", "Title", "Type", "Service"
            ))
            print("-" * 80)
            
            for proc in procedures[:10]:  # Show first 10
                service_name = self.db.query(Service).get(proc.service_id).name if proc.service_id else "N/A"
                print("{:<5} {:<40} {:<15} {:<15}".format(
                    proc.procedure_id,
                    proc.title[:39],
                    (proc.procedure_type or 'N/A')[:14],
                    service_name[:14]
                ))
        
        if self.export:
            self._export_table_data('procedures', procedures)
    
    def _view_documents(self):
        """View documents table"""
        print("\n" + "-"*80)
        print("📄 DOCUMENTS")
        print("-"*80)
        
        documents = self.db.query(Document).all()
        print(f"Total documents: {len(documents)}")
        
        # Group by service
        by_service = {}
        for doc in documents:
            service_id = doc.service_id
            if service_id not in by_service:
                service = self.db.query(Service).get(service_id)
                by_service[service_id] = {
                    'name': service.name if service else 'Unknown',
                    'count': 0
                }
            by_service[service_id]['count'] += 1
        
        if by_service:
            print("\n📊 Documents by Service:")
            print("{:<30} {:>10}".format("Service", "Count"))
            print("-" * 42)
            for service_id, data in by_service.items():
                print("{:<30} {:>10}".format(data['name'][:29], data['count']))
        
        if self.detailed and documents:
            print("\n📋 Sample Document:")
            sample = documents[0]
            print(f"  ID: {sample.doc_id}")
            print(f"  Name: {sample.name}")
            print(f"  Type: {sample.document_type}")
            print(f"  Mandatory: {sample.is_mandatory}")
            print(f"  Processed: {sample.is_processed}")
            print(f"  Raw Content (first 200 chars): {sample.raw_content[:200] if sample.raw_content else 'N/A'}")
        
        if self.export:
            self._export_table_data('documents', documents)
    
    def _view_faqs(self):
        """View FAQs table"""
        print("\n" + "-"*80)
        print("❓ FAQs")
        print("-"*80)
        
        faqs = self.db.query(FAQ).all()
        print(f"Total FAQs: {len(faqs)}")
        
        if faqs and self.detailed:
            print("\n📋 Sample FAQs:")
            for faq in faqs[:3]:  # Show first 3
                print(f"\n  Q: {faq.question[:100]}")
                print(f"  A: {faq.answer[:150]}...")
        
        if self.export:
            self._export_table_data('faqs', faqs)
    
    def _view_content_chunks(self):
        """View content chunks table"""
        print("\n" + "-"*80)
        print("🔍 CONTENT CHUNKS")
        print("-"*80)
        
        chunks = self.db.query(ContentChunk).all()
        print(f"Total content chunks: {len(chunks)}")
        
        # Group by category
        by_category = self.db.query(
            ContentChunk.category,
            func.count(ContentChunk.chunk_id)
        ).group_by(ContentChunk.category).all()
        
        if by_category:
            print("\n📊 Chunks by Category:")
            print("{:<20} {:>10}".format("Category", "Count"))
            print("-" * 32)
            for category, count in by_category:
                print("{:<20} {:>10}".format(category or 'None', count))
        
        if self.detailed and chunks:
            print("\n📋 Sample Chunk:")
            sample = chunks[0]
            print(f"  ID: {sample.chunk_id}")
            print(f"  Category: {sample.category}")
            print(f"  Content (first 200 chars): {sample.content_text[:200]}")
            print(f"  Has Embedding: {sample.embedding is not None}")
        
        if self.export:
            self._export_table_data('content_chunks', chunks)
    
    def _view_raw_content(self):
        """View raw content table"""
        print("\n" + "-"*80)
        print("📦 RAW CONTENT")
        print("-"*80)
        
        raw_contents = self.db.query(RawContent).all()
        print(f"Total raw content entries: {len(raw_contents)}")
        
        # Group by source type
        by_source = self.db.query(
            RawContent.source_type,
            func.count(RawContent.content_id)
        ).group_by(RawContent.source_type).all()
        
        if by_source:
            print("\n📊 Content by Source Type:")
            print("{:<15} {:>10}".format("Source Type", "Count"))
            print("-" * 27)
            for source_type, count in by_source:
                print("{:<15} {:>10}".format(source_type, count))
        
        # Group by processing status
        by_status = self.db.query(
            RawContent.processing_status,
            func.count(RawContent.content_id)
        ).group_by(RawContent.processing_status).all()
        
        if by_status:
            print("\n📊 Content by Processing Status:")
            print("{:<15} {:>10}".format("Status", "Count"))
            print("-" * 27)
            for status, count in by_status:
                print("{:<15} {:>10}".format(status or 'None', count))
        
        if self.detailed and raw_contents:
            print("\n📋 Sample Raw Content:")
            sample = raw_contents[0]
            print(f"  ID: {sample.content_id}")
            print(f"  Source Type: {sample.source_type}")
            print(f"  Source URL: {sample.source_url}")
            print(f"  Title: {sample.title}")
            print(f"  Content Type: {sample.content_type}")
            print(f"  Processed: {sample.is_processed}")
            print(f"  Status: {sample.processing_status}")
            print(f"  Content (first 200 chars): {sample.content[:200] if sample.content else 'N/A'}")
        
        if self.export:
            self._export_table_data('raw_content', raw_contents)
    
    def _view_database_stats(self):
        """View overall database statistics"""
        print("\n" + "-"*80)
        print("💾 DATABASE STATISTICS")
        print("-"*80)
        
        try:
            # Table sizes
            result = self.db.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    pg_total_relation_size(schemaname||'.'||tablename) as bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY bytes DESC
            """))
            
            print("\n📊 Table Sizes:")
            print("{:<25} {:>15}".format("Table", "Size"))
            print("-" * 42)
            for row in result:
                print("{:<25} {:>15}".format(row[1], row[2]))
        
        except Exception as e:
            print(f"Could not fetch database stats: {e}")
        
        # Total record counts
        print("\n📊 Record Counts:")
        tables = [
            ('services', Service),
            ('procedures', Procedure),
            ('documents', Document),
            ('faqs', FAQ),
            ('content_chunks', ContentChunk),
            ('raw_content', RawContent)
        ]
        
        print("{:<25} {:>15}".format("Table", "Records"))
        print("-" * 42)
        total = 0
        for table_name, model in tables:
            count = self.db.query(model).count()
            total += count
            print("{:<25} {:>15,}".format(table_name, count))
        print("-" * 42)
        print("{:<25} {:>15,}".format("TOTAL", total))
    
    def _export_table_data(self, table_name, data):
        """Export table data to JSON"""
        export_file = self.export_dir / f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert SQLAlchemy objects to dicts
        export_data = []
        for item in data:
            item_dict = {}
            for column in item.__table__.columns:
                value = getattr(item, column.name)
                # Handle non-serializable types
                if isinstance(value, datetime):
                    item_dict[column.name] = value.isoformat()
                elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                    item_dict[column.name] = list(value)
                else:
                    item_dict[column.name] = str(value) if value is not None else None
            export_data.append(item_dict)
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=_json_safe_default)
        
        print(f"  💾 Exported to: {export_file}")


def main():
    parser = argparse.ArgumentParser(description='View data warehouse contents')
    parser.add_argument('--detailed', action='store_true', help='Show detailed samples')
    parser.add_argument('--export', action='store_true', help='Export data to JSON files')
    parser.add_argument('--tables', type=str, default='', help='Comma-separated tables to show (services,procedures,documents,faqs,content_chunks,raw_content,stats)')
    
    args = parser.parse_args()
    
    viewer = WarehouseViewer(detailed=args.detailed, export=args.export)
    selected = set([t.strip() for t in (args.tables or '').split(',') if t.strip()])
    if not selected:
        viewer.view_all()
        return
    print("\n" + "="*80)
    print("📊 DATA WAREHOUSE CONTENTS (filtered)")
    print("="*80)
    if 'services' in selected: viewer._view_services()
    if 'procedures' in selected: viewer._view_procedures()
    if 'documents' in selected: viewer._view_documents()
    if 'faqs' in selected: viewer._view_faqs()
    if 'content_chunks' in selected: viewer._view_content_chunks()
    if 'raw_content' in selected: viewer._view_raw_content()
    if 'stats' in selected or not selected: viewer._view_database_stats()


if __name__ == "__main__":
    main()

